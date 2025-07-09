import base64
import cv2
import numpy as np
from pydantic import BaseModel


def decode_image(b64_string: str) -> np.ndarray:
  img_data = base64.b64decode(b64_string)
  np_arr = np.frombuffer(img_data, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
  return img


class ImageModel(BaseModel):
  image: str

  def decode(self) -> np.ndarray:
    return decode_image(self.image)
