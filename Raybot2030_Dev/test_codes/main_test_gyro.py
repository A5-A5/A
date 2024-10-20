import time
import pygame
from gpiozero import PWMOutputDevice, Button
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
from luma.core.interface.serial import i2c as luma_i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
import smbus2
import numpy as np

# MPU-6050 Registers
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# I2C address of the MPU-6050
MPU_ADDR = 0x68

# Initialize I2C bus for MPU-6050
mpu_bus = smbus2.SMBus(1)

# OLED display setup
serial = luma_i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)
font = ImageFont.load_default()

# Initialize I2C bus for PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

class PCA9685Servo:
    def __init__(self, channel, min_pulse=1000, max_pulse=2000):
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.current_angle = 0
        self.target_angle = 0
        self.smoothing_factor = 0.3  # Increased for more responsive movement

    def set_angle(self, angle):
        self.target_angle = max(min(angle, 90), -90)  # Clamp angle between -90 and 90
        print(f"Target angle set to: {self.target_angle}")  # Debug print

    def update(self):
        self.current_angle += (self.target_angle - self.current_angle) * self.smoothing_factor
        pulse_width = self.min_pulse + (self.max_pulse - self.min_pulse) * ((self.current_angle + 90) / 180)
        duty_cycle = int(pulse_width * 0xFFFF / 20000)
        print(f"Setting duty cycle to: {duty_cycle}")  # Debug print
        try:
            self.channel.duty_cycle = duty_cycle
        except Exception as e:
            print(f"Error setting servo angle: {e}")

    def test_range(self):
        print("Testing servo range...")
        for angle in [-90, -45, 0, 45, 90]:
            self.set_angle(angle)
            self.update()
            print(f"Set angle to {angle}")
            time.sleep(1)
        print("Servo range test complete.")

# Initialize I2C bus for PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

# Create a servo object on channel 0 of PCA9685
servo = PCA9685Servo(pca.channels[0])

def test_servo():
    print("Starting servo test...")
    servo.test_range()
    print("Servo test complete.")


def display_info(speed, distance):
    with canvas(device) as draw:
        draw.text((0, 0), f"Motor Speed:", fill="white", font=font)
        draw.text((0, 16), f"{speed:.2f}", fill="white", font=font)
        draw.text((0, 32), f"Distance (cm):", fill="white", font=font)
        draw.text((0, 48), f"{distance:.2f}", fill="white", font=font)



print("it started")
# IBT-2 motor driver pin setup for a single DC motor
RPWM_PIN = 17  # Forward control pin
LPWM_PIN = 27  # Reverse control pin

# Set up the IBT-2 motor driver control pins
motor_forward = PWMOutputDevice(RPWM_PIN)
motor_reverse = PWMOutputDevice(LPWM_PIN)

# GPIO Pin where the Hall sensor is connected
HALL_SENSOR_PIN = 4
DISTANCE_PER_ROTATION = 0.08  # Distance per shaft rotation in meters

# Setup Hall sensor using gpiozero's Button class (it detects edges for us)
hall_sensor = Button(HALL_SENSOR_PIN)


button = Button(26, pull_up=True)



# Function to run when the button is pressed
def on_button_press():
    control_motor(0.6)
    time.sleep(1)
    control_motor(0.3)
    print("Button pressed")

# Function to run when the button is released
def on_button_release():
    print("Button released")


button.when_pressed = on_button_press
button.when_released = on_button_release

# Variables to store hall sensor data
pulse_count = 0
target_distance = 0.0  # Distance we want the car to move

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

# Function to reset pulse count (optional if you want to start fresh)
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
    display_info(speed, get_distance_moved())
    print(f"Motor speed: {speed}  -  Distance Moved: {get_distance_moved()}")  # Print motor speed for debugging


class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, initial_value=0):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = initial_value
        self.estimate_error = 1

    def update(self, measurement):
        prediction = self.estimate
        prediction_error = self.estimate_error + self.process_variance
        kalman_gain = prediction_error / (prediction_error + self.measurement_variance)
        self.estimate = prediction + kalman_gain * (measurement - prediction)
        self.estimate_error = (1 - kalman_gain) * prediction_error
        return self.estimate

