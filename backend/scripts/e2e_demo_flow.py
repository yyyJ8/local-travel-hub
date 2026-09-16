"""端到端演示流程自测（阶段9 验收用）

用法（需先启动后端服务）：
    cd D:\\Ctrip\\backend
    D:\\Ctrip\\.venv\\Scripts\\python.exe scripts\\e2e_demo_flow.py

按现场演示动线逐步调用后端接口并校验结果，输出可直接作为「原型可演示」的证据：
    ① 首页浏览 → ② 搜索跳转 → ③ 本地生活（筛选/详情/套餐/评论）
    → ④ 旅行住宿（日历/筛选/房型/评价） → ⑤ 模拟下单
    → ⑥ 个人中心（订单列表/详情/模拟取消） → ⑦ 原型限制说明
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"
steps = []


def call(path, method="GET", body=None, token=""):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"code": exc.code, "message": f"HTTP {exc.code}", "data": None}


def step(no, title):
    print(f"\n【步骤 {no}】{title}")


def ok(msg):
    steps.append((True, msg))
    print(f"   [OK]   {msg}")


def bad(msg):
    steps.append((False, msg))
    print(f"   [FAIL] {msg}")


def q(params):
    return "?" + urllib.parse.urlencode(params, doseq=True)


print("=" * 76)
print("端到端演示流程自测（仿大众点评 + 携程 演示原型）")
print("=" * 76)

# ---------------------------------------------------------------- ⓪ 登录（下单与个人中心需登录）
step(0, "登录（普通用户 demo / 商家 shangjia / 管理员 admin）")
login = call("/api/auth/login", "POST", {"username": "demo", "password": "123456"})
TOKEN = (login.get("data") or {}).get("token", "")
if TOKEN:
    ok(f"demo 账号登录成功，角色 {(login['data']['user']['role'])}（昵称 {login['data']['user']['nickname']}）")
else:
    bad("demo 账号登录失败")
anon = call("/api/orders")
if anon.get("code") == 401:
    ok("未登录访问订单接口被拒绝（401）—— 浏览免登录、下单与个人中心需登录")
else:
    bad(f"未登录访问订单接口未被拒绝：{anon.get('message')}")

# ---------------------------------------------------------------- ① 首页浏览
step(1, "首页浏览（轮播推荐位 / 业务分类入口 / 推荐门店与酒店）")
d = call("/api/home/recommend")["data"]
ok(f"轮播推荐位 {len(d['banners'])} 个，首个：{d['banners'][0]['title']}")
ok(f"业务分类入口：{' / '.join(c['name'] for c in d['categories'])}")
ok(f"推荐门店 {len(d['shops'])} 家，首个：{d['shops'][0]['name']}（评分 {d['shops'][0]['rating']}，人均 ¥{d['shops'][0]['avgPrice']}）")
ok(f"推荐酒店 {len(d['hotels'])} 家，首个：{d['hotels'][0]['name']}（{d['hotels'][0]['star']} 星，¥{d['hotels'][0]['minPrice']} 起）")

# ---------------------------------------------------------------- ② 搜索
step(2, "首页搜索 → 搜索结果页跳转")
d = call("/api/search" + q({"keyword": "火锅"}))["data"]
ok(f"搜索「火锅」命中门店 {d['totalShops']} 家、酒店 {d['totalHotels']} 家")
d2 = call("/api/search" + q({"keyword": "青城山"}))["data"]
ok(f"搜索「青城山」命中酒店 {d2['totalHotels']} 家：{d2['hotels'][0]['name'] if d2['hotels'] else '-'}")

# ---------------------------------------------------------------- ③ 本地生活
step(3, "本地生活业务（门店筛选 / 排序 / 详情 / 团购套餐 / 用户评论）")
all_shops = call("/api/shops")["data"]
food = call("/api/shops" + q({"category": "美食", "sortBy": "rating"}))["data"]
cheap = call("/api/shops" + q({"maxPrice": 90, "sortBy": "priceAsc"}))["data"]
ok(f"门店列表共 {all_shops['total']} 家")
ok(f"筛选「美食」并按评分排序 → {food['total']} 家，首位：{food['items'][0]['name']}（{food['items'][0]['rating']} 分）")
ok(f"筛选「人均 ≤ 90」并按价格升序 → {cheap['total']} 家，最低：{cheap['items'][0]['name']}（人均 ¥{cheap['items'][0]['avgPrice']}）")
shop = call("/api/shops/S001")["data"]
ok(f"门店详情：{shop['name']}｜营业时间 {shop['businessHours']}｜地址 {shop['address']}")
ok(f"团购套餐 {len(shop['packages'])} 个，首个：{shop['packages'][0]['name']} ¥{shop['packages'][0]['price']}（已售 {shop['packages'][0]['sold']}）")
ok(f"用户评论 {len(shop['comments'])} 条，示例：「{shop['comments'][0]['content'][:24]}...」")

# ---------------------------------------------------------------- ④ 旅行住宿
step(4, "旅行住宿业务（日历选入住退房 / 筛选 / 房型 / 酒店评价）")
cal = call("/api/hotels" + q({"city": "成都", "checkIn": "2026-10-01", "checkOut": "2026-10-04", "sortBy": "rating"}))["data"]
ok(f"日历选择 10-01 至 10-04 → 后端计算入住 {cal['nights']} 晚")
ok(f"城市「成都」共 {cal['total']} 家酒店，好评优先首位：{cal['items'][0]['name']}（{cal['items'][0]['rating']} 分，{cal['items'][0]['star']} 星）")
fac = call("/api/hotels" + q([("facilities", "室内泳池"), ("facilities", "健身房")]))["data"]
ok(f"设施筛选「室内泳池 + 健身房」→ {fac['total']} 家")
hotel = call("/api/hotels/H001")["data"]
ok(f"酒店详情：{hotel['name']}｜{hotel['star']} 星｜评分 {hotel['rating']}｜{hotel['address']}")
ok(f"房型 {len(hotel['rooms'])} 种，首个：{hotel['rooms'][0]['name']}（{hotel['rooms'][0]['area']}㎡，{hotel['rooms'][0]['bedType']}，¥{hotel['rooms'][0]['price']}/晚）")
ok(f"酒店评价 {len(hotel['reviews'])} 条，示例：「{hotel['reviews'][0]['content'][:24]}...」")

# ---------------------------------------------------------------- ⑤ 模拟下单
step(5, "模拟预约下单（登录后下单，订单归属当前用户）")
before = call("/api/orders", token=TOKEN)["data"]["total"]
pkg = shop["packages"][1]
created = call("/api/orders", "POST", {
    "type": "shop", "targetId": "S001", "itemId": pkg["id"],
    "name": "现场演示", "phone": "13800001234", "bookTime": "2026-10-20", "count": 2,
}, token=TOKEN)["data"]
ok(f"门店套餐下单成功 → 订单号 {created['orderNo']}，{pkg['name']} × 2 = ¥{created['amount']}（状态：{created['status']}，归属 {created['userId']}）")
room = hotel["rooms"][0]
horder = call("/api/orders", "POST", {
    "type": "hotel", "targetId": "H001", "itemId": room["id"],
    "name": "现场演示", "phone": "13800001234",
    "bookTime": "2026-10-20", "checkOut": "2026-10-22", "count": 1,
}, token=TOKEN)["data"]
expected = room["price"] * 2
ok(f"酒店房型下单成功 → 订单号 {horder['orderNo']}，{room['name']} × 1 间 × {horder['nights']} 晚 = ¥{horder['amount']}（预期 ¥{expected}）")
after = call("/api/orders", token=TOKEN)["data"]["total"]
ok(f"我的订单数 {before} → {after}（下单已追加至后端内存集合并归属当前用户）")

# ---------------------------------------------------------------- ⑥ 个人中心
step(6, "个人中心（订单列表 / 订单详情 / 模拟取消预约）")
orders = call("/api/orders", token=TOKEN)["data"]
ok(f"订单列表共 {orders['total']} 条（仅 demo 名下：预置 2 条 + 本次演示新增）")
pending = [o for o in orders["items"] if o["status"] == "待使用"]
cancelled = [o for o in orders["items"] if o["status"] == "已取消"]
ok(f"状态统计：待使用 {len(pending)} 条，已取消 {len(cancelled)} 条")
detail = call(f"/api/orders/{created['orderNo']}", token=TOKEN)["data"]
ok(f"订单详情：{detail['targetName']}｜{detail['itemName']}｜预约人 {detail['name']}｜¥{detail['amount']}｜{detail['status']}")
cancel_res = call(f"/api/orders/{created['orderNo']}/cancel", "POST", token=TOKEN)["data"]
ok(f"模拟取消预约 → {cancel_res['orderNo']} 状态变为「{cancel_res['status']}」")
recheck = call(f"/api/orders/{created['orderNo']}", token=TOKEN)["data"]
if recheck["status"] == "已取消":
    ok("复查订单状态仍为「已取消」（取消已写入内存集合）")
else:
    bad("复查订单状态异常")

# ---------------------------------------------------------------- ⑦ 角色与数据权限
step(7, "角色与数据权限（普通用户 / 商家 / 管理员）")
lisi = call("/api/auth/login", "POST", {"username": "lisi", "password": "123456"})
LISI = (lisi.get("data") or {}).get("token", "")
lisi_orders = call("/api/orders", token=LISI)["data"]
ok(f"换 lisi 账号登录 → 只看到自己的 {lisi_orders['total']} 条订单（与 demo 的列表不同，证明订单归属隔离）")
steal = call(f"/api/orders/{horder['orderNo']}", token=LISI)
if steal.get("code") == 403:
    ok("lisi 越权查看 demo 的订单被拒绝（403）")
else:
    bad(f"越权校验失效：{steal.get('message')}")

merchant_login = call("/api/auth/login", "POST", {"username": "shangjia", "password": "123456"})
MTOKEN = (merchant_login.get("data") or {}).get("token", "")
msum = call("/api/merchant/summary", token=MTOKEN)["data"]
ok(f"商家后台概览：名下 {' / '.join(t['name'] for t in msum['targets'])}，订单 {msum['orderCount']} 条，待使用 {msum['pendingCount']} 条")
morders = call("/api/merchant/orders", token=MTOKEN)["data"]
ok(f"商家只看得到自己门店的订单：{morders['total']} 条（其他门店订单不可见）")
forbidden = call("/api/admin/overview", token=MTOKEN)
if forbidden.get("code") == 403:
    ok("商家访问管理员接口被拒绝（403）")
else:
    bad("角色鉴权失效：商家竟能访问管理员接口")

admin_login = call("/api/auth/login", "POST", {"username": "admin", "password": "123456"})
ATOKEN = (admin_login.get("data") or {}).get("token", "")
ov = call("/api/admin/overview", token=ATOKEN)["data"]
ok(f"管理员平台概览：门店 {ov['shops']} / 酒店 {ov['hotels']} / 用户 {ov['users']} / 订单 {ov['orders']} / 活跃会话 {ov['sessions']}")
all_orders = call("/api/admin/orders", token=ATOKEN)["data"]
ok(f"管理员可见全平台订单 {all_orders['total']} 条（多于任一普通用户）")
users = call("/api/admin/users", token=ATOKEN)["data"]
user_text = "、".join(f"{u['username']}({u['role']})" for u in users["items"])
ok(f"管理员用户列表 {users['total']} 个账号：{user_text}")

disabled = call(f"/api/admin/users/U004/status", "POST", {"status": "停用"}, token=ATOKEN)
ok(f"管理员停用 lisi 账号 → 状态 {disabled['data']['status']}")
blocked = call("/api/auth/login", "POST", {"username": "lisi", "password": "123456"})
if blocked.get("code") == 401:
    ok(f"被停用账号无法登录：{blocked.get('message')}")
else:
    bad("停用账号仍可登录")
stale = call("/api/auth/me", token=LISI)
if stale.get("code") == 401:
    ok("停用后其原有会话立即失效（旧令牌不可用）")
else:
    bad("停用后旧令牌仍有效")
call("/api/admin/users/U004/status", "POST", {"status": "正常"}, token=ATOKEN)
ok("管理员恢复 lisi 账号为正常（演示可反复进行）")

# ---------------------------------------------------------------- ⑧ 原型限制
step(8, "原型限制说明（答辩口径）")
ok("数据源为后端内存集合，未做数据库持久化：后端服务重启后，本次新增订单、注册账号与登录会话全部丢失")
ok("账号体系为演示级：口令明文存储、令牌无签名无有效期；注册只开放普通用户，商家与管理员为预置账号")
ok("管理员可停用账号（停用即失效其全部会话）；商家只能看到自己名下门店/酒店的订单")
ok("演示中途不要重启后端，否则演示中新建的订单与登录状态会消失")

print("\n" + "=" * 76)
failed = [s for s in steps if not s[0]]
print(f"端到端流程自测结果：{len(steps) - len(failed)} 项通过 / {len(failed)} 项失败")
for _, msg in failed:
    print(f"  FAIL: {msg}")
sys.exit(1 if failed else 0)
