"""统一响应结构：{code, message, data}

课程原型说明：全部接口统一返回该结构，前端 Axios 拦截器统一解包。
"""
from typing import Any


def ok(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "message": message, "data": data}


def fail(message: str = "error", code: int = 1, data: Any = None) -> dict:
    """失败响应（原型阶段仅用于资源不存在等场景）"""
    return {"code": code, "message": message, "data": data}
