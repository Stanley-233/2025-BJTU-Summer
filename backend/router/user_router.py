import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from model.security_event import SecurityEvent
from model.user import User, UserType
from util.engine import get_session
from util.security import get_current_user

user_router = APIRouter()

@user_router.get("/users/", summary="获取用户列表", response_model=List[User])
def get_users(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """
    获取所有用户
    """
    if user.user_type != UserType.SYSADMIN:
        raise HTTPException(status_code=403, detail="权限不足，只有系统管理员可以获取用户列表")

    users = session.exec(select(User)).all()
    return users

@user_router.put("/user_change_permission", summary="修改用户权限")
def change_user_permission(
    username: str,
    new_user_type: UserType,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    修改用户权限

    参数说明：
    - username: 要修改权限的用户 ID
    - new_user_type: 新的用户类型，必须是 UserType 枚举中的值

    示例请求：
    PUT /user_change_permission?username=mzf&new_user_type=SYSADMIN
    """
    if current_user.user_type != UserType.SYSADMIN:
        raise HTTPException(status_code=403, detail="权限不足，只有系统管理员可以修改用户权限")

    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.user_type = new_user_type
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": "用户权限修改成功", "user": user}


@user_router.get("/users/get_logs", summary="获取用户关联日志事件", response_model=List[SecurityEvent])
def get_user_logs(
    username: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户关联的日志事件

    参数说明：
    - username: 用户 ID

    示例请求：
    GET /users/get_logs?username=mzf
    """
    if current_user.user_type not in [UserType.SYSADMIN, UserType.GOV_ADMIN]:
        raise HTTPException(status_code=403, detail="权限不足，只有管理员可以获取用户日志")

    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    logs = session.exec(select(SecurityEvent).where(SecurityEvent.link_username == username)).all()
    return logs
