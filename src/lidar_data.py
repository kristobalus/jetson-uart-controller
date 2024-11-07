from typing import TypedDict


class LidarData(TypedDict):
    distance: int
    strength: int
    mode: int

    # def __init__(self,
    #              distance: int,
    #              strength: int,
    #              mode: int):
    #     self.distance = distance
    #     self.strength = strength
    #     self.mode = mode
