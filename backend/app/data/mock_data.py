"""内存模拟数据集（课程演示原型专用）

设计说明：
1. 本模块是原型阶段的「数据源」，全部数据存放于 Python 内存集合中，程序重启即回到初始状态；
2. 门店 / 酒店为核心静态数据（手工编写，保证多品类、多价位，便于演示筛选与排序）；
3. 套餐、评论、房型、酒店评价由确定性算法生成（固定随机种子），保证每次启动数据一致；
4. 生产版本应迁移至数据库，表结构见报告「领域对象模型与表设计」章节。
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List

# ---------------------------------------------------------------- 首页数据
BANNERS: List[Dict] = [
    {
        "id": "B001",
        "title": "春日美食节",
        "subtitle": "精选火锅 · 5 折起",
        "colorFrom": "#ff7a45",
        "colorTo": "#ff4d4f",
        "targetType": "shop",
        "targetId": "S001",
    },
    {
        "id": "B002",
        "title": "周末出游住好店",
        "subtitle": "高端酒店 · 限时立减 300",
        "colorFrom": "#1890ff",
        "colorTo": "#0050b3",
        "targetType": "hotel",
        "targetId": "H001",
    },
    {
        "id": "B003",
        "title": "休闲娱乐专场",
        "subtitle": "SPA / 密室 / KTV 特惠",
        "colorFrom": "#722ed1",
        "colorTo": "#391085",
        "targetType": "shop",
        "targetId": "S009",
    },
]

CATEGORIES: List[Dict] = [
    {"id": "C001", "name": "美食", "icon": "Food", "color": "#ff6633", "targetType": "shop", "targetCategory": "美食"},
    {"id": "C002", "name": "休闲娱乐", "icon": "Coffee", "color": "#722ed1", "targetType": "shop", "targetCategory": "休闲娱乐"},
    {"id": "C003", "name": "酒店", "icon": "OfficeBuilding", "color": "#0086f6", "targetType": "hotel", "targetCategory": ""},
]

# ---------------------------------------------------------------- 生成素材池
_NICKNAMES = [
    "阿宝", "小鹿乱撞", "Coco", "老张同志", "Amy", "一只猫", "大熊", "柠檬茶",
    "Kevin", "小米粒", "行走的胃", "甜筒", "江户川", "路人甲", "饭桶本桶", "摄影师老王",
]

_AVATAR_COLORS = [
    "#ff7875", "#ffa940", "#ffc53d", "#95de64", "#5cdbd3",
    "#69c0ff", "#85a5ff", "#b37feb", "#ff85c0", "#d9d9d9",
]

_SHOP_COMMENT_TPL = [
    "{dish}真的很惊艳，分量足，服务也热情，下次还来！",
    "环境不错，人均{price}元左右，性价比高，{dish}必点。",
    "排队等了一会儿，但味道对得起等待，强烈推荐{dish}。",
    "和朋友聚餐选的这里，整体体验很好，就是周末人有点多。",
    "口味偏重，喜欢重口味的会很爱，{dish}很入味。",
    "位置好找，就在{district}，店里干净整洁，服务员态度好。",
    "第二次来了，依旧稳定发挥，{dish}还是那个味道。",
    "价格小贵，不过食材新鲜，偶尔来一次还是值得的。",
    "带爸妈来吃的，长辈也说好吃，菜品摆盘也精致。",
    "上菜速度快，团购套餐很划算，比单点便宜不少。",
]

_HOTEL_REVIEW_TPL = [
    "位置非常方便，离地铁口很近，{room}很干净，床品舒服。",
    "前台办理入住很快，房间隔音不错，晚上睡得很安稳。",
    "酒店环境安静，早餐种类多，{room}空间比想象中大。",
    "性价比不错，设施稍微有点旧，但卫生做得很到位。",
    "带娃出行，服务人员很贴心，还主动帮忙加了床。",
    "窗外视野很好，晚上看夜景很舒服，下次还会再来。",
    "{room}的洗漱用品不错，热水稳定，水压也足。",
    "离商圈近，逛街吃饭都方便，出行体验很好。",
]

_ROOM_BLUEPRINT = [
    {"suffix": "高级大床房", "area": 28, "bed": "1.8m 大床", "breakfast": "含单早", "window": "有窗", "priceRate": 1.00, "cancel": "免费取消"},
    {"suffix": "高级双床房", "area": 32, "bed": "1.2m 双床", "breakfast": "含双早", "window": "有窗", "priceRate": 1.06, "cancel": "免费取消"},
    {"suffix": "豪华大床房", "area": 42, "bed": "2.0m 大床", "breakfast": "含双早", "window": "有窗", "priceRate": 1.42, "cancel": "限时取消"},
    {"suffix": "行政套房", "area": 60, "bed": "2.0m 大床", "breakfast": "含双早", "window": "有窗", "priceRate": 2.20, "cancel": "不可取消"},
]

_FACILITY_POOL = [
    "免费WiFi", "免费停车场", "健身房", "室内泳池", "24小时前台",
    "行李寄存", "中西餐厅", "接机服务", "洗衣服务", "温泉", "会议室", "儿童乐园",
]


def _rng(seed: str) -> random.Random:
    """按业务 ID 生成确定性随机数发生器，保证每次启动数据一致。"""
    return random.Random(f"ctrip-prototype-{seed}")


def _gen_packages(shop: Dict) -> List[Dict]:
    """为门店生成 3~4 个团购套餐。"""
    rng = _rng(shop["id"] + "-pkg")
    avg = shop["avgPrice"]
    dish = shop["tags"][0]
    blueprint = [
        ("单人套餐", round(avg * 0.95), 1),
        ("双人套餐", round(avg * 1.85), 2),
        ("四人套餐", round(avg * 3.40), 4),
        ("100元代金券", 88, 1),
    ]
    packages = []
    for idx, (name, price, _people) in enumerate(blueprint):
        price = float(max(price, 28))
        original = round(price * rng.uniform(1.20, 1.45), 0)
        packages.append(
            {
                "id": f"{shop['id']}-P{idx + 1:02d}",
                "name": f"{name}·{dish}",
                "price": price,
                "originalPrice": max(original, price + 10),
                "sold": rng.randint(120, 3800),
                "desc": f"{name}，含{dish}等招牌菜，到店可用，不可与其他优惠同享。",
            }
        )
    return packages


def _gen_comments(shop: Dict) -> List[Dict]:
    """为门店生成 10~12 条模拟用户评论（数量足够撑起评论区滚动）。"""
    rng = _rng(shop["id"] + "-cmt")
    count = rng.randint(10, 12)
    comments = []
    now = datetime.now()
    for i in range(count):
        tpl = _SHOP_COMMENT_TPL[(hash(shop["id"]) + i) % len(_SHOP_COMMENT_TPL)]
        rating = min(5.0, max(3.5, round(shop["rating"] + rng.choice([0.0, 0.0, 0.0, -0.5, 0.2]), 1)))
        comments.append(
            {
                "id": f"{shop['id']}-C{i + 1:02d}",
                "user": _NICKNAMES[(hash(shop["id"]) + i * 3) % len(_NICKNAMES)],
                "avatarColor": _AVATAR_COLORS[(hash(shop["id"]) + i) % len(_AVATAR_COLORS)],
                "rating": rating,
                "content": tpl.format(
                    dish=shop["tags"][i % len(shop["tags"])],
                    price=shop["avgPrice"],
                    district=shop["district"],
                ),
                "date": (now - timedelta(days=rng.randint(1, 120))).strftime("%Y-%m-%d"),
            }
        )
    return comments


def _gen_rooms(hotel: Dict) -> List[Dict]:
    """为酒店生成 3~4 个房型。"""
    rng = _rng(hotel["id"] + "-room")
    rooms = []
    for idx, bp in enumerate(_ROOM_BLUEPRINT):
        price = round(hotel["minPrice"] * bp["priceRate"] / 10) * 10
        rooms.append(
            {
                "id": f"{hotel['id']}-R{idx + 1:02d}",
                "name": bp["suffix"],
                "area": bp["area"],
                "bedType": bp["bed"],
                "breakfast": bp["breakfast"],
                "window": bp["window"],
                "cancelPolicy": bp["cancel"],
                "price": float(price),
                "originalPrice": float(round(price * 1.25 / 10) * 10),
                "remain": rng.randint(1, 9),
            }
        )
    return rooms


def _gen_reviews(hotel: Dict) -> List[Dict]:
    """为酒店生成 10~12 条模拟评价。"""
    rng = _rng(hotel["id"] + "-rev")
    count = rng.randint(10, 12)
    reviews, rooms = [], _gen_rooms(hotel)
    now = datetime.now()
    for i in range(count):
        tpl = _HOTEL_REVIEW_TPL[(hash(hotel["id"]) + i) % len(_HOTEL_REVIEW_TPL)]
        rating = min(5.0, max(3.5, round(hotel["rating"] + rng.choice([0.0, 0.0, 0.0, -0.3, 0.1]), 1)))
        reviews.append(
            {
                "id": f"{hotel['id']}-V{i + 1:02d}",
                "user": _NICKNAMES[(hash(hotel["id"]) + i * 5) % len(_NICKNAMES)],
                "avatarColor": _AVATAR_COLORS[(hash(hotel["id"]) + i * 2) % len(_AVATAR_COLORS)],
                "rating": rating,
                "content": tpl.format(room=rooms[i % len(rooms)]["name"]),
                "date": (now - timedelta(days=rng.randint(1, 150))).strftime("%Y-%m-%d"),
                "roomType": rooms[i % len(rooms)]["name"],
            }
        )
    return reviews


# ---------------------------------------------------------------- 门店原始数据（12 家）
_SHOPS_RAW: List[Dict] = [
    {"id": "S001", "name": "蜀大侠火锅（春熙路店）", "category": "美食", "subCategory": "火锅", "rating": 4.8, "reviewCount": 8642, "avgPrice": 128, "popularity": 98600, "tags": ["麻辣牛肉", "毛肚", "鲜切黄牛肉"], "district": "锦江区", "address": "成都市锦江区春熙路东段 18 号 3 层", "businessHours": "11:00 - 次日 02:00", "phone": "028-8611-0001", "coverColor": "#ff6633", "coverTag": "火锅"},
    {"id": "S002", "name": "海底捞火锅（万象城店）", "category": "美食", "subCategory": "火锅", "rating": 4.7, "reviewCount": 7320, "avgPrice": 156, "popularity": 91200, "tags": ["捞派滑牛肉", "虾滑", "番茄锅底"], "district": "成华区", "address": "成都市成华区双庆路 8 号万象城 4 层", "businessHours": "10:30 - 次日 03:00", "phone": "028-8432-0002", "coverColor": "#fa541c", "coverTag": "火锅"},
    {"id": "S003", "name": "陈麻婆豆腐（宽窄巷子店）", "category": "美食", "subCategory": "川菜", "rating": 4.6, "reviewCount": 5210, "avgPrice": 78, "popularity": 68400, "tags": ["麻婆豆腐", "夫妻肺片", "回锅肉"], "district": "青羊区", "address": "成都市青羊区窄巷子 12 号", "businessHours": "10:00 - 21:30", "phone": "028-8623-0003", "coverColor": "#d4380d", "coverTag": "川菜"},
    {"id": "S004", "name": "大龙燚火锅（建设路店）", "category": "美食", "subCategory": "火锅", "rating": 4.5, "reviewCount": 4108, "avgPrice": 112, "popularity": 57300, "tags": ["麻辣牛肉", "鸭肠", "千层毛肚"], "district": "成华区", "address": "成都市成华区建设路 33 号", "businessHours": "11:30 - 次日 01:00", "phone": "028-8433-0004", "coverColor": "#cf1322", "coverTag": "火锅"},
    {"id": "S005", "name": "一风堂拉面（IFS 店）", "category": "美食", "subCategory": "日料", "rating": 4.4, "reviewCount": 2980, "avgPrice": 96, "popularity": 42600, "tags": ["豚骨拉面", "叉烧饭", "煎饺"], "district": "锦江区", "address": "成都市锦江区红星路三段 1 号 IFS 国际金融中心 5 层", "businessHours": "11:00 - 22:00", "phone": "028-8665-0005", "coverColor": "#ffa940", "coverTag": "日料"},
    {"id": "S006", "name": "星巴克臻选（太古里店）", "category": "美食", "subCategory": "咖啡", "rating": 4.5, "reviewCount": 3360, "avgPrice": 45, "popularity": 48900, "tags": ["手冲咖啡", "冷萃", "芝士蛋糕"], "district": "锦江区", "address": "成都市锦江区中纱帽街 8 号远洋太古里 M 座 1 层", "businessHours": "07:30 - 22:30", "phone": "028-8677-0006", "coverColor": "#8c6b4f", "coverTag": "咖啡"},
    {"id": "S007", "name": "西贝莜面村（环球中心店）", "category": "美食", "subCategory": "中餐", "rating": 4.3, "reviewCount": 2450, "avgPrice": 88, "popularity": 35400, "tags": ["莜面窝窝", "烤羊排", "牛大骨"], "district": "武侯区", "address": "成都市武侯区天府大道北段 1700 号环球中心 3 层", "businessHours": "10:30 - 21:30", "phone": "028-8553-0007", "coverColor": "#d48806", "coverTag": "中餐"},
    {"id": "S008", "name": "泰香米（大悦城店）", "category": "美食", "subCategory": "东南亚菜", "rating": 4.4, "reviewCount": 1980, "avgPrice": 102, "popularity": 29800, "tags": ["冬阴功汤", "菠萝饭", "咖喱蟹"], "district": "武侯区", "address": "成都市武侯区大悦路 518 号大悦城 4 层", "businessHours": "11:00 - 22:00", "phone": "028-8521-0008", "coverColor": "#52c41a", "coverTag": "东南亚菜"},
    {"id": "S009", "name": "足下生辉足疗SPA（桐梓林店）", "category": "休闲娱乐", "subCategory": "SPA", "rating": 4.6, "reviewCount": 1560, "avgPrice": 198, "popularity": 24600, "tags": ["精油全身按摩", "足底按摩", "艾灸"], "district": "武侯区", "address": "成都市武侯区桐梓林北路 6 号 2 层", "businessHours": "12:00 - 次日 02:00", "phone": "028-8556-0009", "coverColor": "#722ed1", "coverTag": "SPA"},
    {"id": "S010", "name": "星空密室逃脱（天府广场店）", "category": "休闲娱乐", "subCategory": "密室", "rating": 4.7, "reviewCount": 2210, "avgPrice": 108, "popularity": 33200, "tags": ["盗墓主题", "民国谍战", "恐怖医院"], "district": "青羊区", "address": "成都市青羊区人民中路一段 5 号 6 层", "businessHours": "13:00 - 23:30", "phone": "028-8622-0010", "coverColor": "#391085", "coverTag": "密室"},
    {"id": "S011", "name": "纯K KTV（九眼桥店）", "category": "休闲娱乐", "subCategory": "KTV", "rating": 4.2, "reviewCount": 1320, "avgPrice": 138, "popularity": 19800, "tags": ["豪华中包", "果盘畅吃", "无线麦克风"], "district": "锦江区", "address": "成都市锦江区滨江东路 88 号 3 层", "businessHours": "14:00 - 次日 04:00", "phone": "028-8666-0011", "coverColor": "#eb2f96", "coverTag": "KTV"},
    {"id": "S012", "name": "漫咖啡（天府三街店）", "category": "休闲娱乐", "subCategory": "咖啡休闲", "rating": 4.3, "reviewCount": 1120, "avgPrice": 68, "popularity": 16400, "tags": ["华夫饼", "美式咖啡", "免费续杯"], "district": "高新区", "address": "成都市高新区天府三街 69 号 1 层", "businessHours": "09:00 - 23:00", "phone": "028-8512-0012", "coverColor": "#a0522d", "coverTag": "咖啡休闲"},
    # ---- 重庆（4 家）----
    {"id": "S013", "name": "重庆老火锅（解放碑店）", "city": "重庆", "category": "美食", "subCategory": "火锅", "rating": 4.7, "reviewCount": 13200, "avgPrice": 118, "popularity": 87600, "tags": ["毛肚", "鸭肠", "九宫格锅底"], "district": "渝中区", "address": "重庆市渝中区民权路 22 号 2 层", "businessHours": "11:00 - 次日 03:00", "phone": "023-6388-0013", "coverColor": "#fa541c", "coverTag": "重庆火锅"},
    {"id": "S014", "name": "花市豌杂面（较场口店）", "city": "重庆", "category": "美食", "subCategory": "小面", "rating": 4.6, "reviewCount": 8900, "avgPrice": 26, "popularity": 52300, "tags": ["豌杂面", "牛肉面", "酸辣粉"], "district": "渝中区", "address": "重庆市渝中区较场口 88 号", "businessHours": "06:30 - 20:30", "phone": "023-6377-0014", "coverColor": "#d46b08", "coverTag": "重庆小面"},
    {"id": "S015", "name": "江湖菜馆（观音桥店）", "city": "重庆", "category": "美食", "subCategory": "江湖菜", "rating": 4.4, "reviewCount": 5600, "avgPrice": 86, "popularity": 41200, "tags": ["辣子鸡", "水煮鱼", "蒜泥白肉"], "district": "江北区", "address": "重庆市江北区观音桥步行街 9 号 3 层", "businessHours": "10:30 - 22:00", "phone": "023-6777-0015", "coverColor": "#cf1322", "coverTag": "江湖菜"},
    {"id": "S016", "name": "星光KTV（南坪店）", "city": "重庆", "category": "休闲娱乐", "subCategory": "KTV", "rating": 4.3, "reviewCount": 2100, "avgPrice": 126, "popularity": 22400, "tags": ["豪华大包", "自助餐台", "音响出色"], "district": "南岸区", "address": "重庆市南岸区南坪西路 15 号 5 层", "businessHours": "14:00 - 次日 04:00", "phone": "023-6288-0016", "coverColor": "#eb2f96", "coverTag": "KTV"},
    # ---- 西安（4 家）----
    {"id": "S017", "name": "老孙家泡馍（钟楼店）", "city": "西安", "category": "美食", "subCategory": "泡馍", "rating": 4.5, "reviewCount": 9800, "avgPrice": 66, "popularity": 58600, "tags": ["羊肉泡馍", "小炒泡馍", "糖蒜"], "district": "碑林区", "address": "西安市碑林区东大街 364 号", "businessHours": "09:00 - 21:30", "phone": "029-8721-0017", "coverColor": "#ad6800", "coverTag": "泡馍"},
    {"id": "S018", "name": "秦豫肉夹馍（回民街店）", "city": "西安", "category": "美食", "subCategory": "小吃", "rating": 4.6, "reviewCount": 12400, "avgPrice": 30, "popularity": 69400, "tags": ["腊汁肉夹馍", "凉皮", "冰峰"], "district": "莲湖区", "address": "西安市莲湖区北院门 129 号", "businessHours": "08:00 - 22:00", "phone": "029-8727-0018", "coverColor": "#d48806", "coverTag": "西安小吃"},
    {"id": "S019", "name": "大唐不夜城烧烤（大雁塔店）", "city": "西安", "category": "美食", "subCategory": "烧烤", "rating": 4.4, "reviewCount": 4300, "avgPrice": 96, "popularity": 34800, "tags": ["烤羊肉串", "烤茄子", "冰镇啤酒"], "district": "雁塔区", "address": "西安市雁塔区雁南一路 1 号", "businessHours": "16:00 - 次日 02:00", "phone": "029-8555-0019", "coverColor": "#d4380d", "coverTag": "烧烤"},
    {"id": "S020", "name": "秦岭养生SPA（高新店）", "city": "西安", "category": "休闲娱乐", "subCategory": "SPA", "rating": 4.5, "reviewCount": 1800, "avgPrice": 218, "popularity": 25300, "tags": ["中式推拿", "药浴", "肩颈理疗"], "district": "高新区", "address": "西安市高新区科技路 33 号 6 层", "businessHours": "11:00 - 次日 01:00", "phone": "029-8833-0020", "coverColor": "#531dab", "coverTag": "SPA"},
]

# ---------------------------------------------------------------- 酒店原始数据（10 家）
_HOTELS_RAW: List[Dict] = [
    {"id": "H001", "name": "成都太古里博舍酒店", "city": "成都", "star": 5, "rating": 4.9, "reviewCount": 6420, "minPrice": 1280, "popularity": 58200, "district": "锦江区", "address": "成都市锦江区笔帖式街 81 号", "facilities": ["免费WiFi", "室内泳池", "健身房", "中西餐厅", "24小时前台", "行李寄存"], "tags": ["太古里核心", "设计感强", "网红打卡"], "intro": "位于太古里核心区，与千年大慈寺相邻，由老宅院改造而成，庭院式布局兼顾私密与静谧。客房采用川西民居与现代设计融合的风格，配备高端床品与独立浴缸，适合追求品质与位置的客人。", "coverColor": "#0050b3", "coverTag": "豪华五星"},
    {"id": "H002", "name": "成都香格里拉大酒店", "city": "成都", "star": 5, "rating": 4.8, "reviewCount": 5310, "minPrice": 1080, "popularity": 49600, "district": "锦江区", "address": "成都市锦江区滨江东路 9 号", "facilities": ["免费WiFi", "免费停车场", "室内泳池", "健身房", "接机服务", "洗衣服务"], "tags": ["锦江夜景", "老牌五星", "服务稳定"], "intro": "坐拥锦江一线江景，紧邻九眼桥与兰桂坊商圈。酒店拥有大面积客房与行政酒廊，康体设施齐全，是商务出行与城市度假的稳妥之选。", "coverColor": "#096dd9", "coverTag": "江景五星"},
    {"id": "H003", "name": "成都环球中心天堂洲际大饭店", "city": "成都", "star": 5, "rating": 4.7, "reviewCount": 4780, "minPrice": 980, "popularity": 44100, "district": "武侯区", "address": "成都市武侯区天府大道北段 1700 号", "facilities": ["免费WiFi", "免费停车场", "室内泳池", "健身房", "儿童乐园", "会议室"], "tags": ["亲子友好", "海洋乐园", "体量超大"], "intro": "位于环球中心内部，可直接连通购物与海洋乐园，亲子设施完善。大堂挑高气势十足，客房分为多栋楼，适合家庭出游与会议团体。", "coverColor": "#1890ff", "coverTag": "亲子五星"},
    {"id": "H004", "name": "成都春熙路亚朵酒店", "city": "成都", "star": 4, "rating": 4.7, "reviewCount": 3920, "minPrice": 520, "popularity": 37800, "district": "锦江区", "address": "成都市锦江区总府路 2 号", "facilities": ["免费WiFi", "健身房", "24小时前台", "行李寄存", "中西餐厅"], "tags": ["春熙路商圈", "人文书房", "位置极佳"], "intro": "步行可达春熙路与太古里，酒店设有亚朵人文书房与属地早餐，房间隔音良好，适合逛街购物与城市观光。", "coverColor": "#40a9ff", "coverTag": "商圈四星"},
    {"id": "H005", "name": "成都天府广场全季酒店", "city": "成都", "star": 4, "rating": 4.6, "reviewCount": 3140, "minPrice": 420, "popularity": 29600, "district": "青羊区", "address": "成都市青羊区人民中路一段 12 号", "facilities": ["免费WiFi", "24小时前台", "行李寄存", "洗衣服务"], "tags": ["地铁直达", "干净简约", "性价比高"], "intro": "紧邻地铁天府广场站，出行便利。客房以原木色调为主，配置智能马桶与高支纱床品，主打干净与实用。", "coverColor": "#69c0ff", "coverTag": "便捷四星"},
    {"id": "H006", "name": "成都宽窄巷子桔子水晶酒店", "city": "成都", "star": 4, "rating": 4.6, "reviewCount": 2760, "minPrice": 468, "popularity": 26800, "district": "青羊区", "address": "成都市青羊区同仁路 5 号", "facilities": ["免费WiFi", "免费停车场", "24小时前台", "中西餐厅"], "tags": ["宽窄巷子旁", "设计酒店", "拍照出片"], "intro": "距宽窄巷子步行约 5 分钟，整体为现代中式设计风格，公共区域陈设讲究，适合休闲旅行与拍照打卡。", "coverColor": "#85a5ff", "coverTag": "设计四星"},
    {"id": "H007", "name": "成都双流机场智选假日酒店", "city": "成都", "star": 3, "rating": 4.4, "reviewCount": 2180, "minPrice": 328, "popularity": 19200, "district": "双流区", "address": "成都市双流区西航港大道 5 号", "facilities": ["免费WiFi", "免费停车场", "接机服务", "24小时前台"], "tags": ["近机场", "免费接送", "早班机首选"], "intro": "距双流机场约 10 分钟车程，提供定时免费接送机服务，办理入住快捷，适合早晚航班与中转停留。", "coverColor": "#5cdbd3", "coverTag": "机场三星"},
    {"id": "H008", "name": "成都高新金融城希尔顿欢朋酒店", "city": "成都", "star": 4, "rating": 4.5, "reviewCount": 2650, "minPrice": 458, "popularity": 24300, "district": "高新区", "address": "成都市高新区天府大道中段 666 号", "facilities": ["免费WiFi", "健身房", "会议室", "中西餐厅", "行李寄存"], "tags": ["商务出差", "金融城核心", "早餐丰富"], "intro": "位于金融城商务核心区，周边写字楼与餐饮聚集，客房配备办公桌与人体工学椅，适合商务出行。", "coverColor": "#36cfc9", "coverTag": "商务四星"},
    {"id": "H009", "name": "成都东站汉庭酒店", "city": "成都", "star": 3, "rating": 4.2, "reviewCount": 1840, "minPrice": 218, "popularity": 14600, "district": "成华区", "address": "成都市成华区邛崃山路 33 号", "facilities": ["免费WiFi", "24小时前台", "行李寄存"], "tags": ["近东站", "价格实惠", "干净整洁"], "intro": "距成都东站步行约 8 分钟，房型紧凑但整洁，适合高铁出行与短途停留，性价比突出。", "coverColor": "#95de64", "coverTag": "经济三星"},
    {"id": "H010", "name": "成都青城山六善酒店", "city": "成都", "star": 5, "rating": 4.8, "reviewCount": 2960, "minPrice": 1880, "popularity": 32400, "district": "都江堰市", "address": "成都市都江堰市青城山镇青城村 8 号", "facilities": ["免费WiFi", "免费停车场", "温泉", "室内泳池", "健身房", "中西餐厅"], "tags": ["山景度假", "温泉私汤", "避世静谧"], "intro": "坐落于青城山脚下，主打庭院式别墅与温泉私汤，环境清幽，适合度假静养与周末微度假出行。", "coverColor": "#237804", "coverTag": "度假五星"},
    # ---- 重庆（3 家）----
    {"id": "H011", "name": "重庆解放碑威斯汀酒店", "city": "重庆", "star": 5, "rating": 4.8, "reviewCount": 5210, "minPrice": 1080, "popularity": 46800, "district": "渝中区", "address": "重庆市渝中区民权路 77 号", "facilities": ["免费WiFi", "室内泳池", "健身房", "中西餐厅", "24小时前台", "接机服务"], "tags": ["解放碑核心", "江景客房", "商务首选"], "intro": "位于解放碑步行街核心，高层客房可俯瞰两江夜景，行政酒廊与会议设施完善，商务与观光皆宜。", "coverColor": "#0050b3", "coverTag": "江景五星"},
    {"id": "H012", "name": "重庆洪崖洞亚朵酒店", "city": "重庆", "star": 4, "rating": 4.6, "reviewCount": 3120, "minPrice": 468, "popularity": 30500, "district": "渝中区", "address": "重庆市渝中区沧白路 56 号", "facilities": ["免费WiFi", "健身房", "24小时前台", "行李寄存", "中西餐厅"], "tags": ["洪崖洞旁", "夜景绝佳", "人文书房"], "intro": "步行可达洪崖洞与朝天门，酒店设有属地早餐与人文书房，夜景房型尤其受欢迎。", "coverColor": "#096dd9", "coverTag": "网红四星"},
    {"id": "H013", "name": "重庆江北机场希尔顿花园酒店", "city": "重庆", "star": 4, "rating": 4.5, "reviewCount": 2450, "minPrice": 398, "popularity": 21300, "district": "渝北区", "address": "重庆市渝北区两路寸滩保税港区 5 号", "facilities": ["免费WiFi", "免费停车场", "接机服务", "24小时前台", "健身房"], "tags": ["近机场", "免费接送", "隔音好"], "intro": "距江北国际机场约 10 分钟车程，提供定时免费接送机，房间隔音处理到位，适合早晚航班与中转。", "coverColor": "#40a9ff", "coverTag": "机场四星"},
    # ---- 西安（3 家）----
    {"id": "H014", "name": "西安钟楼索菲特传奇酒店", "city": "西安", "star": 5, "rating": 4.8, "reviewCount": 4180, "minPrice": 1180, "popularity": 39600, "district": "碑林区", "address": "西安市碑林区东大街 319 号", "facilities": ["免费WiFi", "室内泳池", "健身房", "中西餐厅", "24小时前台", "洗衣服务"], "tags": ["钟楼地标", "法式服务", "城墙景观"], "intro": "紧邻钟楼与城墙，法式建筑风格，客房可远眺古城墙，服务细致，适合深度游与商务接待。", "coverColor": "#1d39c4", "coverTag": "地标五星"},
    {"id": "H015", "name": "西安大唐不夜城亚朵酒店", "city": "西安", "star": 4, "rating": 4.7, "reviewCount": 3860, "minPrice": 528, "popularity": 33400, "district": "雁塔区", "address": "西安市雁塔区慈恩路 12 号", "facilities": ["免费WiFi", "健身房", "行李寄存", "中西餐厅", "会议室"], "tags": ["大雁塔旁", "唐风设计", "亲子友好"], "intro": "毗邻大雁塔与大唐不夜城，整体唐风设计，步行即达景区，家庭出行便利。", "coverColor": "#2f54eb", "coverTag": "景区四星"},
    {"id": "H016", "name": "西安城墙根青旅酒店", "city": "西安", "star": 3, "rating": 4.3, "reviewCount": 1620, "minPrice": 258, "popularity": 15200, "district": "莲湖区", "address": "西安市莲湖区南门里书院门 8 号", "facilities": ["免费WiFi", "行李寄存", "24小时前台"], "tags": ["近城墙", "背包客", "价格实惠"], "intro": "紧邻南门城墙，青旅与快捷房型混合，公共区域有咖啡吧与图书角，适合背包客与短途停留。", "coverColor": "#95de64", "coverTag": "经济三星"},
]

# ---------------------------------------------------------------- 配图计划（供图片下载脚本使用）
# 每个门店/酒店分配 1 张封面图 + 3 张详情页图库图，关键词按品类/星级归组；
# 下载脚本按关键词到 Wikimedia Commons 检索并本地化到 frontend/public/images/。
_SHOP_PHOTO_KEYWORDS: Dict[str, List[str]] = {
    "火锅": ["sichuan hot pot", "hot pot restaurant", "hot pot ingredients", "chinese hotpot table"],
    "川菜": ["sichuan cuisine", "mapo tofu", "chinese stir fried dish", "chinese restaurant table"],
    "日料": ["ramen noodle soup", "japanese restaurant interior", "sushi platter", "japanese food"],
    "咖啡": ["coffee shop interior", "latte art coffee", "espresso machine", "cheesecake dessert"],
    "中餐": ["chinese food dishes", "chinese restaurant interior", "noodle soup bowl", "roast lamb dish"],
    "东南亚菜": ["thai food", "tom yum soup", "pineapple fried rice", "thai curry"],
    "小面": ["chongqing noodles", "chinese noodle bowl", "spicy noodle soup", "chinese street food"],
    "江湖菜": ["chinese home style dishes", "spicy chinese food", "chinese restaurant table", "stir fried dishes"],
    "泡馍": ["xian cuisine", "chinese lamb soup", "shaanxi food", "chinese bread soup"],
    "小吃": ["chinese street food", "roujiamo", "xian muslim quarter food", "chinese snack food"],
    "烧烤": ["chinese barbecue skewers", "bbq grill restaurant", "grilled meat skewers", "chinese night market"],
    "SPA": ["massage spa", "spa treatment room", "foot massage", "spa interior"],
    "密室": ["escape room", "puzzle room game", "escape game room", "mystery room"],
    "KTV": ["karaoke room", "karaoke microphone", "ktv room interior", "nightclub interior"],
    "咖啡休闲": ["coffee shop interior", "cafe table", "cappuccino coffee", "cozy cafe"],
}

_HOTEL_PHOTO_KEYWORDS: Dict[int, List[str]] = {
    5: ["luxury hotel lobby", "hotel suite room", "hotel swimming pool", "hotel exterior night"],
    4: ["hotel room interior", "hotel lobby reception", "hotel breakfast buffet", "hotel building exterior"],
    3: ["budget hotel room", "hotel reception desk", "hotel corridor", "hotel exterior"],
}

_BANNER_PHOTO_KEYWORDS: List[str] = [
    "chinese food festival",
    "hotel resort swimming pool",
    "massage spa relaxation",
]

# ---------------------------------------------------------------- 组装完整数据集
SHOPS: List[Dict] = []
for _shop in _SHOPS_RAW:
    _shop.setdefault("city", "成都")  # 早期数据未含城市字段，统一按成都处理
    _item = dict(_shop)
    _item["packages"] = _gen_packages(_shop)
    _item["comments"] = _gen_comments(_shop)
    SHOPS.append(_item)

HOTELS: List[Dict] = []
for _hotel in _HOTELS_RAW:
    _item = dict(_hotel)
    _item["rooms"] = _gen_rooms(_hotel)
    _item["reviews"] = _gen_reviews(_hotel)
    HOTELS.append(_item)

# 图片路径（本地静态资源，前后端分离下由前端 public 目录提供，断网可用）
PHOTO_PLAN: Dict[str, Dict] = {}

for _shop in SHOPS:
    _kws = _SHOP_PHOTO_KEYWORDS.get(_shop["subCategory"], _SHOP_PHOTO_KEYWORDS["中餐"])
    _shop["cover"] = f"/images/shops/{_shop['id']}.jpg"
    _shop["gallery"] = [f"/images/shops/{_shop['id']}-{i}.jpg" for i in (1, 2, 3)]
    PHOTO_PLAN[_shop["id"]] = {
        "kind": "shop",
        "keywords": _kws,
        "paths": [_shop["cover"]] + _shop["gallery"],
    }

for _hotel in HOTELS:
    _kws = _HOTEL_PHOTO_KEYWORDS.get(_hotel["star"], _HOTEL_PHOTO_KEYWORDS[3])
    _hotel["cover"] = f"/images/hotels/{_hotel['id']}.jpg"
    _hotel["gallery"] = [f"/images/hotels/{_hotel['id']}-{i}.jpg" for i in (1, 2, 3)]
    PHOTO_PLAN[_hotel["id"]] = {
        "kind": "hotel",
        "keywords": _kws,
        "paths": [_hotel["cover"]] + _hotel["gallery"],
    }

for _banner, _kw in zip(BANNERS, _BANNER_PHOTO_KEYWORDS):
    _banner["image"] = f"/images/banners/{_banner['id']}.jpg"
    PHOTO_PLAN[_banner["id"]] = {
        "kind": "banner",
        "keywords": [_kw, "chinese food", "travel hotel", "spa wellness"],
        "paths": [_banner["image"]],
    }

# ---------------------------------------------------------------- 预置模拟订单（首次进入个人中心即有数据）
_NOW = datetime.now()


def _preset_orders() -> List[Dict]:
    shop = SHOPS[0]
    shop2 = SHOPS[8]
    hotel = HOTELS[0]
    return [
        {
            "orderNo": "ORD" + (_NOW - timedelta(days=6)).strftime("%Y%m%d") + "1001",
            "type": "shop",
            "targetId": shop["id"],
            "targetName": shop["name"],
            "itemId": shop["packages"][1]["id"],
            "itemName": shop["packages"][1]["name"],
            "name": "张三",
            "phone": "13800001111",
            "bookTime": (_NOW + timedelta(days=2)).strftime("%Y-%m-%d"),
            "checkOut": "",
            "nights": 0,
            "count": 1,
            "amount": shop["packages"][1]["price"],
            "status": "待使用",
            "createdAt": (_NOW - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "coverColor": shop["coverColor"],
            "coverTag": shop["coverTag"],
        },
        {
            "orderNo": "ORD" + (_NOW - timedelta(days=4)).strftime("%Y%m%d") + "1002",
            "type": "hotel",
            "targetId": hotel["id"],
            "targetName": hotel["name"],
            "itemId": hotel["rooms"][0]["id"],
            "itemName": hotel["rooms"][0]["name"],
            "name": "张三",
            "phone": "13800001111",
            "bookTime": (_NOW + timedelta(days=10)).strftime("%Y-%m-%d"),
            "checkOut": (_NOW + timedelta(days=12)).strftime("%Y-%m-%d"),
            "nights": 2,
            "count": 1,
            "amount": hotel["rooms"][0]["price"] * 2,
            "status": "待使用",
            "createdAt": (_NOW - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "coverColor": hotel["coverColor"],
            "coverTag": hotel["coverTag"],
        },
        {
            "orderNo": "ORD" + (_NOW - timedelta(days=15)).strftime("%Y%m%d") + "1003",
            "type": "shop",
            "targetId": shop2["id"],
            "targetName": shop2["name"],
            "itemId": shop2["packages"][0]["id"],
            "itemName": shop2["packages"][0]["name"],
            "name": "李四",
            "phone": "13900002222",
            "bookTime": (_NOW - timedelta(days=12)).strftime("%Y-%m-%d"),
            "checkOut": "",
            "nights": 0,
            "count": 1,
            "amount": shop2["packages"][0]["price"],
            "status": "已取消",
            "createdAt": (_NOW - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"),
            "coverColor": shop2["coverColor"],
            "coverTag": shop2["coverTag"],
        },
    ]


PRESET_ORDERS: List[Dict] = _preset_orders()
