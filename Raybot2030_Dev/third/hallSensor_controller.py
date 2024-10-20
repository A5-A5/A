from gpiozero import Button
import time

class HallSensorController:
    def __init__(self, pin=4, distance_per_rotation=0.07):
        self.hall_sensor = Button(pin)
        self.distance_per_rotation = distance_per_rotation
        self.pulse_count = 0
        self.hall_sensor.when_pressed = self._hall_sensor_triggered

    def _hall_sensor_triggered(self):
        self.pulse_count += 1

    def get_distance_moved(self):
        """Calculate and return the distance moved based on pulse count."""
        return self.pulse_count * self.distance_per_rotation

    def reset_distance(self):
        """Reset the pulse count to zero."""
        self.pulse_count = 0

    def move_one_meter(self, motor, display_function=None):
        """
        Move the vehicle forward by approximately one meter.
        
        :param motor: An instance of a motor controller with set_speed and stop methods.
        :param display_function: Optional function to update a display with current info.
        """
        self.reset_distance()
        target_distance = 0.6  # Exactly one meter
        target_pulses = int(target_distance / self.distance_per_rotation)
        
        INITIAL_SPEED = 0.4
        SLOW_SPEED = 0.1
        CRAWL_SPEED = 0.05
        
        SLOW_THRESHOLD = 0.2  # 20cm
        CRAWL_THRESHOLD = 0.05  # 5cm
        OVERSHOOT_TOLERANCE = 0.01  # 1cm
        
        while True:
            current_pulses = self.pulse_count
            distance_moved = self.get_distance_moved()
            remaining_pulses = target_pulses - current_pulses
            
            if remaining_pulses <= 0:
                motor.stop()
                if abs(distance_moved - target_distance) <= OVERSHOOT_TOLERANCE:
                    print(f"Successfully moved {distance_moved:.3f} meters.")
                    break
                elif distance_moved < target_distance:
                    # Slight undershoot, creep forward
                    motor.set_speed(CRAWL_SPEED)
                else:
                    # Overshoot, we'll have to live with it
                    print(f"Moved {distance_moved:.3f} meters. Slight overshoot.")
                    break
            
            if remaining_pulses > SLOW_THRESHOLD / self.distance_per_rotation:
                speed = INITIAL_SPEED
            elif remaining_pulses > CRAWL_THRESHOLD / self.distance_per_rotation:
                speed = SLOW_SPEED
            else:
                speed = CRAWL_SPEED
                
            motor.set_speed(speed)
            if display_function:
                display_function(speed, distance_moved)
            print(f"Target: {target_distance:.3f}m, Current: {distance_moved:.3f}m, Speed: {speed:.2f}")
            time.sleep(0.01)  # Shorter delay for more frequent updates
        
        motor.stop()
        time.sleep(0.5)  # Ensure complete stop

def create_hall_sensor(pin=4, distance_per_rotation=0.07):
    """Create and return a HallSensorController instance."""
    return HallSensorController(pin, distance_per_rotation)