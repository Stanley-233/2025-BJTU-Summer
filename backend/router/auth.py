import os
from typing import Optional

import aip
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session

from model.security_event import LogLevel, EventType
from util.engine import get_session
from util.image import ImageModel, UserCheckFaceRequest
from util.log import add_face_spoofing_event, add_unverified_user_event, add_general_event
from util.security import create_token, get_current_user, encrypt_password, aes_decrypt
from model.user import User, UserEmail, UserPhone, UserType

auth_router = APIRouter()

# 百度云配置
load_dotenv("config.env")
app_id = os.getenv("BAIDU_APP_ID")
api_key = os.getenv("BAIDU_API_KEY")
secret_key = os.getenv("BAIDU_SECRET_KEY")
AES_KEY = os.getenv("AES_KEY")
if not AES_KEY:
  raise HTTPException(status_code=500, detail="AES_KEY 未设置")
PASSWORD = AES_KEY.encode()

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
  add_general_event(session, f"用户 {new_user.username} 注册成功", link_user=user, log_level=LogLevel.INFO)
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
def login(request: UserLoginRequest, req: Request, session: Session = Depends(get_session)):
  user = session.get(User, request.username)
  if not user:
    add_general_event(session, f"用户 {request.username} 不存在", log_level=LogLevel.WARNING)
    raise HTTPException(status_code=404, detail="User not found")

  if user.password != encrypt_password(request.password):
    add_general_event(session, f"用户 {request.username} 尝试登陆密码错误", link_user=user, log_level=LogLevel.WARNING)
    raise HTTPException(status_code=403, detail="Incorrect password")

  token = create_token(user)
  # 记录登录IP为字符串
  try:
    user.last_ip = req.client.host
    session.add(user)
    session.commit()
  except Exception:
    pass

  add_general_event(session, f"用户 {user.username} 登录成功", link_user=user, log_level=LogLevel.INFO)
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
  image = aes_decrypt(face_data.image, PASSWORD)
  image_type = "BASE64"

  options = {
    "quality_control": "NORMAL"
  }

  result = client.addUser(image, image_type, "default", user.username, options)

  if result.get("error_code") != 0:
    error_msg = result.get("error_msg", "未知错误")
    add_general_event(session, f"人脸注册失败, {result.get("error_code")}, {result.get("error_msg")}", link_user=user, log_level=LogLevel.INFO)
    raise HTTPException(status_code=500, detail=f"百度云错误: {error_msg}")


  user.face_data = image
  session.add(user)
  session.commit()
  session.refresh(user)
  add_general_event(session, f"用户 {user.username} 人脸注册成功", link_user=user, log_level=LogLevel.INFO)
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
  image = aes_decrypt(face_data.image, PASSWORD)
  image_type = "BASE64"

  options = {
    "quality_control": "NORMAL"
  }

  result = client.updateUser(image, image_type, "default", user.username, options)

  if result.get("error_code") != 0:
    error_msg = result.get("error_msg", "未知错误")
    add_general_event(session, f"人脸更新失败, {result.get("error_code")}, {result.get("error_msg")}", link_user=user, log_level=LogLevel.INFO)
    raise HTTPException(status_code=500, detail=f"百度云错误: {error_msg}")

  user.face_data = image
  session.add(user)
  session.commit()
  session.refresh(user)
  add_general_event(session, f"用户 {user.username} 人脸更新成功", link_user=user, log_level=LogLevel.INFO)
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
def check_face_data(request: UserCheckFaceRequest, req: Request, session: Session = Depends(get_session)):
  """ Base64 人脸识别匹配，识别成功后返回用户登录Token """
  face_video = aes_decrypt(request.face_data, PASSWORD)
  liveness_result = client.facelivenessVerifyV1(video_base64=face_video, options={
    "face_field": "spoofing,quality"
  })

  if liveness_result.get("error_code") != 0:
    if liveness_result.get("error_code") == 216909:
      add_face_spoofing_event(session, "活体检测失败: 两人同时出现", request.face_data)
      raise HTTPException(status_code=406, detail="活体检测失败，有两人同时出现")
    add_face_spoofing_event(session, "活体检测失败: 两人同时出现", request.face_data)
    raise HTTPException(status_code=406, detail=f"活体检测失败：{liveness_result.get('error_msg', '未知错误')}")

  best_img = liveness_result.get("result").get("best_image")

  if best_img is None:
    add_face_spoofing_event(session, "活体检测失败: 未检测到人像", request.face_data)
    raise HTTPException(status_code=402, detail="活体检测失败，未检测到人像")
  if best_img.get("liveness_score") < 0.3:
    add_face_spoofing_event(session, "活体检测失败: 未检测到人像", request.face_data,
                            liveness_score=best_img.get("liveness_score"),
                            spoofing_score=best_img.get("spoofing_score"))
    raise HTTPException(status_code=402, detail="活体检测失败，活体分数过低")
  if best_img.get("spoofing") > 0.00048:
    add_face_spoofing_event(session, "活体检测失败: 可能为合成图", request.face_data,
                            liveness_score=best_img.get("liveness_score"),
                            spoofing_score=best_img.get("spoofing_score"))
    raise HTTPException(status_code=402, detail="活体检测失败，为合成图")

  search_response = client.search(image=best_img.get("pic"), image_type="BASE64", group_id_list="default", options={
    "max_user_num": 1,
    "match_threshold": 80
  })

  if search_response.get("error_code") == 222207:
    add_unverified_user_event(session, "非认证用户，用户不存在或人脸数据未注册", request.face_data)
    raise HTTPException(status_code=404, detail="非认证用户，用户不存在或人脸数据不存在")

  # 获取搜索结果中的用户信息
  result = search_response.get("result").get("user_list")[0]
  username = result.get("user_id")
  user = session.get(User, username)

  if not user:
    add_unverified_user_event(session, "非认证用户，用户不存在或人脸数据未注册", request.face_data)
    raise HTTPException(status_code=404, detail="非认证用户，用户不存在或人脸数据不存在")

  # 生成 Token
  token = create_token(user)
  # 记录登录IP为字符串
  try:
    user.last_ip = req.client.host
    session.add(user)
    session.commit()
  except Exception:
    pass
  add_general_event(session, f"用户 {user.username} 人脸认证登录成功", link_user=user, log_level=LogLevel.INFO)
  return {
    "message": "人脸数据匹配",
    "token": token,
    "user": {
      "username": user.username,
      "email": user.email.email_address if user.email else None,
      "phone": user.phone.phone_number if user.phone else None
    }
  }



@auth_router.get("/get_user_info/", summary="获取用户信息", response_model=User)
def get_user_info(user: User = Depends(get_current_user)):
  """获取当前用户信息"""
  return user

