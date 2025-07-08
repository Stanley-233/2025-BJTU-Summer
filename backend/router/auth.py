from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, SQLModel
from deepface import DeepFace

from model.user import User
from util.engine import get_session
from util.image import decode_image, ImageModel
from util.security import create_token, get_current_user, encrypt_password

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

@auth_router.post("/register", summary="用户注册", description="用户注册，返回注册成功消息")
def register(request: UserRegisterRequest, session: Session = Depends(get_session)):
    """ 用户注册 """
    # 检查用户名是否已存在
    user = session.get(User, request.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(
        username=request.username,
        email=request.email,
        phone=request.phone,
        password=encrypt_password(request.password),
        is_admin=False
    )
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

    if user.password != encrypt_password(request.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    token = create_token(user)

    return {"message": "登录成功",
            "is_admin": user.is_admin,
            "token": token}

@auth_router.put("/post_face/", summary="上传用户脸部数据")
def post_face_data(face_data: ImageModel, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """ 更新用户脸部数据 """
    user.face_data = face_data.image
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Face data uploaded successfully"}

@auth_router.post("/check_face/", summary="人脸识别比对")
def check_face_data(face_data: ImageModel, user: User = Depends(get_current_user)):
    """ Base64 人脸识别匹配 """
    if not user.face_data:
        raise HTTPException(status_code=404, detail="没有找到用户的人脸数据")
    try:
        # 解码存储的人脸数据和传入的人脸数据
        stored_img = decode_image(user.face_data)
        incoming_img = face_data.decode()
        # 使用 DeepFace.verify 进行人脸比对
        result = DeepFace.verify(stored_img, incoming_img, model_name='Facenet512')
        print(result)
        if result.get("verified"):
            return {"message": "人脸数据匹配"}
        else:
            raise HTTPException(status_code=403, detail="人脸数据不匹配")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail="人脸数据不匹配")
    except Exception as e:
        raise HTTPException(status_code=500, detail="<UNK>"+ str(e))
