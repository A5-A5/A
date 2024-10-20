import time
import board
import busio
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C

def scan_i2c_devices():
    i2c = busio.I2C(board.SCL, board.SDA)
    devices = []
    for address in range(128):
        try:
            i2c.try_lock()
            i2c.writeto(address, b'')
            devices.append(hex(address))
        except:
            pass
        finally:
            i2c.unlock()
    return devices

print("Scanning for I2C devices...")
devices = scan_i2c_devices()
print(f"Found devices at addresses: {', '.join(devices)}")

i2c = busio.I2C(board.SCL, board.SDA)

try:
    bno = BNO08X_I2C(i2c, address=0x4B)  # Set the address to 0x4B
    print("BNO085 sensor initialized successfully")
except ValueError as e:
    print(f"Error initializing BNO085: {e}")
    print("Make sure the sensor is connected properly and the address is correct.")
    print("Available I2C devices:")
    print(scan_i2c_devices())
    raise

# Enable the necessary reports
bno.enable_feature(adafruit_bno08x.BNO_REPORT_ACCELEROMETER)
bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
bno.enable_feature(adafruit_bno08x.BNO_REPORT_MAGNETOMETER)
bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)

def get_sensor_data():
    accel_x, accel_y, accel_z = bno.acceleration  # m/s^2
    gyro_x, gyro_y, gyro_z = bno.gyro  # rad/s
    mag_x, mag_y, mag_z = bno.magnetic  # µT
    quat_i, quat_j, quat_k, quat_real = bno.quaternion

    # Convert quaternion to Euler angles
    roll, pitch, yaw = quat_to_euler(quat_i, quat_j, quat_k, quat_real)

    return {
        'acceleration': (accel_x, accel_y, accel_z),
        'gyro': (gyro_x, gyro_y, gyro_z),
        'magnetic': (mag_x, mag_y, mag_z),
        'euler': (roll, pitch, yaw)
    }

def quat_to_euler(x, y, z, w):
    """Convert quaternion to Euler angles (roll, pitch, yaw)"""
    import math
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return (math.degrees(roll), math.degrees(pitch), math.degrees(yaw))

try:
    while True:
        data = get_sensor_data()
        
        print("\033[H\033[J", end="")  # Clear the console
        print(f"Acceleration (m/s^2): X={data['acceleration'][0]:.2f}, Y={data['acceleration'][1]:.2f}, Z={data['acceleration'][2]:.2f}")
        print(f"Gyro (rad/s): X={data['gyro'][0]:.2f}, Y={data['gyro'][1]:.2f}, Z={data['gyro'][2]:.2f}")
        print(f"Magnetic (µT): X={data['magnetic'][0]:.2f}, Y={data['magnetic'][1]:.2f}, Z={data['magnetic'][2]:.2f}")
        print(f"Euler Angles (degrees): Roll={data['euler'][0]:.2f}, Pitch={data['euler'][1]:.2f}, Yaw={data['euler'][2]:.2f}")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
except Exception as e:
    print(f"An error occurred: {e}")