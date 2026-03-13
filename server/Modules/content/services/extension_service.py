"""
Content 浏览器扩展服务 - 处理浏览器扩展相关业务逻辑
"""

import json
from typing import Any

from fastapi.responses import JSONResponse
from sqlmodel import select

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import success
from Modules.common.libs.time.utils import now
from Modules.content.models.content_platform_account import ContentPlatformAccount

# 平台域名映射配置
PLATFORM_DOMAIN_MAP = {
    "zhihu": {
        "name": "知乎",
        "domains": ["zhihu.com", "www.zhihu.com"],
        "icon": "https://static.zhihu.com/heifetz/favicon.ico",
    },
    "xiaohongshu": {
        "name": "小红书",
        "domains": [
            "xiaohongshu.com",
            "www.xiaohongshu.com",
            "edith.xiaohongshu.com",
            "fe.xiaohongshu.com",
            "xhslink.com",
        ],
        "icon": "https://www.xiaohongshu.com/favicon.ico",
    },
    "toutiao": {
        "name": "今日头条",
        "domains": [
            "toutiao.com",
            "www.toutiao.com",
            "mp.toutiao.com",
            "zijieapi.com",
            "mon.zijieapi.com",
            "toutiaostatic.com",
        ],
        "icon": "https://www.toutiao.com/favicon.ico",
    },
}


class ExtensionService:
    """浏览器扩展服务 - 处理浏览器扩展相关业务逻辑"""

    def __init__(self):
        pass

    async def get_platform_list(self) -> JSONResponse:
        """
        获取平台列表

        返回所有支持的平台配置
        """
        platforms = []
        for platform_id, config in PLATFORM_DOMAIN_MAP.items():
            platforms.append(
                {
                    "id": platform_id,
                    "name": config["name"],
                    "domains": config["domains"],
                    "icon": config.get("icon", ""),
                }
            )

        return success(data=platforms, message="获取成功")

    async def import_cookies(
        self,
        cookies_data: list[dict[str, Any]],
        user_id: int = 0,
        user_agent: str | None = None,
    ) -> JSONResponse:
        """从浏览器扩展导入Cookies

        Args:
            cookies_data: Cookie数据列表
            user_id: 当前用户ID
            user_agent: 浏览器 User-Agent（从浏览器扩展获取）

        Returns:
            导入结果
        """

        # 按平台分组Cookies（而不是按域名）
        cookies_by_platform: dict[str, list[dict[str, Any]]] = {}
        for cookie in cookies_data:
            domain = cookie.get("domain", "")
            # 识别平台
            platform = self._identify_platform(domain.lstrip("."))
            if not platform:
                continue  # 跳过未知平台的 Cookie

            if platform not in cookies_by_platform:
                cookies_by_platform[platform] = []
            cookies_by_platform[platform].append(cookie)

        # 更新或创建账号
        updated_accounts = []
        created_accounts = []
        errors = []

        async with get_async_session() as session:
            for platform, cookies in cookies_by_platform.items():
                # 查找现有账号
                existing = await session.execute(
                    select(ContentPlatformAccount).where(
                        ContentPlatformAccount.platform == platform
                    )
                )
                account = existing.scalar_one_or_none()

                # 构建Cookie JSON（合并该平台的所有 Cookie）
                cookies_json = json.dumps(cookies, ensure_ascii=False)

                if account:
                    # 更新现有账号
                    account.cookies = cookies_json
                    if user_agent:  # 更新 User-Agent（如果提供了）
                        account.user_agent = user_agent
                    account.last_verified = now()
                    account.status = 1  # 标记为有效
                    account.updated_at = now()
                    updated_accounts.append(
                        {
                            "id": account.id,
                            "platform": platform,
                            "account_name": account.account_name,
                            "cookies_count": len(cookies),
                        }
                    )
                else:
                    # 创建新账号
                    # 尝试从Cookie中提取用户名
                    account_name = self._extract_account_name(platform, cookies)

                    new_account = ContentPlatformAccount(
                        platform=platform,
                        account_name=account_name or f"{platform}_账号",
                        cookies=cookies_json,
                        user_agent=user_agent,  # 使用浏览器扩展获取的 UA
                        status=1,
                        last_verified=now(),
                        created_by=user_id,
                        created_at=now(),
                        updated_at=now(),
                    )
                    session.add(new_account)
                    await session.flush()  # 获取生成的ID

                    created_accounts.append(
                        {
                            "id": new_account.id,
                            "platform": platform,
                            "account_name": new_account.account_name,
                            "cookies_count": len(cookies),
                        }
                    )

            await session.commit()

        return success(
            {
                "message": "Cookies导入成功",
                "updated": updated_accounts,
                "created": created_accounts,
                "errors": errors,
                "summary": {
                    "updated_count": len(updated_accounts),
                    "created_count": len(created_accounts),
                    "error_count": len(errors),
                },
            }
        )

    def _identify_platform(self, domain: str) -> str | None:
        """根据域名识别平台

        Args:
            domain: 域名

        Returns:
            平台标识
        """
        for platform_id, config in PLATFORM_DOMAIN_MAP.items():
            for platform_domain in config["domains"]:
                if platform_domain in domain or domain in platform_domain:
                    return platform_id
        return None

    def _extract_account_name(
        self, platform: str, cookies: list[dict[str, Any]]
    ) -> str | None:
        """从Cookie中提取账号名称

        Args:
            platform: 平台标识
            cookies: Cookie列表

        Returns:
            账号名称
        """
        # 根据不同平台提取用户名的Cookie名称
        username_cookies = {
            "zhihu": ["z_c0"],
            "xiaohongshu": ["a1", "web_session"],
            "toutiao": ["sessionid", "sid_tt"],
        }

        key_names = username_cookies.get(platform, [])
        for cookie in cookies:
            if cookie.get("name") in key_names:
                # 使用Cookie名称的前8位作为标识
                return f"{platform}_{cookie.get('name', 'user')[:8]}"
        return None
