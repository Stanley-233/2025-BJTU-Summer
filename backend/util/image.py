import base64
import cv2
import numpy as np
from pydantic import BaseModel

class ImageModel(BaseModel):
  image: str

  def decode(self) -> np.ndarray:
    return decode_image(self.image)

  class Config:
    json_schema_extra = {
      "example": {
        "image": "base64_encoded_image_string"
      }
    }

class UserCheckFaceRequest(BaseModel):
  face_data: str

  class Config:
    json_schema_extra = {
      "example": {
        "username": "test_user",
        "face_data": "base64_encoded_video_string"
      }
    }

def decode_image(b64_string: str) -> np.ndarray:
  img_data = base64.b64decode(b64_string)
  np_arr = np.frombuffer(img_data, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
  return img

def extract_last_frame_from_base64_video(base64_video: str) -> str:
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
  # 定位到最后一帧（或倒数第10帧，如需精准最后一帧可设为 frame_count-1）
  cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
  ret, frame = cap.read()
  if not ret:
    raise Exception("获取最后一帧失败")
  cap.release()
  # 将图像编码为 jpg 格式
  ret, buffer = cv2.imencode('.jpg', frame)
  if not ret:
    raise Exception("编码图像失败")
  # 转换为 base64 字符串
  jpg_as_text = base64.b64encode(buffer).decode('utf-8')
  return jpg_as_text
