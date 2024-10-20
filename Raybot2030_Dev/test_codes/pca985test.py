from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# Initialize I2C bus
i2c = busio.I2C(SCL, SDA)

# Create a PCA9685 object
pca = PCA9685(i2c)
pca.frequency = 50  # Set frequency to 50Hz for servos

# Define the custom servo class
class PCA9685Servo:
    def __init__(self, channel, min_pulse=1000, max_pulse=2000):
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

    def set_angle(self, angle):
        # Angle should be between -1 (full left) to 1 (full right)
        # Convert angle to pulse width
        pulse_width = self.min_pulse + (self.max_pulse - self.min_pulse) * ((angle + 1) / 2)
        self.channel.duty_cycle = int(pulse_width * 0xFFFF / 20000)

# Create a servo on channel 0
servo = PCA9685Servo(pca.channels[0])

# Test the servo with angles
servo.set_angle(-1)  # Full counterclockwise
time.sleep(1)
servo.set_angle(0)   # Center
time.sleep(1)
servo.set_angle(1)   # Full clockwise
time.sleep(1)

# Cleanup
pca.deinit()
