"""管理员后台接口（角色：admin）

原型口径：管理员可查看全平台概览、用户列表与全平台订单，并停用/启用账号；
停用账号会**立即失效该用户的所有会话**，被停用账号无法登录。
"""
import logging

from fastapi import APIRouter, Header

from app.api.deps import require_role
from app.core.response import fail, ok
from app.data import store
from app.models.schemas import UserStatusUpdate

logger = logging.getLogger("ctrip-prototype")
router = APIRouter(prefix="/api/admin", tags=["管理员后台"])

ADMIN_ONLY = ("admin",)


@router.get("/overview", summary="D1 平台概览（门店/酒店/用户/订单/会话）")
def overview(authorization: str = Header(default="")):
    user, err = require_role(authorization, ADMIN_ONLY)
    if err:
        return err
    return ok(store.admin_overview())


@router.get("/users", summary="D2 用户列表（含角色与状态）")
def users(authorization: str = Header(default="")):
    user, err = require_role(authorization, ADMIN_ONLY)
    if err:
        return err
    items = store.list_users()
    return ok({"total": len(items), "items": items})


@router.post("/users/{user_id}/status", summary="D3 停用 / 启用账号（停用即失效其全部会话）")
def set_status(user_id: str, payload: UserStatusUpdate, authorization: str = Header(default="")):
    user, err = require_role(authorization, ADMIN_ONLY)
    if err:
        return err
    if payload.status not in ("正常", "停用"):
        return fail(message="status 只能为 正常 或 停用", code=400)
    if user_id == user["id"] and payload.status != "正常":
        return fail(message="不能停用当前登录的管理员账号", code=400)
    target = store.set_user_status(user_id, payload.status)
    if not target:
        return fail(message=f"用户不存在：{user_id}", code=404)
    logger.info("[账号状态] %s（%s）-> %s（操作人 %s）",
                target["username"], target["id"], payload.status, user["username"])
    return ok(store.public_user(target))


@router.get("/orders", summary="D4 全平台订单")
def orders(authorization: str = Header(default="")):
    user, err = require_role(authorization, ADMIN_ONLY)
    if err:
        return err
    items = store.list_orders()
    return ok({"total": len(items), "items": items})
