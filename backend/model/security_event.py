import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class SecurityEvent(SQLModel, table=True):
  id: uuid.UUID = Field(primary_key=True, index=True)
  event_type: str = Field(index=True, description="事件类型")
  description: Optional[str] = Field(description="事件描述")
  timestamp: datetime
