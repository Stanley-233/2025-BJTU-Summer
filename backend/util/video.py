import cv2
import base64
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO

def load_model(model_path: str):
    # 加载预训练的模型
    model = torch.load(model_path, map_location=torch.device('cpu'))
    # 设置为评估模式
    model.eval()
    return model

def process_frame(frame, model):
    # 将图像转换为模型输入格式
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = Image.fromarray(frame)
    frame = np.array(frame.resize((640, 640))) / 255.0
    frame = frame.transpose(2, 0, 1).astype(np.float32)
    frame = torch.from_numpy(frame).unsqueeze(0)

    # 进行推理
    with torch.no_grad():
        results = model(frame)

    # 提取检测结果
    detections = results[0].numpy()

    # 在图像上绘制检测框
    for *xyxy, conf, cls in detections:
        cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (255, 0, 0), 2)
        cv2.putText(frame, f'{model.names[int(cls)]} {conf:.2f}', (int(xyxy[0]), int(xyxy[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return frame

def extract_and_process_video(base64_video: str, model_path: str):
    # 解码 base64 视频数据
    video_data = base64.b64decode(base64_video)
    temp_video_path = 'temp_video.mp4'
    with open(temp_video_path, 'wb') as f:
        f.write(video_data)

    # 打开视频文件
    cap = cv2.VideoCapture(temp_video_path)
    if not cap.isOpened():
        raise Exception("无法打开视频文件")

    # 获取总帧数
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        raise Exception("视频文件无有效帧")

    # 定位到最后一帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
    ret, frame = cap.read()
    if not ret:
        raise Exception("获取最后一帧失败")
    cap.release()

    # 加载模型
    model = load_model(model_path)

    # 处理帧
    frame = process_frame(frame, model)

    # 将图像编码为 jpg 格式
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        raise Exception("编码图像失败")

    # 转换为 base64 字符串
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

def predict_result():
    model = YOLO("runs/train/road_defect_detection_yolo12n_5/weights/best.pt")#自定义使用模型路径
    results = model.predict(
        source="datasets/BJTU2025_RDD/test",#自定义训练集路径
        save=True,
    )
    return results
