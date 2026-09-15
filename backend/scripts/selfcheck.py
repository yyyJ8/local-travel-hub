"""原型系统自检脚本（各阶段验收用）

用法：
    cd D:\\Ctrip\\backend
    D:\\Ctrip\\.venv\\Scripts\\python.exe scripts\\selfcheck.py

检查项：
    阶段2  内存数据规模是否满足下限；筛选/排序/下单/取消的内存行为是否正确
说明：本脚本直接导入 store 模块，运行在独立进程中，不会影响正在运行的后端服务。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data import store  # noqa: E402
from app.models.schemas import OrderCreateRequest  # noqa: E402

PASS, FAIL = "PASS", "FAIL"
results = []


def check(name, condition, detail=""):
    results.append((PASS if condition else FAIL, name, detail))
    print(f"[{PASS if condition else FAIL}] {name}" + (f"  -> {detail}" if detail else ""))


print("=" * 72)
print("阶段2：内存数据层自检")
print("=" * 72)
st = store.stats()
for k, v in st.items():
    print(f"  {k:22} = {v}")
print("-" * 72)

check("门店数量 ≥ 20", st["shops"] >= 20, f"实际 {st['shops']}")
check("酒店数量 ≥ 16", st["hotels"] >= 16, f"实际 {st['hotels']}")
check("覆盖城市 = 3（成都/重庆/西安）", st["cities"] == 3, f"实际 {st['cities']}：{'、'.join(st['cityList'])}")
check("套餐 ≥ 3/门店", st["packagesMinPerShop"] >= 3, f"最少 {st['packagesMinPerShop']}")
check("房型 ≥ 3/酒店", st["roomsMinPerHotel"] >= 3, f"最少 {st['roomsMinPerHotel']}")
check("评论 ≥ 10/门店", st["commentsMinPerShop"] >= 10, f"最少 {st['commentsMinPerShop']}")
check("评价 ≥ 10/酒店", st["reviewsMinPerHotel"] >= 10, f"最少 {st['reviewsMinPerHotel']}")
check("全部门店与酒店均已配置图片路径", st["withPhoto"] == st["shops"] + st["hotels"],
      f"{st['withPhoto']} / {st['shops'] + st['hotels']}")
check("预置订单 2~3 条", 2 <= st["orders"] <= 3, f"实际 {st['orders']}")
check("首页轮播 ≥ 3", st["banners"] >= 3, f"实际 {st['banners']}")
check("分类入口 = 3（美食/休闲娱乐/酒店）", st["categories"] == 3, f"实际 {st['categories']}")
check("美食与休闲娱乐门店均存在", st["shopsFood"] > 0 and st["shopsLeisure"] > 0,
      f"美食 {st['shopsFood']} / 休闲娱乐 {st['shopsLeisure']}")
check("各城市门店分布均衡（每城 ≥ 4 家）", all(v >= 4 for v in st["shopsByCity"].values()),
      "、".join(f"{k} {v} 家" for k, v in st["shopsByCity"].items()))
check("各城市酒店分布均衡（每城 ≥ 3 家）", all(v >= 3 for v in st["hotelsByCity"].values()),
      "、".join(f"{k} {v} 家" for k, v in st["hotelsByCity"].items()))

print("-" * 72)
print("筛选与排序行为")
print("-" * 72)
all_shops = store.list_shops()
food = store.list_shops(category="美食")
cheap = store.list_shops(max_price=90)
high = store.list_shops(min_rating=4.6)
by_rating = store.list_shops(sort_by="rating")
by_price = store.list_shops(sort_by="priceAsc")
check("品类筛选生效（美食 < 全部）", 0 < len(food) < len(all_shops), f"{len(food)} < {len(all_shops)}")
check("人均价格筛选生效", 0 < len(cheap) < len(all_shops), f"人均≤90 共 {len(cheap)} 家")
check("评分筛选生效", 0 < len(high) < len(all_shops), f"评分≥4.6 共 {len(high)} 家")
check("评分排序生效", all(by_rating[i]["rating"] >= by_rating[i + 1]["rating"] for i in range(len(by_rating) - 1)),
      f"首位 {by_rating[0]['name']} {by_rating[0]['rating']}")
check("价格升序排序生效", all(by_price[i]["avgPrice"] <= by_price[i + 1]["avgPrice"] for i in range(len(by_price) - 1)),
      f"首位 {by_price[0]['name']} 人均{by_price[0]['avgPrice']}")

cq = store.list_shops(city="重庆")
xa = store.list_shops(city="西安")
check("门店城市筛选生效", 0 < len(cq) < len(all_shops) and 0 < len(xa) < len(all_shops),
      f"重庆 {len(cq)} 家 / 西安 {len(xa)} 家 / 合计 {len(all_shops)} 家")

star5 = store.list_hotels(star=5)
by_hotel_price = store.list_hotels(sort_by="priceAsc")
fac = store.list_facilities()
check("星级筛选生效", 0 < len(star5) < st["hotels"], f"五星 {len(star5)} 家")
check("酒店价格排序生效",
      all(by_hotel_price[i]["minPrice"] <= by_hotel_price[i + 1]["minPrice"] for i in range(len(by_hotel_price) - 1)),
      f"最低价 {by_hotel_price[0]['name']} ¥{by_hotel_price[0]['minPrice']}")
check("设施选项可枚举", len(fac) >= 6, f"{len(fac)} 项：{'、'.join(fac[:6])}...")

print("-" * 72)
print("搜索与详情")
print("-" * 72)
search = store.search("火锅")
check("关键词搜索命中门店", len(search["shops"]) > 0, f"火锅 -> 门店 {len(search['shops'])} 家")
search_hotel = store.search("青城山")
check("关键词搜索命中酒店", len(search_hotel["hotels"]) > 0, f"青城山 -> 酒店 {len(search_hotel['hotels'])} 家")
shop = store.get_shop("S001")
check("门店详情含套餐与评论", bool(shop) and len(shop["packages"]) >= 3 and len(shop["comments"]) >= 5,
      f"{shop['name']}：套餐 {len(shop['packages'])}、评论 {len(shop['comments'])}")
hotel = store.get_hotel("H001")
check("酒店详情含房型与评价", bool(hotel) and len(hotel["rooms"]) >= 3 and len(hotel["reviews"]) >= 5,
      f"{hotel['name']}：房型 {len(hotel['rooms'])}、评价 {len(hotel['reviews'])}")

print("-" * 72)
print("内存订单行为（本进程内测试，不影响运行中的服务）")
print("-" * 72)
before = len(store.list_orders())
req = OrderCreateRequest(type="shop", targetId="S001", itemId="S001-P02", name="自检用户",
                         phone="13712345678", bookTime="2026-04-01", count=2)
order = store.create_order(req)
after = len(store.list_orders())
check("下单后订单追加至内存集合", order is not None and after == before + 1, f"{before} -> {after}")
check("门店订单金额 = 单价 × 份数",
      order is not None and abs(order["amount"] - store.get_shop("S001")["packages"][1]["price"] * 2) < 0.01,
      f"金额 ¥{order['amount'] if order else '-'}")

hreq = OrderCreateRequest(type="hotel", targetId="H001", itemId="H001-R01", name="自检用户",
                          phone="13712345678", bookTime="2026-04-01", checkOut="2026-04-03", count=1)
horder = store.create_order(hreq)
check("酒店订单自动计算晚数（2 晚）", horder is not None and horder["nights"] == 2,
      f"晚数 {horder['nights'] if horder else '-'}")
check("酒店订单金额 = 房价 × 间数 × 晚数",
      horder is not None and abs(horder["amount"] - store.get_hotel("H001")["rooms"][0]["price"] * 2) < 0.01,
      f"金额 ¥{horder['amount'] if horder else '-'}")

cancelled = store.cancel_order(order["orderNo"])
check("取消后状态改为「已取消」", cancelled is not None and cancelled["status"] == "已取消",
      f"订单 {order['orderNo']} -> {cancelled['status'] if cancelled else '-'}")
check("取消不存在的订单返回 None", store.cancel_order("ORD-NOT-EXIST") is None)

print("=" * 72)
failed = [r for r in results if r[0] == FAIL]
print(f"自检结果：{len(results) - len(failed)} 项通过 / {len(failed)} 项失败")
if failed:
    for _, name, detail in failed:
        print(f"  FAIL: {name} {detail}")
    sys.exit(1)
print("阶段2 验收通过")
