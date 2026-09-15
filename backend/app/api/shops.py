"""I3 门店列表接口、I4 门店详情接口（本地生活模块）"""
from typing import Optional

from fastapi import APIRouter, Query

from app.core.response import fail, ok
from app.data import store

router = APIRouter(prefix="/api/shops", tags=["本地生活"])


@router.get("", summary="I3 门店列表接口（支持筛选与排序）")
def list_shops(
    keyword: str = Query(default="", description="关键词，匹配门店名/标签/品类/区域"),
    category: str = Query(default="", description="品类：美食 / 休闲娱乐"),
    minRating: Optional[float] = Query(default=None, description="最低评分，如 4.5"),
    maxPrice: Optional[int] = Query(default=None, description="人均价格上限，如 100"),
    sortBy: str = Query(default="popularity", description="排序：popularity 人气优先 / rating 评分优先 / priceAsc 价格升序 / priceDesc 价格降序"),
):
    """门店列表查询。筛选与排序均在后端内存集合上完成。"""
    items = store.list_shops(
        keyword=keyword,
        category=category,
        min_rating=minRating,
        max_price=maxPrice,
        sort_by=sortBy,
    )
    return ok({"total": len(items), "items": items})


@router.get("/{shop_id}", summary="I4 门店详情接口")
def shop_detail(shop_id: str):
    """门店详情：基础信息 + 营业时间 + 地址 + 团购套餐 + 用户评论。"""
    shop = store.get_shop(shop_id)
    if not shop:
        return fail(message=f"门店不存在：{shop_id}", code=404)
    return ok(shop)
