"""I7 模拟预约下单 / I8 我的订单 / I9 订单详情 / I10 模拟取消预约

登录与权限（step2 起）：
- 四个接口均需登录：请求头 `Authorization: Bearer <token>`；
- 下单写入订单归属（order.userId）；
- 列表按角色过滤：普通用户仅自己的订单、商家仅自己名下门店/酒店的订单、管理员全部；
- 详情与取消做**归属校验**，越权访问返回 403。

原型约束：订单只存于内存集合，服务重启后新增订单与取消状态全部丢失。
"""
import logging

from fastapi import APIRouter, Header

from app.api.deps import require_login
from app.core.response import fail, ok
from app.data import store
from app.models.schemas import OrderCreateRequest

logger = logging.getLogger("ctrip-prototype")
router = APIRouter(prefix="/api/orders", tags=["预约下单与个人中心"])


@router.post("", summary="I7 模拟预约下单（需登录，订单归属当前用户）")
def create_order(payload: OrderCreateRequest, authorization: str = Header(default="")):
    """模拟提交预约：校验套餐/房型 → 控制台打印 → 追加至内存集合（记录归属用户）。"""
    user, err = require_login(authorization)
    if err:
        return err
    if payload.type not in ("shop", "hotel"):
        return fail(message="参数 type 只能为 shop 或 hotel", code=400)

    logger.info(
        "[模拟下单] 用户=%s(%s) 类型=%s 对象=%s 项目=%s 姓名=%s 手机号=%s 预约时间=%s 退房时间=%s 数量=%s",
        user["username"], user["id"], payload.type, payload.targetId, payload.itemId,
        payload.name, payload.phone, payload.bookTime, payload.checkOut or "-", payload.count,
    )

    order = store.create_order(payload, user_id=user["id"])
    if not order:
        return fail(message="门店/酒店或套餐/房型不存在，无法下单", code=404)

    logger.info("[模拟下单] 订单已写入内存集合：%s 金额=¥%s（服务重启后丢失）", order["orderNo"], order["amount"])
    return ok(order)


@router.get("", summary="I8 我的订单列表（按角色过滤归属）")
def list_orders(authorization: str = Header(default="")):
    """普通用户看自己的订单；商家看自己名下门店/酒店的订单；管理员看全部。"""
    user, err = require_login(authorization)
    if err:
        return err
    items = store.list_orders_for(user)
    return ok({"total": len(items), "items": items, "role": user["role"]})


@router.get("/{order_no}", summary="I9 订单详情（含归属校验）")
def order_detail(order_no: str, authorization: str = Header(default="")):
    user, err = require_login(authorization)
    if err:
        return err
    order = store.get_order(order_no)
    if not order:
        return fail(message=f"订单不存在：{order_no}", code=404)
    if not store.can_access_order(order, user):
        logger.info("[越权拦截] 用户=%s 试图查看订单 %s", user["username"], order_no)
        return fail(message="无权查看该订单（该订单不属于当前账号）", code=403)
    return ok(order)


@router.post("/{order_no}/cancel", summary="I10 模拟取消预约（含归属校验）")
def cancel_order(order_no: str, authorization: str = Header(default="")):
    """模拟取消预约：仅修改内存集合中订单的状态字段，给出界面反馈。"""
    user, err = require_login(authorization)
    if err:
        return err
    order = store.get_order(order_no)
    if not order:
        return fail(message=f"订单不存在：{order_no}", code=404)
    if not store.can_access_order(order, user):
        logger.info("[越权拦截] 用户=%s 试图取消订单 %s", user["username"], order_no)
        return fail(message="无权取消该订单（该订单不属于当前账号）", code=403)
    store.cancel_order(order_no)
    logger.info("[模拟取消] 订单 %s 状态已改为「已取消」（仅内存变更，重启后丢失）", order_no)
    return ok(order)
