from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout, ErrNoServers
import json
import os
from inference import run_yolov5
from postgreSQL import SQLogger


class NatsClient:
    def __init__(self):
        assert os.path.exists("config.json")
        with open("config.json", 'r') as file:
            config = json.load(file)

        self.model = config["inference"]["modelPath"]
        self.thresh = config["inference"]["threshold"]
        self.iou_thresh = config["inference"]["iouThreshold"]
        self.rstp_address = config["inference"]["rstpAddress"]
        self._url = config["inference"]["natsUrl"]
        self._topic = config["inference"]["sendResultsTopic"]
        self.crop_config = config["crop"]
        self._nc = NATS()
        self._size = (640, 640)  # input tensor shape
        self._actionCompleted_topic = 'complexos.bus.actionCompleted'

        # Uncomment if you want to use PostgreSQL support

        # self.dbname = config["yolov5_inference"]["dbname"]
        # self.usr = config["yolov5_inference"]["usr"]
        # self.pwd = config["yolov5_inference"]["pwd"]
        # self.host = config["yolov5_inference"]["host"]
        # self.autocommit_flag = True

        # self.logger = SQLogger(self.dbname, self.usr, self.pwd, self.host, self.autocommit_flag)
        # self.logger.create_database(self.dbname)
        # self.logger.set_conn_dbase(self.dbname)
        # self.logger.create_dur_table(self.dbname)
        # self.logger.create_stats_table(self.dbname)

    async def receive_msg(self, event_loop):
        """Receive message from self.topic"""
        try:
            await self._nc.connect(servers=[self._url], loop=event_loop)
        except (ErrNoServers, ErrTimeout) as err:
            print(err)

        # Init yolov5 and publish reply
        async def _receive_callback(msg):
            data = json.loads(msg.data.decode())
            if data['action']['name'] == 'take free cup and make a coffee':
                order_id = data['action']['orderId']
                order_number = data['meta']['orderNumber']
                nozzle_id = data['order']['productDump']['nozzleId']
                menu_item_id = data['order']['menuItemId']
                reply = run_yolov5(self.rstp_address, self.model, self.thresh, order_number, order_id, nozzle_id,
                                   menu_item_id, self._size, self.crop_config)

                # Uncomment if you want to use PostgreSQL support
                # self.logger.write_stats(self.dbname, reply)
                # self.logger.write_dur_stats(self.dbname, reply)

                await self._nc.publish(self._topic, json.dumps(reply).encode())
        await self._nc.subscribe(self._actionCompleted_topic, cb=_receive_callback)
