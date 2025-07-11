import base64
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session
from util.engine import get_session
from model.user import User
from util.security import get_current_user
from util.video import extract_and_process_video

video_detect_router = APIRouter()


class VideoDetectRequest(BaseModel):
    video: str
    model_type: Optional[str] = "yolov8n"


@video_detect_router.post("/video_detect/")
def video_detect(request: VideoDetectRequest, user: User = Depends(get_current_user),
                 session: Session = Depends(get_session)):
    try:
        # 指定模型文件路径（暂用yolov8n）
        model_path = 'backend/model/RDD_yolov8n_best.pt'

        # 调用 video.py 中的函数进行视频处理
        result = extract_and_process_video(request.video, request.model_type, model_path)
        return {"image": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
