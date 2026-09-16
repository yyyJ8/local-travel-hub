"""认证接口自检（登录/注册 step1 验收用）

用法（需先启动后端服务）：
    cd D:\\Ctrip\\backend
    D:\\Ctrip\\.venv\\Scripts\\python.exe scripts\\check_auth.py

覆盖：注册（含重复用户名、弱密码、手机号格式）、登录（含错误口令、账号停用）、
      me（含无令牌、伪令牌）、注销（注销后令牌失效）、预置三角色账号、密码不外泄。
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
results = []


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
    except urllib.error.HTTPError as exc:  # 便于区分"接口报错"与业务失败
        return {"code": exc.code, "message": f"HTTP {exc.code}", "data": None}


def check(name, condition, detail=""):
    results.append((bool(condition), name, detail))
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))


print("=" * 74)
print("认证接口自检 A1~A4（演示级账号体系）")
print("=" * 74)

# ---------------------------------------------------------------- A1 注册
print("\n--- A1 注册 ---")
suffix = str(int(time.time()))[-6:]
new_user = f"shiyong{suffix}"
r = call("/api/auth/register", "POST", {"username": new_user, "password": "abc123456",
                                        "nickname": "演示注册用户", "phone": "13900001234"})
d = r.get("data") or {}
check("注册成功并直接返回令牌", r.get("code") == 0 and d.get("token"), f"用户 {d.get('user', {}).get('username')}")
check("注册用户角色固定为 user", d.get("user", {}).get("role") == "user", d.get("user", {}).get("role"))
check("注册返回体不含密码字段", "password" not in json.dumps(d, ensure_ascii=False))
reg_token = d.get("token", "")

r = call("/api/auth/register", "POST", {"username": new_user, "password": "abc123456"})
check("重复用户名被拒绝（409）", r.get("code") == 409, r.get("message"))

r = call("/api/auth/register", "POST", {"username": "ab", "password": "abc123456"})
check("用户名过短被拒绝（400）", r.get("code") == 400, r.get("message"))

r = call("/api/auth/register", "POST", {"username": f"weak{suffix}", "password": "123"})
check("弱密码被拒绝（400）", r.get("code") == 400, r.get("message"))

r = call("/api/auth/register", "POST", {"username": f"phone{suffix}", "password": "abc123456", "phone": "123"})
check("手机号格式非法被拒绝（400）", r.get("code") == 400, r.get("message"))

# ---------------------------------------------------------------- A2 登录
print("\n--- A2 登录 ---")
r = call("/api/auth/login", "POST", {"username": new_user, "password": "abc123456"})
d = r.get("data") or {}
check("新注册账号可登录", r.get("code") == 0 and d.get("token"), f"token 前缀 {str(d.get('token'))[:8]}")
check("登录返回用户信息且不含密码", d.get("user", {}).get("username") == new_user and "password" not in json.dumps(d))

r = call("/api/auth/login", "POST", {"username": new_user, "password": "wrong-password"})
check("错误口令被拒绝（401）", r.get("code") == 401, r.get("message"))

r = call("/api/auth/login", "POST", {"username": "not-exist-user", "password": "abc123456"})
check("不存在账号被拒绝（401）", r.get("code") == 401, r.get("message"))

presets = {"demo": "user", "shangjia": "merchant", "admin": "admin"}
tokens = {}
for name, role in presets.items():
    r = call("/api/auth/login", "POST", {"username": name, "password": "123456"})
    d = r.get("data") or {}
    tokens[name] = d.get("token", "")
    check(f"预置账号 {name} 可登录且角色={role}", r.get("code") == 0 and d.get("user", {}).get("role") == role,
          f"角色 {d.get('user', {}).get('role')}")
check("商家账号绑定商家 ID M001", call("/api/auth/me", token=tokens["shangjia"])["data"].get("merchantId") == "M001")

# ---------------------------------------------------------------- A4 当前用户
print("\n--- A4 当前登录用户 ---")
r = call("/api/auth/me", token=tokens["demo"])
check("带令牌可取当前用户", r.get("code") == 0 and r["data"]["username"] == "demo", r["data"].get("nickname"))
check("当前用户信息不含密码", "password" not in json.dumps(r.get("data"), ensure_ascii=False))
r = call("/api/auth/me")
check("不带令牌访问被拒绝（401）", r.get("code") == 401, r.get("message"))
r = call("/api/auth/me", token="fake-token-123456")
check("伪造令牌访问被拒绝（401）", r.get("code") == 401, r.get("message"))

# ---------------------------------------------------------------- A3 注销
print("\n--- A3 注销 ---")
r = call("/api/auth/logout", "POST", token=reg_token)
check("注销成功", r.get("code") == 0, r.get("message"))
r = call("/api/auth/me", token=reg_token)
check("注销后原令牌立即失效（401）", r.get("code") == 401, r.get("message"))
r = call("/api/auth/logout", "POST", token=reg_token)
check("重复注销被拒绝（401）", r.get("code") == 401, r.get("message"))

# ---------------------------------------------------------------- 统计与账号状态
print("\n--- 内存数据统计 ---")
st = call("/api/meta/stats")["data"]
check("统计接口包含用户数与角色分布",
      st.get("users", 0) >= 4 and st.get("usersByRole", {}).get("admin") == 1,
      f"users={st.get('users')} 分布={st.get('usersByRole')} 活跃会话={st.get('sessions')}")

# ---------------------------------------------------------------- 角色与数据权限（step2）
print("\n--- 角色与数据权限（普通用户 / 商家 / 管理员）---")
r = call("/api/merchant/summary", token=tokens["demo"])
check("普通用户访问商家接口被拒绝（403）", r.get("code") == 403, r.get("message"))
r = call("/api/admin/overview", token=tokens["demo"])
check("普通用户访问管理员接口被拒绝（403）", r.get("code") == 403, r.get("message"))

r = call("/api/merchant/summary", token=tokens["shangjia"])
targets = (r.get("data") or {}).get("targets", [])
check("商家可查看自己名下门店概览（S001）",
      r.get("code") == 0 and any(t["id"] == "S001" for t in targets),
      f"名下 {len(targets)} 个：{[t['id'] for t in targets]}")

r = call("/api/merchant/orders", token=tokens["shangjia"])
morders = (r.get("data") or {}).get("items", [])
check("商家订单只包含自己门店产生的订单",
      r.get("code") == 0 and all(o["targetId"] == "S001" for o in morders),
      f"{len(morders)} 条，门店集合 {sorted({o['targetId'] for o in morders})}")

r = call("/api/admin/users", token=tokens["shangjia"])
check("商家访问管理员接口被拒绝（403）", r.get("code") == 403, r.get("message"))

before_hours = call("/api/shops/S002")["data"]["businessHours"]
r = call("/api/merchant/profile", "PUT", {"businessHours": "09:00 - 23:00"}, token=tokens["shangjia"])
check("商家可维护自己门店的营业时间", r.get("code") == 0 and r["data"].get("updated") == 1, str(r.get("data")))
check("营业时间已更新（内存生效）",
      call("/api/shops/S001")["data"]["businessHours"] == "09:00 - 23:00",
      call("/api/shops/S001")["data"]["businessHours"])
check("其他门店未被改动（越权隔离）",
      call("/api/shops/S002")["data"]["businessHours"] == before_hours,
      f"S002 仍为 {before_hours}")
r = call("/api/merchant/profile", "PUT", {"businessHours": ""}, token=tokens["shangjia"])
check("商家维护空内容被拒绝（400）", r.get("code") == 400, r.get("message"))
# 还原演示数据
call("/api/merchant/profile", "PUT", {"businessHours": before_hours}, token=tokens["shangjia"])

r = call("/api/admin/overview", token=tokens["admin"])
check("管理员可查看平台概览", r.get("code") == 0 and r["data"]["shops"] == 20 and r["data"]["users"] >= 4,
      f"门店 {r['data']['shops']} / 用户 {r['data']['users']} / 订单 {r['data']['orders']}")
r = call("/api/admin/users", token=tokens["admin"])
check("管理员可查看用户列表且不含密码字段",
      r.get("code") == 0 and r["data"]["total"] >= 4 and all("password" not in json.dumps(u) for u in r["data"]["items"]),
      f"{r['data']['total']} 个账号")
r = call("/api/admin/orders", token=tokens["admin"])
check("管理员可查看全平台订单", r.get("code") == 0 and r["data"]["total"] >= 3, f"{r['data']['total']} 条")

r = call("/api/admin/users/U004/status", "POST", {"status": "停用"}, token=tokens["admin"])
check("管理员可停用账号", r.get("code") == 0 and r["data"]["status"] == "停用", str(r.get("data")))
r = call("/api/auth/login", "POST", {"username": "lisi", "password": "123456"})
check("被停用账号无法登录（401）", r.get("code") == 401, r.get("message"))
r = call("/api/admin/users/U003/status", "POST", {"status": "停用"}, token=tokens["admin"])
check("管理员不能停用自己（400）", r.get("code") == 400, r.get("message"))
r = call("/api/admin/users/U999/status", "POST", {"status": "停用"}, token=tokens["admin"])
check("停用不存在的账号返回 404", r.get("code") == 404, r.get("message"))
r = call("/api/admin/users/U004/status", "POST", {"status": "正常"}, token=tokens["admin"])
check("管理员可恢复账号为正常", r.get("code") == 0 and r["data"]["status"] == "正常")
r = call("/api/auth/login", "POST", {"username": "lisi", "password": "123456"})
check("恢复后 lisi 可正常登录", r.get("code") == 0, str(r.get("code")))

print("=" * 74)
failed = [r for r in results if not r[0]]
print(f"认证自检结果：{len(results) - len(failed)} 项通过 / {len(failed)} 项失败")
for _, name, detail in failed:
    print(f"  FAIL: {name} {detail}")
sys.exit(1 if failed else 0)
