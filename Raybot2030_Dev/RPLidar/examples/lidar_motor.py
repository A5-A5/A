import time
import pygame
from gpiozero import PWMOutputDevice, Button
from adafruit_pca9685 import PCA9685
import busio
from board import SCL, SDA
from rplidar import RPLidar

# Initialize I2C bus and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50  # Set frequency to 50Hz for servos

# Custom servo class for PCA9685
class PCA9685Servo:
    def __init__(self, channel, min_pulse=1000, max_pulse=2000):
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.current_angle = 0  # Keep track of the current angle

    def set_angle(self, angle):
        # Constrain angle between -90 and 90 degrees
        self.current_angle = max(-90, min(90, angle))
        pulse_width = self.min_pulse + (self.max_pulse - self.min_pulse) * ((self.current_angle + 90) / 180)
        self.channel.duty_cycle = int(pulse_width * 0xFFFF / 20000)

    def get_angle(self):
        return self.current_angle

# Create servo object
servo = PCA9685Servo(pca.channels[0])

# Motor driver setup
RPWM_PIN = 17
LPWM_PIN = 27
motor_forward = PWMOutputDevice(RPWM_PIN)
motor_reverse = PWMOutputDevice(LPWM_PIN)

# Hall sensor setup
HALL_SENSOR_PIN = 4
DISTANCE_PER_ROTATION = 0.10  # meters
hall_sensor = Button(HALL_SENSOR_PIN)

# Global variables
pulse_count = 0
target_distance = 0.0

# RPLIDAR setup
lidar = RPLidar('/dev/ttyUSB0')

def hall_sensor_triggered():
    global pulse_count
    pulse_count += 1

hall_sensor.when_pressed = hall_sensor_triggered

def get_distance_moved():
    return pulse_count * DISTANCE_PER_ROTATION

def reset_distance():
    global pulse_count
    pulse_count = 0

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

def scan_environment():
    scan_data = []
    for scan in lidar.iter_scans():
        scan_data.extend(scan)
        if len(scan_data) > 360:
            break
    return scan_data

def process_lidar_data(scan_data):
    obstacles = []
    for _, angle, distance in scan_data:
        if distance < 500:  # Detect obstacles within 500mm
            obstacles.append((angle, distance))
    return obstacles

def navigate(obstacles, current_angle):
    if not obstacles:
        return current_angle, 0.5  # No change in steering, half speed forward
    
    closest = min(obstacles, key=lambda x: x[1])
    if closest[0] < 90 or closest[0] > 270:
        return current_angle + 45, 0.3  # Turn right, slow speed
    else:
        return current_angle - 45, 0.3  # Turn left, slow speed

def control_loop():
    pygame.init()
    pygame.joystick.init()

    joystick = None
    while joystick is None:
        try:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print("DS4 controller connected.")
        except pygame.error:
            print("Waiting for DS4 controller to be connected...")
            time.sleep(1)

    running = True
    autonomous_mode = False
    rounds = 0

    while running and rounds < 3:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Cross button
                    autonomous_mode = not autonomous_mode
                    print(f"Autonomous mode: {'On' if autonomous_mode else 'Off'}")

        if autonomous_mode:
            scan_data = scan_environment()
            obstacles = process_lidar_data(scan_data)
            new_angle, speed = navigate(obstacles, servo.get_angle())
            
            servo.set_angle(new_angle)
            control_motor(speed)

            # Check if a round is completed (you'll need to implement this logic)
            if get_distance_moved() > 10:  # Assume 10 meters is one round
                rounds += 1
                reset_distance()
                print(f"Completed round {rounds}")
        else:
            steering_input = -joystick.get_axis(0)
            throttle_input = -joystick.get_axis(4)

            servo.set_angle(steering_input * 90)
            control_motor(throttle_input * 0.6)

        time.sleep(0.05)

    print("Navigation complete or stopped.")
    control_motor(0)
    servo.set_angle(0)

if __name__ == "__main__":
    try:
        control_loop()
    finally:
        lidar.stop()
        lidar.disconnect()
        pygame.quit()