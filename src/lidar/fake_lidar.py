import time
import math
import random

from typing import Optional

from lidar import LidarData, Lidar


class FakeLidar(Lidar):
    period: int = 10  # Time period for one oscillation in seconds
    strength_min: int = 0
    strength_max: int = 100

    async def open(self):
        pass

    async def close(self):
        pass

    async def read_data(self) -> Optional[LidarData]:
        amplitude = (self.distance_max - self.distance_min) / 2
        offset = (self.distance_max + self.distance_min) / 2
        current_time = time.time()

        # Calculate the sine wave value based on time
        distance = int(amplitude * math.sin(2 * math.pi * current_time / self.period) + offset)

        strength = random.randint(self.strength_min, self.strength_max)
        normalized_distance = self.normalize_distance(distance)

        return LidarData(distance=normalized_distance, strength=strength, mode=None)