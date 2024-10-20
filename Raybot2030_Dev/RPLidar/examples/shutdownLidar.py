from rplidar import RPLidar
from time import sleep

PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(PORT_NAME)

try:
    info = lidar.get_info()
    print(info)
   
    health = lidar.get_health()
    print(health)
   
    lidar.start_motor()
    print("Motor started")
    sleep(3)
   
    lidar.stop()
    print("Scanning stopped")
    sleep(1)
   
    lidar.stop_motor()
    print("Motor stop command sent")
    sleep(5)  # Give more time for the motor to stop
   
    # Added while loop after stop motor function
    print("Motor is stopped. Enter 'q' to quit.")
    while True:
        
        user_input = input()
        if user_input.lower() == 'q':
            break
        sleep(1)
   
    print("Disconnecting...")
    lidar.disconnect()
    print("Disconnected")
except KeyboardInterrupt:
    print("Stopping...")
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
print("Program ended")