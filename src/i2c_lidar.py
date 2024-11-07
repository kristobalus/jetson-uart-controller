import asyncio

from asyncio import Queue
from smbus2 import SMBus, i2c_msg
from logging import Logger, getLogger
from lidar_data import LidarData

class I2CLidar:
    logger: Logger
    bus: SMBus
    i2c_bus: str
    i2c_address: str
    i2c_write_msg: i2c_msg
    i2c_read_msg: i2c_msg
    distance_min: int
    distance_max: int
    read_interval_secs: int
    read_task: asyncio.tasks.Task

    def __init__(self,
                 i2c_bus: str,
                 i2c_address: str,
                 distance_min: int,
                 distance_max: int,
                 read_interval_secs: int,
                 logger: Logger = None):
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.distance_max = distance_max
        self.distance_min = distance_min
        self.read_interval_secs = read_interval_secs
        if logger is None:
            self.logger = getLogger(f"i2c-lidar-{i2c_bus}-{i2c_address}")
        else:
            self.logger = logger

    def start(self) -> Queue[LidarData]:
        self.__create_bus()
        queue = Queue()

        async def read_bus():
            while True:
                lidar_data = self.__read_data()
                await queue.put(lidar_data)
                await asyncio.sleep(self.read_interval_secs)

        self.read_task = asyncio.create_task(read_bus())
        self.read_task.add_done_callback(lambda t: None)

        return queue

    def stop(self) -> None:
        if self.read_task is not None:
            self.read_task.cancel()
        if self.bus is not None:
            self.bus.close()

    def __create_bus(self):
        self.bus = SMBus(self.i2c_bus)

        self.i2c_write_msg = i2c_msg.write(self.i2c_address, [0x5A, 0x05, 0x00, 0x01, 0x60])
        """
        this is a buffer with message to be sent to i2c lidar to fetch distance and other readings
        """

        self.i2c_read_msg = i2c_msg.read(self.i2c_address, 11)
        """
        this is buffer to be filled while reading a message from i2c
        11 bytes is allocated since first 2 zero bytes
          are stop bytes between messages, just like separator
        """

    def __normalize(self, value, min_value, max_value):
        """
        should normalize distance within range
        """
        value = min(max_value, value)
        return 1 - (value - min_value) / (max_value - min_value)

    def __read_data(self) -> LidarData:
        self.bus.i2c_rdwr(self.i2c_write_msg, self.i2c_read_msg)
        data = list(self.i2c_read_msg)
        distance = (data[5] << 8 | data[4])
        strength = data[7] << 8 | data[6]
        mode = data[8]
        normalized_distance = self.__normalize(distance, self.distance_min, self.distance_max)
        output_data = LidarData(distance=normalized_distance, strength=strength, mode=mode)
        return output_data
