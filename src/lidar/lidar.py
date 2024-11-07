import asyncio

from abc import ABC, abstractmethod
from typing import TypedDict, Optional
from logging import Logger
from asyncio import Queue


class LidarData(TypedDict):
    distance: int
    strength: int
    mode: Optional[int]


class Lidar(ABC):
    logger: Logger
    distance_min: int
    distance_max: int
    read_interval_secs: int
    read_task: asyncio.tasks.Task

    def __init__(self,
                 distance_min: int,
                 distance_max: int,
                 read_interval_secs: int,
                 logger: Logger = None):
        self.logger = logger
        self.distance_max = distance_max
        self.distance_min = distance_min
        self.read_interval_secs = read_interval_secs

    @abstractmethod
    async def open(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def read_data(self) -> Optional[LidarData]:
        pass

    async def start(self) -> Queue[LidarData]:
        await self.open()
        queue = Queue()

        async def read_bus():
            while True:
                lidar_data = self.read_data()
                await queue.put(lidar_data)
                await asyncio.sleep(self.read_interval_secs)

        self.read_task = asyncio.create_task(read_bus())
        self.read_task.add_done_callback(lambda t: None)

        return queue

    async def stop(self) -> None:
        await self.stop()
        if self.read_task is not None:
            self.read_task.cancel()

    def normalize_distance(self, distance):
        distance = min(self.distance_max, distance)
        return 1 - (distance - self.distance_min) / (self.distance_max - self.distance_min)



