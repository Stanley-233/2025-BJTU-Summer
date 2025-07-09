import base64
import os

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from dotenv import load_dotenv
import jwt
import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from model.user import User
from util.engine import get_session

security = HTTPBearer()

load_dotenv(dotenv_path="config.env")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")  # 默认值仅用于开发
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 300


def create_token(user: User):
  expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
  payload = {"sub": user.username, "exp": expire}
  token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
  return token


def decode_token(token: str):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token expired")
  except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)):
  token = credentials.credentials
  payload = decode_token(token)
  username = payload.get("sub")
  if username is None:
    raise HTTPException(status_code=401, detail="Invalid token payload")
  user = session.get(User, username)
  if user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return user


def encrypt_password(password: str) -> str:
  key = b'my_16_byte_key!!'
  cipher = AES.new(key, AES.MODE_ECB)
  padded_password = pad(password.encode(), AES.block_size)
  encrypted = cipher.encrypt(padded_password)
  return base64.b64encode(encrypted).decode()


def decrypt_password(encrypted_password: str) -> str:
  key = b'my_16_byte_key!!'  # 与加密时使用的密钥相同
  cipher = AES.new(key, AES.MODE_ECB)
  encrypted_data = base64.b64decode(encrypted_password)
  decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
  return decrypted_data.decode()
