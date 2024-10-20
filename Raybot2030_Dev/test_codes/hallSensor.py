from gpiozero import Button
import time

# GPIO Pin where the Hall sensor is connected
HALL_SENSOR_PIN = 4

# Distance per shaft rotation in meters (adjust based on your car's gear ratio)
DISTANCE_PER_ROTATION = 0.05  # Example: 0.05 meters per shaft rotation

# Setup Hall sensor using gpiozero's Button class (it detects edges for us)
hall_sensor = Button(HALL_SENSOR_PIN)

# Variables to store data
pulse_count = 0
distance_moved = 0.0

# Function to increment pulse count
def hall_sensor_triggered():
    global pulse_count
    pulse_count += 1

# Register the event handler for the Hall sensor
hall_sensor.when_pressed = hall_sensor_triggered

try:
    while True:
        # Calculate the distance based on the number of pulses
        distance_moved = pulse_count * DISTANCE_PER_ROTATION
        
        # Display the calculated distance
        print(f"Distance moved: {distance_moved:.2f} meters")
        
        # Wait for a short time before checking again
        time.sleep(1)

except KeyboardInterrupt:
    # Cleanup happens automatically with gpiozero
    pass
