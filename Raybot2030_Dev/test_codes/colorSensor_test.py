import time
import board
import adafruit_as7341
import statistics

# Initialize I2C
i2c = board.I2C()
# Initialize the AS7341 sensor
sensor = adafruit_as7341.AS7341(i2c)

# Define wavelength ranges for each channel
channel_wavelengths = {
    "415nm": 'channel_415nm', "445nm": 'channel_445nm', 
    "480nm": 'channel_480nm', "515nm": 'channel_515nm',
    "555nm": 'channel_555nm', "590nm": 'channel_590nm', 
    "630nm": 'channel_630nm', "680nm": 'channel_680nm',
    "Clear": 'channel_clear', "NIR": 'channel_nir'
}

def get_spectral_data(num_samples=5):
    spectral_data = {name: [] for name in channel_wavelengths}
    for _ in range(num_samples):
        for name, attribute in channel_wavelengths.items():
            spectral_data[name].append(getattr(sensor, attribute))
        time.sleep(0.01)  # Short delay between samples
    
    # Calculate median for each channel
    return {name: statistics.median(values) for name, values in spectral_data.items()}

def analyze_spectrum(spectral_data):
    total = sum(spectral_data.values())
    if total == 0:
        return "No color detected", {name: 0 for name in spectral_data}
    
    # Calculate ratios for each channel
    ratios = {name: value / total for name, value in spectral_data.items()}
    
    # Define color detection thresholds and wavelength importance
    color_profiles = {
        "Blue": {"primary": ['445nm', '480nm'], "secondary": ['415nm'], "threshold": 0.4},
        "Orange": {"primary": ['590nm', '630nm'], "secondary": ['555nm'], "threshold": 0.4},
        "White": {"primary": ['Clear'], "secondary": [], "threshold": 0.5}
    }
    
    # Calculate color scores
    color_scores = {}
    for color, profile in color_profiles.items():
        primary_score = sum(ratios[wave] for wave in profile["primary"])
        secondary_score = sum(ratios[wave] for wave in profile["secondary"]) * 0.5
        color_scores[color] = primary_score + secondary_score
    
    # Determine the color
    detected_color = max(color_scores, key=color_scores.get)
    if color_scores[detected_color] < color_profiles[detected_color]["threshold"]:
        detected_color = "Undefined"
    
    return detected_color, ratios

# Main program
try:
    # Turn on the LED
    sensor.led_current = 25  # Set LED current (0-150 mA)
    sensor.led = True  # Turn on the LED

    while True:
        start_time = time.time()
        
        spectral_data = get_spectral_data(num_samples=5)
        color, ratios = analyze_spectrum(spectral_data)
        
        print(f"Detected Color: {color}")
        print("Spectral Ratios:")
        for name, ratio in ratios.items():
            print(f"  {name}: {ratio:.3f}")
        
        print("Raw Channel Readings:")
        for name, value in spectral_data.items():
            print(f"  {name}: {value}")
        
        end_time = time.time()
        print(f"Processing time: {(end_time - start_time)*1000:.2f} ms")
        print("\n" + "-"*40 + "\n")

except KeyboardInterrupt:
    print("Program terminated by user.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Turn off the LED when done
    sensor.led = False
    print("LED turned off. Program ended.")