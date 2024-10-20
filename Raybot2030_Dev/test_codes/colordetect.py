import cv2
import numpy as np
from picamera2 import Picamera2
import time

def detect_colors(frame):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define color ranges in HSV for red, green, blue, orange, black, magenta
    color_ranges = {
        'red': ([0, 120, 70], [10, 255, 255]),
        'red2': ([170, 120, 70], [180, 255, 255]),  # Red upper bound for HSV wrapping
        'green': ([40, 50, 50], [80, 255, 255]),
        'blue': ([100, 150, 0], [140, 255, 255]),
        'orange': ([10, 100, 20], [25, 255, 255]),
        'black': ([0, 0, 0], [180, 255, 30]),
        'magenta': ([140, 50, 50], [170, 255, 255])
    }
    
    detected_colors = []
    
    for color, (lower, upper) in color_ranges.items():
        lower = np.array(lower)
        upper = np.array(upper)
        
        # Create a mask for the color
        mask = cv2.inRange(hsv, lower, upper)
        
        # Clean the mask using morphological operations to remove noise
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=1)
        
        # If any color is detected (non-zero pixels), store the color name
        if cv2.countNonZero(mask) > 0:
            detected_colors.append(color)
            
            # Optionally, draw contours for each detected color
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 500:  # Filter small areas
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, color, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return detected_colors, frame

# Initialize the camera with autofocus and maximum FPS configuration for wide-angle camera
picam2 = Picamera2()

# Create a wide-angle configuration for the RPi Camera Module 3 Wide Angle
camera_config = picam2.create_preview_configuration(
    main={"format": 'XRGB8888', "size": (800, 480)},  # Set to a higher resolution for wide-angle view
    controls={
        "AfMode": 1,  # Enable Continuous Autofocus (CAF)
        "AfTrigger": 0,  # Autofocus mode
        "FrameRate": 120  # Set the frame rate to the maximum (120 FPS)
    }
)
picam2.configure(camera_config)
picam2.start()

# Variables for FPS calculation
frame_count = 0
start_time = time.time()
fps = 0  # Initialize the fps variable

while True:
    # Capture frame-by-frame
    frame = picam2.capture_array()

    # Apply slight Gaussian blur to reduce noise
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    
    # Detect multiple colors
    detected_colors, frame_with_detections = detect_colors(frame)
    
    frame_count += 1
    
    # Calculate FPS every 120 frames
    if frame_count == 120:
        end_time = time.time()
        fps = frame_count / (end_time - start_time)
        start_time = time.time()
        frame_count = 0
    
    # Display FPS on the frame
    cv2.putText(frame_with_detections, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if detected_colors:
        color_text = ', '.join(detected_colors)
        cv2.putText(frame_with_detections, f"Colors: {color_text}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        cv2.putText(frame_with_detections, "No colors detected", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Display the resulting frame
    cv2.imshow('Frame', frame_with_detections)
    
    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cv2.destroyAllWindows()
picam2.stop()
