import os
from typing import Optional
from datetime import datetime, timedelta, timezone
import random
import string

import aip
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from util.engine import get_session
from util.image import ImageModel, UserCheckFaceRequest
from util.security import create_token, get_current_user, encrypt_password
from util.mail import send_email
from model.user import User, UserEmail, UserPhone, UserType

auth_router = APIRouter()

# 百度云配置
load_dotenv("config.env")
app_id = os.getenv("BAIDU_APP_ID")
api_key = os.getenv("BAIDU_API_KEY")
secret_key = os.getenv("BAIDU_SECRET_KEY")

if not app_id or not api_key or not secret_key:
    raise HTTPException(status_code=500, detail="百度云配置未正确设置")

client = aip.AipFace(app_id, api_key, secret_key)

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
    user_type=UserType.DRIVER
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


@auth_router.post("/login", summary="用户登录", description="用户登录", responses={
  200: {
    "description": "登录成功",
    "content": {
      "application/json": {
        "example": {
          "message": "登录成功",
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
          "token": token}


@auth_router.post("/post_face/", summary="注册用户脸部数据", responses={
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
def post_face_data(face_data: ImageModel, session: Session = Depends(get_session),
                   user: User = Depends(get_current_user)):
    """ 注册用户脸部数据 """
    image = face_data.image
    image_type = "BASE64"

    options = {
        "quality_control": "NORMAL"
    }

    result = client.addUser(image, image_type, "default", user.username, options)

    if result.get("error_code") != 0:
        error_msg = result.get("error_msg", "未知错误")
        raise HTTPException(status_code=500, detail=f"百度云错误: {error_msg}")

    user.face_data = image
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "脸部数据上传成功"}


@auth_router.put("/update_face/", summary="更新用户脸部数据", responses={
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
def update_face_data(face_data: ImageModel, session: Session = Depends(get_session),
                     user: User = Depends(get_current_user)):
    """ 更新用户脸部数据 """
    image = face_data.image
    image_type = "BASE64"

    options = {
        "quality_control": "NORMAL"
    }

    result = client.updateUser(image, image_type, "default", user.username, options)

    if result.get("error_code") != 0:
        error_msg = result.get("error_msg", "未知错误")
        raise HTTPException(status_code=500, detail=f"百度云错误: {error_msg}")

    user.face_data = image
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "脸部数据上传成功"}


@auth_router.post("/check_face/", summary="人脸识别获取Token", responses={
  200: {
    "description": "人脸成功识别",
    "content": {
      "application/json": {
        "example": {
          "message": "人脸数据匹配",
          "token": "example_token",
          "user": {
            "username": "test_user",
            "email": "test@bjtu.edu.cn",
            "phone": "12341234123"
          }
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
  402: {
    "description": "活体检测失败",
    "content": {
      "application/json": {
        "example": {
          "detail": "活体检测失败"
        }
      }
    }
  },
  406: {
    "description": "活体检测失败，有两人同时出现",
    "content": {
      "application/json": {
        "example": {
          "detail": "活体检测失败，有两人同时出现"
        }
      }
    }
  }
})
def check_face_data(request: UserCheckFaceRequest, session: Session = Depends(get_session)):
  """ Base64 人脸识别匹配，识别成功后返回用户登录Token """
  liveness_result = client.facelivenessVerifyV1(video_base64=request.face_data, options={
    "face_field": "spoofing,quality"
  })

  if liveness_result.get("error_code") != 0:
    if liveness_result.get("error_code") == 216909:
      raise HTTPException(status_code=406, detail="活体检测失败，有两人同时出现")
    raise HTTPException(status_code=500, detail=f"活体检测失败：{liveness_result.get('error_msg', '未知错误')}")

  best_img = liveness_result.get("result").get("best_image")

  if best_img is None:
    raise HTTPException(status_code=402, detail="活体检测失败，未检测到人像")
  if best_img.get("liveness_score") < 0.3:
    raise HTTPException(status_code=402, detail="活体检测失败，分数过低")
  if best_img.get("spoofing") > 0.00048:
    raise HTTPException(status_code=402, detail="活体检测失败，为合成图")

  search_response = client.search(image=best_img.get("pic"), image_type="BASE64", group_id_list="default", options={
    "max_user_num": 1
  })

  if search_response.get("error_code") == 222207:
    raise HTTPException(status_code=404, detail="非认证用户，用户不存在或人脸数据不存在")

  # 获取搜索结果中的用户信息
  result = search_response.get("result").get("user_list")[0]
  username = result.get("user_id")
  user = session.get(User, username)

  if not user:
    raise HTTPException(status_code=404, detail="非认证用户，用户不存在或人脸数据不存在")

  # 生成 Token
  token = create_token(user)

  return {
    "message": "人脸数据匹配",
    "token": token,
    "user": {
      "username": user.username,
      "email": user.email.email_address if user.email else None,
      "phone": user.phone.phone_number if user.phone else None
    }
  }


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


@auth_router.get("/get_user_info/", summary="获取用户信息", response_model=User)
def get_user_info(user: User = Depends(get_current_user)):
  """获取当前用户信息"""
  return user

@auth_router.get("/get_user_email/", summary="获取用户邮箱信息", response_model=UserEmail)
def get_user_email(user: User = Depends(get_current_user)):
  """获取用户邮箱信息"""
  if not user.email:
    raise HTTPException(status_code=404, detail="User email not found")
  return user.email
