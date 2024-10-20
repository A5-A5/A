import time
import pygame
import os  # For system shutdown
from gpiozero import PWMOutputDevice, Button
from smbus2 import SMBus
import math

# I2C address of PCA9685
PCA9685_ADDRESS = 0x40

# Register addresses
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

# Initialize I2C bus
bus = SMBus(1)  # 1 indicates /dev/i2c-1

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

# GPIO Pin where the Hall sensor is connected
HALL_SENSOR_PIN = 4
DISTANCE_PER_ROTATION = 0.40  # Distance per shaft rotation in meters

# Setup Hall sensor using gpiozero's Button class (it detects edges for us)
hall_sensor = Button(HALL_SENSOR_PIN)

# Servo channel on the PCA9685 (adjust as needed)
SERVO_CHANNEL = 0

# IBT-2 motor driver pin setup for a single DC motor
RPWM_PIN = 17  # Forward control pin
LPWM_PIN = 27  # Reverse control pin

# Set up the IBT-2 motor driver control pins
motor_forward = PWMOutputDevice(RPWM_PIN)
motor_reverse = PWMOutputDevice(LPWM_PIN)

# Variables to store hall sensor data
pulse_count = 0
target_distance = 0.0  # Distance we want the car to move

# Function to increment pulse count when Hall sensor is triggered
def hall_sensor_triggered():
    global pulse_count
    pulse_count += 1

# Register Hall sensor callback
hall_sensor.when_pressed = hall_sensor_triggered

# Function to initialize PCA9685
def pca9685_init():
    try:
        # Set sleep mode
        bus.write_byte_data(PCA9685_ADDRESS, MODE1, 0x00)
        time.sleep(0.005)
        bus.write_byte_data(PCA9685_ADDRESS, MODE1, 0x10)  # Set to auto increment
        time.sleep(0.005)
        # Set PWM frequency to 50Hz
        prescale = int(math.floor((25000000.0 / 4096.0 / 50.0) - 1))
        old_mode = bus.read_byte_data(PCA9685_ADDRESS, MODE1)
        bus.write_byte_data(PCA9685_ADDRESS, MODE1, (old_mode & 0x7F) | 0x10)
        bus.write_byte_data(PCA9685_ADDRESS, PRESCALE, prescale)
        bus.write_byte_data(PCA9685_ADDRESS, MODE1, old_mode)
        time.sleep(0.005)
        bus.write_byte_data(PCA9685_ADDRESS, MODE1, old_mode | 0xA1)
        print("PCA9685 initialized successfully")
    except Exception as e:
        print(f"Error initializing PCA9685: {e}")

# Function to set servo angle
def set_servo_angle(angle):
    try:
        pulse = int((angle / 180.0 * 400) + 100)  # Map angle to pulse width
        bus.write_i2c_block_data(PCA9685_ADDRESS, LED0_ON_L + 4 * SERVO_CHANNEL, [0, 0, pulse & 0xFF, pulse >> 8])
        print(f"Servo angle set to {angle} degrees")
    except Exception as e:
        print(f"Error setting servo angle: {e}")

# Function to test servo movement
def test_servo():
    print("Testing servo movement")
    for angle in [0, 90, 180, 90, 0]:  # Move to key positions
        print(f"Setting servo to {angle} degrees")
        set_servo_angle(angle)
        time.sleep(1)  # Wait for 1 second at each position
    print("Servo test complete")

# Function to control DC motor
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
    print(f"Motor speed set to {speed}")

# Function to move the car forward by 1 meter
def move_one_meter():
    global pulse_count, target_distance
    pulse_count = 0  # Reset pulse count
    target_distance = 1.0  # We want to move 1 meter

    while True:
        distance_moved = pulse_count * DISTANCE_PER_ROTATION
        if distance_moved >= target_distance:
            control_motor(0)  # Stop the motor after moving 1 meter
            print("Moved 1 meter. Stopping.")
            break

        control_motor(0.5)  # Move forward at half speed
        time.sleep(0.05)  # Small delay for smoother control

# Wait for DS4 controller to be connected
def wait_for_joystick():
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
    return joystick

# Control loop to handle DS4 input and control both the servo and DC motor
def control_loop(joystick):
    running = True
    dead_zone = 0.1  # Dead zone for joystick
    max_speed = 1.0  # Max speed value for motor (from 0.0 to 1.0)
    cross_button = 0  # DS4 Cross (X) button ID for moving 1 meter
    options_button = 9  # DS4 Options button ID for shutdown
    triangle_button = 3  # DS4 Triangle button ID for servo test
    button_press_time = None  # To track the time the Options button is pressed

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == cross_button:
                    print("Cross (X) button pressed. Moving 1 meter.")
                    move_one_meter()
                elif event.button == options_button:
                    button_press_time = time.time()
                    print("Options button pressed.")
                elif event.button == triangle_button:
                    print("Triangle button pressed. Testing servo.")
                    test_servo()

            elif event.type == pygame.JOYBUTTONUP:
                if event.button == options_button:
                    if button_press_time and (time.time() - button_press_time >= 5):
                        print("Options button held for 5 seconds. Initiating shutdown.")
                    button_press_time = None  # Reset button press time

        if button_press_time and (time.time() - button_press_time >= 6):
            os.system('sudo shutdown now -h')  # Initiate system shutdown
            print("Shutdown command executed.")
            running = False  # Stop the control loop

        # Get joystick axes for controlling the motor and servo
        steering_input = -joystick.get_axis(0)  # Left joystick horizontal for steering
        throttle_input =  joystick.get_axis(4)  # Left joystick vertical for motor speed

        # Apply dead zone
        if abs(steering_input) < dead_zone:
            steering_input = 0
        if abs(throttle_input) < dead_zone:
            throttle_input = 0

        # Map joystick input to servo angle (convert to a value between 0 and 180 degrees)
        angle = int((steering_input + 1) * 90)  # Convert -1 to 1 range to 0 to 180
        set_servo_angle(angle)  # Set servo angle for steering
        print(f"Joystick steering input: {steering_input}, Calculated angle: {angle}")

        # Map joystick input to motor speed
        motor_speed = throttle_input * -max_speed  # Invert to match forward/backward
        control_motor(motor_speed)  # Set motor speed

        time.sleep(0.1)  # Small delay for loop

if __name__ == '__main__':
    try:
        pca9685_init()
        joystick = wait_for_joystick()
        control_loop(joystick)
    except KeyboardInterrupt:
        print("Program terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleaning up...")
        set_servo_angle(90)  # Reset servo to neutral position
        control_motor(0)  # Stop the motor
        bus.close()
        print("Cleanup complete")