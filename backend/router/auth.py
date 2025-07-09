from typing import Optional
from datetime import datetime, timedelta, timezone
import random
import string

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from deepface import DeepFace

from model.user import User, UserEmail
from util.engine import get_session
from util.image import decode_image, ImageModel
from util.security import create_token, get_current_user, encrypt_password
from util.mail import send_email

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
        password=encrypt_password(request.password),
        is_admin=False
    )
    new_user.email.email_address = request.email
    new_user.phone.phone_number = request.phone
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    token = create_token(new_user)
    return {
        "message": "注册成功",
        "is_admin": new_user.is_admin,
        "token" : token
    }

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
def put_face_data(face_data: ImageModel, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
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

@auth_router.get("/is_mail_verified/", summary="获取用户是否已验证邮箱")
def is_mail_verified(user: User = Depends(get_current_user)):
    """ 获取用户是否已验证邮箱 """
    return user.email

@auth_router.put("/verify_email/", summary="请求验证邮箱")
def request_email_verification(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """生成验证码并发送到用户邮箱"""
    if not user.email or user.email.email_address is None:
        raise HTTPException(status_code=400, detail="用户未绑定邮箱")

    # 生成随机验证码
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    # 更新用户信息
    user.email.email_verification_code = code
    user.email.email_verification_expiry = expiry
    session.add(user)
    session.commit()

    # 发送邮件
    try:
        send_email(user.email.email_address, "邮箱验证码", f"您的验证码是：{code}，有效期为10分钟。")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "验证码已发送"}

@auth_router.post("/verify_email_code/", summary="验证邮箱验证码")
def verify_email_code(code: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """验证用户提交的验证码"""
    if not user.email_verification_code or not user.email_verification_expiry:
        raise HTTPException(status_code=400, detail="未请求验证码")

    if datetime.now(timezone.utc) > user.email_verification_expiry:
        raise HTTPException(status_code=400, detail="验证码已过期")

    if user.email_verification_code != code:
        raise HTTPException(status_code=400, detail="验证码错误")

    # 验证成功，更新用户状态
    user.email_verified = True
    user.email_verification_code = None
    user.email_verification_expiry = None
    session.add(user)
    session.commit()

    return {"message": "邮箱验证成功"}
