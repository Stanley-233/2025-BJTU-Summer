import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from model.user import User
from util.engine import get_session
from util.security import create_token

auth_router = APIRouter()

class UserRegisterRequest(BaseModel):
    username: str
    email: Optional[str]
    phone: Optional[int]
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "test_user",
                "email": "test@bjtu.edu.cn",
                "phone": 12341234123,
                "password": "test_password"
            }
        }

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@auth_router.post("/register", summary="用户注册", description="用户注册，返回注册成功消息")
def register(request: UserRegisterRequest, session: Session = Depends(get_session)):
    """ 用户注册 """
    # 检查用户名是否已存在
    user = session.get(User, request.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User.model_validate(user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "注册成功"}

class UserLoginRequest(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "test_user",
                "password": "test_password"
            }
        }

@auth_router.post("/login", summary="用户登录", description="用户登录，返回token")
def login(request: UserLoginRequest, session: Session = Depends(get_session)):
    user = session.get(User, request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.password != hash_password(request.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    token = create_token(user)

    return {"message": "登录成功",
            "is_admin": user.is_admin,
            "token": token}
