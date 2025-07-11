import random
import string
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from util.engine import get_session
from util.image import ImageModel, UserCheckFaceRequest
from util.security import create_token, get_current_user, encrypt_password
from util.mail import send_email
from model.user import User, UserEmail, UserPhone, UserType

mail_router = APIRouter()

@mail_router.put("/verify_email/", summary="请求邮箱认证", responses={
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
  expiry = datetime.now() + timedelta(minutes=10)

  # 更新用户信息
  user.email.email_verification_code = code
  user.email.email_verification_expiry = expiry
  session.add(user)
  session.commit()

  # 发送邮件
  try:
    send_email(user.email.email_address, "邮箱认证验证码", f"用户{user.username}，您的验证码是：{code}，有效期为10分钟。")
  except RuntimeError as e:
    raise HTTPException(status_code=500, detail=str(e))

  return {"message": "验证码已发送"}


@mail_router.post("/verify_email_code/", summary="邮箱认证验证码", responses={
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
  if not user.email.email_verification_code or not user.email.email_verification_expiry:
    raise HTTPException(status_code=201, detail="未请求验证码")

  if datetime.now() > user.email.email_verification_expiry:
    raise HTTPException(status_code=202, detail="验证码已过期")

  if user.email.email_verification_code != code:
    raise HTTPException(status_code=203, detail="验证码错误")

  # 验证成功，更新用户状态
  user.email.email_verified = True
  user.email.email_verification_code = None
  user.email.email_verification_expiry = None
  session.add(user)
  session.commit()

  return {"message": "邮箱验证成功"}

@mail_router.get("/is_mail_verified/", summary="获取用户是否已验证邮箱", responses={
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

@mail_router.get("/get_user_email/", summary="获取用户邮箱信息", response_model=UserEmail)
def get_user_email(user: User = Depends(get_current_user)):
  """获取用户邮箱信息"""
  if not user.email:
    raise HTTPException(status_code=404, detail="User email not found")
  return user.email

class MailLoginRequest(BaseModel):
  """通过邮箱登录请求体"""
  email: str
  class Config:
    json_schema_extra = {
      "example": {
        "email": "test@bearingwall.top"
      }
    }

@mail_router.post("/login/mail/", summary="通过邮箱登录", responses={
  404: {
    "description": "邮箱未注册",
    "content": {
      "application/json": {
        "example": {
          "detail": "User not found"
        }
      }
    }
  },
  200: {
    "description": "成功发送验证邮件",
    "content": {
      "application/json": {
        "example": {
          "message": "邮件成功发送"
        }
      }
    }
  },
  401: {
    "description": "邮箱未验证",
    "content": {
      "application/json": {
        "example": {
          "detail": "<UNK>"
        }
      }
    }
  },
})
def login_with_email(request: MailLoginRequest, session: Session = Depends(get_session)):
  """通过邮箱登录，请求验证码"""
  user = session.exec(select(User).where(User.email.has(UserEmail.email_address == request.email))).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  if not user.email.email_verified:
    raise HTTPException(status_code=401, detail="邮箱未验证")
  # 生成随机验证码
  code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
  expiry = datetime.now() + timedelta(minutes=10)

  # 更新用户信息
  user.email.email_verification_code = code
  user.email.email_verification_expiry = expiry
  session.add(user)
  session.commit()

  try:
    send_email(user.email.email_address, "邮箱登录验证码 - 滴嘟打车", f"用户{user.username}，您的登录验证码是：{code}，有效期为10分钟。")
  except RuntimeError as e:
    raise HTTPException(status_code=500, detail=str(e))

  return {"message": "邮件成功发送"}


class MailCodeLoginRequest(BaseModel):
  """邮箱+验证码登录请求体"""
  email: str
  code: str
  class Config:
    json_schema_extra = {
      "example": {
        "email": "test@bearingwall.top",
        "code": "123456"
      }
    }


@mail_router.post("/login/mail_code/", summary="通过邮箱验证码登录", responses={
  200: {
    "description": "邮箱登录成功",
    "content": {
      "application/json": {
        "example": {
          "message": "登录成功",
          "token": "example_token",
          "username": "example_user"
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
  },
})
def verify_login_email_code(request: MailCodeLoginRequest, session: Session = Depends(get_session)):
  """通过邮箱登录，检查验证码"""
  user = session.exec(select(User).where(User.email.has(UserEmail.email_address == request.email))).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  if not user.email or not user.email.email_verification_code or not user.email.email_verification_expiry:
    raise HTTPException(status_code=201, detail="未请求验证码")
  if datetime.now() > user.email.email_verification_expiry:
    raise HTTPException(status_code=202, detail="验证码已过期")
  if user.email.email_verification_code != request.code:
    raise HTTPException(status_code=203, detail="验证码错误")

  user.email.email_verification_code = None
  user.email.email_verification_expiry = None

  session.add(user)
  session.commit()

  token = create_token(user)

  return {
    "message": "邮箱验证成功",
    "token": token,
    "username": user.username
  }
