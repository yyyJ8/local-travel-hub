"""内存集合与数据访问层（store）

架构说明：
- 本模块是原型阶段的「伪数据访问层」，用 Python 列表模拟数据库表；
- 所有筛选、排序逻辑集中在此，API 层只负责参数接收与响应封装（分层清晰，便于生产版本替换为真实 DAO）；
- 订单集合在服务启动时载入预置数据，运行期间通过 append / cancel 变更，**服务重启即恢复到初始状态**。
"""
from datetime import datetime
from itertools import count
from typing import Dict, List, Optional

from app.core.auth import new_token
from app.data.mock_data import BANNERS, CATEGORIES, HOTELS, PRESET_ORDERS, SHOPS, USERS

# ---------------------------------------------------------------- 内存集合（模拟数据表）
_shops: List[Dict] = [dict(item) for item in SHOPS]
_hotels: List[Dict] = [dict(item) for item in HOTELS]
_orders: List[Dict] = [dict(item) for item in PRESET_ORDERS]

_order_seq = count(2001)  # 订单号流水（运行期自增，重启后重置）


# ---------------------------------------------------------------- 查询：首页
def home_recommend() -> Dict:
    """首页推荐数据：轮播 + 分类入口 + 热门门店 + 热门酒店。"""
    hot_shops = sorted(_shops, key=lambda s: s["popularity"], reverse=True)[:4]
    hot_hotels = sorted(_hotels, key=lambda h: h["popularity"], reverse=True)[:4]
    return {
        "banners": BANNERS,
        "categories": CATEGORIES,
        "shops": [_brief_shop(s) for s in hot_shops],
        "hotels": [_brief_hotel(h) for h in hot_hotels],
    }


# ---------------------------------------------------------------- 查询：门店
def _brief_shop(shop: Dict) -> Dict:
    """列表页字段裁剪：不返回套餐与评论明细。"""
    return {
        "id": shop["id"],
        "name": shop["name"],
        "city": shop["city"],
        "category": shop["category"],
        "subCategory": shop["subCategory"],
        "rating": shop["rating"],
        "reviewCount": shop["reviewCount"],
        "avgPrice": shop["avgPrice"],
        "tags": shop["tags"],
        "district": shop["district"],
        "address": shop["address"],
        "coverColor": shop["coverColor"],
        "coverTag": shop["coverTag"],
        "cover": shop.get("cover", ""),
        "packageCount": len(shop["packages"]),
    }


def list_shops(
    keyword: str = "",
    city: str = "",
    category: str = "",
    min_rating: Optional[float] = None,
    max_price: Optional[int] = None,
    sort_by: str = "popularity",
) -> List[Dict]:
    """门店列表：支持关键词、城市、品类、评分、人均价格筛选与人气/评分/价格排序。"""
    result = list(_shops)

    if keyword:
        kw = keyword.strip().lower()
        result = [
            s
            for s in result
            if kw in s["name"].lower()
            or any(kw in t.lower() for t in s["tags"])
            or kw in s["subCategory"].lower()
            or kw in s["district"].lower()
        ]
    if city:
        result = [s for s in result if s["city"] == city]
    if category:
        result = [s for s in result if s["category"] == category]
    if min_rating is not None:
        result = [s for s in result if s["rating"] >= min_rating]
    if max_price is not None:
        result = [s for s in result if s["avgPrice"] <= max_price]

    if sort_by == "rating":
        result.sort(key=lambda s: (s["rating"], s["reviewCount"]), reverse=True)
    elif sort_by == "priceAsc":
        result.sort(key=lambda s: s["avgPrice"])
    elif sort_by == "priceDesc":
        result.sort(key=lambda s: s["avgPrice"], reverse=True)
    else:  # popularity：人气优先（默认）
        result.sort(key=lambda s: s["popularity"], reverse=True)

    return [_brief_shop(s) for s in result]


