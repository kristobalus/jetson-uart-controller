import asyncio
from logging import Logger

from smbus2 import SMBus, i2c_msg

from src.lidar.lidar import LidarData, Lidar


class I2CLidar(Lidar):
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
        super().__init__(distance_min, distance_max, read_interval_secs, logger)
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address

    async def open(self):
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

    async def close(self):
        if self.bus is not None:
            self.bus.close()

    async def read_data(self) -> LidarData:
        self.bus.i2c_rdwr(self.i2c_write_msg, self.i2c_read_msg)
        data = list(self.i2c_read_msg)
        distance = (data[5] << 8 | data[4])
        strength = data[7] << 8 | data[6]
        mode = data[8]
        normalized_distance = self.normalize_distance(distance)
        output_data = LidarData(distance=normalized_distance, strength=strength, mode=mode)
        return output_data
