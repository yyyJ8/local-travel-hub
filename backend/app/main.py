"""极简后端服务入口（课程演示原型）

职责：
1. 创建 FastAPI 实例，开启 CORS 供前端本地调用；
2. 挂载各业务模块路由（首页/搜索/门店/酒店/订单）；
3. 提供 /api/health 探针接口，用于前后端联调自检。

原型限制：数据全部保存在内存集合中，服务重启后新增订单与状态变更丢失。
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, home, hotels, orders, search, shops
from app.core.response import ok
from app.data import store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ctrip-prototype")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 68)
    logger.info("本地生活旅行综合演示原型系统 - 后端服务启动（内存数据源，不持久化）")
    logger.info("接口文档: http://127.0.0.1:8000/docs")
    logger.info("=" * 68)
    yield
    logger.info("后端服务已停止：内存中的新增订单与状态变更已丢失（原型预期行为）")


app = FastAPI(
    title="本地生活旅行综合演示原型系统 - 后端服务",
    description=(
        "《软件架构与应用开发实践》课程实训原型：仿大众点评 + 携程。\n\n"
        "- 架构：前后端分离，极简后端骨架\n"
        "- 数据源：内存集合（不落库，重启丢失）\n"
        "- 接口：以查询接口为主，写接口仅模拟下单与模拟取消预约"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# 原型本地演示：允许 Vite 开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["系统"], summary="健康探针（前后端联调自检）")
def health():
    return ok(
        {
            "service": "ctrip-dianping-prototype-backend",
            "status": "running",
            "dataSource": "in-memory",
            "persistence": False,
        }
    )


@app.get("/api/meta/stats", tags=["系统"], summary="内存数据规模自检（阶段验收用）")
def meta_stats():
    """返回各内存集合的规模，用于验证是否满足原型数据规模下限。"""
    return ok(store.stats())


@app.get("/api/meta/cities", tags=["系统"], summary="可选城市列表（供城市切换器渲染）")
def meta_cities():
    return ok(store.list_cities())


# ---- 业务模块路由（前后端分离：前端通过 /api/** 调用）----
app.include_router(home.router)     # I1 首页推荐
app.include_router(search.router)   # I2 关键词搜索
app.include_router(shops.router)    # I3 门店列表 / I4 门店详情
app.include_router(hotels.router)   # I5 酒店列表 / I6 酒店详情
app.include_router(orders.router)   # I7 模拟下单 / I8 订单列表 / I9 订单详情 / I10 模拟取消
app.include_router(auth.router)     # A1 注册 / A2 登录 / A3 注销 / A4 当前用户
