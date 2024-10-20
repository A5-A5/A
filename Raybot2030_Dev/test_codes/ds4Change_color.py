import time
import os

def set_ds4_led_color(hex_color):
    """Set the DS4 LED color using a hex color code."""
    # Use the ds4drv command to change the LED color using hex directly
    os.system(f"ds4drv control --led {hex_color}")

# Example: Change LED color to red (#FF0000)
set_ds4_led_color("#FF0000")
time.sleep(3)  # Keep the color for 3 seconds

# Example: Change LED color to blue (#0000FF)
set_ds4_led_color("#0000FF")
time.sleep(3)  # Keep the color for 3 seconds

# You can modify the hex values and duration as needed
