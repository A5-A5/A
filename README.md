# Hi there, we are the RayBot2030 team!
a passionate team of high school students, including **AlJawharah AlQahtani** and **Aseel AlJaseer**, committed to advancing the field of autonomous vehicle technology. Our participation in the **WRO Future Engineers** challenge allows us to pursue ambitious goals while fostering innovation and teamwork.


## Our Objectives:
- **Understand the mechanics of autonomous vehicles**, including sensing technologies and control systems.
- **Gain practical experience in building and testing systems** to enhance safety and efficiency.
- **Effectively integrate hardware and software components**.
- **Strengthen teamwork and communication skills**, leveraging our diverse strengths to tackle challenges.

Our mission is to build a solid foundation of knowledge that prepares us to drive technological advancements and inspire future generations.

---


# Vehicle Components

Our chassis is controlled by the **Raspberry Pi 5**, which processes information from various sensors and uses that data to navigate and control the motors. The key components used in our self-driving vehicle are as follows:

## 1. LiPo Battery

<img src="https://github.com/user-attachments/assets/908b8404-baff-41fb-9149-9b81a1c1a1dc" alt="LiPo Battery" width="115"/> 

- **Type:** 52000mAh 7.4V 2S LiPo Battery
- **Purpose:** Provides significant power for all electrical components of the vehicle.
- **Advantages:**
  - High energy density for prolonged usage.
  - Lightweight design enhances overall vehicle performance.
  - Supports high-current draw needed for effective operation.

---

## 2. Raspberry Pi 5

<img src="https://github.com/user-attachments/assets/42fb6adc-8708-4bbc-a607-6fa7e811c71d" alt="Raspberry Pi 5" width="115"/> 

- **Role:** Acts as the brain of the vehicle.
- **Functions:**
  - Processes data from sensors to control vehicle movement.
  - Facilitates obstacle detection and avoidance.
- **Obstacle Avoidance:**
  - Utilizes coordinates from the **RPLIDAR**.
  - Analyzes color data from the **RPi Camera** to determine the nature of obstacles (green or red).
  - Implements maneuvering logic based on obstacle colors:
    - If the obstacle is green, the vehicle avoids it from the left.
    - If the obstacle is red, it executes a different maneuver to navigate around it.

---

## 3. Slamtec RPLIDAR A1M8

<img src="https://github.com/user-attachments/assets/9c29cec8-1050-4cdb-90a4-da71437b7734" alt="Slamtec RPLIDAR A1M8" width="115"/> 

- **Function:** Measures distances and identifies object positions.
- **Uses:**
  - Determines coordinates of surrounding objects such as walls and obstacles.
  - Aids in navigation strategy during movement.
- **Example Application:**
  - When moving clockwise, it measures the distance to the left wall.
  - If the wall is far away, the vehicle moves closer to it, utilizing it as a reference for navigation.

---

## 4. Servo Motor

<img src="https://github.com/user-attachments/assets/c1670549-f9af-4a37-8fa1-179a9e9dd13b" alt="Servo Motor" width="115"/> 

- **Purpose:** Controls the vehicle's steering mechanism.
- **Input Data:**
  - Receives data from the **Raspberry Pi 5**.
  - Works in conjunction with inputs from **RPLIDAR** and **RPi Camera** to adjust direction based on obstacle proximity.

---

## 5. DC Motor

<img src="https://github.com/user-attachments/assets/786b7cfa-312f-42eb-9389-e2e87b348060" alt="DC Motor" width="115"/> 

- **Function:** Drives the wheels of the vehicle.
- **Operation:**
  - Converts electrical energy into mechanical movement.
  - Responsible for propelling the vehicle forward, ensuring smooth operation.
- **Importance:**
  - Essential for dynamic movement and maneuverability of the vehicle.

---

## 6. Button

<img src="https://github.com/user-attachments/assets/65c64ba1-5371-4502-a137-03b5c4c18d32" alt="Button" width="115"/> 

- **Components:**
  - Two buttons are integrated:
    - **Switch Button:** Powers on the robot.
    - **Execution Button:** Initiates the program or code execution.
- **Usage:**
  - Facilitates manual control over the robot's start-up and operational procedures.

---

## 7. Servo Shield

<img src="https://github.com/user-attachments/assets/7363483b-6689-4da0-88c1-e9cdde50f219" alt="Servo Shield" width="115"/> 

- **Function:** Enhances control over the **Servo Motor**.
- **Benefits:**
  - Provides additional power management for servo operations.
  - Simplifies connections and control logic for steering mechanisms.

---

## 8. RPi Camera 3

<img src="https://github.com/user-attachments/assets/65bd3e56-2714-4778-b2c9-bc456a161742" alt="RPi Camera 3" width="115"/> 

- **Components:**
  - Two distinct functions:
    - **First Camera:** Captures the lines on the track.
      - **Line Detection:** Recognizes blue and orange lines.
      - **Movement Logic:**
        - If the first detected line is orange, the vehicle moves clockwise.
        - If blue, the vehicle moves counterclockwise.
      - **Line Counting:** Tracks the number of orange and blue lines crossed, essential for strategic maneuvering during races.
    - **Second Camera:** Detects colors of obstacles (green and red).
      - **Decision Making:**
        - If a green obstacle is detected, the vehicle continues in the same direction.
        - If a red obstacle is detected, it performs a maneuver to avoid it.
- **Collaboration with RPLIDAR:**
  - Works together with **RPLIDAR** to ensure obstacle detection and avoidance.

---

## 9. Step-Down Converter

<img src="https://github.com/user-attachments/assets/f6231631-9f1b-4582-92bc-95a66b89b68c" alt="Step-Down Converter" width="115"/> 

- **Function:** Acts as a power regulator.
- **Voltage Adjustment:**
  - Reduces voltage from **7.4V** to **5V** for the **Raspberry Pi**.
- **Importance:**
  - Ensures the correct power levels are supplied to all electronic components.
  - Improves system efficiency and reduces the risk of damage from over-voltage.

---
Our autonomous vehicle is constructed using these components, all working together seamlessly to execute the programmed navigation strategy and respond effectively to environmental changes.

---

## Installation
```bash
# Clone the repository
git clone https://github.com/blo0ck/Block.git

# Install dependencies
pip install -r requirements.txt
