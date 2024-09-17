
import time
import math


def get_distance():
    # Parameters
    distance_min = 10  # Minimum distance
    distance_max = 100  # Maximum distance
    period = 10  # Time period for one oscillation in seconds

    # Calculate amplitude and offset
    amplitude = (distance_max - distance_min) / 2
    offset = (distance_max + distance_min) / 2

    # Get the current time (in seconds)
    current_time = time.time()

    # Calculate the sine wave value based on time
    distance = amplitude * math.sin(2 * math.pi * current_time / period) + offset

    return int(distance)


while True:
    print(get_distance())