# Color thresholds (HSV) loaded from JSON or defaults
color_ranges = {
    'black': {'lower': np.array([0, 0, 0]), 'upper': np.array([180, 255, 50]), 'label': 'Black'},
    'red': {'lower': np.array([0, 120, 70]), 'upper': np.array([10, 255, 255]), 'label': 'Red'},
    'green': {'lower': np.array([40, 70, 70]), 'upper': np.array([80, 255, 255]), 'label': 'Green'},
    'orange': {'lower': np.array([5, 100, 100]), 'upper': np.array([15, 255, 255]), 'label': 'Orange'},
    'blue': {'lower': np.array([100, 150, 0]), 'upper': np.array([140, 255, 255]), 'label': 'Blue'},
    'maginta': {'lower': np.array([0, 100, 100]), 'upper': np.array([10, 255, 255]), 'label':'Magenta'}
}

# Pattern detection counters
orange_blue_counter = 0

# Minimum contour area threshold to filter small contours
MIN_CONTOUR_AREA = 700  # You can adjust this value as needed

# Function to create the mask and return the pixel positions within the masked region
def detect_color_pixels(hsv_frame, color):
    mask = cv2.inRange(hsv_frame, color_ranges[color]['lower'], color_ranges[color]['upper'])
    blurred_mask = cv2.GaussianBlur(mask, (5, 5), 0)
    # Apply thresholding after the blur
    _, thresh_mask = cv2.threshold(blurred_mask, 127, 255, cv2.THRESH_BINARY)
    # Extract the coordinates of non-zero pixels in the mask
    pixel_positions = np.argwhere(thresh_mask > 0)
    return pixel_positions, thresh_mask

# Function to detect the color contours and return bounding rectangles
def detect_color_contours(hsv_frame, color):
    mask = cv2.inRange(hsv_frame, color_ranges[color]['lower'], color_ranges[color]['upper'])
    blurred_mask = cv2.GaussianBlur(mask, (5, 5), 0)
    # Apply thresholding after the blur
    _, thresh_mask = cv2.threshold(blurred_mask, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours by area
    filtered_contours = [c for c in contours if cv2.contourArea(c) > MIN_CONTOUR_AREA]
    
    return filtered_contours

# Function to define rectangles
def define_rectangles(frame_shape):
    h, w = frame_shape[:2]
    center_x = w // 2
    center_y = h // 2
    
    # Define key regions
    width_middle_center = 200
    middle_center = ((center_x - width_middle_center, center_y - 100), (center_x + width_middle_center, center_y + 100))
    left_center = ((0, center_y - 50), (center_x - 200, center_y + 50))
    right_center = ((center_x + 200, center_y - 50), (w, center_y + 50))
    left_block_detector = ((0, 250), (center_x - 200, h))
    right_block_detector = ((center_x + 200, 250), (w, h))
    lower_middle = ((center_x - 100, center_y + 150), (center_x + 100, h))

    return middle_center, left_center, right_center, left_block_detector, right_block_detector, lower_middle

threshold_pixels_num = 100
# Check if a set of pixels are in a specific rectangle
def are_pixels_in_rectangle(pixels, rectangle):
    (rx1, ry1), (rx2, ry2) = rectangle
    
    # Count the number of pixels that fall inside the rectangle
    pixels_in_rectangle = [p for p in pixels if rx1 <= p[1] <= rx2 and ry1 <= p[0] <= ry2]
    
    # Define a threshold for pixel count to consider it detected
    return len(pixels_in_rectangle)  # Adjust threshold based on testing

# Check if part of a contour is in a specific rectangle
def is_contour_in_rectangle(contour, rectangle):
    x, y, w, h = cv2.boundingRect(contour)
    (rx1, ry1), (rx2, ry2) = rectangle
    
    # Check if the bounding rectangle of the contour overlaps with the detection rectangle
    if x < rx2 and x + w > rx1 and y < ry2 and y + h > ry1:
        return True
    return False

# Function to draw bounding boxes and label contours
def draw_labeled_contours(frame, contours, color_label, color):
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, color_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Function to compare frames for similarity
def frames_are_similar(frame1, frame2, threshold=similarity_threshold):
    if frame1 is None or frame2 is None:
        return False

    # Convert to grayscale for simpler comparison
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Compute structural similarity
    difference = cv2.absdiff(gray1, gray2)
    _, diff_thresh = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)

    # Calculate the ratio of non-difference pixels
    non_zero_count = np.count_nonzero(diff_thresh)
    total_pixels = frame1.shape[0] * frame1.shape[1]
    similarity_ratio = (total_pixels - non_zero_count) / total_pixels

    return similarity_ratio >= threshold

