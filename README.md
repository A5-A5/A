

## Team Information

- **Team Members**:
  - AlJawharah AlQahtani: A driven innovator with a passion for robotics and engineering.
  - Aseel AlJaseer: A creative thinker who excels in problem-solving and team collaboration.
- **Coach**: Elaf Abunayyan: An experienced mentor guiding our team toward success.

## Vehicle Components
Here is a detailed overview of the key components used in our self-driving vehicle:

## Vehicle Components
Here is a detailed overview of the key components used in our self-driving vehicle:

### 1. LiPo Battery
![LiPo Battery](https://github.com/user-attachments/assets/908b8404-baff-41fb-9149-9b81a1c1a1dc)

We use a lightweight, rechargeable **LiPo battery** that provides **7.4V**. This battery features high energy density, making it ideal for supplying the vehicle with the necessary power to operate all electrical components effectively.


### 2. Raspberry Pi 5
![Raspberry Pi 5](https://github.com/user-attachments/assets/42fb6adc-8708-4bbc-a607-6fa7e811c71d)

The **Raspberry Pi 5** is the core component of our vehicle, equipped with **4GB of RAM** and a **quad-core processor**. This board controls all vehicle functions, including processing data received from sensors and determining the path.


### 3. Slamtec RPLIDAR A1M8
![Slamtec RPLIDAR A1M8](https://github.com/user-attachments/assets/733fbc9b-d4b4-4c74-9c21-c21d30e1321c)

The **Slamtec RPLIDAR A1M8** is a laser sensor that accurately measures distances, helping our vehicle map its surrounding environment and detect obstacles. We have calibrated the LIDAR to ensure it effectively identifies obstacles up to **10 cm** in height, which is crucial for proper vehicle navigation and obstacle avoidance.


### 4. Servo Motor
![Servo Motor](https://github.com/user-attachments/assets/c1670549-f9af-4a37-8fa1-179a9e9dd13b)

The **Servo Motor** is used for precise control of the vehicle's movement, allowing it to change direction accurately. It operates at **5-6V** and is ideal for robotics applications that require precise control.


### 5. DC Motor
![DC Motor](https://github.com/user-attachments/assets/786b7cfa-312f-42eb-9389-e2e87b348060)

We utilized **one DC Motor** solely for driving the vehicle's wheels. It converts electrical energy into mechanical motion, allowing the vehicle to move smoothly.


### 6. Button
![Button](https://github.com/user-attachments/assets/65c64ba1-5371-4502-a137-03b5c4c18d32)

The **Button** acts as a switch to run the main code for the vehicle, simplifying operation by initiating the program without any additional functions. Its sole purpose is to start the code, enabling the vehicle's functionality.


### 7. Servo Shield
![Servo Shield](https://github.com/user-attachments/assets/7363483b-6689-4da0-88c1-e9cdde50f219)

The **Servo Shield** is a crucial component of our servo control system. It is designed to facilitate flexible and precise servo control. We use the **I2C (Inter-Integrated Circuit)** protocol for communication between the **Servo Shield** and the **Raspberry Pi 5**, enabling us to control multiple servos simultaneously with fewer wires, thereby reducing connection complexity.


### 8. RPi Camera 3
![RPi Camera 3](https://github.com/user-attachments/assets/65bd3e56-2714-4778-b2c9-bc456a161742)

The **RPi Camera 3 module** for the Raspberry Pi enables image and video capture. In our project, we utilize the camera primarily for color detection, specifically to identify obstacles. For instance, when the camera detects the color green, indicating an obstacle, the vehicle will turn left to ensure that the obstacle is on its right side. This functionality is crucial for effective navigation and obstacle avoidance. We implement these steps using OpenCV, which allows us to process the camera feed in real-time, accurately detect colors, and respond accordingly.


### 9. Hall Sensor
![Hall Sensor](https://github.com/user-attachments/assets/9d366444-3e11-4463-a1bf-e6da3ee52555)

We used the **Hall sensor** in our autonomous vehicle as an essential part of the motion control system. This sensor accurately detects the position and speed of the wheels, enhancing the vehicle's response efficiency to changes in its surrounding environment. The goal of using the Hall sensor is to provide immediate feedback to the control unit (Raspberry Pi) regarding the vehicle's location and speed.


### 10. Step-Down Converter
![Step-Down Converter](https://github.com/user-attachments/assets/f6231631-9f1b-4582-92bc-95a66b89b68c)

The **Step-Down Converter** is a power regulator that reduces voltage from a higher level to a lower, stable level suitable for powering various components in electronic circuits.

The strategy for the robot, from start to completing a full lap while avoiding obstacles and then parking, is as follows

## Installation
```bash
# Clone the repository
git clone https://github.com/RayBot-2030/WRO-2024-RayBot.git

# Install dependencies
pip install -r requirements.txt
