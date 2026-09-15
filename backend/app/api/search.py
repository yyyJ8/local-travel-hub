"""I2 关键词搜索接口"""
from fastapi import APIRouter, Query

from app.core.response import ok
from app.data import store

router = APIRouter(prefix="/api/search", tags=["搜索"])


@router.get("", summary="I2 关键词搜索接口")
def search(keyword: str = Query(default="", description="搜索关键词，匹配门店名/标签/品类与酒店名/标签/区域")):
    """按关键词同时检索门店与酒店，返回两类结果，供搜索结果页分区展示。"""
    data = store.search(keyword)
    data["totalShops"] = len(data["shops"])
    data["totalHotels"] = len(data["hotels"])
    data["total"] = data["totalShops"] + data["totalHotels"]
    return ok(data)