class GyroSystem:
    def __init__(self):
        self.kf_z = KalmanFilter(process_variance=0.01, measurement_variance=0.1)
        self.offset_z = 0
        self.current_heading = 0
        self.target_heading = 0
        self.steering_kp = 0.1
        self.calibrate_gyro()

    def calibrate_gyro(self, samples=1000):
        print("Calibrating gyroscope. Keep the RC car still...")
        sum_z = 0
        for _ in range(samples):
            _, _, z = self.get_raw_data()
            sum_z += z
            time.sleep(0.001)
        self.offset_z = sum_z / samples
        print(f"Calibration complete. Z-axis offset: {self.offset_z:.2f}")

    def get_raw_data(self):
        gyro_z = read_word_2c(GYRO_ZOUT_H) / 131
        return 0, 0, gyro_z  # We're only using z-axis for yaw

    def get_filtered_data(self):
        _, _, z = self.get_raw_data()
        return 0, 0, self.kf_z.update(z - self.offset_z)

    def update_heading(self, yaw_rate, dt):
        self.current_heading += yaw_rate * dt
        self.current_heading = (self.current_heading + 180) % 360 - 180

    def get_steering_correction(self):
        error = self.target_heading - self.current_heading
        error = (error + 180) % 360 - 180
        return self.steering_kp * error

def init_mpu():
    mpu_bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)

def read_word(reg):
    high = mpu_bus.read_byte_data(MPU_ADDR, reg)
    low = mpu_bus.read_byte_data(MPU_ADDR, reg + 1)
    return (high << 8) + low

def read_word_2c(reg):
    val = read_word(reg)
    return -((65535 - val) + 1) if val >= 0x8000 else val

# ... (your existing code for PCA9685Servo, motor control, etc.)

gyro_system = GyroSystem()


# Wait for DS4 controller to be connected
# Initialize Pygame and the joystick
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


def control_loop():
    running = True
    dead_zone = 0.1
    last_time = time.time()
    max_speed = 0.6  # Max speed value for motor (from 0.0 to 1.0)
    cross_button = 0  # DS4 Cross (X) button ID for moving 1 meter
    options_button = 9  # DS4 Options button ID for shutdown
    circle_button = 2  # DS4 Circle button ID for clear distance


    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Check for Cross (X) button press
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == cross_button:
                    print("Cross (X) button pressed. Moving 1 meter.")
                    move_one_meter()

                # Check for Options button press to start shutdown countdown
                elif event.button == options_button:
                    button_press_time = time.time()
                    print("Options button pressed.")
                    
                    
                elif event.button == circle_button:
                    button_press_time = time.time()
                    print("circle button pressed.")
                    reset_distance()
        
        
        throttle_input = joystick.get_axis(4)  # Left joystick vertical for motor speed

        # Apply dead zone
        if abs(steering_input) < dead_zone:
            steering_input = 0
        if abs(throttle_input) < dead_zone:
            throttle_input = 0

        steering_input = -joystick.get_axis(0)
        print(f"Raw steering input: {steering_input}")  # Debug print

        if abs(steering_input) < dead_zone:
            steering_input = 0

        # Apply gyro-based correction to steering
        gyro_correction = gyro_system.get_steering_correction()
        corrected_steering = steering_input + gyro_correction
        print(f"Corrected steering: {corrected_steering}")  # Debug print
        
        # Ensure steering is within bounds
        corrected_steering = max(min(corrected_steering, 1), -1)

        angle = corrected_steering * 90
        print(f"Calculated servo angle: {angle}")  # Debug print
        servo.set_angle(angle)
        servo.update()  # Update servo position
        # Map joystick input to motor speed
        motor_speed = throttle_input * -max_speed  # Invert to match forward/backward
        control_motor(motor_speed)  # Set motor speed


        # ... (rest of the control loop code)

        time.sleep(0.01)  # Increased update rate for more responsive control  # Increased update rate for more responsive control
def destroy():
    servo.set_angle(0)
    control_motor(0)
    pca.deinit()


if __name__ == '__main__':
    try:
        init_mpu()
        test_servo()  # Run servo test at startup
        control_loop()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        servo.set_angle(0)  # Reset servo to center position
        servo.update()
        pca.deinit()
        pygame.quit()
