import smbus

# Initialize I2C bus
bus = smbus.SMBus(1)

# Magnetometer (possibly at address 0x70)
magnetometer_address = 0x70

# Example: Reading from the magnetometer's data registers (assuming standard setup)
mag_x = bus.read_byte_data(magnetometer_address, 0x03)  # X-axis low byte
mag_y = bus.read_byte_data(magnetometer_address, 0x05)  # Y-axis low byte
mag_z = bus.read_byte_data(magnetometer_address, 0x07)  # Z-axis low byte

print(f"Magnetometer X: {mag_x}, Y: {mag_y}, Z: {mag_z}")