def get_shop(shop_id: str) -> Optional[Dict]:
    """门店详情：包含团购套餐与用户评论。"""
    for shop in _shops:
        if shop["id"] == shop_id:
            return shop
    return None


# ---------------------------------------------------------------- 查询：酒店
def _brief_hotel(hotel: Dict) -> Dict:
    """列表页字段裁剪：不返回房型与评价明细。"""
    return {
        "id": hotel["id"],
        "name": hotel["name"],
        "city": hotel["city"],
        "star": hotel["star"],
        "rating": hotel["rating"],
        "reviewCount": hotel["reviewCount"],
        "minPrice": hotel["minPrice"],
        "district": hotel["district"],
        "address": hotel["address"],
        "facilities": hotel["facilities"],
        "tags": hotel["tags"],
        "coverColor": hotel["coverColor"],
        "coverTag": hotel["coverTag"],
        "cover": hotel.get("cover", ""),
        "roomCount": len(hotel["rooms"]),
    }


def list_hotels(
    keyword: str = "",
    city: str = "",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    star: Optional[int] = None,
    facilities: Optional[List[str]] = None,
    sort_by: str = "popularity",
) -> List[Dict]:
    """酒店列表：支持关键词、城市、价格、星级、设施筛选与价格/好评排序。"""
    result = list(_hotels)

    if keyword:
        kw = keyword.strip().lower()
        result = [
            h
            for h in result
            if kw in h["name"].lower()
            or any(kw in t.lower() for t in h["tags"])
            or kw in h["district"].lower()
        ]
    if city:
        result = [h for h in result if h["city"] == city]
    if min_price is not None:
        result = [h for h in result if h["minPrice"] >= min_price]
    if max_price is not None:
        result = [h for h in result if h["minPrice"] <= max_price]
    if star is not None:
        result = [h for h in result if h["star"] == star]
    if facilities:
        result = [h for h in result if all(f in h["facilities"] for f in facilities)]

    if sort_by == "priceAsc":
        result.sort(key=lambda h: h["minPrice"])
    elif sort_by == "priceDesc":
        result.sort(key=lambda h: h["minPrice"], reverse=True)
    elif sort_by == "rating":
        result.sort(key=lambda h: (h["rating"], h["reviewCount"]), reverse=True)
    else:  # popularity：好评优先（默认）
        result.sort(key=lambda h: h["popularity"], reverse=True)

    return [_brief_hotel(h) for h in result]


def get_hotel(hotel_id: str) -> Optional[Dict]:
    """酒店详情：包含房型与酒店评价。"""
    for hotel in _hotels:
        if hotel["id"] == hotel_id:
            return hotel
    return None


def list_facilities() -> List[str]:
    """全部可选设施（供前端筛选面板渲染）。"""
    pool: List[str] = []
    for hotel in _hotels:
        for fac in hotel["facilities"]:
            if fac not in pool:
                pool.append(fac)
    return pool


# ---------------------------------------------------------------- 查询：全局搜索
def list_cities() -> List[str]:
    """全部可选城市（门店与酒店共同覆盖），供前端城市切换器渲染。"""
    cities: List[str] = []
    for item in _shops + _hotels:
        if item["city"] not in cities:
            cities.append(item["city"])
    return cities


def search(keyword: str) -> Dict:
    """关键词搜索：同时匹配门店与酒店。"""
    return {
        "keyword": keyword,
        "shops": list_shops(keyword=keyword),
        "hotels": list_hotels(keyword=keyword),
    }


# ---------------------------------------------------------------- 订单：内存集合读 / 写
def nights_between(check_in: str, check_out: str) -> int:
    """计算入住晚数；同一天或格式非法时按 1 晚处理。"""
    try:
        d1 = datetime.strptime(check_in, "%Y-%m-%d")
        d2 = datetime.strptime(check_out, "%Y-%m-%d")
        delta = (d2 - d1).days
        return delta if delta > 0 else 1
    except (ValueError, TypeError):
        return 1


