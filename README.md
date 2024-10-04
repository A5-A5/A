# WRO 2024 Self-Driving Car Project

## Project Overview
This repository contains the documentation, code, and resources for our participation in the **WRO 2024 Future Engineers - Self-Driving Car Challenge**. Our goal is to build an autonomous vehicle capable of navigating a track, avoiding obstacles, and performing parallel parking as part of the competition.

## Team Information
- **Team Name**: RayBot 2030
- **Team Members**:
  - AlJawharah AlQahtani 
  - Aseel AlJaseer 
 
- **Coach**: Elaf Abunayyan

## Vehicle Overview
Our vehicle is designed using Raspberry Pi 5, along with various sensors and motors to autonomously complete the challenge tasks.

## Technical Approach

### 1. Mobility
- **Motor Type**: One DC Motor for forward-movements.
- **Steering Mechanism**: One Servo-Motor.

### 2. Sensors
- **Sensors Used**: Rpi-Camera Module 3, LiDAR, Whole Sensor, Battery Monitor, USB to TTL converter, Compas.
- **Functionality**:
  Rpi-Camera Module 3: We used the camera to detect colors.
  LiDAR: We used the LiDAR to avoid obsticals.
  Whole Sensor: We used the whole sensor to mesure distance.

### 4. Power Management
- **Power Supply**: Lipo Battery 7.4V 2200mAh. 
  
3. **Wiring Diagram**: [Include a link to the wiring diagram or upload it to this repo].
4. **Assembly Instructions**: [Provide detailed steps to assemble the vehicle, including CAD files if applicable].

     
2. **Installation**:
   ```bash
   # Clone the repository
   git clone https://github.com/RayBot-2030/WRO-2024-RayBot.git

   # Install dependencies
   pip install -r requirements.txt
   ```
3. **Code Execution**:
   ```bash
   # Example to run the code on Raspberry Pi
   python3 main.py
   ```
