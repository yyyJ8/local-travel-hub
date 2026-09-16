"""会话令牌工具（演示级认证）

原型说明（必须写进报告与答辩口径）：
1. 令牌为随机字符串，**不做 JWT 签名、不做有效期、不做刷新**；
2. 会话保存在后端内存字典中，**服务重启后全部失效，需要重新登录**（与内存数据源定位一致）；
3. 口令为明文比对，生产版本必须替换为加盐哈希 + 正规令牌方案。
"""
import secrets

TOKEN_BYTES = 24


def new_token() -> str:
    """生成随机会话令牌。"""
    return secrets.token_urlsafe(TOKEN_BYTES)


def parse_bearer(authorization: str) -> str:
    """从 Authorization 请求头解析令牌。

    兼容两种写法：`Bearer <token>` 与直接传 `<token>`（便于用 /docs 调试）。
    """
    if not authorization:
        return ""
    value = authorization.strip()
    if value.lower().startswith("bearer "):
        return value[7:].strip()
    return value
