"""
URL辅助工具

用于获取当前请求的基础URL，支持多种部署场景
"""

from fastapi import Request


def get_base_url(request: Request) -> str:
    """
    获取当前请求的基础URL

    支持多种部署场景：
    1. 直接访问FastAPI应用
    2. 使用Nginx反向代理
    3. 使用CDN
    4. 无Request对象时从配置降级

    Args:
        request: FastAPI Request对象

    Returns:
        str: 完整的基础URL，如 https://example.com:8009


    """
    # 优先从Request对象获取
    # FastAPI的base_url会自动处理X-Forwarded-*头
    base_url = str(request.base_url).rstrip("/")
    return base_url
