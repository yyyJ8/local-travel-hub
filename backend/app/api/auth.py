"""认证接口：注册 / 登录 / 注销 / 当前用户（演示级账号体系）

原型口径（答辩需主动说明）：
1. 令牌为随机字符串，会话保存在内存字典，**后端重启后全部失效，需要重新登录**；
2. **注册仅开放「普通用户」角色**，商家与管理员通过预置账号提供；
3. 口令**明文比对**，不做加盐哈希、不做有效期与刷新 —— 仅课程演示，生产必须替换。
"""
import logging

from fastapi import APIRouter, Header

from app.core.auth import parse_bearer
from app.core.response import fail, ok
from app.data import store
from app.models.schemas import LoginRequest, RegisterRequest

logger = logging.getLogger("ctrip-prototype")
router = APIRouter(prefix="/api/auth", tags=["账号与登录"])


def current_user(authorization: str) -> dict:
    """从 Authorization 头解析当前登录用户（未登录返回 None）。

    供各业务接口复用（step2 起订单/商家/管理接口按当前用户过滤与鉴权）。
    """
    return store.get_user_by_token(parse_bearer(authorization))


@router.post("/register", summary="A1 用户注册（仅普通用户角色）")
def register(payload: RegisterRequest):
    user, err = store.register_user(
        payload.username, payload.password, payload.nickname, payload.phone
    )
    if err:
        return fail(message=err, code=409 if "已存在" in err else 400)
    logger.info("[注册] 新用户 %s（%s），角色固定为 user", user["username"], user["id"])
    token = store.create_session(user["id"])  # 注册后直接登录，省去再登录一步
    return ok({"token": token, "user": store.public_user(user)})


@router.post("/login", summary="A2 登录（返回令牌与用户信息）")
def login(payload: LoginRequest):
    user, err = store.authenticate(payload.username, payload.password)
    if err:
        return fail(message=err, code=401)
    token = store.create_session(user["id"])
    logger.info("[登录] %s 角色=%s 令牌=%s...", user["username"], user["role"], token[:8])
    return ok({"token": token, "user": store.public_user(user)})


@router.post("/logout", summary="A3 注销（删除内存会话）")
def logout(authorization: str = Header(default="", description="Bearer <token>")):
    token = parse_bearer(authorization)
    user = store.get_user_by_token(token)
    if not user:
        return fail(message="未登录或会话已失效", code=401)
    store.delete_session(token)
    logger.info("[注销] %s 已退出登录", user["username"])
    return ok({"message": "已退出登录"})


@router.get("/me", summary="A4 当前登录用户（前端刷新页面时恢复登录态）")
def me(authorization: str = Header(default="", description="Bearer <token>")):
    user = current_user(authorization)
    if not user:
        return fail(message="未登录或会话已失效", code=401)
    return ok(store.public_user(user))
