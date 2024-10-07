import cv2
import numpy as np
from gpiozero import LED, Motor, Servo
import time
from adafruit_servokit import ServoKit
from picamera2 import Picamera2
import json
import os

def _init_camera(self):
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": (500, 400), "format": "RGB888"})
    picam2.configure(video_config)
    picam2.start()
    return picam2

# Initialize motor and servo for movement control
motor = Motor(forward=27, backward=17)
kit = ServoKit(channels=8)

# File to store the HSV values
json_file_path = 'hsv_values.json'

# Movement variables
original_speed = 0.12
steer_speed = 0.1
speed = original_speed
left_angle = 90+60
right_angle = 90-60
center_angle = 90

start_robot = False
steer_lock_end_time = 0
similarity_start_time = 0

# Threshold for frame similarity
similarity_threshold = 0.9  # Similarity percentage
similarity_duration = 3  # 3 seconds

last_backward_time = 0
backward_delay = 4

# Store previous frame to compare
previous_frame = None
similar_frame_count_start = 0

# Initialize orange strip count
orange_strip_count = 0
orange_in_previous_frame = False  # Flag to track orange detection between frames
blue_strip_count = 0
blue_in_previous_frame = False

# Function to move the car forward, backward, and stop
def motor_forward(speed=speed):
    global start_robot
    print("Move Forward")
    if start_robot:
        motor.forward(speed)

def motor_backward():
    print("Move Backward")
    if start_robot:
        motor.backward(speed)

def motor_stop():
    print("Stop")
    motor.stop()

# Servo control for steering
def steer_left(angle=left_angle):
    print("Steer Left")
    global speed
    speed = steer_speed
    kit.servo[0].angle = int(left_angle)

def steer_right(angle=right_angle):
    print("Steer Right")
    global speed
    speed = steer_speed
    kit.servo[0].angle = int(right_angle)

def steer_center():
    print("Steer Center")
    global speed
    speed = original_speed
    kit.servo[0].angle = int(center_angle)
