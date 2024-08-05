import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def count_steps(accel_data, threshold=1.0, min_distance=1):
    # print('entering steps')
    accel_data = pd.DataFrame(accel_data)
    """
    Count the number of steps given accelerometer data.
    
    Parameters:
    accel_data (array-like): Nx3 array with columns representing x, y, z accelerometer data.
    threshold (float): Minimum height of peaks to consider as steps.
    min_distance (int): Minimum distance between peaks to be considered separate steps.
    
    Returns:
    int: Number of steps counted.
    """
    try:
        accel_data = np.array(accel_data)
    except:
        pass
    # Calculate the magnitude of acceleration
    magnitudes = np.sqrt(np.sum(accel_data**2, axis=1))
    # Find peaks in the magnitude
    peaks, _ = find_peaks(magnitudes, height=threshold, distance=min_distance)
    # Return the number of peaks
    # print('returning steps')
    return len(peaks)