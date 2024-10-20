#!/usr/bin/env python3
from gpiozero import Button
from signal import pause
import subprocess
import time

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

# OLED Controller
class OLEDController:
    def __init__(self, port=1, address=0x3C, width=128, height=64):
        serial = i2c(port=port, address=address)
        self.device = ssd1306(serial, width=width, height=height)
        self.font = ImageFont.load_default()

    def display_info(self, lines):
        """
        Display multiple lines of text on the OLED.
        :param lines: List of strings to display.
        """
        with canvas(self.device) as draw:
            for i, line in enumerate(lines):
                draw.text((0, i * 16), line, fill="white", font=self.font)

    def clear(self):
        """Clear the OLED display."""
        self.device.clear()

def create_oled(port=1, address=0x3C, width=128, height=64):
    """Create and return an OLEDController instance."""
    return OLEDController(port, address, width, height)

# Create OLED instance
oled = create_oled()

# Button handling
button = Button(22)
press_start_time = 0
long_press_threshold = 1.0  # seconds

def handle_press():
    global press_start_time
    press_start_time = time.time()

def handle_release():
    global press_start_time
    press_duration = time.time() - press_start_time
   
    if press_duration < long_press_threshold:
        message = "Single click - anticlock"
        print("Single click detected! Running single_click_action.py")
        oled.display_info([message, "Running", "single_click_action.py"])
        # subprocess.run(["python3", "/home/jojo/third/no_camera_anticlock.py"])
    else:
        message = "Long press - clock"
        print("Long press detected! Running long_press_action.py")
        oled.display_info([message, "Running", "long_press_action.py"])
        # subprocess.run(["python3", "/home/jojo/third/no_camera_clock.py"])
    
    # Clear the display after 3 seconds
    time.sleep(3)
    oled.clear()

button.when_pressed = handle_press
button.when_released = handle_release

# Main execution
if __name__ == "__main__":
    oled.display_info(["Press button", "to start"])
    pause()