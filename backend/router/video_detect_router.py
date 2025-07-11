import base64
import io

from PIL import Image
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session
from util.engine import get_session
from model.user import User
from util.security import get_current_user
from util.image import extract_last_frame_from_base64_video
from util.video import predict_result

video_detect_router = APIRouter()


class VideoDetectRequest(BaseModel):
  video: str
  model_type: Optional[str] = "yolov8n"


@video_detect_router.post("/video_detect/")
def video_detect(request: VideoDetectRequest, user: User = Depends(get_current_user),
                 session: Session = Depends(get_session)):
  try:
    model_path = 'backend/model/RDD_yolov8n_best.pt'
    img_base64 = extract_last_frame_from_base64_video(request.video)
    img_bytes = base64.b64decode(img_base64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    result = predict_result(img, model_path=model_path)
    return {
      "image": result
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
