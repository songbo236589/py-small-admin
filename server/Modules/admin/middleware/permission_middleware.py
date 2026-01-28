"""
Admin 权限验证中间件 - 简化版本
提供基础的权限验证功能
"""

import jwt
from fastapi import HTTPException, Request

from Modules.common.libs.config.config import Config
from Modules.common.libs.jwt.utils import jwt_verify_token


def require_authentication():
    """
    仅需要登录验证的依赖函数

    Returns:
        依赖函数
    """

    async def auth_dependency(request: Request) -> dict | list:
        """登录验证依赖函数"""
        try:
            # 对于特殊路径，使用API密钥验证
            x_api_key = request.headers.get("X-API-Key")

            admin_x_api_key = Config.get("app.admin_x_api_key")

            # 验证API密钥
            if x_api_key != admin_x_api_key:
                raise HTTPException(status_code=455, detail="API密钥无效")

            path_arr = [
                "/api/admin/common/login",
                "/api/admin/common/refresh",
                "/api/admin/common/generate_captcha",
                "/api/admin/common/verify_captcha",
                "/api/admin/common/get_system_config",
            ]
            path = request.url.path

            # 判断路径是否在需要特殊处理的路径数组中
            if path not in path_arr:
                # 对于不在path_arr中的路径，使用JWT令牌验证
                # 获取Authorization头
                authorization = request.headers.get("authorization")
                if not authorization or not authorization.startswith("Bearer "):
                    raise HTTPException(status_code=477, detail="未提供有效的访问令牌")

                access_token = authorization[7:]  # 移除 "Bearer " 前缀

                # 验证令牌
                payload = await jwt_verify_token(access_token, token_type="access")

                # 设置用户信息到请求状态
                request.state.user_id = payload.get("sub")  # JWT标准使用sub作为用户ID
                request.state.username = payload.get("username")
                request.state.user = payload
                return payload

            return {}

        except (jwt.InvalidTokenError, ValueError) as e:
            # 捕获JWT相关异常
            raise HTTPException(status_code=477, detail="访问令牌无效或已过期") from e
        except Exception as e:
            # 捕获其他未预期异常
            raise HTTPException(status_code=477, detail="认证服务异常") from e

    return auth_dependency