def list_orders() -> List[Dict]:
    """订单列表：原型无登录，返回内存集合中全部订单（按创建时间倒序）。"""
    return sorted(_orders, key=lambda o: o["createdAt"], reverse=True)


def get_order(order_no: str) -> Optional[Dict]:
    for order in _orders:
        if order["orderNo"] == order_no:
            return order
    return None


def _next_order_no() -> str:
    return "ORD" + datetime.now().strftime("%Y%m%d") + str(next(_order_seq))


def create_order(payload, user_id: str = "") -> Optional[Dict]:
    """模拟下单：校验套餐/房型存在后，将订单对象追加至内存集合。

    user_id：下单用户 ID（登录后传入），用于订单归属与个人中心过滤。
    返回 None 表示门店/酒店或套餐/房型不存在（原型仅做存在性判断，不做真实业务校验）。
    """
    target_type = payload.type
    count_ = max(1, payload.count or 1)

    if target_type == "shop":
        target = get_shop(payload.targetId)
        if not target:
            return None
        item = next((p for p in target["packages"] if p["id"] == payload.itemId), None)
        if not item:
            return None
        nights = 0
        amount = float(item["price"]) * count_
        check_out = ""
    else:
        target = get_hotel(payload.targetId)
        if not target:
            return None
        item = next((r for r in target["rooms"] if r["id"] == payload.itemId), None)
        if not item:
            return None
        check_out = payload.checkOut or payload.bookTime
        nights = nights_between(payload.bookTime, check_out)
        amount = float(item["price"]) * count_ * nights

    order = {
        "orderNo": _next_order_no(),
        "userId": user_id,  # ★ 订单归属：个人中心按此字段过滤
        "type": target_type,
        "targetId": target["id"],
        "targetName": target["name"],
        "itemId": item["id"],
        "itemName": item["name"],
        "name": payload.name,
        "phone": payload.phone,
        "bookTime": payload.bookTime,
        "checkOut": check_out,
        "nights": nights,
        "count": count_,
        "amount": round(amount, 2),
        "status": "待使用",
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "coverColor": target["coverColor"],
        "coverTag": target["coverTag"],
        "cover": target.get("cover", ""),
    }
    _orders.append(order)  # ★ 追加至内存集合：仅当前服务运行期间可查询
    return order


def cancel_order(order_no: str) -> Optional[Dict]:
    """模拟取消预约：仅修改内存集合中订单的状态字段，不落库。"""
    order = get_order(order_no)
    if not order:
        return None
    order["status"] = "已取消"  # ★ 内存状态变更：服务重启后丢失
    return order


# ---------------------------------------------------------------- 自检统计（阶段2验收用）
def stats() -> Dict:
    """返回各内存集合的规模，用于验证是否满足数据规模下限。"""
    shops = _shops
    hotels = _hotels
    shop_pkg = [len(s["packages"]) for s in shops]
    shop_cmt = [len(s["comments"]) for s in shops]
    hotel_room = [len(h["rooms"]) for h in hotels]
    hotel_rev = [len(h["reviews"]) for h in hotels]
    return {
        "shops": len(shops),
        "shopsFood": len([s for s in shops if s["category"] == "美食"]),
        "shopsLeisure": len([s for s in shops if s["category"] == "休闲娱乐"]),
        "hotels": len(hotels),
        "cities": len(list_cities()),
        "cityList": list_cities(),
        "shopsByCity": {c: len([s for s in shops if s["city"] == c]) for c in list_cities()},
        "hotelsByCity": {c: len([h for h in hotels if h["city"] == c]) for c in list_cities()},
        "withPhoto": len([s for s in shops if s.get("cover")]) + len([h for h in hotels if h.get("cover")]),
        "packagesTotal": sum(shop_pkg),
        "packagesMinPerShop": min(shop_pkg),
        "roomsTotal": sum(hotel_room),
        "roomsMinPerHotel": min(hotel_room),
        "commentsTotal": sum(shop_cmt),
        "commentsMinPerShop": min(shop_cmt),
        "reviewsTotal": sum(hotel_rev),
        "reviewsMinPerHotel": min(hotel_rev),
        "orders": len(_orders),
        "banners": len(BANNERS),
        "categories": len(CATEGORIES),
        "users": len(_users),
        "usersByRole": {
            r: len([u for u in _users if u["role"] == r]) for r in ("user", "merchant", "admin")
        },
        "sessions": len(_sessions),
    }


