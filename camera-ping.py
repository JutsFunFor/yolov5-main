from inference import run_yolov5
import cv2 as cv
import json

if __name__ == "__main__":

    with open("config.json", 'r') as file:
        config = json.load(file)
    cap_address = config["inference"]["rstpAddress"]
    cap = cv.VideoCapture(rf'{cap_address}')
    ret, frame_raw = cap.read()

    if ret:
        print("Successfully shoot frame with shape: ", frame_raw.shape)
    else:
        print("Access error")