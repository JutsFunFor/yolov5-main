import json
import numpy as np
import torch
import cv2 as cv
from PIL import Image
from utils.augmentations import letterbox
from utils.torch_utils import select_device, time_sync
from models.common import DetectMultiBackend
from utils.general import check_img_size, non_max_suppression, scale_coords, xyxy2xywh
from utils.plots import Annotator, colors
from datetime import datetime
import os


def run_yolov5(cap_address, model_path, thresh, order_number, order_id, nozzle_id, menu_item_id, image_size, latte_id,
               crop_config):
    dt = []
    t1 = time_sync()

    cap = cv.VideoCapture(rf'{cap_address}')
    ret, frame_raw = cap.read()
    nozzle_id = str(nozzle_id)

    if ret:
        frame_raw = Image.fromarray(frame_raw)
        if nozzle_id == '0':
            yCropMin = crop_config["nozzleId0"]['yCropMin']
            yCropMax = crop_config["nozzleId0"]['yCropMax']
            xCropMin = crop_config["nozzleId0"]['xCropMin']
            xCropMax = crop_config["nozzleId0"]['xCropMax']

            frame0 = frame_raw[yCropMin:yCropMax, xCropMin:xCropMax]
            pixel_coeff = crop_config["nozzleId0"]["pixelCoeff"]  # real distance in mm in one pixel
            clipLimit = crop_config["nozzleId0"]["clipLimit"]  # clipLimit for CLAHE equalization
        else:
            yCropMin = crop_config["nozzleId1"]['yCropMin']
            yCropMax = crop_config["nozzleId1"]['yCropMax']
            xCropMin = crop_config["nozzleId1"]['xCropMin']
            xCropMax = crop_config["nozzleId1"]['xCropMax']

            frame0 = frame_raw[yCropMin:yCropMax, xCropMin:xCropMax]
            pixel_coeff = crop_config["nozzleId1"]["pixelCoeff"]  # real distance in mm in one pixel
            clipLimit = crop_config["nozzleId1"]["clipLimit"]  # clipLimit for CLAHE equalization

        #  Check for latte preprocessing
        if menu_item_id != latte_id:
            # Apply hist equalization
            clahe = cv.createCLAHE(clipLimit=clipLimit, tileGridSize=(3, 3))
            lab = cv.cvtColor(frame0, cv.COLOR_BGR2LAB)
            lab[..., 0] = clahe.apply(lab[..., 0])
            dst_lab = cv.cvtColor(lab, cv.COLOR_LAB2BGR)

            img = letterbox(dst_lab, image_size, stride=32, auto=True)[0]

        else:
            img = letterbox(frame0, image_size, stride=32, auto=True)[0]

        # Convert
        img = img[..., ::-1].transpose((2, 0, 1))  # BGR to RGB, BHWC to BCHW
        img = np.ascontiguousarray(img)
    else:
        raise AssertionError

    t2 = time_sync()

    # Load model
    device = select_device('cpu')
    model = DetectMultiBackend(model_path, device=device, dnn=False)
    stride, names, pt, jit, onnx, engine = model.stride, model.names, model.pt, model.jit, model.onnx, model.engine
    imgsz = check_img_size(image_size, s=stride)  # check image size
    model.model.float()
    bs = 1  # batch size

    # Run inference
    model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup

    # im = to_tensor(img) #torch.from_numpy(img).to(device)
    im = torch.from_numpy(img).float().to('cpu')
    im /= 255

    if len(im.shape) == 3:
        im = im[None]  # expand for batch dim

    # Inference
    pred = model(im, augment=False, visualize=False)

    # NMS
    pred = non_max_suppression(pred, thresh, 0.45, None, False, max_det=2)

    t3 = time_sync()

    if not os.path.exists(crop_config["rawImagesSavePath"]):
        os.mkdir(crop_config["rawImagesSavePath"])

    if not os.path.exists('pred/'):
        os.mkdir('pred/')

    save_raw_path = crop_config["rawImagesSavePath"]
    save_pred_path = crop_config["predictionImagesSavePath"]
    save_json_path = crop_config["saveJsonResultsPath"]

    # Format to datetime
    f = '%Y-%m-%d %H:%M:%S'

    # score, real_distance = 0, 0
    y_max_det = np.array([])  # yMaxDet[0] refers to Coffee class, yMaxDet[1] - to CupTop class
    res_line = {"Detection": {"Coffee": {}, "CupTop": {}},
                "OrderId": f"{order_id}",
                "OrderNumber": f"{order_number}",
                "NozzleId": nozzle_id,
                "MenuItemId": f"{menu_item_id}",
                "DateTime": f"{datetime.now().strftime(f)}"}

    for i, det in enumerate(pred):

        # gn = torch.tensor(frame_raw.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        annotator = Annotator(np.ascontiguousarray(frame0), line_width=2, example=str(names))

        if len(det):
            # Rescale boxes from im_size to frame0 size
            det[:, :4] = scale_coords(im.shape[2:], det[:, :4], frame0.shape).round()

            # Write results
            for *xyxy, conf, cls in reversed(det):
                # xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                y_max_det = np.append(y_max_det, np.abs(np.float32(xyxy[1])))
                c = int(cls)
                res_line["Detection"][str(names[c])] = {
                    "Xmax": f"{np.float32(xyxy[2])}",
                    "Ymax": f"{np.float32(xyxy[1])}",
                    "Ymin": f"{np.float32(xyxy[3])}",
                    "Score": f"{np.float32(conf):.2f}"
                }  # label format

                label = f"{names[c]} {conf:.2f}"
                annotator.box_label(xyxy, label, color=colors(c, True))

        im0 = annotator.result()
        cv.imwrite(f'{save_pred_path}/{order_number}-{datetime.now()}.png', im0)
    cv.imwrite(f'{save_raw_path}/{order_number}-{datetime.now()}.png', frame0)

    t4 = time_sync()
    dt.append(t2 - t1)  # Capture and crop + change colorspace time
    dt.append(t3 - t2)  # Loading model + inference + NMS time
    dt.append(t4 - t3)  # Save img time
    dt.append(t4 - t1)  # Total time

    # Add time measurement to resLine
    res_line["Capture_duration"] = f"{np.float32(dt[0]):.2f}"
    res_line["Inference_duration"] = f"{np.float32(dt[1]):.2f}"
    res_line["Save_img_duration"] = f"{np.float32(dt[2]):.2f}"
    res_line["Total_time"] = f"{np.float32(dt[3]):.2f}"

    # Add RealDistance if exists to resLine
    if len(y_max_det) > 1:
        res_line["RealDistance"] = f"{np.abs(pixel_coeff * (y_max_det[0] - y_max_det[1])):.2f}"
    else:
        res_line["RealDistance"] = -1

    with open(save_json_path, 'a') as f:
        f.write(json.dumps(str(res_line)) + '\n')

    return res_line
