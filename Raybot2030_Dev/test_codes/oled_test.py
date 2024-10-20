from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Create the I2C interface
serial = i2c(port=1, address=0x3C)

# Create the OLED device
device = ssd1306(serial, width=128, height=64)

# Clear the display
device.clear()

# Draw something
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Test", fill="white")

print("If you can see a white rectangle with 'Test' written inside, the display is working.")
print("If not, there might be a connection or configuration issue.")

input("Press Enter to exit...")