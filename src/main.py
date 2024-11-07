import asyncio
import json
from asyncio import Task

from logging import getLogger

from fluxmq.node_state import NodeState
from fluxmq.service import Service
from fluxmq.message import Message
from fluxmq.node import Node

from fluxmq.adapter.mqtt import MQTT, Topic, Status

from lidar.lidar import Lidar, LidarData
from lidar.i2c_lidar import I2CLidar
from lidar.uart_lidar import UARTLidar
from lidar.fake_lidar import FakeLidar


class LidarNode(Node):
    lidar: Lidar
    task: Task

    def set_lidar(self, lidar: Lidar):
        self.lidar = lidar

    async def on_start(self) -> None:
        queue = await self.lidar.start()

        async def read_queue(queue: asyncio.queues.Queue[LidarData]):
            while True:
                lidar_data = await queue.get()
                for topic in self.output_topics:
                    await self.service.publish(topic, lidar_data)

        self.task = asyncio.create_task(read_queue(queue))
        self.task.add_done_callback(lambda t: None)
        return

    async def on_stop(self) -> None:
        self.logger.debug(f"Node {self.node_id} stopped.")
        await self.lidar.stop()
        if self.task:
            self.task.cancel()

    async def on_error(self, err: Exception) -> None:
        self.logger.error(f"Node {self.node_id} error.")
        self.logger.error(err)


class LidarService(Service):
    async def on_configuration(self, message: Message):
        await self.destroy_nodes()

        config = json.loads(message.payload.encode())

        for node_config in config['nodes']:
            # node settings
            node_type = node_config['type']
            node_id = node_config['alias']
            output_topics = node_config['output_topics']
            input_topics = node_config['input_topics']

            lidar = None

            if node_type == 'i2c':
                # i2c lidar settings
                distance_max = node_config['distance_max']
                distance_min = node_config['distance_min']
                read_interval_secs = node_config['read_interval_secs']
                i2c_bus = node_config['i2c_bus']
                i2c_address = node_config['i2c_address']

                lidar = I2CLidar(logger=getLogger(),
                                 distance_max=distance_max,
                                 distance_min=distance_min,
                                 read_interval_secs=read_interval_secs,
                                 i2c_bus=i2c_bus,
                                 i2c_address=i2c_address)

            if node_type == 'uart':
                # lidar settings
                distance_max = node_config['distance_max']
                distance_min = node_config['distance_min']
                read_interval_secs = node_config['read_interval_secs']
                serial_port = node_config['serial_port']
                baud_rate = node_config['baud_rate']

                lidar = UARTLidar(logger=getLogger(),
                                  distance_max=distance_max,
                                  distance_min=distance_min,
                                  read_interval_secs=read_interval_secs,
                                  serial_port=serial_port,
                                  baud_rate=baud_rate)

            if node_type == 'fake':
                # fake lidar settings
                distance_max = node_config['distance_max']
                distance_min = node_config['distance_min']
                read_interval_secs = node_config['read_interval_secs']

                lidar = FakeLidar(logger=getLogger(),
                                  distance_max=distance_max,
                                  distance_min=distance_min,
                                  read_interval_secs=read_interval_secs)

            if lidar is not None:
                node = LidarNode(logger=getLogger(),
                                 service=self,
                                 state_factory=NodeState(),
                                 node_id=node_id,
                                 output_topics=output_topics,
                                 input_topics=input_topics)
                node.set_lidar(lidar)
                self.append_node(node)

        await self.start_nodes()
        return


async def main():
    service = LidarService(service_id="lidars")
    service.attach(transport=MQTT(), topic=Topic(), status=Status())
    await service.run()


asyncio.run(main())
