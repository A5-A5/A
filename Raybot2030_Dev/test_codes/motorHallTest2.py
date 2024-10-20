import time
import pygame
import os  # For system shutdown
from gpiozero import PWMOutputDevice, Button
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import ydlidar

# Initialize I2C bus for PCA9685
i2c = busio.I2C(SCL, SDA)

# Create a PCA9685 object
pca = PCA9685(i2c)
pca.frequency = 50  # Set frequency to 50Hz for servos

# Define the custom servo class for PCA9685
class PCA9685Servo:
    def __init__(self, channel, min_pulse=1000, max_pulse=2000):
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

    def set_angle(self, angle):
        # Convert angle (-90 to 90) to pulse width
        pulse_width = self.min_pulse + (self.max_pulse - self.min_pulse) * ((angle + 90) / 180)
        self.channel.duty_cycle = int(pulse_width * 0xFFFF / 20000)

# Create a servo object on channel 0 of PCA9685
servo = PCA9685Servo(pca.channels[0])

print("It started")
# IBT-2 motor driver pin setup for a single DC motor
RPWM_PIN = 17  # Forward control pin
LPWM_PIN = 27  # Reverse control pin

# Set up the IBT-2 motor driver control pins
motor_forward = PWMOutputDevice(RPWM_PIN)
motor_reverse = PWMOutputDevice(LPWM_PIN)

# GPIO Pin where the Hall sensor is connected
HALL_SENSOR_PIN = 4
DISTANCE_PER_ROTATION = 0.10  # Distance per shaft rotation in meters

# Setup Hall sensor using gpiozero's Button class (it detects edges for us)
hall_sensor = Button(HALL_SENSOR_PIN)

# Variables to store hall sensor data
pulse_count = 0
target_distance = 0.0  # Distance we want the car to move

SAFE_DISTANCE = 0.4  # in meters, adjust based on your needs
STRAIGHT_THRESHOLD = 1.0  # Narrow the straight-ahead threshold for testing (±1 degrees)
MAX_ANGLE = 80.0  # Max angle in your LIDAR setup

# Initialize LIDAR globally so it can be used in multiple functions
def initialize_lidar():
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
        laser.turnOn()
        return laser
    else:
        print("Failed to initialize LIDAR")
        return None

# Detect obstacle function
def detect_obstacle(scan):
    """Check if there's any obstacle within the safe distance and determine its location."""
    for point in scan.points:
        if point.range > 0.02 and point.range < SAFE_DISTANCE:
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

# Function to increment pulse count when Hall sensor is triggered
def hall_sensor_triggered():
    global pulse_count
    pulse_count += 1

# Register Hall sensor callback
hall_sensor.when_pressed = hall_sensor_triggered

# Function to calculate the distance moved
def get_distance_moved():
    # Calculate the distance based on the number of pulses
    distance_moved = pulse_count * DISTANCE_PER_ROTATION
    return distance_moved

# Function to reset pulse count
def reset_distance():
    global pulse_count
    pulse_count = 0

# Function to control DC motor using the joystick's forward/backward axis
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

# Function to move the car forward by 2 meters and turn right at each corner
def move_square_avoiding_obstacles(laser):
    global pulse_count
    target_distance = 4.0  # Distance to move forward before turning (2 meters)
    turn_angle = -90  # Right turn angle
    num_corners = 4  # Move in a square (four corners)

    scan = ydlidar.LaserScan()

    for corner in range(num_corners):  # Loop through 4 corners
        # Reset pulse count for distance measurement
        pulse_count = 0

        # Move forward 2 meters
        while get_distance_moved() < target_distance:
            # Check for obstacles
            r = laser.doProcessSimple(scan)
            if r:
                obstacle_detected, angle, distance, position = detect_obstacle(scan)
                if obstacle_detected:
                    print(f"Obstacle detected {position} at {distance:.2f} meters. Stopping to avoid collision.")
                    control_motor(0)  # Stop the motor
                    return  # Exit the function if an obstacle is detected

            control_motor(0.5)  # Move forward at half speed
            time.sleep(0.1)  # Small delay for smoother control

        # Stop motor after moving the desired distance
        control_motor(0)
        print(f"Moved 2 meters. Preparing to turn right at corner {corner + 1}.")

        # Turn right by adjusting the servo to 90 degrees (turn right)
        servo.set_angle(turn_angle)
        time.sleep(1)  # Give some time to complete the turn

        # Reset servo to straight position (0 degrees)
        servo.set_angle(0)
        print(f"Turned right at corner {corner + 1}.")
        time.sleep(1)  # Pause briefly before next move

# Control loop to handle DS4 input and control both the servo, DC motor, and LIDAR
def control_loop(laser):
    scan = ydlidar.LaserScan()

    running = True
    dead_zone = 0.1  # Dead zone for joystick
    max_speed = 0.6  # Max speed value for motor (from 0.0 to 1.0)
    cross_button = 0  # DS4 Cross (X) button ID for moving square
    options_button = 9  # DS4 Options button ID for shutdown
    circle_button = 2  # DS4 Circle button ID for clear distance
    button_press_time = None  # To track the time the Options button is pressed

    while running and ydlidar.os_isOk():
        r = laser.doProcessSimple(scan)
        if r:
            # Check if there's an obstacle within the safe distance
            obstacle_detected, angle, distance, position = detect_obstacle(scan)
            if obstacle_detected:
                print(f"Obstacle detected {position} at angle {angle:.2f} degrees, distance: {distance:.2f} meters.")
                # Take action to avoid obstacle
            else:
                print("No obstacles detected.")

        # Process DS4 controller events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == cross_button:
                    print("Cross (X) button pressed. Moving in a square.")
                    move_square_avoiding_obstacles(laser)

                elif event.button == options_button:
                    button_press_time = time.time()
                    print("Options button pressed.")

                elif event.button == circle_button:
                    print("Circle button pressed. Resetting distance.")
                    reset_distance()

            elif event.type == pygame.JOYBUTTONUP:
                if event.button == options_button:
                    if button_press_time and (time.time() - button_press_time >= 5):
                        print("Options button held for 5 seconds. Initiating shutdown.")
                    button_press_time = None

        # Get joystick axes for controlling the motor and servo
        steering_input = -joystick.get_axis(0)  # Left joystick horizontal for steering
        throttle_input = joystick.get_axis(4)  # Left joystick vertical for motor speed

        # Apply dead zone
        if abs(steering_input) < dead_zone:
            steering_input = 0
        if abs(throttle_input) < dead_zone:
            throttle_input = 0

        # Map joystick input to servo angle (convert to a value between -90 and 90 degrees)
        angle = steering_input * 90
        servo.set_angle(angle)  # Set servo angle for steering

        # Map joystick input to motor speed
        motor_speed = throttle_input * -max_speed  # Invert to match forward/backward
        control_motor(motor_speed)  # Set motor speed

        time.sleep(0.1)  # Small delay for loop

def destroy():
    servo.set_angle(0)  # Reset servo to neutral position (0 degrees)
    control_motor(0)  # Stop the motor

if __name__ == '__main__':
    try:
        laser = initialize_lidar()  # Initialize LIDAR once
        if laser:
            pygame.init()
            pygame.joystick.init()

            joystick = None
            while joystick is None:
                pygame.joystick.quit()
                pygame.joystick.init()
                try:
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    print("DS4 controller connected.")
                except pygame.error:
                    print("Waiting for DS4 controller to be connected...")
                    time.sleep(1)

            control_loop(laser)  # Start control loop using LIDAR

    except KeyboardInterrupt:
        destroy()
    finally:
        if laser:
            laser.turnOff()
            laser.disconnecting()
