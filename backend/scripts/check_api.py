"""HTTP 接口自检脚本（阶段3 / 阶段8 验收用）

用法（需先启动后端服务）：
    cd D:\\Ctrip\\backend
    D:\\Ctrip\\.venv\\Scripts\\python.exe scripts\\check_api.py

仅使用标准库 urllib，不额外引入依赖。逐条验证 I1~I10 接口的返回结构、筛选排序效果与订单内存行为。
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"
results = []


def call(path, method="GET", body=None, token=""):
    url = BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"code": exc.code, "message": f"HTTP {exc.code}", "data": None}


def check(name, condition, detail=""):
    results.append((bool(condition), name, detail))
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))


def q(params):
    return "?" + urllib.parse.urlencode(params, doseq=True)


print("=" * 74)
print("HTTP 接口自检（I1~I10）")
print("=" * 74)
print("-" * 74)
print("阶段3：查询接口 I1~I6")
print("-" * 74)

# ---- I1 首页推荐 ----
r = call("/api/home/recommend")
d = r.get("data", {})
check("I1 首页推荐返回统一结构 code=0", r.get("code") == 0)
check("I1 含轮播/分类/推荐门店/推荐酒店",
      len(d.get("banners", [])) >= 3 and len(d.get("categories", [])) == 3
      and len(d.get("shops", [])) >= 4 and len(d.get("hotels", [])) >= 4,
      f"轮播 {len(d.get('banners', []))} / 分类 {len(d.get('categories', []))} / 门店 {len(d.get('shops', []))} / 酒店 {len(d.get('hotels', []))}")
check("I1 首页推荐不含景点字段", "景点" not in json.dumps(d, ensure_ascii=False))

# ---- I2 搜索 ----
r = call("/api/search" + q({"keyword": "火锅"}))
d = r.get("data", {})
check("I2 关键词搜索命中门店", d.get("totalShops", 0) >= 1, f"火锅 -> 门店 {d.get('totalShops')}")
r2 = call("/api/search" + q({"keyword": "青城山"}))
check("I2 关键词搜索命中酒店", r2["data"].get("totalHotels", 0) >= 1, f"青城山 -> 酒店 {r2['data'].get('totalHotels')}")

# ---- I3 门店列表：筛选与排序 ----
base = call("/api/shops")["data"]
food = call("/api/shops" + q({"category": "美食"}))["data"]
leisure = call("/api/shops" + q({"category": "休闲娱乐"}))["data"]
cheap = call("/api/shops" + q({"maxPrice": 90}))["data"]
top = call("/api/shops" + q({"minRating": 4.6}))["data"]
by_rating = call("/api/shops" + q({"sortBy": "rating"}))["data"]["items"]
by_price = call("/api/shops" + q({"sortBy": "priceAsc"}))["data"]["items"]
city_cq = call("/api/shops" + q({"city": "重庆"}))["data"]
city_xa = call("/api/shops" + q({"city": "西安"}))["data"]
check("I3 门店列表返回全部 20 家", base["total"] == 20, f"实际 {base['total']}")
check("I3 城市筛选生效", 0 < city_cq["total"] < base["total"] and 0 < city_xa["total"] < base["total"],
      f"重庆 {city_cq['total']} 家 / 西安 {city_xa['total']} 家")
check("I3 品类筛选生效", food["total"] + leisure["total"] == base["total"],
      f"美食 {food['total']} + 休闲娱乐 {leisure['total']} = {base['total']}")
check("I3 人均价格筛选生效", 0 < cheap["total"] < base["total"], f"人均≤90 -> {cheap['total']} 家")
check("I3 评分筛选生效", 0 < top["total"] < base["total"], f"评分≥4.6 -> {top['total']} 家")
check("I3 评分排序生效", all(by_rating[i]["rating"] >= by_rating[i + 1]["rating"] for i in range(len(by_rating) - 1)),
      f"首位 {by_rating[0]['name']} {by_rating[0]['rating']}")
check("I3 价格排序生效", all(by_price[i]["avgPrice"] <= by_price[i + 1]["avgPrice"] for i in range(len(by_price) - 1)),
      f"最低人均 {by_price[0]['name']} ¥{by_price[0]['avgPrice']}")
check("I3 列表项含评分/人均/标签", all(k in base["items"][0] for k in ("rating", "avgPrice", "tags", "subCategory")))

# ---- I4 门店详情 ----
d = call("/api/shops/S001")["data"]
check("I4 门店详情含套餐与评论", len(d.get("packages", [])) >= 3 and len(d.get("comments", [])) >= 5,
      f"{d['name']}：套餐 {len(d['packages'])} / 评论 {len(d['comments'])}")
check("I4 门店详情含营业时间与地址", bool(d.get("businessHours")) and bool(d.get("address")),
      f"{d.get('businessHours')} | {d.get('address')}")
r = call("/api/shops/S999")
check("I4 门店不存在时返回错误码", r.get("code") == 404, r.get("message"))

# ---- I5 酒店列表：筛选、日历、排序 ----
hbase = call("/api/hotels")["data"]
star5 = call("/api/hotels" + q({"star": 5}))["data"]
price = call("/api/hotels" + q({"minPrice": 300, "maxPrice": 600}))["data"]
fac = call("/api/hotels" + q([("facilities", "室内泳池"), ("facilities", "健身房")]))["data"]
cal = call("/api/hotels" + q({"city": "成都", "checkIn": "2026-10-01", "checkOut": "2026-10-04"}))["data"]
hprice = call("/api/hotels" + q({"sortBy": "priceAsc"}))["data"]["items"]
hrating = call("/api/hotels" + q({"sortBy": "rating"}))["data"]["items"]
check("I5 酒店列表返回全部 16 家", hbase["total"] == 16, f"实际 {hbase['total']}")
check("I5 酒店城市筛选生效", 0 < cal["total"] < hbase["total"], f"成都 -> {cal['total']} 家 / 全部 {hbase['total']} 家")
check("I5 星级筛选生效", 0 < star5["total"] < hbase["total"], f"五星 -> {star5['total']} 家")
check("I5 价格区间筛选生效", 0 < price["total"] < hbase["total"], f"300~600 -> {price['total']} 家")
check("I5 设施多选筛选生效", 0 < fac["total"] < hbase["total"], f"泳池+健身房 -> {fac['total']} 家")
check("I5 日历晚数计算正确（10-01 至 10-04 = 3 晚）", cal.get("nights") == 3, f"nights={cal.get('nights')}")
check("I5 价格排序生效", all(hprice[i]["minPrice"] <= hprice[i + 1]["minPrice"] for i in range(len(hprice) - 1)),
      f"最低价 {hprice[0]['name']} ¥{hprice[0]['minPrice']}")
check("I5 好评优先排序生效", all(hrating[i]["rating"] >= hrating[i + 1]["rating"] for i in range(len(hrating) - 1)),
      f"首位 {hrating[0]['name']} {hrating[0]['rating']}")
check("I5 列表项含星级/价格/服务标签", all(k in hbase["items"][0] for k in ("star", "minPrice", "facilities", "tags")))

# ---- I6 酒店详情 ----
d = call("/api/hotels/H001")["data"]
check("I6 酒店详情含房型与评价", len(d.get("rooms", [])) >= 3 and len(d.get("reviews", [])) >= 5,
      f"{d['name']}：房型 {len(d['rooms'])} / 评价 {len(d['reviews'])}")
check("I6 房型含房价与配套字段", all(k in d["rooms"][0] for k in ("price", "area", "bedType", "breakfast", "remain")))
r = call("/api/hotels/H999")
check("I6 酒店不存在时返回错误码", r.get("code") == 404, r.get("message"))

# ---- 设施选项 ----
fac_list = call("/api/hotels/facilities")["data"]
check("设施选项接口可用", isinstance(fac_list, list) and len(fac_list) >= 6, f"{len(fac_list)} 项")

print("-" * 74)
print("阶段8：写接口与订单闭环 I7~I10（登录后按用户归属）")
print("-" * 74)
try:
    # ---- 未登录访问必须被拒绝（401）----
    anon = call("/api/orders")
    check("I8 未登录访问订单列表被拒绝（401）", anon.get("code") == 401, anon.get("message"))

    # ---- 登录 demo 账号（预置普通用户，名下有 2 条预置订单）----
    login = call("/api/auth/login", method="POST", body={"username": "demo", "password": "123456"})
    TOKEN = (login.get("data") or {}).get("token", "")
    check("登录 demo 账号成功并取得令牌", bool(TOKEN), f"角色 {(login.get('data') or {}).get('user', {}).get('role')}")

    mine = call("/api/orders", token=TOKEN)["data"]
    check("I8 普通用户只看到自己的订单",
          mine["total"] >= 2 and all(o["userId"] == "U001" for o in mine["items"]),
          f"demo 名下 {mine['total']} 条，全部归属 U001（预置 2 条 + 之前自检运行产生的订单）")
    check("I8 看不到其他用户的订单",
          all(o["orderNo"] != "ORD1003" and not o["orderNo"].endswith("1003") for o in mine["items"]),
          "lisi 的订单未出现在 demo 列表中")

    before = mine

    body = {"type": "shop", "targetId": "S001", "itemId": "S001-P02", "name": "答辩演示",
            "phone": "13800008888", "bookTime": "2026-10-08", "count": 2}
    created = call("/api/orders", method="POST", body=body, token=TOKEN)
    check("I7 模拟下单返回成功与订单号", created.get("code") == 0 and created["data"].get("orderNo"),
          f"订单号 {created.get('data', {}).get('orderNo')}")
    order_no = created["data"]["orderNo"]
    check("I7 新订单归属当前登录用户", created["data"].get("userId") == "U001", created["data"].get("userId"))

    after = call("/api/orders", token=TOKEN)["data"]
    check("I7 下单后订单追加至内存集合", after["total"] == before["total"] + 1,
          f"{before['total']} -> {after['total']}")

    detail = call(f"/api/orders/{order_no}", token=TOKEN)["data"]
    check("I9 订单详情返回完整字段", detail["orderNo"] == order_no and detail["status"] == "待使用",
          f"{detail['targetName']} / {detail['itemName']} / ¥{detail['amount']}")

    hbody = {"type": "hotel", "targetId": "H001", "itemId": "H001-R01", "name": "答辩演示",
             "phone": "13800008888", "bookTime": "2026-10-08", "checkOut": "2026-10-10", "count": 1}
    hcreated = call("/api/orders", method="POST", body=hbody, token=TOKEN)["data"]
    check("I7 酒店订单自动计算晚数与总价", hcreated["nights"] == 2 and hcreated["amount"] > 0,
          f"{hcreated['nights']} 晚 / ¥{hcreated['amount']}")

    # ---- 越权：用 lisi 账号访问 demo 的订单必须被拒绝（403）----
    lisi = call("/api/auth/login", method="POST", body={"username": "lisi", "password": "123456"})
    LISI = (lisi.get("data") or {}).get("token", "")
    check("lisi 账号可登录", bool(LISI))
    other = call(f"/api/orders/{order_no}", token=LISI)
    check("越权查看他人订单被拒绝（403）", other.get("code") == 403, other.get("message"))
    other_cancel = call(f"/api/orders/{order_no}/cancel", method="POST", token=LISI)
    check("越权取消他人订单被拒绝（403）", other_cancel.get("code") == 403, other_cancel.get("message"))
    lisi_mine = call("/api/orders", token=LISI)["data"]
    check("lisi 只看到自己的 1 条订单", lisi_mine["total"] == 1 and lisi_mine["items"][0]["userId"] == "U004",
          f"{lisi_mine['total']} 条")

    cancelled = call(f"/api/orders/{order_no}/cancel", method="POST", token=TOKEN)["data"]
    check("I10 取消后状态变为「已取消」", cancelled["status"] == "已取消", f"{order_no} -> {cancelled['status']}")
    again = call(f"/api/orders/{order_no}", token=TOKEN)["data"]
    check("I10 状态变更已写入内存（复查仍为已取消）", again["status"] == "已取消")
    bad = call("/api/orders/ORD-NOT-EXIST", token=TOKEN)
    check("I9 订单不存在时返回错误码", bad.get("code") == 404, bad.get("message"))
except urllib.error.HTTPError as e:
    check("阶段8 接口可用", False, f"HTTP {e.code}：{e.reason}（若接口尚未实现属预期）")

print("=" * 74)
failed = [r for r in results if not r[0]]
print(f"接口自检结果：{len(results) - len(failed)} 项通过 / {len(failed)} 项失败")
for _, name, detail in failed:
    print(f"  FAIL: {name} {detail}")
sys.exit(1 if failed else 0)
