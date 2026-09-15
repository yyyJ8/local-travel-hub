"""I7 模拟预约下单接口、I8 订单列表、I9 订单详情、I10 模拟取消预约

原型约束（与报告口径一致）：
- 下单接口接收到预约请求后，将订单对象**追加至后端内存集合**，仅当前服务运行期间可查询；
- 后端服务重启后，新增订单与取消状态全部丢失，不持久化；
- 不做真实支付、消息通知与服务端业务校验（仅做对象存在性判断）。
"""
import logging

from fastapi import APIRouter

from app.core.response import fail, ok
from app.data import store
from app.models.schemas import OrderCreateRequest

logger = logging.getLogger("ctrip-prototype")
router = APIRouter(prefix="/api/orders", tags=["预约下单与个人中心"])


@router.post("", summary="I7 模拟预约下单接口")
def create_order(payload: OrderCreateRequest):
    """模拟提交预约：接收请求 → 控制台打印 → 追加至内存集合 → 返回订单号。"""
    if payload.type not in ("shop", "hotel"):
        return fail(message="参数 type 只能为 shop 或 hotel", code=400)

    logger.info(
        "[模拟下单] 类型=%s 对象=%s 项目=%s 姓名=%s 手机号=%s 预约时间=%s 退房时间=%s 数量=%s",
        payload.type, payload.targetId, payload.itemId, payload.name,
        payload.phone, payload.bookTime, payload.checkOut or "-", payload.count,
    )

    order = store.create_order(payload)
    if not order:
        return fail(message="门店/酒店或套餐/房型不存在，无法下单", code=404)

    logger.info("[模拟下单] 订单已写入内存集合：%s 金额=¥%s（服务重启后丢失）", order["orderNo"], order["amount"])
    return ok(order)


@router.get("", summary="I8 查询内存模拟订单列表接口")
def list_orders():
    """返回内存集合中的全部订单（原型无登录注册，不做用户维度过滤）。"""
    items = store.list_orders()
    return ok({"total": len(items), "items": items})


@router.get("/{order_no}", summary="I9 订单详情接口")
def order_detail(order_no: str):
    order = store.get_order(order_no)
    if not order:
        return fail(message=f"订单不存在：{order_no}", code=404)
    return ok(order)


@router.post("/{order_no}/cancel", summary="I10 模拟取消预约接口")
def cancel_order(order_no: str):
    """模拟取消预约：仅修改内存集合中订单的状态字段，给出界面反馈。"""
    order = store.cancel_order(order_no)
    if not order:
        return fail(message=f"订单不存在：{order_no}", code=404)
    logger.info("[模拟取消] 订单 %s 状态已改为「已取消」（仅内存变更，重启后丢失）", order_no)
    return ok(order)
