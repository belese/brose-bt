import time
import asyncio
import brose_pb2 as brose
from bleak import BleakClient
import struct
import logging

log = logging.getLogger(__name__)

import brose_pb2 as brose

class BroseEbike:
    def __init__(self, connection):
        # Initialisez la connexion ou les ressources nécessaires ici
        self.connection = connection
        self._live_data =  brose.V1().response.read_live_data
        self._static_data = brose.V1().response.read_static_data
        self._request_id = 0
    
    @property
    def request_id(self) :
        #self increment id
        self._request_id+=1
        return self._request_id
    
    @property
    def live_data(self):    
        return self._live_data
    
    @property   
    def static_data(self):    
        return self._static_data
    
    async def request_live_data(self):
        # Créez une requête read_live_data
        log.debug('Request Live data')
        request_message = brose.V1()
        request_message.request.id = self.request_id
        request_message.request.read_live_data.CopyFrom(brose.Empty())
        serialized_request = request_message.SerializeToString()
        serialized_response = await self.connection.write_message(serialized_request)
        response_message = brose.V1()
        response_message.ParseFromString(serialized_response)
        self._live_data = response_message.response.read_live_data 
        
    async def request_static_data(self):
        # Créez une requête read_static_data
        log.debug('Request Static data')
        request_message = brose.V1()
        request_message.request.id = self.request_id
        request_message.request.read_static_data.CopyFrom(brose.Empty())
        serialized_request = request_message.SerializeToString()
        serialized_response = await self.connection.write_message(serialized_request)
        response_message = brose.V1()
        response_message.ParseFromString(serialized_response)
        self._static_data = response_message.response.read_static_data
       
    async def set_support_profile(self, profile):
        # Créez une requête set_support_profile
        # profile : The profile to be changed
        #   brose.ECO
        #   brose.TOUR
        #   brose.SPORT
        #   brose.TURBO
        request_message = brose.V1()
        request_message.request.id = self.request_id
        request_message.request.write_support_profile = profile
        serialized_request = request_message.SerializeToString()
        serialized_response = await self.connection.write_message(serialized_request)

    async def set_thrustfactor(self, profile, thrustfactor):
        # Créez une requête set_thrustfactor
        # profile : The profile to be changed
        #   brose.ECO
        #   brose.TOUR
        #   brose.SPORT
        #   brose.TURBO
        # thrustfactor : The new thrustfactor to be set (0...320)

        request_message = brose.V1()
        request_message.request.id = self.request_id 
        request_message.request.write_thrustfactor.profile = profile
        request_message.request.write_thrustfactor.thrustfactor = thrustfactor
        serialized_request = request_message.SerializeToString()
        await self.connection.write_message(serialized_request)
    
    async def set_current_scaling(self, current_scaling):
        #The new current scaling to be set (10...100)
        request_message = brose.V1()
        request_message.request.id = self.request_id  
        request_message.request.write_current_scaling = current_scaling
        serialized_request = request_message.SerializeToString()
        await self.connection.write_message(serialized_request)

    async def set_support_profile_scale(self, support_profile_scale):
        # The new support profile scale to be set (0...100)
        request_message = brose.V1()
        request_message.request.id = self.request_id 
        request_message.request.write_support_profile_scale.support_profile_scale = support_profile_scale
        serialized_request = request_message.SerializeToString()
        await self.connection.write_message(serialized_request)
    
    async def reset_trip_distance(self):
        # Créez une requête reset_trip_distance
        request_message = brose.V1()
        request_message.request.id = self.request_id 
        request_message.request.reset_trip_distance.CopyFrom(brose.Empty())
        serialized_request = request_message.SerializeToString()
        await self.connection.write_message(serialized_request)

    
    def debug_static_data(self) :
        print("Drive Unit Data:")
        print(f"\tfirmware_version: {self.static_data.drive_unit_data.firmware_version}")
        print(f"\tserial_number: {self.static_data.drive_unit_data.serial_number}")
        print(f"\tebike_id: {self.static_data.drive_unit_data.ebike_id}")
        print(f"\tboard_serial_number: {self.static_data.drive_unit_data.board_serial_number}")
        print(f"\twheel_circumference: {self.static_data.drive_unit_data.wheel_circumference}")

        print("\tThrustfactors:")
        for tf in self.static_data.drive_unit_data.thrustfactors:
            print(f"\t\tProfile: {tf.profile}, Thrustfactor: {tf.thrustfactor}")

        print("\nBattery Data:")
        print(f"\tfirmware_version: {self.static_data.battery_data.firmware_version}")
        print(f"\tserial_number: {self.static_data.battery_data.serial_number}")
        print(f"\tstate_of_health: {self.static_data.battery_data.state_of_health}")
        print(f"\tload_cycles: {self.static_data.battery_data.load_cycles}")
        print(f"\tfull_charge_capacity: {self.static_data.battery_data.full_charge_capacity}")

        print("\nHMI Data:")
        print(f"\tfirmware_version: {self.static_data.hmi_data.firmware_version}")
        print(f"\tserial_number: {self.static_data.hmi_data.serial_number}")
    
    def debug_live_data(self) :
        print("Drive Unit Data:")
        print(f"\tbike_speed: {self.live_data.drive_unit_data.bike_speed}")
        print(f"\ttreadle_cadence: {self.live_data.drive_unit_data.treadle_cadence}")
        print(f"\tsupport_profile: {self.live_data.drive_unit_data.support_profile}")
        print(f"\ttreadle_power: {self.live_data.drive_unit_data.treadle_power}")
        print(f"\tpedal_trq: {self.live_data.drive_unit_data.pedal_trq}")
        print(f"\todometer: {self.live_data.drive_unit_data.odometer}")
        print(f"\tlight: {self.live_data.drive_unit_data.light}")
        print(f"\tmotor_temperature: {self.live_data.drive_unit_data.motor_temperature}")
        print(f"\tpushing_help: {self.live_data.drive_unit_data.pushing_help}")
        print(f"\testimated_range: {self.live_data.drive_unit_data.estimated_range}")

        print("\nBattery Data:")
        print(f"\tbattery_level_relative: {self.live_data.battery_data.battery_level_relative}")
        print(f"\tbattery_level_absolute: {self.live_data.battery_data.battery_level_absolute}")
        print(f"\tactual_current: {self.live_data.battery_data.actual_current}")
        print(f"\tactual_voltage: {self.live_data.battery_data.actual_voltage}")
        print(f"\tstate_register: {self.live_data.battery_data.state_register}")
        print(f"\ttemperature: {self.live_data.battery_data.temperature}")

        print("\nHMI Data:")
        print(f"\ttrip_distance: {self.live_data.hmi_data.trip_distance}")
        print(f"\tcurrent_scaling: {self.live_data.hmi_data.current_scaling}")
        print(f"\tsupport_profile_scale: {self.live_data.hmi_data.support_profile_scale}")

        print("\nError Data:")
        print(f"\terror_bytes: {self.live_data.error_data.error_bytes}")


  
async def main() :
    from connection import BleConnection
    import sys
    log.setLevel(logging.DEBUG)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.DEBUG)
    log.addHandler(h)
    
    #my_bike_connection = BleConnection("DB:6A:44:0C:7A:5C")
    my_bike_connection = await BleConnection.auto()
    await my_bike_connection.start_listening()
    
    mybike = BroseEbike(my_bike_connection)
     
    await mybike.request_static_data()
    mybike.debug_static_data()
    await mybike.request_live_data()
    mybike.debug_live_data()    
    
    #await mybike.reset_trip_distance()
    #await mybike.set_thrustfactor(brose.ECO,40)
    #await mybike.set_support_profile(brose.ECO)
    #await mybike.set_current_scaling(100)
    #await mybike.set_support_profile_scale(100)

    await my_bike_connection.stop_listening()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
