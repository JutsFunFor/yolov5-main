import asyncio
from yolov5_client import NatsClient

if __name__ == '__main__':
    client = NatsClient()
    loop = asyncio.get_event_loop()
    loop.create_task(client.receive_msg(loop))

    try:
        loop.run_forever()
    except Exception as err:
        print(err)
    finally:
        loop.close()