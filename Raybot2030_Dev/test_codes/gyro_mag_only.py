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

# Enable only the magnetometer report
bno.enable_feature(adafruit_bno08x.BNO_REPORT_MAGNETOMETER)

def get_magnetic_data():
    return bno.magnetic  # µT

def calculate_heading(x, y):
    import math
    heading = math.atan2(y, x)
    heading = math.degrees(heading)
    if heading < 0:
        heading += 360
    return heading

try:
    while True:
        mag_x, mag_y, mag_z = get_magnetic_data()
        heading = calculate_heading(mag_x, mag_y)
        
        print("\033[H\033[J", end="")  # Clear the console
        print(f"Magnetic Field (µT): X={mag_x:.2f}, Y={mag_y:.2f}, Z={mag_z:.2f}")
        print(f"Heading: {heading:.2f}°")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
except Exception as e:
    print(f"An error occurred: {e}")