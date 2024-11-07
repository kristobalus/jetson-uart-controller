import asyncio
import serial

from logging import Logger
from serial import Serial

from src.lidar.lidar import LidarData, Lidar
from typing import Optional


class UARTLidar(Lidar):
    serial_port: str
    baud_rate: int
    serial_reader: Serial
    read_task: asyncio.tasks.Task

    def __init__(self,
                 logger: Logger,
                 distance_min: int,
                 distance_max: int,
                 read_interval_secs: int,
                 serial_port: str,
                 baud_rate: int):
        super().__init__(distance_min, distance_max, read_interval_secs, logger)
        self.serial_port = serial_port
        self.baud_rate = baud_rate

    async def open(self):
        self.serial_reader = serial.Serial(self.serial_port, self.baud_rate)

    async def close(self):
        if self.serial_reader is not None:
            self.serial_reader.close()

    def read_data(self) -> Optional[LidarData]:
        count = self.serial_reader.in_waiting
        if count > 8:
            recv = self.serial_reader.read(9)
            self.serial_reader.reset_input_buffer()
            if recv[0] == 0x59 and recv[1] == 0x59:
                distance = recv[2] + recv[3] * 256
                strength = recv[4] + recv[5] * 256
                normalized_distance = self.normalize_distance(distance)
                output_data = LidarData(distance=normalized_distance, strength=strength, mode=None)
                return output_data
        return None
