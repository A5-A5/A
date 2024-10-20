import smbus2
import time

# MPU-6050 Registers
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# I2C address of the MPU-6050
DEVICE_ADDRESS = 0x68

# Initialize I2C bus
bus = smbus2.SMBus(1)  # Use 1 for Raspberry Pi 5 (might be different on older models)

def init_mpu():
    # Wake up the MPU-6050
    bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0)

def read_word(reg):
    high = bus.read_byte_data(DEVICE_ADDRESS, reg)
    low = bus.read_byte_data(DEVICE_ADDRESS, reg + 1)
    value = (high << 8) + low
    return value

def read_word_2c(reg):
    val = read_word(reg)
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

def get_gyro_data():
    gyro_xout = read_word_2c(GYRO_XOUT_H) / 131
    gyro_yout = read_word_2c(GYRO_YOUT_H) / 131
    gyro_zout = read_word_2c(GYRO_ZOUT_H) / 131
    return gyro_xout, gyro_yout, gyro_zout

def main():
    init_mpu()
    try:
        while True:
            gyro_x, gyro_y, gyro_z = get_gyro_data()
            print(f"Gyro X: {gyro_x:.2f} deg/s")
            print(f"Gyro Y: {gyro_y:.2f} deg/s")
            print(f"Gyro Z: {gyro_z:.2f} deg/s")
            print("------------------------")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program stopped by user")

if __name__ == "__main__":
    main()
