import asyncio
import json

from logging import getLogger
from fluxmq.service import Service
from fluxmq.adapter.mqtt import MQTT, Topic, Status
from fluxmq.message import Message
from fluxmq.node import Node
from fluxmq.topicfactory import TopicFactory

from i2c_lidar import I2CLidar
from lidar_data import LidarData


class I2CNode(Node):
    lidar: I2CLidar
    i2c_bus: str
    i2c_address: str
    distance_min: int
    distance_max: int
    read_interval_secs: int

    def config(self,
               i2c_bus: str,
               i2c_address: str,
               distance_min: int,
               distance_max: int,
               read_interval_secs: int):
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.distance_min = distance_min
        self.distance_max = distance_max
        self.read_interval_secs = read_interval_secs

    async def on_start(self) -> None:
        self.lidar = I2CLidar(i2c_bus=self.i2c_bus,
                              i2c_address=self.i2c_address,
                              distance_min=self.distance_min,
                              distance_max=self.distance_max,
                              read_interval_secs=self.read_interval_secs)
        queue = self.lidar.start()

        async def read_queue(queue: asyncio.queues.Queue[LidarData]):
            while True:
                lidar_data = await queue.get()
                for topic in self.output_topics:
                    await self.service.publish(topic, lidar_data)

        task = asyncio.create_task(read_queue(queue))
        task.add_done_callback(lambda t: None)
        return

    async def on_error(self, err: Exception) -> None:
        pass

    async def on_stop(self) -> None:
        self.logger.debug(f"Node stopped {self.alias}")
        pass


class LidarService(Service):
    def on_configuration(self, message: Message):
        self.stop_nodes()
        self.clear_nodes()

        config = json.loads(message.payload.encode())

        for node_config in config['nodes']:
            alias = node_config['alias']
            output_topics = node_config['output_topics']
            input_topics = node_config['input_topics']

            node = Node(logger=getLogger(),
                        service=self,
                        alias=alias,
                        output_topics=output_topics,
                        input_topics=input_topics)
            self.append_node(node)

        self.start_nodes()
        return


async def main():
    service = LidarService(service_id="lidars")
    service.attach(transport=MQTT(), topic=Topic(), status=Status())
    await service.run()


asyncio.run(main())
