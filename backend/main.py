# main.py
import logging
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from util.engine import init_db
from db_connection import DatabaseConnection

import router.auth, router.mail_router, \
    router.log_router, router.video_detect_router, \
    router.alarm_router, router.user_router, \
    router.taxi_data_router

app = FastAPI(
    title="滴嘟出行",
    description="滴嘟出行后端 API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

app.include_router(router.auth.auth_router)
app.include_router(router.mail_router.mail_router)
app.include_router(router.log_router.log_router)
app.include_router(router.video_detect_router.video_detect_router)
app.include_router(router.alarm_router.alarm_router)
app.include_router(router.user_router.user_router)
app.include_router(router.taxi_data_router.taxi_data_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/speed-data")
async def get_speed_data(start_date: str = None, end_date: str = None):
    db = DatabaseConnection()
    data = db.get_speed_data(start_date, end_date)
    logging.info(f"Speed data: {data}")
    return data



@app.get("/taxi-weather-data")
async def get_taxi_weather_data(start_date: str = None, end_date: str = None):
    db = DatabaseConnection()
    data = db.get_taxi_weather_data(start_date, end_date)
    logging.info(f"Taxi weather data: {data}")
    return data


@app.get("/combined-speed-data")
async def get_combined_speed_data(start_date: str = None, end_date: str = None):
    db = DatabaseConnection()

    # 获取速度数据
    speed_data = db.get_speed_data(start_date, end_date)

    # 获取订单百分比数据
    trip_data = db.get_trip_percentage_data(start_date, end_date)

    return {
        "speed": speed_data,
        "trip_percentage": trip_data
    }

@app.get("/trip-percentage-data")
async def get_trip_percentage_data(start_date: str = None, end_date: str = None):
    db = DatabaseConnection()
    data = db.get_trip_percentage_data(start_date, end_date)
    return data


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)