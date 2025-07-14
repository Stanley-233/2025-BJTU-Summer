import base64
import os
import subprocess
from datetime import datetime
from typing import List, Optional

import cv2
from PIL import Image, ImageDraw, ImageFont
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from ultralytics import YOLO

from model.security_event import SecurityEvent, EventType, RoadDetail, RoadDangerType, RoadDanger, LogLevel
from model.user import User
from router.alarm_router import broadcast_sys_event, broadcast_gov_event, broadcast_road_event
from util.engine import get_session
from util.security import get_current_user
import numpy as np

video_detect_router = APIRouter()


class VideoDetectRequest(BaseModel):
  video: str
  model_type: Optional[str] = "yolov8n"


class RoadDangerInfo(BaseModel):
  type: RoadDangerType
  confidence: float


class VideoDetectResponse(BaseModel):
  predicted_image: str
  danger_nums: int
  dangers: List[RoadDangerInfo]


@video_detect_router.post("/video_detect/", summary="视频流道路病害检测", response_model=VideoDetectResponse)
def video_detect(request: VideoDetectRequest, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
  """从上传的短视频中道路病害"""
  new_names = {
    0: "纵向",
    1: "横向",
    2: "网状",
    3: "坑洼",
    4: "补丁"
  }
  try:
    model_path = f'D:\\GitHub\\2025-BJTU-Summer\\backend\\model\\RDD_{request.model_type}_best.pt'
    video_base64 = request.video
    video_data = base64.b64decode(video_base64)
    temp_video_path = 'temp_video.mp4'
    with open(temp_video_path, 'wb') as f:
      f.write(video_data)
    model = YOLO(model_path)
    model.model.names = new_names  # 设置模型类别名称
    # 执行预测但不保存默认绘制结果
    results = model.predict(
        source=temp_video_path,
        save=True,
    )
    # 自定义绘制中文标签，生成带框视频
    cap = cv2.VideoCapture(temp_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    avi_path = os.path.join(results[0].save_dir, 'temp_video_zh.avi')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # type: ignore
    writer = cv2.VideoWriter(avi_path, fourcc, fps, (width, height))
    # 加载中文字体，字体文件 simhei.ttf 应放在 router/fonts 目录下，字体大小可调
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'simhei.ttf')
    font = ImageFont.truetype(font_path, 26 )
    frame_idx = 0
    while True:
      ret, frame = cap.read()
      if not ret:
        break
      img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
      draw = ImageDraw.Draw(img_pil)
      boxes = results[frame_idx].boxes.xyxy.cpu().numpy()
      confs = results[frame_idx].boxes.conf.cpu().numpy()
      cls_ids = results[frame_idx].boxes.cls.cpu().numpy().astype(int)
      for (x1, y1, x2, y2), conf, cid in zip(boxes, confs, cls_ids):
        draw.rectangle([x1, y1, x2, y2], outline='red', width=2)
        text = f"{new_names[cid]} {conf:.2f}"
        # 在文本上添加黑色描边并使用更大字体
        draw.text(
          (x1, y1 - font.size - 5), text,
          font=font, fill='red', stroke_width=2, stroke_fill='black'
        )
      frame_draw = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
      writer.write(frame_draw)
      frame_idx += 1
    cap.release()
    writer.release()
    # 转码为 mp4
    mp4_path = os.path.join(results[0].save_dir, 'temp_video.mp4')
    subprocess.run([
        'ffmpeg', '-i', avi_path,
        '-vcodec', 'libx264', '-crf', '28', '-preset', 'veryfast',
        mp4_path
    ], check=True)
    with open(mp4_path, 'rb') as f:
      video_bytes = f.read()
    predicted_video_base64 = base64.b64encode(video_bytes).decode()

    event = SecurityEvent(event_type=EventType.ROAD_SAFETY,
                          timestamp=datetime.now(),
                          description="识别到道路病害",
                          link_username=user.username,
                          log_level=LogLevel.WARNING)
    session.add(event)
    session.commit()

    # Build danger lists for DB and response
    dangers_db = []
    dangers_resp = []
    for box in results[0].boxes:
      class_idx = int(box.cls)
      confidence = float(box.conf)
      danger_type = RoadDangerType(class_idx)
      # DB model
      dangers_db.append(RoadDanger(id=event.id, type=danger_type, confidence=confidence))
      # Response model
      dangers_resp.append(RoadDangerInfo(type=danger_type, confidence=confidence))
    danger_count = len(dangers_db)
    event.description = f"通过视频识别到 {danger_count} 种道路病害"

    detail = RoadDetail(id=event.id, predicted_image=predicted_video_base64, danger_nums=danger_count)
    session.add(detail)
    session.commit()
    session.add_all(dangers_db)
    session.commit()
    broadcast_sys_event(event)
    broadcast_gov_event(event)
    broadcast_road_event(event)
    return VideoDetectResponse(
      predicted_image=predicted_video_base64,
      danger_nums=danger_count,
      dangers=dangers_resp)
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
