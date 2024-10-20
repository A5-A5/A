import os
import ydlidar
import time

ydlidar.os_init()

# Get the available ports
ports = ydlidar.lidarPortList()

# Print available ports for debugging
print("Available ports:", ports)

# Automatically select the last available port or hardcode the correct one
port = "/dev/ydlidar"
for key, value in ports.items():
    port = value
    print("Using port:", port)  # Debugging print

# Initialize the LIDAR
laser = ydlidar.CYdLidar()
laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 230400)
laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0)
laser.setlidaropt(ydlidar.LidarPropSampleRate, 9)
laser.setlidaropt(ydlidar.LidarPropSingleChannel, False)

# Initialize and turn on the LIDAR
ret = laser.initialize()
if ret:
    ret = laser.turnOn()
    scan = ydlidar.LaserScan()

    # Start scanning and collecting data
    while ret and ydlidar.os_isOk():
        r = laser.doProcessSimple(scan)
        if r:
            print("Scan received[", scan.stamp, "]:", scan.points.size(), "ranges at [", 1.0 / scan.config.scan_time, "] Hz")
            for point in scan.points:
                print(f"Angle: {point.angle:.2f}, Range: {point.range:.2f} meters")
        else:
            print("Failed to get Lidar Data")
        
        time.sleep(0.05)
    
    laser.turnOff()

# Disconnect the LIDAR
laser.disconnecting()
