import uuid
from datetime import datetime

import PIL.Image
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional

from sqlmodel import Session, select, desc
from sqlalchemy import func

from model.security_event import SecurityEvent, RoadDangerType, EventType, SpoofingDetail, RoadDetail, RoadDanger, \
  LogLevel
from model.user import User, UserType
from util.engine import get_session
from util.log import add_face_spoofing_event, add_unverified_user_event, add_road_safety_event
from util.security import get_current_user

log_router = APIRouter()


@log_router.get("/logs/test", summary="添加日志记录")
def test_add_logs(session: Session = Depends(get_session)):
  """
  测试添加日志记录的接口
  """
  # 这里添加实际的添加日志逻辑，例如向数据库中插入一条日志记录
  add_face_spoofing_event(session, "test_device1", "test_base64", 0.1, 0.2)
  add_unverified_user_event(session, "test_device2", "test_base64")
  add_road_safety_event(session, "test_device3", 1, [(RoadDangerType.CHAP, 0.1)],
                        predicted_image=PIL.Image.open("C:/Users/stanl/Pictures/头像/portrait.jpg"))
  return {"message": "Log entry added successfully"}

@log_router.get("/logs", summary="查询日志记录")
def query_logs(
    log_type: Optional[str] = Query(None, description="事件类型过滤"),
    log_range: Optional[str] = Query(None, description="日志范围过滤，例如：2021-01-01~2021-12-31"),
    limit: int = Query(10, description="查询返回条数，默认返回 10 条"),
    offset: int = Query(0, description="起始条数，默认从第 0 条记录开始"),
    level: Optional[int] = Query(None, description="日志级别过滤"),
    log_username: Optional[str] = Query(None, description="查询关联用户名"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
  """
  根据查询条件返回日志记录，需要认证权限

  参数说明：
  - log_type：允许根据日志类型过滤
  - log_range：允许根据日志时间范围过滤
  - limit：限制返回结果数量，默认为 10
  - offset：指定从哪个位置开始返回结果
  - level: 日志级别过滤，0=INFO, 1=WARNING, 2=ERROR
  - log_username: 查询关联用户名

  示例请求：
  /logs?log_type=ERROR&log_range=2025-07-01~2025-07-31&limit=20&offset=0
  """
  # 这里添加实际的查询逻辑，例如从数据库中根据条件查询
  if user.user_type not in [UserType.SYSADMIN, UserType.GOV_ADMIN, UserType.ROAD_MAINTAINER]:
    raise HTTPException(status_code=403, detail="权限不足，只有管理员可以查询日志")

  stmt = select(SecurityEvent)

  if log_type == "0":
    stmt = stmt.where(SecurityEvent.event_type == EventType.UNVERIFIED_USER)
  elif log_type == "1":
    stmt = stmt.where(SecurityEvent.event_type == EventType.FACE_SPOOFING)
  elif log_type == "2":
    stmt = stmt.where(SecurityEvent.event_type == EventType.ROAD_SAFETY)
  elif log_type == "3":
    stmt = stmt.where(SecurityEvent.event_type == EventType.GENERAL)

  if user.user_type not in [UserType.SYSADMIN]:
    stmt = stmt.where(SecurityEvent.event_type == EventType.ROAD_SAFETY)

  if level == 0:
    stmt = stmt.where(SecurityEvent.log_level == LogLevel.INFO)
  elif level == 1:
    stmt = stmt.where(SecurityEvent.log_level == LogLevel.WARNING)
  elif level == 2:
    stmt = stmt.where(SecurityEvent.log_level == LogLevel.ERROR)

  if log_username:
    stmt.where(SecurityEvent.link_username == log_username)

  if log_range:
    try:
      start_str, end_str = log_range.split("~")
      start_dt = datetime.fromisoformat(start_str)
      end_dt = datetime.fromisoformat(end_str)
    except Exception:
      raise HTTPException(status_code=500, detail="时间范围格式错误，应为YYYY-MM-DD~YYYY-MM-DD")
    stmt = stmt.where(SecurityEvent.timestamp.between(start_dt, end_dt))
    stmt = (stmt
      .order_by(desc(SecurityEvent.timestamp))
      .limit(limit)
      .offset(offset)
    )
  results = session.exec(stmt).all()
  return results

@log_router.get("/log_detail", summary="获取日志类型列表")
def query_log_detail(
    log_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
  """
  获取日志类型列表

  参数说明：
  - log_id：日志 ID，用于查询特定日志的详细信息

  示例请求：
  /logs_detail?log_id=123e4567-e89b-12d3-a456-426614174000
  """
  # 这里添加实际的查询逻辑，例如从数据库中查询所有日志类型
  if user.user_type not in [UserType.SYSADMIN, UserType.GOV_ADMIN, UserType.ROAD_MAINTAINER]:
    raise HTTPException(status_code=403, detail="权限不足，只有管理员可以查询日志详情")

  log = session.get(SecurityEvent, log_id)
  if log.event_type == EventType.FACE_SPOOFING:
    if user.user_type not in [UserType.SYSADMIN]:
      raise HTTPException(status_code=403, detail="权限不足，只有管理员可以查询人脸识别告警详情")
    detail = session.get(SpoofingDetail, log_id)
    return {
      "log" : log,
      "detail": detail
    }
  elif log.event_type == EventType.UNVERIFIED_USER:
    if user.user_type not in [UserType.SYSADMIN]:
      raise HTTPException(status_code=403, detail="权限不足，只有管理员可以查询人脸识别告警详情")
    detail = session.get(SpoofingDetail, log_id)
    return {
      "log": log,
      "detail": detail
    }
  elif log.event_type == EventType.ROAD_SAFETY:
    detail = session.get(RoadDetail, log_id)
    dangers = session.exec(select(RoadDanger).where(RoadDanger.id == log_id)).all()
    return {
      "log": log,
      "detail": detail,
      "dangers": dangers
    }
  return HTTPException(status_code=404, detail="未找到日志详情")

@log_router.get("/log_counts", summary="获取日志条数")
def get_log_count(log_type: Optional[str] = Query(None, description="事件类型过滤"),
                  log_range: Optional[str] = Query(None, description="日志范围过滤，例如：2021-01-01~2021-12-31"),
                  log_username: Optional[str] = Query(None, description="查询关联用户名"),
                  level: Optional[int] = Query(None, description="日志级别过滤，0=INFO, 1=WARNING, 2=ERROR"),
                  session: Session = Depends(get_session),
                  user: User = Depends(get_current_user)):
  """
  获取日志条数
  - 参数说明：
  - log_type：允许根据日志类型过滤
  - log_range：允许根据日志时间范围过滤
  - log_username: 查询关联用户名
  - level: 日志级别过滤，0=INFO, 1=WARNING, 2=ERROR
  """
  if user.user_type not in [UserType.SYSADMIN, UserType.GOV_ADMIN, UserType.ROAD_MAINTAINER]:
    raise HTTPException(status_code=403, detail="权限不足，只有管理员可以查询日志条数")

  stmt = select(func.count()).select_from(SecurityEvent)
  # 根据日志类型过滤
  if log_type == "0":
    stmt = stmt.where(SecurityEvent.event_type == EventType.UNVERIFIED_USER)
  elif log_type == "1":
    stmt = stmt.where(SecurityEvent.event_type == EventType.FACE_SPOOFING)
  elif log_type == "2":
    stmt = stmt.where(SecurityEvent.event_type == EventType.ROAD_SAFETY)
  elif log_type == "3":
    stmt = stmt.where(SecurityEvent.event_type == EventType.GENERAL)
  # 非SYSADMIN仅允许查询ROAD_SAFETY日志
  if user.user_type != UserType.SYSADMIN:
    stmt = stmt.where(SecurityEvent.event_type == EventType.ROAD_SAFETY)

  if level == "0":
      stmt = stmt.where(SecurityEvent.log_level == LogLevel.INFO)
  elif level == "1":
    stmt = stmt.where(SecurityEvent.log_level == LogLevel.WARNING)
  elif level == "2":
    stmt = stmt.where(SecurityEvent.log_level == LogLevel.ERROR)

  if log_username:
    stmt.where(SecurityEvent.link_username == log_username)

  # 根据时间范围过滤
  if log_range:
    try:
      start_str, end_str = log_range.split("~")
      start_dt = datetime.fromisoformat(start_str)
      end_dt = datetime.fromisoformat(end_str)
    except Exception:
      raise HTTPException(status_code=500, detail="时间范围格式错误，应为YYYY-MM-DD~YYYY-MM-DD")
    stmt = stmt.where(SecurityEvent.timestamp.between(start_dt, end_dt))

  log_count = session.execute(stmt).scalar_one()
  return log_count
