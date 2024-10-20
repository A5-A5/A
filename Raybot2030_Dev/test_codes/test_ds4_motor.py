import time
import pygame
from gpiozero import AngularServo, PWMOutputDevice

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

# Servo setup using gpiozero AngularServo
servo = AngularServo(18, min_angle=-90, max_angle=90, min_pulse_width=0.0006, max_pulse_width=0.0023)

# IBT-2 motor driver pin setup for a single DC motor
# Using GPIO 17 for forward and GPIO 27 for reverse
RPWM_PIN = 17  # Forward control pin
LPWM_PIN = 27  # Reverse control pin

# Set up the IBT-2 motor driver control pins
motor_forward = PWMOutputDevice(RPWM_PIN)
motor_reverse = PWMOutputDevice(LPWM_PIN)

# Wait for DS4 controller to be connected
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

# Function to control DC motor using the joystick's forward/backward axis
def control_motor(speed):
    if speed > 0:
        motor_forward.value = speed
        motor_reverse.off()
    elif speed < 0:
        motor_reverse.value = -speed
        motor_forward.off()
    else:
        motor_forward.off()
        motor_reverse.off()

# Control loop to handle DS4 input and control both the servo and DC motor
def control_loop():
    running = True
    dead_zone = 0.1  # Dead zone for joystick
    max_speed = 1.0  # Max speed value for motor (from 0.0 to 1.0)
    options_button = 9  # DS4 Options button ID
    button_press_time = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check for Options button press and release
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == options_button:
                    button_press_time = time.time()
                    print("Options button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == options_button:
                    if button_press_time and (time.time() - button_press_time >= 5):
                        print("Options button held for 5 seconds. Initiating shutdown.")
                    button_press_time = None

        if button_press_time and (time.time() - button_press_time >= 6):
            os.system('sudo shutdown now -h')
            print("Shutdown command executed.")
            running = False

        # Get joystick axes for controlling the motor and servo
        steering_input = - joystick.get_axis(0)  # Left joystick horizontal for steering
        throttle_input = - joystick.get_axis(4)  # Left joystick vertical for motor speed

        # Apply dead zone
        if abs(steering_input) < dead_zone:
            steering_input = 0
        if abs(throttle_input) < dead_zone:
            throttle_input = 0

        # Map joystick input to servo angle (convert to a value between -90 and 90 degrees)
        angle = steering_input * 90
        servo.angle = angle  # Set servo angle for steering

        # Map joystick input to motor speed
        motor_speed = throttle_input * -max_speed  # Invert to match forward/backward
        control_motor(motor_speed)  # Set motor speed

        time.sleep(0.1)  # Small delay for loop

def destroy():
    servo.angle = 0  # Reset servo to neutral position (0 degrees)
    control_motor(0)  # Stop the motor

if __name__ == '__main__':
    try:
        control_loop()
    except KeyboardInterrupt:
        destroy()
