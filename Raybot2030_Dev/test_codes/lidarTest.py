import os
import ydlidar
import time
import math

SAFE_DISTANCE = 0.5  # in meters, adjust based on your needs
STRAIGHT_THRESHOLD = 1.0  # Narrow the straight-ahead threshold for testing (±1 degrees)
MAX_ANGLE = 80.0  # Max angle in your LIDAR setup

def detect_obstacle(scan):
    """Check if there's any obstacle within the safe distance and determine its location."""
    for point in scan.points:
        if point.range > 0.02 and point.range < SAFE_DISTANCE:
            # Print the angle to diagnose whether you're detecting a wide enough range
            # print(f"Detected angle: {point.angle:.2f} degrees")
            
            # Classify obstacle as left, right, or straight ahead based on the angle
            if point.angle < -STRAIGHT_THRESHOLD and point.angle >= -MAX_ANGLE:
                position = "left"
            elif point.angle > STRAIGHT_THRESHOLD and point.angle <= MAX_ANGLE:
                position = "right"
            elif -STRAIGHT_THRESHOLD <= point.angle <= STRAIGHT_THRESHOLD:
                position = "straight ahead"
            else:
                continue  # Ignore angles outside of the valid range
            return True, point.angle, point.range, position
    return False, None, None, None

def main():
    ydlidar.os_init()
    ports = ydlidar.lidarPortList()
    port = "/dev/ydlidar"
    for key, value in ports.items():
        port = value
        print(port)

    laser = ydlidar.CYdLidar()
    laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
    laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 230400)
    laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
    laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
    laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0)
    laser.setlidaropt(ydlidar.LidarPropSampleRate, 4)
    laser.setlidaropt(ydlidar.LidarPropSingleChannel, False)
    laser.setlidaropt(ydlidar.LidarPropMaxAngle, MAX_ANGLE)
    laser.setlidaropt(ydlidar.LidarPropMinAngle, -MAX_ANGLE)
    laser.setlidaropt(ydlidar.LidarPropMaxRange, 16.0)
    laser.setlidaropt(ydlidar.LidarPropMinRange, 0.02)
    laser.setlidaropt(ydlidar.LidarPropIntenstiy, True)

    ret = laser.initialize()
    if ret:
        ret = laser.turnOn()
        scan = ydlidar.LaserScan()

        while ret and ydlidar.os_isOk():
            r = laser.doProcessSimple(scan)
            if r:
                # Check if there's an obstacle within the safe distance
                obstacle_detected, angle, distance, position = detect_obstacle(scan)
                if obstacle_detected:
                    print(f"Obstacle detected {position} at angle {angle:.2f} degrees, distance: {distance:.2f} meters.")
                    # Take action to avoid obstacle
                else:
                    print("No obstacles detected, moving forward.")
                    # Command robot to move forward

            time.sleep(0.05)

        laser.turnOff()
    laser.disconnecting()

if __name__ == "__main__":
    main()
