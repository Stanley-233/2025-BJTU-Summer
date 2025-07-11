# Python
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

# 生成密钥，开发过程中可以保存并安全传输密钥
load_dotenv("config.env")
key = os.getenv("AES_KEY").encode()
fernet = Fernet(key)

# 模拟待加密的 Base64 编码人脸数据
face_data_base64 = "your_base64_encoded_image_string"

# 加密数据
encrypted_face_data = fernet.encrypt(face_data_base64.encode())

# 解密数据（接收端使用相同密钥）
decrypted_face_data = fernet.decrypt(encrypted_face_data).decode()

print("加密后数据：", encrypted_face_data)
print("解密后数据：", decrypted_face_data)