# Function to drive car based on contours
def drive_based_on_contours(frame, hsv_frame):
    global start_robot, orange_blue_counter, threshold_pixels_num, steer_lock_end_time, similarity_start_time, previous_frame, orange_strip_count, orange_in_previous_frame, blue_strip_count, blue_in_previous_frame
    global speed, last_backward_time 
    # Detect all colors
    black_contours = detect_color_contours(hsv_frame, 'black')
    red_contours = detect_color_contours(hsv_frame, 'red')
    green_contours = detect_color_contours(hsv_frame, 'green')
    orange_contours = detect_color_contours(hsv_frame, 'orange')
    blue_contours = detect_color_contours(hsv_frame, 'blue')
    
    # Define rectangles
    middle_center, left_center, right_center, left_block_detector, right_block_detector, lower_middle = define_rectangles(frame.shape)

    # Draw rectangles on the frame (for visualization)
    cv2.rectangle(frame, middle_center[0], middle_center[1], (255, 255, 255), 2)
    cv2.rectangle(frame, left_center[0], left_center[1], (255, 255, 255), 2)
    cv2.rectangle(frame, right_center[0], right_center[1], (255, 255, 255), 2)
    cv2.rectangle(frame, left_block_detector[0], left_block_detector[1], (0, 0, 255), 1)
    cv2.rectangle(frame, right_block_detector[0], right_block_detector[1], (0, 255, 0), 1)
    cv2.rectangle(frame, lower_middle[0], lower_middle[1], (255, 255, 255), 2)

    # Draw and label contours
    draw_labeled_contours(frame, black_contours, color_ranges['black']['label'], (0, 0, 0))
    draw_labeled_contours(frame, red_contours, color_ranges['red']['label'], (0, 0, 255))
    draw_labeled_contours(frame, green_contours, color_ranges['green']['label'], (0, 255, 0))
    draw_labeled_contours(frame, orange_contours, color_ranges['orange']['label'], (0, 165, 255))
    draw_labeled_contours(frame, blue_contours, color_ranges['blue']['label'], (255, 0, 0))

    # Handle locked steering (car is locked in a steering direction)
    if start_robot == False:
        return frame
    current_time = time.time()
    if current_time < steer_lock_end_time :
        # If steering is locked, do nothing else
        return frame    
    # Check for frame similarity over time (car is stuck)
    if frames_are_similar(previous_frame, frame):
        if similarity_start_time == 0:
            similarity_start_time = current_time
        elif current_time - similarity_start_time >= similarity_duration :
            # If frames are similar for 3 seconds, move the car backward
            print("Stuckck")
            motor_backward()
            if (blue_strip_count > orange_strip_count):
                steer_right()
            else:
                steer_left()
            steer_lock_end_time = time.time()
            steer_lock_end_time += 1
            similarity_start_time = 0  # Reset the timer
            return frame
    else:
        # Reset similarity timer if the frames are not similar
        similarity_start_time = 0

    # Store current frame as the previous frame for the next iteration
    previous_frame = frame.copy()
    
    # Detect all colors and get pixel positions
    black_pixels, black_mask = detect_color_pixels(hsv_frame, 'black')
    red_pixels, red_mask = detect_color_pixels(hsv_frame, 'red')
    green_pixels, green_mask = detect_color_pixels(hsv_frame, 'green')
    orange_pixels, orange_mask = detect_color_pixels(hsv_frame, 'orange')
    blue_pixels, blue_mask = detect_color_pixels(hsv_frame, 'blue')

    # Check contours in key regions
    red_in_center = any(is_contour_in_rectangle(c, middle_center) for c in red_contours)
    green_in_center = any(is_contour_in_rectangle(c, middle_center) for c in green_contours)
    red_in_right = any(is_contour_in_rectangle(c, right_center) for c in red_contours)
    green_in_left = any(is_contour_in_rectangle(c, left_center) for c in green_contours)
    green_in_right_desired = any(is_contour_in_rectangle(c, right_block_detector) for c in green_contours)
    red_in_left_desired = any(is_contour_in_rectangle(c, left_block_detector) for c in red_contours)
    red_in_lower = any(is_contour_in_rectangle(c, lower_middle) for c in red_contours)
    green_in_lower = any(is_contour_in_rectangle(c, lower_middle) for c in green_contours)
    block_detected = red_in_center or green_in_center or green_in_left or red_in_right or green_in_lower or red_in_lower
    # Prioritize closest contours
    if red_in_center and green_in_center:
        # If both red and green detected, steer based on the closest one
        motor_forward()
        if red_contours[0][0][0][1] < green_contours[0][0][0][1]:
            steer_right()
        else:
            steer_left()
    elif