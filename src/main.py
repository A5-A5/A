import os
import ydlidar
import time
import math
import matplotlib.pyplot as plt
import cv2
from gpiozero import AngularServo, PWMOutputDevice, Button
from gpiozero.pins.pigpio import PiGPIOFactory

factory = PiGPIOFactory()

def plot_lidar_scan(scan, plot, ax):
    x_points = []
    y_points = []
    for point in scan.points:
        if 0.02 < point.range < 16.0:
            angle_rad = math.radians(point.angle)
            x = point.range * math.cos(angle_rad)
            y = point.range * math.sin(angle_rad)
            x_points.append(x)
            y_points.append(y)
    plot.set_offsets(list(zip(x_points, y_points)))
    ax.set_xlim(-16, 16)
    ax.set_ylim(-16, 16)
    plt.draw()
    plt.pause(0.001)

HALL_SENSOR_PIN = 4
DISTANCE_PER_ROTATION = 0.40
TARGET_ROTATIONS = 3

hall_sensor = Button(HALL_SENSOR_PIN)
servo = AngularServo(18, min_angle=-90, max_angle=90, min_pulse_width=0.0006, max_pulse_width=0.0023, pin_factory=factory)
RPWM_PIN = 17
LPWM_PIN = 27

motor_forward = PWMOutputDevice(RPWM_PIN)
motor_reverse = PWMOutputDevice(LPWM_PIN)

pulse_count = 0
target_distance = 0.0

def hall_sensor_triggered():
    global pulse_count
    pulse_count += 1

hall_sensor.when_pressed = hall_sensor_triggered

def control_motor(speed):
    if speed < 0:
        motor_forward.value = -speed
        motor_reverse.off()
    elif speed > 0:
        motor_reverse.value = speed
        motor_forward.off()
    else:
        motor_forward.off()
        motor_reverse.off()

def move_one_meter():
    global pulse_count, target_distance
    pulse_count = 0
    target_distance = 1.0
    while True:
        distance_moved = pulse_count * DISTANCE_PER_ROTATION
        if distance_moved >= target_distance:
            control_motor(0)
            break
        control_motor(0.5)
        time.sleep(0.05)

def turn(rotation_count):
    for _ in range(rotation_count):
        control_motor(0.5)
        time.sleep(1)
        control_motor(0)
        time.sleep(0.5)

def avoid_obstacles():
    scan = ydlidar.LaserScan()
    r = laser.doProcessSimple(scan)
    if r:
        for point in scan.points:
            if point.range < 0.5:
                turn(1)

def process_camera():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = (40, 100, 100)
        upper_green = (80, 255, 255)
        mask = cv2.inRange(hsv, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow('Camera Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def control_loop():
    running = True
    ydlidar.os_init()
    ports = ydlidar.lidarPortList()
    port = "/dev/ydlidar"
    for key, value in ports.items():
        port = value
    laser = ydlidar.CYdLidar()
    laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
    laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 230400)
    laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
    laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
    laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0)
    laser.setlidaropt(ydlidar.LidarPropSampleRate, 4)
    laser.setlidaropt(ydlidar.LidarPropSingleChannel, False)
    laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0)
    laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0)
    laser.setlidaropt(ydlidar.LidarPropMaxRange, 16.0)
    laser.setlidaropt(ydlidar.LidarPropMinRange, 0.02)
    laser.setlidaropt(ydlidar.LidarPropIntenstiy, True)
    ret = laser.initialize()
    if ret:
        ret = laser.turnOn()
        scan = ydlidar.LaserScan()
        plt.ion()
        fig, ax = plt.subplots()
        ax.set_xlim(-16, 16)
        ax.set_ylim(-16, 16)
        ax.set_title("2D LIDAR Mapping of Walls")
        ax.set_xlabel("X (meters)")
        ax.set_ylabel("Y (meters)")
        plot = ax.scatter([], [], s=5)
        plt.show()
        try:
            while ret and ydlidar.os_isOk() and running:
                r = laser.doProcessSimple(scan)
                if r:
                    plot_lidar_scan(scan, plot, ax)
                    avoid_obstacles()
                move_one_meter()
                turn(TARGET_ROTATIONS)
                time.sleep(1)
        except KeyboardInterrupt:
            running = False
        laser.turnOff()
    laser.disconnecting()

def destroy():
    servo.angle = 0
    control_motor(0)

if __name__ == "__main__":
    try:
        process_camera() 
        control_loop()
    except KeyboardInterrupt:
        destroy()
