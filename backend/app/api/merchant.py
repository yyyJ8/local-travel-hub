"""商家后台接口（角色：merchant）

原型口径：商家只能看到**自己名下**门店/酒店的订单与经营数据；
除"维护营业时间与简介"外全部为只读查询，避免引入一批可写接口与校验逻辑。
"""
import logging

from fastapi import APIRouter, Header

from app.api.deps import require_role
from app.core.response import fail, ok
from app.data import store
from app.models.schemas import MerchantProfileUpdate

logger = logging.getLogger("ctrip-prototype")
router = APIRouter(prefix="/api/merchant", tags=["商家后台"])

MERCHANT_ROLES = ("merchant", "admin")  # 管理员可代看，便于演示与排障


@router.get("/summary", summary="M1 我的经营概览（门店/酒店 + 订单统计）")
def summary(authorization: str = Header(default="")):
    user, err = require_role(authorization, MERCHANT_ROLES)
    if err:
        return err
    mid = user.get("merchantId") or ""
    if not mid:
        return fail(message="该商家账号未绑定任何门店或酒店", code=400)
    data = store.merchant_summary(mid)
    data["user"] = store.public_user(user)
    return ok(data)


@router.get("/orders", summary="M2 我的订单（仅自己名下门店/酒店）")
def orders(authorization: str = Header(default="")):
    user, err = require_role(authorization, MERCHANT_ROLES)
    if err:
        return err
    items = store.list_orders_for(user)
    return ok({"total": len(items), "items": items})


@router.put("/profile", summary="M3 维护门店/酒店信息（仅营业时间与简介）")
def update_profile(payload: MerchantProfileUpdate, authorization: str = Header(default="")):
    user, err = require_role(authorization, ("merchant",))
    if err:
        return err
    mid = user.get("merchantId") or ""
    if not mid:
        return fail(message="该商家账号未绑定任何门店或酒店", code=400)
    if not payload.businessHours and not payload.intro:
        return fail(message="请至少填写营业时间或简介中的一项", code=400)
    count = store.update_merchant_profile(mid, payload.businessHours, payload.intro)
    logger.info("[商家维护] 商家=%s 更新了 %s 个对象（仅内存变更）", mid, count)
    return ok({"updated": count, "merchantId": mid})
