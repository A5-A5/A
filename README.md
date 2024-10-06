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

- **LiPo Battery**  
  <img src="https://github.com/user-attachments/assets/908b8404-baff-41fb-9149-9b81a1c1a1dc" alt="LiPo Battery" width="300"/>  
  A lightweight, rechargeable battery providing **7.4V**, ideal for powering all electrical components with high energy density.

- **Raspberry Pi 5**  
  <img src="https://github.com/user-attachments/assets/42fb6adc-8708-4bbc-a607-6fa7e811c71d" alt="Raspberry Pi 5" width="300"/>  
  The core control unit, equipped with **4GB of RAM** and a **quad-core processor**, managing all vehicle functions and processing sensor data.

- **Slamtec RPLIDAR A1M8**  
  <img src="https://github.com/user-attachments/assets/9c29cec8-1050-4cdb-90a4-da71437b7734" alt="Slamtec RPLIDAR A1M8" width="300"/>  
  A laser sensor that accurately measures distances, helping our vehicle map its environment and detect obstacles effectively.

- **Servo Motor**  
  <img src="https://github.com/user-attachments/assets/c1670549-f9af-4a37-8fa1-179a9e9dd13b" alt="Servo Motor" width="300"/>  
  Used for precise control of the vehicle’s direction, ensuring accurate movement adjustments.

- **DC Motor**  
  <img src="https://github.com/user-attachments/assets/786b7cfa-312f-42eb-9389-e2e87b348060" alt="DC Motor" width="300"/>  
  Drives the wheels of the vehicle, converting electrical energy into mechanical motion for smooth operation.

- **Button**  
  <img src="https://github.com/user-attachments/assets/65c64ba1-5371-4502-a137-03b5c4c18d32" alt="Button" width="300"/>  
  Acts as a simple switch to initiate the main code, streamlining vehicle operation.

- **Servo Shield**  
  <img src="https://github.com/user-attachments/assets/7363483b-6689-4da0-88c1-e9cdde50f219" alt="Servo Shield" width="300"/>  
  Facilitates flexible and precise servo control, utilizing the **I2C protocol** to minimize wiring complexity while allowing simultaneous control of multiple servos.

- **RPi Camera 3**  
  <img src="https://github.com/user-attachments/assets/65bd3e56-2714-4778-b2c9-bc456a161742" alt="RPi Camera 3" width="300"/>  
  Captures images and video, primarily used for color detection to identify obstacles and facilitate effective navigation through real-time processing with **OpenCV**.

- **Hall Sensor**  
  <img src="https://github.com/user-attachments/assets/9d366444-3e11-4463-a1bf-e6da3ee52555" alt="Hall Sensor" width="300"/>  
  Detects the position and speed of the wheels, enhancing the vehicle's responsiveness to its surroundings by providing immediate feedback to the **Raspberry Pi**.

- **Step-Down Converter**  
  <img src="https://github.com/user-attachments/assets/f6231631-9f1b-4582-92bc-95a66b89b68c" alt="Step-Down Converter" width="300"/>  
  A power regulator that stabilizes voltage, ensuring various electronic components receive the appropriate power levels.

#
Our autonomous vehicle is constructed using these components, all working together seamlessly to execute the programmed navigation strategy and respond effectively to environmental changes.

## Installation
```bash
# Clone the repository
git clone https://github.com/blo0ck/Block.git

# Install dependencies
pip install -r requirements.txt