# ---------------------------------------------------------------- 账号与会话（内存用户表）
_users: List[Dict] = [dict(u) for u in USERS]
_sessions: Dict[str, Dict] = {}
_user_seq = count(101)

# 对外返回的用户字段（**绝不返回 password**）
_PUBLIC_FIELDS = ("id", "username", "role", "nickname", "phone", "avatarColor", "status", "merchantId")


def public_user(user: Dict) -> Dict:
    """裁剪用户字段：去掉密码等敏感信息。"""
    return {k: user.get(k, "") for k in _PUBLIC_FIELDS}


def list_users() -> List[Dict]:
    return [public_user(u) for u in _users]


def get_user(user_id: str) -> Optional[Dict]:
    for u in _users:
        if u["id"] == user_id:
            return u
    return None


def get_user_by_username(username: str) -> Optional[Dict]:
    name = (username or "").strip().lower()
    for u in _users:
        if u["username"].lower() == name:
            return u
    return None


def register_user(username: str, password: str, nickname: str = "", phone: str = ""):
    """注册普通用户（注册只开放 user 角色）。返回 (user, 错误信息)。"""
    name = (username or "").strip()
    if not 3 <= len(name) <= 20:
        return None, "用户名需为 3~20 位"
    if len(password or "") < 6:
        return None, "密码至少 6 位"
    if get_user_by_username(name):
        return None, "用户名已存在"
    if phone and (not phone.isdigit() or len(phone) != 11):
        return None, "手机号需为 11 位数字"

    user = {
        "id": f"U{next(_user_seq):03d}",
        "username": name,
        "password": password,  # ★ 明文存储，仅课程演示
        "role": "user",
        "nickname": (nickname or "").strip() or name,
        "phone": phone or "",
        "avatarColor": "#409eff",
        "status": "正常",
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "merchantId": "",
    }
    _users.append(user)  # ★ 追加至内存用户表：服务重启后自注册账号丢失
    return user, ""


def authenticate(username: str, password: str):
    """登录校验。返回 (user, 错误信息)。"""
    user = get_user_by_username(username)
    if not user or user["password"] != (password or ""):
        return None, "用户名或密码错误"
    if user["status"] != "正常":
        return None, "账号已被停用，请联系管理员"
    return user, ""


