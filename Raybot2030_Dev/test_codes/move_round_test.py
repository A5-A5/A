import time
import smbus2
import numpy as np
from gpiozero import PWMOutputDevice, Button
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# MPU-6050 Registers
PWR_MGMT_1 = 0x6B
GYRO_ZOUT_H = 0x47

# I2C address of the MPU-6050
DEVICE_ADDRESS = 0x68

# Initialize I2C bus for MPU-6050
mpu_bus = smbus2.SMBus(1)  # Use 1 for Raspberry Pi 5

# Initialize I2C bus for PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50  # Set frequency to 50Hz for servos

class PCA9685Servo:
    def __init__(self, channel, min_pulse=1000, max_pulse=2000):
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

    def set_angle(self, angle):
        pulse_width = self.min_pulse + (self.max_pulse - self.min_pulse) * ((angle + 90) / 180)
        self.channel.duty_cycle = int(pulse_width * 0xFFFF / 20000)

# Create a servo object on channel 0 of PCA9685
servo = PCA9685Servo(pca.channels[0])

# IBT-2 motor driver pin setup for a single DC motor
RPWM_PIN = 17  # Forward control pin
LPWM_PIN = 27  # Reverse control pin

# Set up the IBT-2 motor driver control pins
motor_forward = PWMOutputDevice(RPWM_PIN)
motor_reverse = PWMOutputDevice(LPWM_PIN)

# GPIO Pin where the Hall sensor is connected
HALL_SENSOR_PIN = 4
DISTANCE_PER_ROTATION = 0.08  # Distance per shaft rotation in meters

# Setup Hall sensor using gpiozero's Button class
hall_sensor = Button(HALL_SENSOR_PIN)

# Variables to store hall sensor data
pulse_count = 0
STRAIGHT_DISTANCE = 2.0  # Length of one side of the rectangle (3 meters)

def init_mpu():
    mpu_bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0)

def read_word(reg):
    high = mpu_bus.read_byte_data(DEVICE_ADDRESS, reg)
    low = mpu_bus.read_byte_data(DEVICE_ADDRESS, reg + 1)
    return (high << 8) + low

def read_word_2c(reg):
    val = read_word(reg)
    return -((65535 - val) + 1) if val >= 0x8000 else val

def get_yaw_rate():
    return read_word_2c(GYRO_ZOUT_H) / 131

def hall_sensor_triggered():
    global pulse_count
    pulse_count += 1

hall_sensor.when_pressed = hall_sensor_triggered

def get_distance_moved():
    return pulse_count * DISTANCE_PER_ROTATION

def control_motor(speed):
    if speed > 0:
        motor_forward.value = speed
        motor_reverse.off()
    elif speed < 0:
        motor_reverse.value = -speed
        motor_forward.off()
    else:
        motor_forward.off()
        motor_reverse.off()

def adjust_steering(yaw_rate):
    steering_angle = -yaw_rate * 0.5  # Adjust this factor as needed
    steering_angle = max(-45, min(45, steering_angle))  # Limit steering angle
    servo.set_angle(steering_angle)

def move_straight(distance):
    global pulse_count
    pulse_count = 0
    
    print(f"Moving straight for {distance} meters...")
    
    while get_distance_moved() < distance:
        yaw_rate = get_yaw_rate()
        adjust_steering(yaw_rate)
        
        remaining_distance = distance - get_distance_moved()
        motor_speed = - min(0.3, max(0.2, remaining_distance / distance))
        
        control_motor(motor_speed)
        
        print(f"Distance: {get_distance_moved():.2f}m, Yaw Rate: {yaw_rate:.2f}°/s, Motor Speed: {motor_speed:.2f}")
        time.sleep(0.05)  # Small delay for smoother control
    
    control_motor(0)  # Stop the motor

def turn_right():
    print("Turning right...")
    servo.set_angle(-45)  # Set maximum right turn
    control_motor(-0.2)  # Slow speed for turning
    time.sleep(1.0)  # Adjust this time based on your car's turning radius
    servo.set_angle(0)  # Center the steering
    control_motor(0)  # Stop the motor

def complete_lap():
    for _ in range(4):  # 4 sides of the rectangle
        move_straight(STRAIGHT_DISTANCE)
        turn_right()

def main():
    init_mpu()
    
    try:
        for lap in range(3):  # 3 laps
            print(f"Starting lap {lap + 1}")
            complete_lap()
            print(f"Completed lap {lap + 1}")

        print("All laps completed.")

    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        
    finally:
        control_motor(0)  # Ensure motor is stopped
        servo.set_angle(0)  # Center the steering

if __name__ == "__main__":
    main()
