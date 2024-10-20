import json
import time

INPUT_FILE = 'home/wroKhalid/RPLidar/examples/lidar_output.json'

def process_lidar_data(data):
    print(f"Processing scan #{data['scan_number']}")
    print("Sector information:")
    for sector, info in data['sectors'].items():
        print(f"  {sector.capitalize()}:")
        print(f"    Measurements: {info['measurements']}")
        if info['measurements'] > 0:
            print(f"    Distance range: {info['min_distance']:.2f}mm to {info['max_distance']:.2f}mm")
        else:
            print("    No valid measurements")
    
    print(f"Occupied cells: {data['analysis']['occupied_cells']}")
    print(f"Occupancy percentage: {data['analysis']['occupancy_percentage']:.2f}%")
    
    if data['analysis']['center_of_mass']:
        com_y, com_x = data['analysis']['center_of_mass']
        print(f"Center of mass of obstacles: ({com_x * 0.05 - 3:.2f}m, {com_y * 0.05 - 3:.2f}m)")
    else:
        print("No obstacles detected in the grid")
    
    print(f"Navigation recommendation: {data['recommendation']}")
    print("--------------------")

def main():
    last_processed_scan = -1
    
    while True:
        try:
            with open(INPUT_FILE, 'r') as f:
                data = json.load(f)
            
            if data['scan_number'] > last_processed_scan:
                process_lidar_data(data)
                last_processed_scan = data['scan_number']
        
        except FileNotFoundError:
            print("Waiting for LiDAR data...")
        except json.JSONDecodeError:
            print("Error reading LiDAR data. Retrying...")
        
        time.sleep(0.1)  # Adjust this to control how often we check for new data

if __name__ == "__main__":
    main()
