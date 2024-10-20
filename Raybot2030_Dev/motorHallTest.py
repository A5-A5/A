import time
import pygame

from motor_controller import create_dc_motor
from servo_controller import create_servo
from oled_controller import create_oled
from hallSensor_controller import create_hall_sensor



# Create an instance from each controller
motor = create_dc_motor()  # Uses default pins 17 and 27
servo = create_servo(channel=0)  # Use channel 0, you can change this as needed
oled = create_oled() # address 0x3C
hall_sensor = create_hall_sensor()


print("it started")

# Wait for DS4 controller to be connected
# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()


joystick = None
while joystick is None:
    pygame.joystick.quit()
    pygame.joystick.init()
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print("DS4 controller connected.")
    except pygame.error:
        print("Waiting for DS4 controller to be connected...")
        time.sleep(1)



# Control loop to handle DS4 input and control both the servo and DC motor
def control_loop():
    running = True
    dead_zone = 0.1  # Dead zone for joystick
    max_speed = 0.6  # Max speed value for motor (from 0.0 to 1.0)
    cross_button = 0  # DS4 Cross (X) button ID for moving 1 meter
    options_button = 9  # DS4 Options button ID for shutdown
    circle_button = 2  # DS4 Circle button ID for clear distance

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check for Cross (X) button press
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == cross_button:
                    print("Cross (X) button pressed. Moving 1 meter.")
                    hall_sensor.move_one_meter(motor, None)

                # Check for Options button press to start shutdown countdown
                elif event.button == options_button:
                    button_press_time = time.time()
                    print("Options button pressed.")
                    
                    
                elif event.button == circle_button:
                    button_press_time = time.time()
                    print("circle button pressed.")
                    hall_sensor.reset_distance()



        # Get joystick axes for controlling the motor and servo
        steering_input = -joystick.get_axis(0)  # Left joystick horizontal for steering
        throttle_input = joystick.get_axis(4)  # Left joystick vertical for motor speed

        # Apply dead zone
        if abs(steering_input) < dead_zone:
            steering_input = 0
        if abs(throttle_input) < dead_zone:
            throttle_input = 0

        # Map joystick input to servo angle (convert to a value between -90 and 90 degrees)
        angle = steering_input * 90
        # servo.set_angle(angle)  # Set servo angle for steering
        servo.set_angle(angle)

        # Map joystick input to motor speed
        motor_speed = throttle_input * -max_speed  # Invert to match forward/backward
        motor.set_speed(motor_speed) # Set motor speed
        
        
        oled.display_info(["Motor Speed:",f"{motor_speed:.2f}","Distance (cm):",f"{hall_sensor.get_distance_moved():.2f}"])
        print(f"Motor speed: {motor_speed}  -  Distance Moved: {hall_sensor.get_distance_moved()}  -  Steer Angle: {angle}")  # Print motor speed for debugging


        time.sleep(0.1)  # Small delay for loop

def destroy():
    servo.center()  # Reset servo to neutral position (0 degrees)
    motor.stop()  # Stop the motor

if __name__ == '__main__':
    try:
        control_loop()
    except KeyboardInterrupt:
        print("Stopping...")

        destroy()
