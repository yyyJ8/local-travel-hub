"""I1 首页推荐接口"""
from fastapi import APIRouter

from app.core.response import ok
from app.data import store

router = APIRouter(prefix="/api/home", tags=["首页"])


@router.get("/recommend", summary="I1 首页推荐接口")
def recommend():
    """返回首页所需的轮播推荐位、业务分类入口、推荐门店与推荐酒店。

    - 推荐门店 / 酒店按人气值（popularity）倒序取前 4 条；
    - 业务分类入口数据同时供首页分类导航使用。
    """
    return ok(store.home_recommend())
