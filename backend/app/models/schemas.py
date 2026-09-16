"""领域对象模型（Pydantic）

用途：
1. 作为后端接口的请求体校验与数据结构说明，自动呈现于 /docs；
2. 作为报告「领域对象模型」章节的代码级映射（文档中仍按业务语义描述属性与关系）。

对象关系：
    门店(Shop)   1 ── N 团购套餐(Package)
    门店(Shop)   1 ── N 评论(Comment)
    酒店(Hotel)  1 ── N 房型(RoomType)
    酒店(Hotel)  1 ── N 酒店评价(HotelReview)
    订单(Order)  N ── 1 门店或酒店；N ── 1 套餐或房型
"""
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------- 公共 / 首页 ----------------------------
class Banner(BaseModel):
    """首页轮播推荐位"""
    id: str
    title: str
    subtitle: str
    colorFrom: str = Field(description="渐变起始色")
    colorTo: str = Field(description="渐变结束色")
    image: str = Field(default="", description="轮播配图路径（本地静态资源）")
    targetType: str = Field(description="跳转类型：shop / hotel")
    targetId: str = Field(default="", description="跳转目标 ID，为空表示跳列表页")


class Category(BaseModel):
    """业务分类入口"""
    id: str
    name: str
    icon: str = Field(description="Element Plus 图标名")
    color: str
    targetType: str
    targetCategory: str = Field(default="", description="跳转列表页时使用的品类过滤值")


# ---------------------------- 本地生活 ----------------------------
class Package(BaseModel):
    """团购套餐"""
    id: str
    name: str
    price: float
    originalPrice: float
    sold: int = Field(description="已售份数")
    desc: str


class Comment(BaseModel):
    """门店用户评论"""
    id: str
    user: str
    avatarColor: str
    rating: float
    content: str
    date: str


class Shop(BaseModel):
    """本地生活门店（美食 / 休闲娱乐）"""
    id: str
    name: str
    city: str = Field(default="成都", description="所属城市：成都 / 重庆 / 西安")
    category: str = Field(description="一级品类：美食 / 休闲娱乐")
    subCategory: str = Field(description="二级品类：火锅 / 川菜 / SPA / 密室 ...")
    rating: float
    reviewCount: int
    avgPrice: int = Field(description="人均消费（元）")
    popularity: int = Field(description="人气值，用于人气排序")
    tags: List[str]
    district: str
    address: str
    businessHours: str
    phone: str
    coverColor: str = Field(description="封面占位图主色（图片加载失败时的回退底色）")
    coverTag: str = Field(description="封面占位图文字标签")
    cover: str = Field(default="", description="封面图路径（本地静态资源）")
    gallery: List[str] = Field(default=[], description="详情页图库（本地静态资源）")
    packages: List[Package] = []
    comments: List[Comment] = []


# ---------------------------- 旅行住宿 ----------------------------
class RoomType(BaseModel):
    """酒店房型"""
    id: str
    name: str
    area: int = Field(description="面积（㎡）")
    bedType: str
    breakfast: str
    window: str = Field(description="有无窗")
    cancelPolicy: str
    price: float
    originalPrice: float
    remain: int = Field(description="剩余房量（模拟）")


class HotelReview(BaseModel):
    """酒店评价"""
    id: str
    user: str
    avatarColor: str
    rating: float
    content: str
    date: str
    roomType: str


class Hotel(BaseModel):
    """酒店"""
    id: str
    name: str
    city: str
    star: int = Field(description="星级 3~5")
    rating: float = Field(description="好评评分")
    reviewCount: int
    minPrice: float = Field(description="最低房价（元/晚）")
    popularity: int = Field(description="好评数，用于好评优先排序")
    district: str
    address: str
    facilities: List[str]
    tags: List[str]
    intro: str = Field(description="酒店图文介绍文字")
    coverColor: str
    coverTag: str
    cover: str = Field(default="", description="封面图路径（本地静态资源）")
    gallery: List[str] = Field(default=[], description="酒店图库（本地静态资源）")
    rooms: List[RoomType] = []
    reviews: List[HotelReview] = []


# ---------------------------- 订单 ----------------------------
class OrderCreateRequest(BaseModel):
    """模拟预约下单请求体（原型不做真实校验，仅必填约束）"""
    type: str = Field(description="预约对象类型：shop（门店套餐）/ hotel（酒店房型）")
    targetId: str = Field(description="门店或酒店 ID")
    itemId: str = Field(description="套餐或房型 ID")
    name: str = Field(description="预约人姓名")
    phone: str = Field(description="预约人手机号")
    bookTime: str = Field(description="预约/入住时间，如 2026-03-20")
    checkOut: str = Field(default="", description="酒店退房时间，门店预约时为空")
    count: int = Field(default=1, description="份数 / 房间数")


class Order(BaseModel):
    """模拟预约订单（仅存于内存集合）"""
    orderNo: str
    type: str
    targetId: str
    targetName: str
    itemId: str
    itemName: str
    name: str
    phone: str
    bookTime: str
    checkOut: str = ""
    nights: int = 0
    count: int = 1
    amount: float
    status: str = Field(description="订单状态：待使用 / 已取消")
    createdAt: str
    coverColor: str = ""
    coverTag: str = ""


class OrderListResponse(BaseModel):
    """订单列表返回结构说明"""
    total: int
    items: List[Order]


# ---------------------------- 账号与会话（演示级） ----------------------------
class User(BaseModel):
    """用户（内存用户表）

    原型说明：password 为明文，仅用于课程演示；生产版本必须改为加盐哈希（如 bcrypt）。
    """
    id: str
    username: str
    password: str = Field(description="明文密码，仅演示用")
    role: str = Field(description="角色：user 普通用户 / merchant 商家 / admin 管理员")
    nickname: str = ""
    phone: str = ""
    avatarColor: str = "#ff6633"
    status: str = Field(default="正常", description="账号状态：正常 / 停用")
    createdAt: str = ""
    merchantId: str = Field(default="", description="商家绑定的门店或酒店 ID，其他角色为空")


class UserPublic(BaseModel):
    """对外返回的用户信息（**不含密码**）"""
    id: str
    username: str
    role: str
    nickname: str = ""
    phone: str = ""
    avatarColor: str = "#ff6633"
    status: str = "正常"
    merchantId: str = ""


class RegisterRequest(BaseModel):
    """注册请求（仅开放普通用户角色）"""
    username: str = Field(description="用户名，3~20 位，不可重复")
    password: str = Field(description="密码，至少 6 位（明文存储，仅演示）")
    nickname: str = Field(default="", description="昵称，留空则默认与用户名相同")
    phone: str = Field(default="", description="手机号，可留空")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应：令牌 + 用户信息（前端存 token，后续请求带在 Authorization 头）"""
    token: str
    user: UserPublic


class Session(BaseModel):
    """会话（内存字典，服务重启即全部失效）"""
    token: str
    userId: str
    createdAt: str
