# WRO 2024 Future Engineers Project

## Project Overview
This repository contains the documentation, code, and resources for our participation in the **WRO 2024 Future Engineers** challenge. Our goal is to build an autonomous vehicle capable of navigating a track, avoiding obstacles, and performing parallel parking.

## Team Information
- **Team Name**: RayBot 2030
- **Team Members**:
  - AlJawharah AlQahtani: A driven innovator with a passion for robotics and engineering.
  - Aseel AlJaseer: A creative thinker who excels in problem-solving and team collaboration.
- **Coach**: Elaf Abunayyan: An experienced mentor guiding our team toward success.

## Vehicle Components
Here is a detailed overview of the key components used in our self-driving vehicle:

## Vehicle Components
Here is a detailed overview of the key components used in our self-driving vehicle:

### 1. LiPo Battery
![LiPo Battery](link-to-image)
We use a lightweight, rechargeable **LiPo battery** that provides **7.4V**. This battery features high energy density, making it ideal for supplying the vehicle with the necessary power to operate all electrical components effectively.

### 2. Raspberry Pi 5
![Raspberry Pi 5](link-to-image)
The **Raspberry Pi 5** is the core component of our vehicle, equipped with **4GB of RAM** and a **quad-core processor**. This board controls all vehicle functions, including processing data received from sensors and determining the path.

### 3. Slamtec RPLIDAR A1M8
![Slamtec RPLIDAR A1M8](link-to-image)
The **Slamtec RPLIDAR A1M8** is a laser sensor that accurately measures distances, helping our vehicle map its surrounding environment and detect obstacles. We have calibrated the LIDAR to ensure it effectively identifies obstacles up to **10 cm** in height, which is crucial for proper vehicle navigation and obstacle avoidance.

### 4. USB to TTL Converter
![USB to TTL Converter](link-to-image)
The **USB to TTL Converter** enables serial communication between the **Raspberry Pi** and other units, ensuring smooth data transfer to execute control commands.

### 5. Servo Motor
![Servo Motor](link-to-image)
The **Servo Motor** is used for precise control of the vehicle's movement, allowing it to change direction accurately. It operates at **5-6V** and is ideal for robotics applications that require precise control.

### 6. DC Motor
![DC Motor](link-to-image)
We utilized **one DC Motor** solely for driving the vehicle's wheels. It converts electrical energy into mechanical motion, allowing the vehicle to move smoothly.

### 7. Button
![Button](link-to-image)
The **Button** acts as a switch to run the main code for the vehicle, simplifying operation by initiating the program without any additional functions. Its sole purpose is to start the code, enabling the vehicle's functionality.
### 8. Servo Shield
![Servo Shield](link-to-image)
The **Servo Shield** is a crucial component of our servo control system. It is designed to facilitate flexible and precise servo control. We use the **I2C (Inter-Integrated Circuit)** protocol for communication between the **Servo Shield** and the **Raspberry Pi 5**, enabling us to control multiple servos simultaneously with fewer wires, thereby reducing connection complexity.

### 9. RPi Camera 3
![RPi Camera 3](link-to-image)
The **RPi Camera 3 module** for the Raspberry Pi enables image and video capture. In our project, we utilize the camera primarily for color detection, specifically to identify obstacles. For instance, when the camera detects the color green, indicating an obstacle, the vehicle will turn left to ensure that the obstacle is on its right side. This functionality is crucial for effective navigation and obstacle avoidance. We implement these steps using OpenCV, which allows us to process the camera feed in real-time, accurately detect colors, and respond accordingly.
### 10. Hall Sensor
![Hall Sensor](link-to-image)
We used the **Hall sensor** in our autonomous vehicle as an essential part of the motion control system. This sensor accurately detects the position and speed of the wheels, enhancing the vehicle's response efficiency to changes in its surrounding environment. The goal of using the Hall sensor is to provide immediate feedback to the control unit (Raspberry Pi) regarding the vehicle's location and speed.

### 11. Step-Down Converter
![Step-Down Converter](link-to-image)
The **Step-Down Converter** is a power regulator that reduces voltage from a higher level to a lower, stable level suitable for powering various components in electronic circuits.

## Technical Approach

### Mobility
- **Motor Type**: One DC Motor for forward movements.
- **Steering Mechanism**: One Servo-Motor.

### Sensors
- **Sensors Used**: RPi-Camera Module 3, LiDAR, Whole Sensor, Battery Monitor, USB to TTL converter, Compass.
- **Functionality**:
  - RPi-Camera Module 3: Used to detect colors.
  - LiDAR: Used to avoid obstacles.
  - Whole Sensor: Used to measure distance.

### Power Management
- **Power Supply**: LiPo Battery 7.4V 2200mAh.
- **Wiring Diagram**: [Include a link to the wiring diagram or upload it to this repo].
- **Assembly Instructions**: [Provide detailed steps to assemble the vehicle, including CAD files if applicable].

## Installation
```bash
# Clone the repository
git clone https://github.com/RayBot-2030/WRO-2024-RayBot.git

# Install dependencies
pip install -r requirements.txt
