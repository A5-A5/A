import smbus2
import time
import numpy as np

# MPU-6050 Registers
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# I2C address of the MPU-6050
DEVICE_ADDRESS = 0x68

# Initialize I2C bus
bus = smbus2.SMBus(1)  # Use 1 for Raspberry Pi 5

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

def init_mpu():
    bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0)

def read_word(reg):
    high = bus.read_byte_data(DEVICE_ADDRESS, reg)
    low = bus.read_byte_data(DEVICE_ADDRESS, reg + 1)
    return (high << 8) + low

def read_word_2c(reg):
    val = read_word(reg)
    return -((65535 - val) + 1) if val >= 0x8000 else val

class RCCarGyroSystem:
    def __init__(self):
        self.kf_x = KalmanFilter(process_variance=0.01, measurement_variance=0.1)
        self.kf_y = KalmanFilter(process_variance=0.01, measurement_variance=0.1)
        self.kf_z = KalmanFilter(process_variance=0.01, measurement_variance=0.1)
        
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        
        self.flip_threshold = 45  # degrees
        self.drift_threshold = 20  # degrees per second
        
        self.calibrate_gyro()

    def calibrate_gyro(self, samples=1000):
        print("Calibrating gyroscope. Keep the RC car still...")
        sum_x = sum_y = sum_z = 0
        for _ in range(samples):
            x, y, z = self.get_raw_data()
            sum_x += x
            sum_y += y
            sum_z += z
            time.sleep(0.001)
        
        self.offset_x = sum_x / samples
        self.offset_y = sum_y / samples
        self.offset_z = sum_z / samples
        print("Calibration complete.")
        print(f"Offsets - X: {self.offset_x:.2f}, Y: {self.offset_y:.2f}, Z: {self.offset_z:.2f}")

    def get_raw_data(self):
        return (read_word_2c(GYRO_XOUT_H) / 131,
                read_word_2c(GYRO_YOUT_H) / 131,
                read_word_2c(GYRO_ZOUT_H) / 131)

    def get_filtered_data(self):
        x, y, z = self.get_raw_data()
        return (
            self.kf_x.update(x - self.offset_x),
            self.kf_y.update(y - self.offset_y),
            self.kf_z.update(z - self.offset_z)
        )

    def update_offset(self, alpha=0.01):
        x, y, z = self.get_raw_data()
        self.offset_x = (1 - alpha) * self.offset_x + alpha * x
        self.offset_y = (1 - alpha) * self.offset_y + alpha * y
        self.offset_z = (1 - alpha) * self.offset_z + alpha * z

    def check_flip_risk(self, roll):
        return abs(roll) > self.flip_threshold

    def drift_assist(self, yaw_rate):
        if abs(yaw_rate) > self.drift_threshold:
            # Implement drift control logic here
            pass

    def terrain_analysis(self, x, y, z):
        # Implement vibration analysis for terrain detection
        pass

    def adjust_motor_power(self, pitch, roll):
        # Implement traction control logic here
        pass

def main():
    init_mpu()
    rc_system = RCCarGyroSystem()

    update_counter = 0
    try:
        while True:
            x, y, z = rc_system.get_filtered_data()

            # Clear the screen and print data
            print("\033[H\033[J", end="")
            print(f"Pitch (X): {x:6.2f} deg/s")
            print(f"Roll  (Y): {y:6.2f} deg/s")
            print(f"Yaw   (Z): {z:6.2f} deg/s")

            # Run RC car control systems
            if rc_system.check_flip_risk(y):
                print("Flip risk detected!")
            
            rc_system.drift_assist(z)
            rc_system.terrain_analysis(x, y, z)
            rc_system.adjust_motor_power(x, y)

            # Periodic offset update
            update_counter += 1
            if update_counter >= 1000:  # Update offset every 1000 iterations
                rc_system.update_offset()
                update_counter = 0

            time.sleep(0.01)  # 100Hz update rate

    except KeyboardInterrupt:
        print("\nProgram stopped by user")

if __name__ == "__main__":
    main()