from gpiozero import Button
from signal import pause

# Set up the button on GPIO 26 with pull-up enabled
button = Button(22, pull_up=True)

# Function to run when the button is pressed
def on_button_press():
    print("Button pressed")

# Function to run when the button is released
def on_button_release():
    print("Button released")

# Assign functions to button events
button.when_pressed = on_button_press
button.when_released = on_button_release

# Keep the program running
pause()
