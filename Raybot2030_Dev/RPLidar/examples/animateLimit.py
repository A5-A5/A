import numpy as np
from rplidar import RPLidar
import time

# LiDAR setup
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(PORT_NAME)

# Constants
MAP_SIZE = 6  # 6x6 meters
RESOLUTION = 0.05  # 5cm resolution
GRID_SIZE = int(MAP_SIZE / RESOLUTION)

# Define the field of view sectors
LEFT_SECTOR = (-90, -30)
CENTER_SECTOR = (-30, 30)
RIGHT_SECTOR = (30, 90)

def process_scan(scan):
    grid = np.zeros((GRID_SIZE, GRID_SIZE))
    sectors = {
        'left': {'measurements': 0, 'min_distance': float('inf'), 'max_distance': 0},
        'center': {'measurements': 0, 'min_distance': float('inf'), 'max_distance': 0},
        'right': {'measurements': 0, 'min_distance': float('inf'), 'max_distance': 0}
    }
    
    for _, angle, distance in scan:
        if distance > 0:  # Valid measurement
            # Normalize angle to -180 to 180 range
            norm_angle = (angle + 180) % 360 - 180
            
            # Determine which sector the measurement belongs to
            if LEFT_SECTOR[0] <= norm_angle < LEFT_SECTOR[1]:
                sector = 'left'
            elif CENTER_SECTOR[0] <= norm_angle < CENTER_SECTOR[1]:
                sector = 'center'
            elif RIGHT_SECTOR[0] <= norm_angle < RIGHT_SECTOR[1]:
                sector = 'right'
            else:
                continue  # Skip measurements outside our sectors of interest
            
            # Update sector information
            sectors[sector]['measurements'] += 1
            sectors[sector]['min_distance'] = min(sectors[sector]['min_distance'], distance)
            sectors[sector]['max_distance'] = max(sectors[sector]['max_distance'], distance)
            
            # Convert polar coordinates to Cartesian
            x = distance * np.cos(np.radians(angle))
            y = distance * np.sin(np.radians(angle))
            
            # Check if the point is within our grid
            if abs(x) < MAP_SIZE/2 and abs(y) < MAP_SIZE/2:
                grid_x = int((x + MAP_SIZE/2) / RESOLUTION)
                grid_y = int((y + MAP_SIZE/2) / RESOLUTION)
                grid[grid_y, grid_x] = 1

    return grid, sectors

def analyze_grid(grid):
    occupied_cells = np.sum(grid)
    total_cells = grid.size
    occupancy_percentage = (occupied_cells / total_cells) * 100

    occupied_coords = np.argwhere(grid == 1)

    if occupied_cells > 0:
        center_of_mass = np.mean(occupied_coords, axis=0)
    else:
        center_of_mass = None

    return {
        "occupied_cells": occupied_cells,
        "occupancy_percentage": occupancy_percentage,
        "center_of_mass": center_of_mass
    }

def get_navigation_recommendation(sectors):
    if sectors['center']['min_distance'] > 1000:  # If center is clear for 1 meter
        if sectors['left']['min_distance'] > sectors['right']['min_distance']:
            return "Slight left turn recommended"
        elif sectors['right']['min_distance'] > sectors['left']['min_distance']:
            return "Slight right turn recommended"
        else:
            return "Continue straight"
    else:
        if sectors['left']['min_distance'] > sectors['right']['min_distance']:
            return "Sharp left turn recommended"
        else:
            return "Sharp right turn recommended"

def main():
    try:
        for i, scan in enumerate(lidar.iter_scans()):
            grid, sectors = process_scan(scan)
            analysis = analyze_grid(grid)
            recommendation = get_navigation_recommendation(sectors)
            
            print(f"Scan #{i + 1}")
            for sector in ['left', 'center', 'right']:
                print(f"{sector.capitalize()} sector:")
                print(f"  Measurements: {sectors[sector]['measurements']}")
                if sectors[sector]['measurements'] > 0:
                    print(f"  Distance range: {sectors[sector]['min_distance']:.2f}mm to {sectors[sector]['max_distance']:.2f}mm")
                else:
                    print("  No valid measurements")
                print()
            
            print(f"Total occupied cells: {analysis['occupied_cells']}")
            print(f"Occupancy percentage: {analysis['occupancy_percentage']:.2f}%")
            
            if analysis['center_of_mass'] is not None:
                com_y, com_x = analysis['center_of_mass']
                print(f"Center of mass of obstacles: ({com_x * RESOLUTION - MAP_SIZE/2:.2f}m, {com_y * RESOLUTION - MAP_SIZE/2:.2f}m)")
            else:
                print("No obstacles detected in the grid")
            
            print(f"Navigation recommendation: {recommendation}")
            print("--------------------")

            time.sleep(0.1)  # Adjust this to control the scan rate

    except KeyboardInterrupt:
        print("Stopping LiDAR...")
    finally:
        lidar.stop()
        lidar.disconnect()

if __name__ == "__main__":
    main()