import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from model.security_event import SecurityEvent
from model.user import User, UserType
from util.engine import get_session
from util.security import get_current_user

warning_queues: list[asyncio.Queue] = []
gov_warning_queues: list[asyncio.Queue] = []
road_warning_queues: list[asyncio.Queue] = []

alarm_router = APIRouter()

def broadcast_sys_event(event: SecurityEvent):
  """
  对外脚本调用此函数向所有订阅者广播 WARNING 告警。
  支持直接传入 SecurityEvent 实例或 dict。
  """
  payload = {
    "event_type": event.event_type.value,
    "description": event.description,
    "timestamp": event.timestamp,
    "log_level": event.log_level.value,
    "link_username": event.link_username
  }
  data = json.dumps(payload, default=str)
  for q in warning_queues:
    q.put_nowait(data)

@alarm_router.get("/alarm/sys_warning/stream", summary="系统管理员告警推送")
async def warning_event_stream(user: User = Depends(get_current_user)):
  # 仅管理员用户可订阅
  if user.user_type != UserType.SYSADMIN:
    raise HTTPException(status_code=403, detail="权限不足，非系统管理员")

  queue: asyncio.Queue = asyncio.Queue()
  warning_queues.append(queue)

  async def event_generator():
    try:
      while True:
        msg = await queue.get()
        yield f"data: {msg}\n\n"
    except asyncio.CancelledError:
      pass
    finally:
      warning_queues.remove(queue)

  return StreamingResponse(event_generator(), media_type="text/event-stream")

def broadcast_gov_event(event: SecurityEvent):
  """
  对外脚本调用此函数向所有 GOV_ADMIN 订阅者广播 WARNING 告警
  """
  payload = {
    "event_type": event.event_type.value,
    "description": event.description,
    "timestamp": event.timestamp,
    "log_level": event.log_level.value,
    "link_username": event.link_username
  }
  data = json.dumps(payload, default=str)
  for q in gov_warning_queues:
    q.put_nowait(data)

@alarm_router.get("/alarm/gov_warning/stream", summary="政府管理员告警推送")
async def gov_warning_event_stream(user: User = Depends(get_current_user)):
  if user.user_type != UserType.GOV_ADMIN:
    raise HTTPException(status_code=403, detail="权限不足，非政府管理员")
  queue: asyncio.Queue = asyncio.Queue()
  gov_warning_queues.append(queue)

  async def event_generator():
    try:
      while True:
        msg = await queue.get()
        yield f"data: {msg}\n\n"
    except asyncio.CancelledError:
      pass
    finally:
      gov_warning_queues.remove(queue)

  return StreamingResponse(event_generator(), media_type="text/event-stream")


def broadcast_road_event(event: SecurityEvent):
  """
  对外脚本调用此函数向所有 ROAD_MAINTAINENCER 订阅者广播 WARNING 告警
  """
  payload = {
    "event_type": event.event_type.value,
    "description": event.description,
    "timestamp": event.timestamp,
    "log_level": event.log_level.value,
    "link_username": event.link_username
  }
  data = json.dumps(payload, default=str)
  for q in road_warning_queues:
    q.put_nowait(data)

@alarm_router.get("/alarm/road_warning/stream", summary="道路养护管理员告警推送")
async def road_warning_event_stream(user: User = Depends(get_current_user)):
  if user.user_type != UserType.ROAD_MAINTAINER:
    raise HTTPException(status_code=403, detail="权限不足，非道路养护管理员")
  queue: asyncio.Queue = asyncio.Queue()
  road_warning_queues.append(queue)

  async def event_generator():
    try:
      while True:
        msg = await queue.get()
        yield f"data: {msg}\n\n"
    except asyncio.CancelledError:
      pass
    finally:
      road_warning_queues.remove(queue)

  return StreamingResponse(event_generator(), media_type="text/event-stream")