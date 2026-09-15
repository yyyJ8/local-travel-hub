"""I5 酒店列表接口、I6 酒店详情接口（旅行住宿模块）"""
from typing import List, Optional

from fastapi import APIRouter, Query

from app.core.response import fail, ok
from app.data import store

router = APIRouter(prefix="/api/hotels", tags=["旅行住宿"])


@router.get("/facilities", summary="酒店设施选项（供筛选面板渲染）")
def facilities():
    """返回内存数据中出现过的全部设施标签，供前端筛选面板动态渲染。"""
    return ok(store.list_facilities())


@router.get("", summary="I5 酒店列表接口（支持筛选、日历区间与排序）")
def list_hotels(
    keyword: str = Query(default="", description="关键词，匹配酒店名/标签/区域"),
    city: str = Query(default="", description="城市，如 成都"),
    minPrice: Optional[float] = Query(default=None, description="最低房价（元/晚）"),
    maxPrice: Optional[float] = Query(default=None, description="最高房价（元/晚）"),
    star: Optional[int] = Query(default=None, description="星级：3 / 4 / 5"),
    facilities: Optional[List[str]] = Query(default=None, description="设施（可多选，需同时满足）"),
    checkIn: str = Query(default="", description="入住日期 YYYY-MM-DD（来自日历选择）"),
    checkOut: str = Query(default="", description="退房日期 YYYY-MM-DD（来自日历选择）"),
    sortBy: str = Query(default="popularity", description="排序：popularity 好评优先 / priceAsc 价格优先 / priceDesc 价格降序 / rating 评分优先"),
):
    """酒店列表查询。返回列表的同时回传日历计算出的入住晚数，供前端联动总价。"""
    items = store.list_hotels(
        keyword=keyword,
        city=city,
        min_price=minPrice,
        max_price=maxPrice,
        star=star,
        facilities=facilities,
        sort_by=sortBy,
    )
    nights = store.nights_between(checkIn, checkOut) if (checkIn and checkOut) else 0
    return ok(
        {
            "total": len(items),
            "nights": nights,
            "checkIn": checkIn,
            "checkOut": checkOut,
            "items": items,
        }
    )


@router.get("/{hotel_id}", summary="I6 酒店详情接口")
def hotel_detail(hotel_id: str):
    """酒店详情：图文信息 + 不同房型房价与配套服务 + 酒店评价。"""
    hotel = store.get_hotel(hotel_id)
    if not hotel:
        return fail(message=f"酒店不存在：{hotel_id}", code=404)
    return ok(hotel)
