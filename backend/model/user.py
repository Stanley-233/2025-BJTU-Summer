from typing import Optional

from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    username: str = Field(primary_key=True, index=True)
    password: str = None
    email: Optional[str] = None
    email_verified: bool = False
    phone: Optional[str] = None
    phone_verified: bool = False
    is_admin: bool = False
    # 用户脸部数据(Base64)
    face_data: Optional[str] = None  # 可选字段，允许为空

