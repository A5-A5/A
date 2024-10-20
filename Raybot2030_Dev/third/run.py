import cv2
import numpy as np
import time
from gpiozero import LED, Motor, Servo
from picamera2 import Picamera2
from motor_controller import create_dc_motor
from servo_controller import create_servo
from oled_controller import create_oled
from hallSensor_controller import create_hall_sensor
from calibration import load_hsv_from_json

class AutonomousCar:
    def __init__(self):
        self.motor = create_dc_motor()
        self.servo = create_servo(channel=0)
        self.oled = create_oled()
        self.hall_sensor = create_hall_sensor()
        self.last_actions = []
        self.max_action_memory = 5
        self.correction_cooldown = 0
        
        self.motor_speed = 0.17
        self.steering_ratio = 0.5
        self.orange_blue_counter = 0
        self.MIN_CONTOUR_AREA = 700
        
        self.color_ranges = self._init_color_ranges()
        self.picam2 = self._init_camera()

    def _init_color_ranges(self):
        return {
            'black': {'lower': np.array([0, 0, 0]), 'upper': np.array([180, 255, 50]), 'label': 'Black', 'color': (0, 0, 0)},
            'red': {'lower': np.array([0, 120, 70]), 'upper': np.array([10, 255, 255]), 'label': 'Red', 'color': (0, 0, 255)},
            'green': {'lower': np.array([40, 70, 70]), 'upper': np.array([80, 255, 255]), 'label': 'Green', 'color': (0, 255, 0)},
            'orange': {'lower': np.array([5, 100, 100]), 'upper': np.array([15, 255, 255]), 'label': 'Orange', 'color': (0, 165, 255)},
            'blue': {'lower': np.array([100, 150, 0]), 'upper': np.array([140, 255, 255]), 'label': 'Blue', 'color': (255, 0, 0)}
        }

    def _init_camera(self):
        picam2 = Picamera2()
        video_config = picam2.create_video_configuration(main={"size": (500, 400), "format": "RGB888"})
        picam2.configure(video_config)
        picam2.start()
        return picam2

    def motor_control(self, direction):
        if direction == 'forward':
            print("Move Forward")
            self.motor.set_speed(self.motor_speed)
        elif direction == 'backward':
            print("Move Backward")
            self.motor.set_speed(-self.motor_speed)
        else:
            print("Stop")
            self.motor.stop()

    def steer_control(self, direction):
        if direction == 'left':
            print("Steer Left")
            self.servo.set_angle(90)
        elif direction == 'right':
            print("Steer Right")
            self.servo.set_angle(-90)
        else:
            print("Steer Center")
            self.servo.center()

    def detect_color_contours(self, hsv_frame, color):
        mask = cv2.inRange(hsv_frame, self.color_ranges[color]['lower'], self.color_ranges[color]['upper'])
        blurred_mask = cv2.GaussianBlur(mask, (5, 5), 0)
        _, thresh_mask = cv2.threshold(blurred_mask, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [c for c in contours if cv2.contourArea(c) > self.MIN_CONTOUR_AREA]

    def define_rectangles(self, frame_shape):
        h, w = frame_shape[:2]
        center_x, center_y = w // 2, h // 2
        width_middle_center = 150
        
        return {
            'middle_center': ((center_x - width_middle_center, center_y - 50), (center_x + width_middle_center, center_y + 50)),
            'left_center': ((0, center_y - 50), (center_x - 150, center_y + 50)),
            'right_center': ((center_x + 150, center_y - 50), (w, center_y + 50)),
            'lower_middle': ((center_x - 50, center_y + 100), (center_x + 50, h))
        }

    def is_contour_in_rectangle(self, contour, rectangle):
        x, y, w, h = cv2.boundingRect(contour)
        (rx1, ry1), (rx2, ry2) = rectangle
        return x < rx2 and x + w > rx1 and y < ry2 and y + h > ry1

    def draw_labeled_contours(self, frame, contours, color_label, color):
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, color_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def drive_based_on_contours(self, frame, hsv_frame):
        contours = {color: self.detect_color_contours(hsv_frame, color) for color in self.color_ranges}
        rectangles = self.define_rectangles(frame.shape)

        for rect_name, rect in rectangles.items():
            cv2.rectangle(frame, rect[0], rect[1], (255, 255, 255), 2)

        for color, color_contours in contours.items():
            self.draw_labeled_contours(frame, color_contours, self.color_ranges[color]['label'], self.color_ranges[color]['color'])

        # Steering logic based on black and blue contours
        black_in_left = any(self.is_contour_in_rectangle(c, rectangles['left_center']) for c in contours['black'])
        black_in_right = any(self.is_contour_in_rectangle(c, rectangles['right_center']) for c in contours['black'])
        blue_in_left = any(self.is_contour_in_rectangle(c, rectangles['left_center']) for c in contours['blue'])
        blue_in_right = any(self.is_contour_in_rectangle(c, rectangles['right_center']) for c in contours['blue'])
        
        # Debug information
        cv2.putText(frame, f"Black Left: {black_in_left}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, f"Black Right: {black_in_right}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, f"Blue Left: {blue_in_left}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, f"Blue Right: {blue_in_right}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Determine action
        if self.correction_cooldown > 0:
            self.correction_cooldown -= 1
            action = 'correction'
        elif black_in_left or blue_in_left:
            action = 'right'
        elif black_in_right or blue_in_right:
            action = 'left'
        else:
            action = 'forward'

        # Perform action
        if action == 'right':
            self.steer_control('right')
            self.motor_control('forward')
            cv2.putText(frame, "Steering: Right", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif action == 'left':
            self.steer_control('left')
            self.motor_control('forward')
            cv2.putText(frame, "Steering: Left", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif action == 'correction':
            self.steer_control('center')
            self.motor_control('backward')
            cv2.putText(frame, "Correction: Backward", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            self.steer_control('center')
            self.motor_control('forward')
            cv2.putText(frame, "Steering: Center", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Update action history
        self.last_actions.append(action)
        if len(self.last_actions) > self.max_action_memory:
            self.last_actions.pop(0)

        # Check for repeated right turns
        if len(self.last_actions) == self.max_action_memory and all(a == 'right' for a in self.last_actions[:-1]) and self.last_actions[-1] == 'forward':
            self.correction_cooldown = 10  # Adjust this value to control how long the correction lasts
            self.last_actions = []  # Clear the action history

        return frame

    def motor_control(self, direction):
        if direction == 'forward':
            print("Move Forward")
            self.motor.set_speed(self.motor_speed)
        elif direction == 'backward':
            print("Move Backward")
            self.motor.set_speed(-self.motor_speed * 0.5)  # Move backward at half speed
        else:
            print("Stop")
            self.motor.stop()

    def run(self):
        while True:
            frame = self.picam2.capture_array()
            if frame is None:
                print("Failed to capture frame")
                break

            load_hsv_from_json()
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            frame = self.drive_based_on_contours(frame, hsv_frame)
            cv2.imshow("Autonomous Car", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                break

        self.picam2.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    car = AutonomousCar()
    car.run()