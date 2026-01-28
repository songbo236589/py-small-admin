"""
系统配置服务 - 负责系统配置相关的业务逻辑
"""

import json

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlmodel import select

from Modules.admin.models.admin_sys_config import AdminSysConfig
from Modules.admin.models.admin_upload import AdminUpload
from Modules.common.libs.cache import get_async_cache_service
from Modules.common.libs.config.config import Config
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime, now
from Modules.common.services.base_service import BaseService
from Modules.common.utils.url_helper import get_base_url


class SysConfigService(BaseService):
    """系统配置服务 - 负责系统配置相关的业务逻辑"""

    async def get_config_by_group(
        self, group_code: str, request: Request | None = None, ttl: int = 3600
    ) -> dict:
        """
        根据分组代码获取配置（带缓存）

        Args:
            group_code: 配置分组代码
            ttl: 缓存过期时间（秒），默认为 3600 秒（1 小时）

        Returns:
            配置字典，键为 config_key，值为转换后的配置值
        """
        cache_key = f"sys_config:group:{group_code}"
        cache = get_async_cache_service()

        # 定义异步工厂函数
        async def load_config():
            return await self._load_config_from_db(group_code, request)

        # 使用 get_or_set 方法实现缓存逻辑
        return await cache.get_or_set(cache_key, load_config, ttl=ttl)

    async def set_config_by_group(
        self, group_code: str, request: Request | None = None, ttl: int = 3600
    ) -> bool:
        """
        手动设置配置到缓存（用于预热缓存或刷新缓存）

        Args:
            group_code: 配置分组代码
            ttl: 缓存过期时间（秒），默认为 3600 秒（1 小时）

        Returns:
            是否设置成功
        """
        cache_key = f"sys_config:group:{group_code}"
        cache = get_async_cache_service()

        # 从数据库加载配置
        config_data = await self._load_config_from_db(group_code, request)

        # 设置到缓存
        return await cache.set(cache_key, config_data, ttl=ttl)

    async def clear_config_cache(self, group_code: str) -> bool:
        """
        清除指定分组的配置缓存

        Args:
            group_code: 配置分组代码

        Returns:
            是否清除成功
        """
        cache_key = f"sys_config:group:{group_code}"
        cache = get_async_cache_service()

        return await cache.delete(cache_key)

    async def _load_config_from_db(
        self, group_code: str, request: Request | None = None
    ) -> dict:
        """
        从数据库加载配置信息

        Args:
            group_code: 配置分组代码

        Returns:
            配置字典，键为 config_key，值为转换后的配置值
        """
        async with get_async_session() as session:
            query = select(
                AdminSysConfig.config_key,
                AdminSysConfig.config_value,
                AdminSysConfig.value_type,
            ).where(AdminSysConfig.group_code == group_code)
            result = await session.execute(query)
            configs = result.mappings().all()

            items = {}
            for config in configs:
                config_key = config["config_key"]
                config_value = config["config_value"]
                value_type = config["value_type"]

                # 根据值类型进行转换
                if value_type == "int":
                    items[config_key] = int(config_value)
                elif value_type == "bool":
                    items[config_key] = config_value.lower() in ("true", "1", "yes")
                elif value_type == "json":
                    items[config_key] = json.loads(config_value)
                else:  # string 类型或其他
                    items[config_key] = config_value

                config_key_arr = ["site_logo", "site_favicon", "upload_watermark_image"]

                # 判断路径是否在需要特殊处理的路径数组中
                if config_key in config_key_arr:
                    items[config_key + "_data"] = await self.get_upload_by_id(
                        items[config_key], session, request
                    )
            return items

    async def get_system_config(self, request: Request) -> JSONResponse:
        system = await self.get_config_by_group("system", request)

        system["upload"] = await self.get_config_by_group("upload")
        return success(system)

    async def edit(self, group_code: str, request: Request) -> JSONResponse:
        """获取指定分组的系统配置信息（用于编辑）"""
        async with get_async_session() as session:
            # 查询指定分组的配置信息
            query = select(
                AdminSysConfig.config_key,
                AdminSysConfig.config_value,
                AdminSysConfig.value_type,
            ).where(AdminSysConfig.group_code == group_code)
            result = await session.execute(query)
            configs = result.mappings().all()
            if not configs:
                return error("该分组下没有配置信息")
            items = {}
            for config in configs:
                config_key = config["config_key"]
                config_value = config["config_value"]
                value_type = config["value_type"]

                # 根据值类型进行转换
                if value_type == "int":
                    items[config_key] = int(config_value)
                elif value_type == "bool":
                    items[config_key] = config_value.lower() in ("true", "1", "yes")
                elif value_type == "json":
                    items[config_key] = json.loads(config_value)
                else:  # string 类型或其他
                    items[config_key] = config_value

                config_key_arr = ["site_logo", "site_favicon", "upload_watermark_image"]

                # 判断路径是否在需要特殊处理的路径数组中
                if config_key in config_key_arr:
                    items[config_key + "_data"] = await self.get_upload_by_id(
                        items[config_key], session, request
                    )
                if config_key == "site_content":
                    # 为 HTML 内容中的 src 属性添加完整的上传路径前缀
                    items[config_key] = self.add_upload_path_prefix_to_html(
                        items[config_key], request
                    )
            return success(items)

    async def update(
        self, group_code: str, data: dict, request: Request
    ) -> JSONResponse:
        """更新指定分组的系统配置信息"""
        async with get_async_session() as session:
            # 查询指定分组的所有配置
            query = select(AdminSysConfig).where(
                AdminSysConfig.group_code == group_code
            )
            result = await session.execute(query)
            configs = result.scalars().all()

            if not configs:
                return error("该分组下没有配置信息")

            # 创建 config_key 到模型对象的映射
            config_map = {config.config_key: config for config in configs}

            # 更新配置值
            updated_count = 0
            for config_key, config_value in data.items():
                if config_key in config_map:
                    if config_key == "site_content":
                        # 从 HTML 内容中的 src 属性移除完整的上传路径前缀
                        config_value = self.remove_upload_path_prefix_from_html(
                            config_value, request
                        )
                    # 根据 value_type 进行转换
                    value_type = config_map[config_key].value_type
                    if value_type == "json":
                        # 将 Python 对象转换为 JSON 字符串
                        config_map[config_key].config_value = json.dumps(
                            config_value, ensure_ascii=False
                        )
                    else:
                        config_map[config_key].config_value = config_value
                    config_map[config_key].updated_at = now()
                    updated_count += 1

            if updated_count == 0:
                return error("没有匹配的配置项")

            # 提交更改
            await session.commit()

            # 清除缓存，确保下次获取时重新从数据库加载最新数据
            await self.clear_config_cache(group_code)
            return success("更新成功")

    async def get_upload_by_id(
        self,
        id: int,
        session,
        request: Request | None = None,
    ) -> list[dict]:
        """
        根据 ID 获取上传文件信息

        Args:
            id: 上传文件 ID
            session: 数据库 session
            request: FastAPI Request 对象 可选

        Returns:
            上传文件信息列表，包含格式化后的数据和 URL
        """
        base_url = ""
        if request:
            base_url = get_base_url(request)
        url_prefix = Config.get("upload.url_prefix", "/uploads").lstrip("/")

        site_logo_result = await session.execute(
            select(AdminUpload).where(AdminUpload.id == id)
        )
        site_logo_data = site_logo_result.scalars().one_or_none()
        if site_logo_data:
            d = site_logo_data.model_dump()
            d["created_at"] = (
                format_datetime(site_logo_data.created_at)
                if site_logo_data.created_at
                else None
            )
            storage_type = d.get("storage_type", "local")
            if storage_type == "local":
                d["url"] = f"{base_url}/{url_prefix}/{d['file_path']}"
            else:
                # 云存储的URL
                d["url"] = d["file_path"]

            # 如果有缩略图，添加缩略图URL
            if d["thumbnail_path"]:
                if storage_type == "local":
                    d["thumbnail_url"] = (
                        f"{base_url}/{url_prefix}/{d['thumbnail_path']}"
                    )
                else:
                    # 云存储的缩略图URL
                    d["thumbnail_url"] = d["thumbnail_path"]
            return [d]
        else:
            return []
