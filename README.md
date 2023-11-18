# brose-bt
Python module to access brose ebike hmi bluetooth API

## Requirements
  bleak, protobuf
  
## Usage
```
from brosebt import BleConnection, BroseEbike, brose

# Instancie a connection with address 
async def main()
        my_bike_connection = BleConnection("DB:6A:44:0C:7A:5C")
        await my_bike_connection.pair() #require only once
        
        #or find bike and pair connection automaticaly   
        #my_bike_connection = await BleConnection.auto()

        # Start the communication_listenning   
        await my_bike_connection.start_listening()

        # Create the Ebike Object
        mybike = BroseEbike(my_bike_connection)
        
        # Calling Api
        #Read static data
        await mybike.request_static_data()
        mybike.debug_static_data()
        
        #Read live data
        await mybike.request_live_data()
        mybike.debug_live_data()    
        
        #Call function
        await mybike.reset_trip_distance()
        await mybike.set_thrustfactor(brose.ECO,40)
        await mybike.set_support_profile(brose.ECO)
        await mybike.set_current_scaling(100)
        await mybike.set_support_profile_scale(100)

        # Stop the communication_listenning   
        await my_bike_connection.stop_listening()

# dont foregt to run the loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```


## BleConnection debug
```
[Service] 0000180a-0000-1000-8000-00805f9b34fb: Device Information
        [Characteristic] 00002a26-0000-1000-8000-00805f9b34fb: (read) | Name: Firmware Revision String, Value: b'43' 
        [Characteristic] 00002a25-0000-1000-8000-00805f9b34fb: (read) | Name: Serial Number String, Value: b'206142201' 
        [Characteristic] 00002a29-0000-1000-8000-00805f9b34fb: (read) | Name: Manufacturer Name String, Value: b'Brose' 
        [Characteristic] 00002a24-0000-1000-8000-00805f9b34fb: (read) | Name: Model Number String, Value: b'E41230-105' 
[Service] 31be2300-d927-11e9-8a34-2a2ae2dbcce4: Unknown
        [Characteristic] 31be3634-d927-11e9-8a34-2a2ae2dbcce4: (write-without-response) | Name: Unknown, Value: None 
        [Characteristic] 31be23a6-d927-11e9-8a34-2a2ae2dbcce4: (read,notify) | Name: Unknown, Value: b'?\x00\x00\x00\x00`v\x0c\xec\x1f\x00\x02`' 
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 26) | Value: b'\x00\x00' 
        [Characteristic] 31be32ba-d927-11e9-8a34-2a2ae2dbcce4: (read,notify) | Name: Unknown, Value: b'\x82\x08\xe0\xec1\x10d\x18d"\x08\n\x06\x00\x00\x00\x00\x00\x00\x08' 
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 31) | Value: b'\x00\x00' 
[Service] 00001801-0000-1000-8000-00805f9b34fb: Generic Attribute Profile
        [Characteristic] 00002a05-0000-1000-8000-00805f9b34fb: (indicate) | Name: Service Changed, Value: None 
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 13) | Value: b'\x02\x00' 

```
## BroseEbike debug
```
Found a bike ble device DB:6A:44:0C:7A:5C: DECA_000_20221128_00664
Request Static data
Sendind a packet 1/1 to 31be3634-d927-11e9-8a34-2a2ae2dbcce4 - 0 : 8006001a0408013200
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 0 : a100229e0108013299010a750a0e372e342e31
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 1 : 2e35392e38322e323212174339313134332d32
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 2 : 30303232303533302d332d303134371a174445
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 3 : 43415f3030305f32303232313132385f303036
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 4 : 36342214393833373032303231383035323230
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 5 : 373732343328e8113204080110283204080210
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 6 : 503205080310a0013205080410c002120f0a05
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 7 : 302e302e301200186428a0c81c1a0f0a023433
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 8 : 1209323036313432323031c81c1a0f0a023433
Receiving message complete (161 bytes) from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4
>> 229e0108013299010a750a0e372e342e312e35392e38322e323212174339313134332d3230303232303533302d332d303134371a17444543415f3030305f32303232313132385f30303636342214393833373032303231383035323230373732343328e8113204080110283204080210503205080310a0013205080410c002120f0a05302e302e301200186428a0c81c1a0f0a0234331209323036313432323031
Drive Unit Data:
        firmware_version: 7.4.1.59.82.22
        serial_number: C91143-200220530-3-0147
        ebike_id: DECA_000_20221128_00664
        board_serial_number: 98370202180522077243
        wheel_circumference: 2280
        Thrustfactors:
                Profile: 1, Thrustfactor: 40
                Profile: 2, Thrustfactor: 80
                Profile: 3, Thrustfactor: 160
                Profile: 4, Thrustfactor: 320

Battery Data:
        firmware_version: 0.0.0
        serial_number: 
        state_of_health: 100
        load_cycles: 0
        full_charge_capacity: 468000

HMI Data:
        firmware_version: 43
        serial_number: 206142201
Request Live data
Sendind a packet 1/1 to 31be3634-d927-11e9-8a34-2a2ae2dbcce4 - 0 : 8006001a0408022a00
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 0 : 3200223008022a2c0a0a180130ec3f4030508d
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 1 : 01120e085e10ece51a20fcbe022a020c001a04
Receiving a packet from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4 - 2 : 1064186422080a06000000000000020c001a04
Receiving message complete (50 bytes) from 31be32ba-d927-11e9-8a34-2a2ae2dbcce4
>> 223008022a2c0a0a180130ec3f4030508d01120e085e10ece51a20fcbe022a020c001a041064186422080a06000000000000
Drive Unit Data:
        bike_speed: 0
        treadle_cadence: 0
        support_profile: 1
        treadle_power: 0
        pedal_trq: 0
        odometer: 8172
        light: False
        motor_temperature: 24
        pushing_help: False
        estimated_range: 141

Battery Data:
        battery_level_relative: 94
        battery_level_absolute: 439020
        actual_current: 0
        actual_voltage: 40828
        state_register: b'\x0c\x00'
        temperature: 0

HMI Data:
        trip_distance: 0
        current_scaling: 100
        support_profile_scale: 100

Error Data:
        error_bytes: b'\x00\x00\x00\x00\x00\x00'
```
