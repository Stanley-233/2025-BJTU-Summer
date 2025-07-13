import base64
import io
from datetime import datetime
from typing import List, Optional

from PIL import Image
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from ultralytics import YOLO

from model.security_event import SecurityEvent, EventType, RoadDetail, RoadDangerType, RoadDanger
from util.engine import get_session
from util.image import extract_last_frame_from_base64_video

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
def video_detect(request: VideoDetectRequest, session: Session = Depends(get_session)):
  """从上传的短视频中道路病害"""
  try:
    model_path = 'D:\\GitHub\\2025-BJTU-Summer\\backend\\model\\RDD_yolov8n_best.pt'
    img_base64 = extract_last_frame_from_base64_video(request.video)
    img_bytes = base64.b64decode(img_base64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    model = YOLO(model_path)
    results = model.predict(
        device='cpu',
        source=img,
        save=True,
    )
    # Annotate image
    annotated = results[0].plot()
    annotated_img = Image.fromarray(annotated)
    buf = io.BytesIO()
    annotated_img.save(buf, format="JPEG", quality=85)

    predicted_image_base64 = base64.b64encode(buf.getvalue()).decode()

    event = SecurityEvent(event_type=EventType.ROAD_SAFETY, timestamp=datetime.now(), description="识别到道路病害")
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

    detail = RoadDetail(id=event.id, predicted_image=predicted_image_base64, danger_nums=danger_count)
    session.add(detail)
    session.commit()
    session.add_all(dangers_db)
    session.commit()
    return VideoDetectResponse(
      predicted_image=predicted_image_base64,
      danger_nums=danger_count,
      dangers=dangers_resp)
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
