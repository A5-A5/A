# Autonomous Robot Control Code

This repository contains the code for operating an autonomous robot equipped with a LIDAR sensor and a Raspberry Pi camera. The code integrates motor control, LIDAR scanning, obstacle detection, and rotation functionalities.

## Requirements
- Python 3.x
- Libraries:
  - gpiozero
  - matplotlib
  - ydlidar
- Hardware:
  - Raspberry Pi
  - YDLIDAR
  - Servo motor
  - Hall sensor

## Code Overview
The main components of the code are:

- **Library Imports:** Necessary libraries for hardware interaction and data processing.
- **LIDAR Settings:** Functions to initialize the LIDAR and plot the scan data.
- **Motor and Servo Settings:** Control mechanisms for the robot's movement.
- **Obstacle Avoidance:** Functions to detect obstacles using LIDAR and adjust the robot's path accordingly.
- **Control Loop:** The main loop that manages LIDAR scanning, motor movement, and rotation for navigating obstacles.