def create_session(user_id: str) -> str:
    """创建会话并返回令牌（内存字典，重启失效）。"""
    token = new_token()
    _sessions[token] = {
        "token": token,
        "userId": user_id,
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return token


def get_user_by_token(token: str) -> Optional[Dict]:
    session = _sessions.get(token or "")
    if not session:
        return None
    return get_user(session["userId"])


def delete_session(token: str) -> bool:
    return _sessions.pop(token or "", None) is not None


def set_user_status(user_id: str, status: str) -> Optional[Dict]:
    """停用 / 启用账号；停用时立即失效该用户的所有会话。"""
    user = get_user(user_id)
    if not user:
        return None
    user["status"] = status
    if status != "正常":
        for tk in [t for t, s in _sessions.items() if s["userId"] == user_id]:
            _sessions.pop(tk, None)
    return user


def user_stats() -> Dict:
    return {
        "users": len(_users),
        "usersByRole": {
            r: len([u for u in _users if u["role"] == r]) for r in ("user", "merchant", "admin")
        },
        "activeSessions": len(_sessions),
    }


# ---------------------------------------------------------------- 权限：订单归属 / 商家 / 管理员视图
def find_target(target_id: str) -> Optional[Dict]:
    """按 ID 找门店或酒店（用于订单归属与商家权限判断）。"""
    return get_shop(target_id) or get_hotel(target_id)


def merchant_targets(merchant_id: str) -> List[Dict]:
    """商家名下的门店与酒店（列表级字段 + kind 标记）。"""
    result: List[Dict] = []
    for s in _shops:
        if s.get("merchantId") == merchant_id:
            result.append({**_brief_shop(s), "kind": "shop"})
    for h in _hotels:
        if h.get("merchantId") == merchant_id:
            result.append({**_brief_hotel(h), "kind": "hotel"})
    return result


def list_orders_for(user: Optional[Dict]) -> List[Dict]:
    """按角色返回可见订单（数据权限的核心）：

    - 普通用户：仅自己的订单（order.userId == 自己）
    - 商家：仅自己名下门店/酒店产生的订单
    - 管理员：全部订单
    - None：全部（仅供内部/自检脚本使用）
    """
    if not user:
        return list_orders()
    role = user.get("role")
    if role == "admin":
        return list_orders()
    if role == "merchant":
        mid = user.get("merchantId") or ""
        if not mid:
            return []
        owned = {t["id"] for t in merchant_targets(mid)}
        return [o for o in list_orders() if o.get("targetId") in owned]
    return [o for o in list_orders() if o.get("userId") == user.get("id")]


def can_access_order(order: Dict, user: Optional[Dict]) -> bool:
    """判断当前用户是否有权查看/操作某订单。"""
    if not user:
        return False
    role = user.get("role")
    if role == "admin":
        return True
    if role == "merchant":
        mid = user.get("merchantId") or ""
        target = find_target(order.get("targetId", ""))
        return bool(mid) and bool(target) and target.get("merchantId") == mid
    return order.get("userId") == user.get("id")


def merchant_summary(merchant_id: str) -> Dict:
    """商家经营概览：名下门店/酒店 + 订单统计。"""
    targets = merchant_targets(merchant_id)
    ids = {t["id"] for t in targets}
    orders = [o for o in _orders if o.get("targetId") in ids]
    pending = [o for o in orders if o["status"] == "待使用"]
    return {
        "merchantId": merchant_id,
        "targets": targets,
        "targetCount": len(targets),
        "orderCount": len(orders),
        "pendingCount": len(pending),
        "cancelledCount": len([o for o in orders if o["status"] == "已取消"]),
        "pendingAmount": round(sum(float(o["amount"]) for o in pending), 2),
        "reviewCount": sum(int(t.get("reviewCount") or 0) for t in targets),
    }


def update_merchant_profile(merchant_id: str, business_hours: str = "", intro: str = "") -> int:
    """商家维护自己门店/酒店的信息（原型只开放营业时间与简介）。返回被更新的对象数。"""
    updated = 0
    for s in _shops:
        if s.get("merchantId") == merchant_id and business_hours:
            s["businessHours"] = business_hours
            updated += 1
    for h in _hotels:
        if h.get("merchantId") == merchant_id and intro:
            h["intro"] = intro
            updated += 1
    return updated


def admin_overview() -> Dict:
    """管理员平台概览。"""
    pending = [o for o in _orders if o["status"] == "待使用"]
    return {
        "shops": len(_shops),
        "hotels": len(_hotels),
        "users": len(_users),
        "usersByRole": {
            r: len([u for u in _users if u["role"] == r]) for r in ("user", "merchant", "admin")
        },
        "disabledUsers": len([u for u in _users if u["status"] != "正常"]),
        "orders": len(_orders),
        "pendingOrders": len(pending),
        "cancelledOrders": len([o for o in _orders if o["status"] == "已取消"]),
        "pendingAmount": round(sum(float(o["amount"]) for o in pending), 2),
        "sessions": len(_sessions),
        "cities": len(list_cities()),
    }
