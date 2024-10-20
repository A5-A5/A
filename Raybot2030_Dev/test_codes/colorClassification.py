import cv2
import numpy as np
from picamera2 import Picamera2

# Initialize the camera
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start()

# Define color ranges (in HSV)
color_ranges = {
    'Red': ([0, 100, 100], [10, 255, 255]),
    'Green': ([40, 40, 40], [80, 255, 255]),
    'Blue': ([100, 100, 100], [140, 255, 255]),
    'Magenta': ([140, 100, 100], [170, 255, 255]),
    'Black': ([0, 0, 0], [180, 255, 30])
}

def detect_colors(frame):
    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    for color_name, (lower, upper) in color_ranges.items():
        # Create a mask for the current color
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        for contour in contours:
            # Calculate area and remove small elements
            area = cv2.contourArea(contour)
            if area > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return frame

try:
    while True:
        # Capture frame
        frame = picam2.capture_array()
        
        # Detect and label colors
        processed_frame = detect_colors(frame)
        
        # Display the resulting frame
        cv2.imshow('Color Detection', processed_frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Clean up
    cv2.destroyAllWindows()
    picam2.stop()