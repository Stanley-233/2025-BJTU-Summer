from typing import Optional
from datetime import datetime, timedelta, timezone
import random
import string

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from deepface import DeepFace

from model.user import User, UserEmail, UserPhone
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


@auth_router.post("/register", summary="用户注册", description="用户注册，返回注册成功消息", responses={
  200: {
    "description": "注册成功",
    "content": {
      "application/json": {
        "example": {
          "message": "注册成功",
          "token": "example_token"
        }
      }
    }
  },
  400: {
    "description": "用户名已存在",
    "content": {
      "application/json": {
        "example": {
          "detail": "Username already registered"
        }
      }
    }
  }
})
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
  new_user.email = UserEmail(
    user=new_user,
    email_address=request.email
  )
  new_user.phone = UserPhone(
    user=new_user,
    phone_number=request.phone
  )
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  token = create_token(new_user)
  return {
    "message": "注册成功",
    "token": token
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


@auth_router.post("/login", summary="用户登录", description="用户登录，返回token", responses={
  200: {
    "description": "登录成功",
    "content": {
      "application/json": {
        "example": {
          "message": "登录成功",
          "is_admin": False,
          "token": "example_token"
        }
      }
    }
  },
  404: {
    "description": "用户不存在",
    "content": {
      "application/json": {
        "example": {
          "detail": "User not found"
        }
      }
    }
  },
  403: {
    "description": "密码错误",
    "content": {
      "application/json": {
        "example": {
          "detail": "Incorrect password"
        }
      }
    }
  }
})
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


@auth_router.put("/post_face/", summary="上传用户脸部数据", responses= {
  200: {
    "description": "成功更改",
    "content": {
      "application/json": {
        "example": {
          "message": "脸部数据上传成功"
        }
      }
    }
  },
  404: {
    "description": "用户不存在",
    "content": {
      "application/json": {
        "example": {
          "detail": "User not found"
        }
      }
    }
  },
  401: {
    "description": "认证错误",
    "content": {
      "application/json": {
        "example": {
          "detail": "Invalid token payload"
        }
      }
    }
  },
})
def put_face_data(face_data: ImageModel, session: Session = Depends(get_session),
                  user: User = Depends(get_current_user)):
  """ 更新用户脸部数据 """
  user.face_data = face_data.image
  session.add(user)
  session.commit()
  session.refresh(user)
  return {"message": "脸部数据上传成功"}


@auth_router.post("/check_face/", summary="人脸识别比对", responses={
  200: {
    "description": "人脸成功识别",
    "content": {
      "application/json": {
        "example": {
          "message": "人脸数据匹配"
        }
      }
    }
  },
  404: {
    "description": "用户不存在或人脸数据不存在",
    "content": {
      "application/json": {
        "example": {
          "detail": "没有找到用户的人脸数据"
        }
      }
    }
  },
  401: {
    "description": "认证错误",
    "content": {
      "application/json": {
        "example": {
          "detail": "Invalid token payload"
        }
      }
    }
  },
  403: {
    "description": "人脸数据不匹配",
    "content": {
      "application/json": {
        "example": {
          "detail": "人脸数据不匹配"
        }
      }
    }
  }
})
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
    raise HTTPException(status_code=500, detail="<UNK>" + str(e))


@auth_router.get("/is_mail_verified/", summary="获取用户是否已验证邮箱", responses={
  200: {
    "description": "返回验证状态",
    "content": {
      "application/json": {
        "example": {
          "email": True
        }
      }
    }
  },
  404: {
    "description": "用户不存在",
    "content": {
      "application/json": {
        "example": {
          "detail": "User not found"
        }
      }
    }
  },
  401: {
    "description": "认证错误",
    "content": {
      "application/json": {
        "example": {
          "detail": "Invalid token payload"
        }
      }
    }
  },
})
def is_mail_verified(user: User = Depends(get_current_user)):
  """ 获取用户是否已验证邮箱 """
  return user.email

@auth_router.put("/verify_email/", summary="请求验证邮箱", responses={
  404: {
    "description": "用户不存在",
    "content": {
      "application/json": {
        "example": {
          "detail": "User not found"
        }
      }
    }
  },
  401: {
    "description": "认证错误",
    "content": {
      "application/json": {
        "example": {
          "detail": "Invalid token payload"
        }
      }
    }
  },
  200: {
    "description": "验证码已发送",
    "content": {
      "application/json": {
        "example": {
          "message": "验证码已发送"
        }
      }
    }
  }
})
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


@auth_router.post("/verify_email_code/", summary="验证邮箱验证码", responses={
  200: {
    "description": "邮箱验证成功",
    "content": {
      "application/json": {
        "example": {
          "message": "邮箱验证成功"
        }
      }
    }
  },
  404: {
    "description": "用户不存在",
    "content": {
      "application/json": {
        "example": {
          "detail": "User not found"
        }
      }
    }
  },
  401: {
    "description": "认证错误",
    "content": {
      "application/json": {
        "example": {
          "detail": "Invalid token payload"
        }
      }
    }
  },
  201: {
    "description": "未请求验证码",
    "content": {
      "application/json": {
        "example": {
          "detail": "未请求验证码"
        }
      }
    }
  },
  202: {
    "description": "验证码已过期",
    "content": {
      "application/json": {
        "example": {
          "detail": "验证码已过期"
        }
      }
    }
  },
  203: {
    "description": "验证码错误",
    "content": {
      "application/json": {
        "example": {
          "detail": "验证码错误"
        }
      }
    }
  }
})
def verify_email_code(code: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
  """验证用户提交的验证码"""
  if not user.email_verification_code or not user.email_verification_expiry:
    raise HTTPException(status_code=201, detail="未请求验证码")

  if datetime.now(timezone.utc) > user.email_verification_expiry:
    raise HTTPException(status_code=202, detail="验证码已过期")

  if user.email_verification_code != code:
    raise HTTPException(status_code=203, detail="验证码错误")

  # 验证成功，更新用户状态
  user.email_verified = True
  user.email_verification_code = None
  user.email_verification_expiry = None
  session.add(user)
  session.commit()

  return {"message": "邮箱验证成功"}
