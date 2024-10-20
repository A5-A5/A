#!/usr/bin/env python3
import time
import threading
from rplidar import RPLidar
import numpy as np

# Constants
PORT_NAME = '/dev/ttyUSB0'
ANGLE_MIN = -100
ANGLE_MAX = 100
MIN_DISTANCE = 500  # Minimum safe distance in mm
SCAN_FREQUENCY = 5  # Hz
SECTORS = 5  # Number of sectors to divide the field of view

class LidarController:
    def __init__(self):
        self.lidar = RPLidar(PORT_NAME)
        self.stop_signal = threading.Event()
        self.distances = [float('inf')] * SECTORS
        self.lock = threading.Lock()

    def run(self):
        scan_thread = threading.Thread(target=self._scan_thread)
        control_thread = threading.Thread(target=self._control_thread)

        scan_thread.start()
        control_thread.start()

        try:
            while not self.stop_signal.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

        scan_thread.join()
        control_thread.join()

    def _scan_thread(self):
        for scan in self.lidar.iter_scans():
            if self.stop_signal.is_set():
                break
            self._process_scan(scan)

    def _process_scan(self, scan):
        filtered_scan = [meas for meas in scan if ANGLE_MIN <= meas[1] <= ANGLE_MAX]
        
        sector_size = (ANGLE_MAX - ANGLE_MIN) / SECTORS
        new_distances = [float('inf')] * SECTORS

        for _, angle, distance in filtered_scan:
            sector = int((angle - ANGLE_MIN) / sector_size)
            if 0 <= sector < SECTORS:
                new_distances[sector] = min(new_distances[sector], distance)

        with self.lock:
            self.distances = new_distances

        # Debug print
        print(f"Current distances: {self.distances}")

    def _control_thread(self):
        while not self.stop_signal.is_set():
            self._avoid_obstacles()
            time.sleep(1 / SCAN_FREQUENCY)

    def _avoid_obstacles(self):
        with self.lock:
            local_distances = self.distances.copy()

        #print(f"Checking obstacles. Distances: {local_distances}")

        if min(local_distances) < MIN_DISTANCE:
            self._handle_obstacle(local_distances)
        else:
            # self._move_forward()
            a = 8

    def _handle_obstacle(self, distances):
        left_distance = sum(distances[:SECTORS//2])
        right_distance = sum(distances[SECTORS//2:])

        print(f"Obstacle detected! Left: {left_distance}, Right: {right_distance}")

        # if left_distance > right_distance:
        #     self._turn_left()
        # elif right_distance > left_distance:
        #     self._turn_right()
        # else:
        #     self._stop()

    def _move_forward(self):
        print("Moving forward")
        # Add code to move the RC car forward

    def _turn_left(self):
        print("Turning left")
        # Add code to turn the RC car left

    def _turn_right(self):
        print("Turning right")
        # Add code to turn the RC car right

    def _stop(self):
        print("Stopping")
        # Add code to stop the RC car

    def stop(self):
        self.stop_signal.set()
        self.lidar.stop()
        self.lidar.disconnect()

if __name__ == '__main__':
    controller = LidarController()
    controller.run()