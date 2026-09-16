"""接口公共依赖：登录用户解析与角色校验

统一返回风格：未登录 → code=401，角色不足 → code=403（HTTP 状态仍为 200，与现有统一响应结构一致）。
"""
from fastapi import Header

from app.core.auth import parse_bearer
from app.core.response import fail
from app.data import store


def current_user(authorization: str = Header(default="", description="Bearer <token>")):
    """解析令牌对应的用户（未登录返回 None）。"""
    return store.get_user_by_token(parse_bearer(authorization))


def require_login(authorization: str):
    """要求已登录。返回 (user, error)，error 非空时应直接返回给前端。"""
    user = current_user(authorization)
    if not user:
        return None, fail(message="请先登录后再操作", code=401)
    return user, None


def require_role(authorization: str, roles):
    """要求指定角色（roles 为角色集合）。返回 (user, error)。"""
    user, err = require_login(authorization)
    if err:
        return None, err
    if user.get("role") not in roles:
        return None, fail(message="当前账号无权访问该功能", code=403)
    return user, None
