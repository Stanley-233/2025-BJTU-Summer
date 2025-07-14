import base64
from typing import Optional

from sqlmodel import Session
from datetime import datetime
from PIL.Image import Image

from model.security_event import SecurityEvent, EventType, SpoofingDetail, RoadDetail, RoadDanger, RoadDangerType, \
  LogLevel
from model.user import User


def add_unverified_user_event(session: Session,
                              description: str,
                              face_data: str):
  event = SecurityEvent(event_type=EventType.UNVERIFIED_USER,
                        description=description,
                        timestamp=datetime.now(),
                        log_level=LogLevel.WARNING)
  detail = SpoofingDetail(id=event.id, face_data=face_data, liveness_score=None, spoofing_score=None)
  session.add(event)
  session.add(detail)
  session.commit()
  return event

def add_face_spoofing_event(session: Session,
                            description: str,
                            face_data: str,
                            liveness_score: Optional[float] = None,
                            spoofing_score: Optional[float] = None):
  event = SecurityEvent(event_type=EventType.FACE_SPOOFING,
                        description=description,
                        timestamp=datetime.now(),
                        log_level=LogLevel.WARNING)
  detail = SpoofingDetail(id=event.id, face_data=face_data, liveness_score=liveness_score, spoofing_score=spoofing_score)
  session.add(event)
  session.add(detail)
  session.commit()
  return event


def add_road_safety_event(session: Session,
                          description: str,
                          danger_nums: int,
                          dangers: list[tuple[RoadDangerType, float]],
                          predicted_image: Image,
                          link_user: Optional[User] = None):
  event = SecurityEvent(event_type=EventType.ROAD_SAFETY,
                        description=description,
                        timestamp=datetime.now(),
                        log_level=LogLevel.WARNING,
                        link_user=link_user)
  # 将图片转换为 JPEG 格式的字节数据
  img_bytes = predicted_image.tobytes("jpeg", "RGB")
  # 将字节数据转成 Base64 字符串
  img_base64 = base64.b64encode(img_bytes).decode("utf-8")
  detail = RoadDetail(id=event.id, danger_nums=danger_nums, predicted_image=img_base64)
  session.add(event)
  session.commit()
  session.add(detail)
  for danger_type, confidence in dangers:
    rd = RoadDanger(id=event.id, type=danger_type, confidence=confidence)
    session.add(rd)
  session.commit()
  return event

def add_general_event(session: Session,
                      description: str,
                      log_level: LogLevel,
                      link_user: User = None):
  event = SecurityEvent(event_type=EventType.GENERAL,
                        description=description,
                        log_level=log_level,
                        link_username= link_user.username if link_user else None,
                        timestamp=datetime.now())
  session.add(event)
  session.commit()
  return event
