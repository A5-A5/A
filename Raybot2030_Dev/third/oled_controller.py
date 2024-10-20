from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

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