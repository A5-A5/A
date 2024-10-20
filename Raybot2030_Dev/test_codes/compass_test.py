import smbus
import time
import math

# Compass module address
COMPASS_ADDRESS = 0x70

# Register addresses (these may need adjustment)
REG_XOUT_LSB = 0x00
REG_XOUT_MSB = 0x01
REG_YOUT_LSB = 0x02
REG_YOUT_MSB = 0x03
REG_ZOUT_LSB = 0x04
REG_ZOUT_MSB = 0x05

bus = smbus.SMBus(1)  # Use bus 1 for Raspberry Pi 5

def init_compass():
    # Your compass might need specific initialization.
    # Consult your compass module's datasheet for details.
    print("Compass initialization complete")

def read_raw_data():
    try:
        data = bus.read_i2c_block_data(COMPASS_ADDRESS, REG_XOUT_LSB, 6)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        
        # Convert to signed values if necessary
        x = x - 65536 if x > 32767 else x
        y = y - 65536 if y > 32767 else y
        z = z - 65536 if z > 32767 else z
        
        print(f"Raw data: X={x}, Y={y}, Z={z}")
        return [x, y, z]
    except OSError as e:
        print(f"Error reading data: {e}")
        return [0, 0, 0]

def get_heading():
    [x, y, z] = read_raw_data()
    if x == 0 and y == 0:
        return 0.0
    heading = math.atan2(y, x)
    heading_deg = math.degrees(heading)
    if heading_deg < 0:
        heading_deg += 360
    return heading_deg

try:
    init_compass()
    while True:
        heading = get_heading()
        print(f"Heading: {heading:.2f} degrees")
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated by user")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    bus.close()