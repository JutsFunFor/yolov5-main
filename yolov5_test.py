from yolov5_client import NatsClient as nc
from inference import run_yolov5

if __name__ == "__main__":
    client = nc()
    run_yolov5(client.rstp_address, client.model, client.thresh, "12", "13", 0, "asd", client._size,
               client._latteMenuItemId, client.crop_config)
