import enum
import uuid
from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

class EventType(enum.Enum):
  UNVERIFIED_USER = 0
  FACE_SPOOFING = 1
  ROAD_SAFETY = 2
  GENERAL = 3

class LogLevel(enum.Enum):
  INFO = 0
  WARNING = 1
  ERROR = 2

class SecurityEvent(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
  log_level: LogLevel = Field(index=True, description="日志级别", default=LogLevel.INFO)
  link_username: Optional[str] = Field(default=None, description="关联用户", foreign_key="user.username")
  event_type: EventType = Field(index=True, description="事件类型")
  description: Optional[str] = Field(description="事件描述")
  timestamp: datetime = Field(description="事件发生时间")

class SpoofingDetail(SQLModel, table=True):
  id: uuid.UUID = Field(primary_key=True, index=True, foreign_key="securityevent.id")
  face_data: Optional[str] = Field(description="人脸数据(Base64视频)")
  # Event Type如果是0，后两项值就没有意义
  liveness_score: Optional[float] = Field(description="活体检测分数")
  spoofing_score: Optional[float] = Field(description="欺诈检测分数")

class RoadDetail(SQLModel, table=True):
  id: uuid.UUID = Field(primary_key=True, index=True, foreign_key="securityevent.id")
  danger_nums: Optional[int] = Field(description="危险物品数量")
  predicted_image: str = Field(description="模型预测结果(Base64)")

class RoadDangerType(enum.Enum):
  HORIZONTAL = 0
  VERTICAL = 1
  CHAP = 2
  HOLE = 3
  REPAIR = 4

class RoadDanger(SQLModel, table=True):
  danger_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  id: uuid.UUID = Field(index=True, foreign_key="roaddetail.id")
  # 病害类型
  type: RoadDangerType = Field(description="病害类型")
  # 置信度
  confidence: Optional[float] = Field(description="置信度")