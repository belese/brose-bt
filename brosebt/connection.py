import asyncio
import struct
from collections import defaultdict 
import logging

from bleak import BleakScanner, BleakClient

log = logging.getLogger(__name__)


def chunks(proto_message, max_packet_size):
    message = struct.pack('<H',len(proto_message)) + proto_message
    total_chunks = (len(message) + max_packet_size - 1) // max_packet_size
    for j,i in enumerate(range(0, len(message), max_packet_size)):
        yield message[i:i+max_packet_size], j, total_chunks


def require_connection(func):
    async def wrapper(self, *args, **kwargs):
        if not self.client.is_connected:
            await self.client.connect()
            if not self.client.is_connected:
                raise Exception("Not connected")
            log.info('Client connected')
        return await func(self, *args, **kwargs)
    return wrapper

class BleConnection:

    UID_SEND = "31be3634-d927-11e9-8a34-2a2ae2dbcce4"
    UID_RECEIVE = "31be32ba-d927-11e9-8a34-2a2ae2dbcce4"
    UID_SERVICE = "31be2300-d927-11e9-8a34-2a2ae2dbcce4"

    def __init__(self, mac):
        self.client = BleakClient(mac)
        self.received_chunks = defaultdict(list)
        self.queues = defaultdict(asyncio.Queue)

    async def write_message(self, message, uid=None, uid_receive=None):
        uid = uid or self.UID_SEND
        if uid_receive is not False :
            uid_receive = uid_receive or self.UID_RECEIVE
        message_chunks = chunks(message, 15)
        for packet, i, total in message_chunks:
            await self.send_packet(packet, i, total, uid)
        if uid_receive is not False :
            return await self.queues[uid_receive].get()

    @require_connection
    async def pair(self):
        await self.client.pair()
    
    @require_connection
    async def unpair(self):
        await self.client.unpair()
    
    @require_connection
    async def send_packet(self, packet, id, total, uid=None):
        trame_id = id
        if id == total - 1:
            last_msg_mask = 0x80
            trame_id = last_msg_mask | trame_id
        trame_id = struct.pack('B', trame_id)
        data = trame_id + packet
        log.debug(f'Sendind a packet {id+1}/{total} to {uid} - {id} : {data.hex()}')
        await self.client.write_gatt_char(uid, data, False)

    def handle_packet(self, uid, trame_id, packet):
        id = trame_id & 0x0F
        log.debug(f'Receiving a packet from {uid.uuid} - {id} : {packet.hex()}')
        
        is_last_msg = trame_id & 0x80 == 0x80

        self.received_chunks[uid.uuid].append(packet)

        if is_last_msg:
            received_data = b"".join(self.received_chunks[uid.uuid])
            del self.received_chunks[uid.uuid]
            lenght = struct.unpack('<H', received_data[0:2])[0]
            received_message = received_data[2:lenght+2]
            # Process the complete message as needed
            log.debug(f"Receiving message complete ({lenght} bytes) from {uid.uuid}\n>> {received_message.hex()}")
            self.queues[uid.uuid].put_nowait(received_message)

    async def notification_handler(self, sender: int, data: bytearray):
        trame_id, packet = data[0], data[1:]
        self.handle_packet(sender,trame_id, packet)

    @require_connection
    async def start_listening(self, uid=None):
        uid = uid or self.UID_RECEIVE
        await self.client.start_notify(uid, self.notification_handler)

    @require_connection
    async def stop_listening(self, uid=None):
        uid = uid or self.UID_RECEIVE
        await self.client.stop_notify(uid)
    
    @require_connection
    async def debug(self) :
        for service in self.client.services:
            log.info(f"[Service] {service.uuid}: {service.description}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await self.client.read_gatt_char(char.uuid))
                    except Exception as e:
                        value = str(e).encode()
                else:
                    value = None
                properties = ",".join(char.properties)
                log.info(
                    f"\t[Characteristic] {char.uuid}: ({properties}) | Name: {char.description}, Value: {value}"
                )
                for descriptor in char.descriptors:
                    value = await self.client.read_gatt_descriptor(descriptor.handle)
                    log.info(f"\t\t[Descriptor] {descriptor.uuid}: (Handle: {descriptor.handle}) | Value: {bytes(value)}")

    @classmethod
    async def auto(cls) :
        import threading
        stop_event = asyncio.Event()
        cb_lock = threading.Lock()
        bike_device = None

        def callback(device, advertising_data):
            nonlocal cb_lock
            with cb_lock :
                nonlocal bike_device
                if stop_event.is_set() :
                    return
                if cls.UID_SERVICE in advertising_data.service_uuids:
                    stop_event.set()
                    log.debug(f'Found a bike ble device {device}')
                    bike_device = device
        
        async with BleakScanner(callback) as scanner:
            await stop_event.wait()

        bike = cls(bike_device.address)
        await bike.pair()
        return bike                


async def main():
    import sys
    log.setLevel(logging.DEBUG)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.DEBUG)
    log.addHandler(h)
    
    my_bike_connection = await BleConnection.auto()
    print (my_bike_connection)
    await my_bike_connection.debug()
    #TODO scan and trust device, your device must be already trusted (ont time) (with hcitool for example)
    #mac = "DB:6A:44:0C:7A:5C"
    #client = BleConnection(mac)
    #await client.debug()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main())