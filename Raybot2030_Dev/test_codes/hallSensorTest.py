from gpiozero import Button
import time

# GPIO Pin where the Hall sensor is connected
HALL_SENSOR_PIN = 4
button = Button(26, pull_up=True)



# Function to run when the button is pressed
def on_button_press():
    print("Button pressed")

# Function to run when the button is released
def on_button_release():
    print("Button released")


button.when_pressed = on_button_press
button.when_released = on_button_release


# Setup Hall sensor using gpiozero's Button class
hall_sensor = Button(HALL_SENSOR_PIN)

# Function to check if the sensor is triggered
def hall_sensor_triggered():
    print("Magnet detected!")

# Register the event handler for when the Hall sensor is triggered
hall_sensor.when_pressed = hall_sensor_triggered

try:
    while True:
        # Continuously monitor the sensor
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Test stopped by user")
