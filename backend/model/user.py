import ipaddress
from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    username: str = Field(primary_key=True, index=True)
    password: str = None
    is_admin: bool = False
    # 用户脸部数据(Base64)
    face_data: Optional[str] = None  # 可选字段，允许为空
    last_ip: Optional[ipaddress.IPv4Address] = None
    # 邮箱信息
    email: Optional["UserEmail"] = Relationship(back_populates="user")
    phone: Optional["UserPhone"] = Relationship(back_populates="user")

class UserEmail(SQLModel, table=True):
    username: str = Field(foreign_key="user.username", primary_key=True, index=True)
    email_address: Optional[str] = Field(index=True)
    email_verified: bool = False
    email_verification_code: Optional[str] = None
    email_verification_expiry: Optional[datetime] = None

class UserPhone(SQLModel, table=True):
    username: str = Field(foreign_key="user.username", primary_key=True, index=True)
    phone_number: Optional[str] = Field(index=True)
    phone_verified: bool = False
    phone_verification_code: Optional[str] = None
    phone_verification_expiry: Optional[datetime] = None