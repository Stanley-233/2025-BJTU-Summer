import os
from typing import Optional
from datetime import datetime, timedelta, timezone
import random
import string
import requests
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from util.engine import get_session
from util.image import ImageModel, UserCheckFaceRequest, extract_last_frame_from_base64_video
from util.security import create_token, get_current_user, encrypt_password
from util.mail import send_email
from model.user import User, UserEmail, UserPhone

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


@auth_router.post("/login", summary="用户登录", description="用户登录", responses={
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

  # 加载百度云 API Key 和 Access Token
  load_dotenv("config.env")
  api_key = os.getenv("BAIDU_API_KEY")
  access_token = os.getenv("BAIDU_ACCESS_TOKEN")

  if not api_key or not access_token:
    raise HTTPException(status_code=500, detail="百度云 API Key 或 Access Token 未配置")

  # 构造百度云人脸注册接口的 HTTP 请求
  url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
  headers = {"Content-Type": "application/json"}
  payload = {
      "image": image,
      "image_type": image_type,
      "group_id": "default",
      "user_id": user.username,
      "user_info": user.username,
      "quality_control": "NORMAL"
  }

  response = requests.post(url, headers=headers, json=payload, params={"access_token": access_token})

  if response.status_code != 200 or response.json().get("error_code"):
    error_msg = response.json().get("error_msg", "未知错误")
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

  load_dotenv("config.env")
  api_key = os.getenv("BAIDU_API_KEY")

  # 构造百度云人脸更新接口的 HTTP 请求
  url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/update"
  access_token = api_key  # 替换为实际的 Access Token
  headers = {"Content-Type": "application/json"}
  payload = {
      "image": image,
      "image_type": image_type,
      "group_id": user.user_type,
      "user_id": user.username,
      "user_info": user.username,
      "quality_control": "NORMAL"
  }

  response = requests.post(url, headers=headers, json=payload, params={"access_token": access_token})

  if response.status_code != 200 or response.json().get("error_code"):
    error_msg = response.json().get("error_msg", "未知错误")
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
  }
})
def check_face_data(request: UserCheckFaceRequest, session: Session = Depends(get_session)):
  """ Base64 人脸识别匹配，识别成功后返回用户登录Token """
  # 加载百度云 API Key 和 Access Token
  load_dotenv("config.env")
  access_token = os.getenv("BAIDU_ACCESS_TOKEN")

  if not access_token:
    raise HTTPException(status_code=500, detail="百度云 Access Token 未配置")

  # 调用 H5 视频活体检测 API
  liveness_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceverify"
  liveness_payload = [{
    "video_base64": request.face_data,
    "face_field": "spoofing,quality"
  }]
  liveness_response = requests.post(liveness_url, json=liveness_payload, params={"access_token": access_token})

  if liveness_response.status_code != 200:
    raise HTTPException(status_code=500, detail=f"活体检测失败: {liveness_response.content}")

  if liveness_response.json().get("error_code") != 0:
    raise HTTPException(status_code=402, detail=f"活体检测失败")

  last_frame = extract_last_frame_from_base64_video(request.face_data)
  # 调用 1:N 搜索 API
  search_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
  search_payload = {
    "image": last_frame,
    "image_type": "BASE64",
    "group_id_list": "default,sysadmin,driver,gov_admin",
    "quality_control": "NORMAL",
    "max_user_num": 1,
  }
  search_response = requests.post(search_url, json=search_payload, params={"access_token": access_token})

  if search_response.status_code != 200 or search_response.json().get("error_code"):
    error_msg = search_response.json().get("error_msg", "未知错误")
    raise HTTPException(status_code=404, detail=f"用户不存在或人脸数据不存在: {error_msg}")

  # 获取搜索结果中的用户信息
  result = search_response.json().get("result", {}).get("user_list", [{}])[0]
  username = result.get("user_id")

  if not username:
    raise HTTPException(status_code=404, detail="用户不存在或人脸数据不存在")

  user = session.get(User, username)
  if not user:
    raise HTTPException(status_code=404, detail="用户不存在")

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
