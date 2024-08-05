# import pandas as pd
# import numpy as np
# from scipy.signal import find_peaks

# def count_steps(accel_data, threshold=1.0, min_distance=1):
#     # print('entering steps')
#     accel_data = pd.DataFrame(accel_data)
#     """
#     Count the number of steps given accelerometer data.
    
#     Parameters:
#     accel_data (array-like): Nx3 array with columns representing x, y, z accelerometer data.
#     threshold (float): Minimum height of peaks to consider as steps.
#     min_distance (int): Minimum distance between peaks to be considered separate steps.
    
#     Returns:
#     int: Number of steps counted.
#     """
#     try:
#         accel_data = np.array(accel_data)
#     except:
#         pass
#     # Calculate the magnitude of acceleration
#     magnitudes = np.sqrt(np.sum(accel_data**2, axis=1))
#     # Find peaks in the magnitude
#     peaks, _ = find_peaks(magnitudes, height=threshold, distance=min_distance)
#     # Return the number of peaks
#     # print('returning steps')
#     return len(peaks)


import pandas as pd

def calculate_magnitude(data):
    """Calculate the magnitude of acceleration."""
    magnitudes = []
    for row in data:
        magnitude = (row[0]**2 + row[1]**2 + row[2]**2) ** 0.5
        magnitudes.append(magnitude)
    return magnitudes

def find_peaks(magnitudes, threshold, min_distance):
    """Find peaks in the magnitude data."""
    peaks = []
    n = len(magnitudes)
    i = 1
    while i < n - 1:
        # Check if current value is a peak
        if magnitudes[i] > threshold and magnitudes[i] > magnitudes[i - 1] and magnitudes[i] > magnitudes[i + 1]:
            # Check if this peak is far enough from the previous one
            if len(peaks) == 0 or i - peaks[-1] >= min_distance:
                peaks.append(i)
        i += 1
    return peaks

def count_steps(accel_data, threshold=1.0, min_distance=1):
    """Count the number of steps given accelerometer data."""
    accel_data = pd.DataFrame(accel_data).values
    magnitudes = calculate_magnitude(accel_data)
    peaks = find_peaks(magnitudes, threshold, min_distance)
    return len(peaks)