import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from util.engine import init_db

import router.auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

app.include_router(router.auth.auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)
