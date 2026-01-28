"""
文件上传服务 - 负责文件上传相关的业务逻辑
"""

from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import select

from Modules.admin.models.admin_upload import AdminUpload
from Modules.admin.services.sys_config_service import SysConfigService
from Modules.common.libs.config.config import Config
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime, now
from Modules.common.libs.upload import UploadLib
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.common.utils.url_helper import get_base_url


class UploadService(BaseService):
    """文件上传服务 - 负责文件上传相关的业务逻辑"""

    async def file(self, data: dict[str, Any], request: Request) -> JSONResponse:
        """
        处理文件上传

        Args:
            data: 包含 file_type 和 file 的字典

        Returns:
            JSONResponse: 上传结果
        """
        file_type = data.get("file_type", "")
        file = data.get("file")

        if not file:
            return error("请选择要上传的文件")
        upload_config = Config.get("upload")
        sys_config_service = SysConfigService()
        try:
            # 获取系统配置
            sys_config = await sys_config_service.get_config_by_group("upload")

            # 一行代码完成文件上传
            result = await UploadLib.upload(
                upload_config=upload_config,
                sys_config=sys_config,
                file=file,
                file_type=file_type,
            )

            # 检查是否上传成功
            if not result["success"]:
                return error(result["error"])

            # 保存到数据库
            upload_data = {
                "original_name": result["original_name"],
                "filename": result["filename"],
                "file_path": result["file_path"],
                "file_size": result["file_size"],
                "mime_type": result["mime_type"],
                "file_ext": result["file_ext"],
                "file_hash": result["file_hash"],
                "storage_type": result.get("storage_type", "local"),
                "file_type": file_type,
                "width": result["width"],
                "height": result["height"],
                "thumbnail_filename": result["thumbnail_filename"],
                "thumbnail_path": result["thumbnail_path"],
                "created_at": now(),
            }
            base_url = get_base_url(request)
            async with get_async_session() as session:
                upload_record = AdminUpload(**upload_data)
                session.add(upload_record)
                await session.commit()
                await session.refresh(upload_record)

            # 返回成功结果
            result_data = {
                "id": upload_record.id,
                "original_name": result["original_name"],
                "filename": result["filename"],
                "file_path": result["file_path"],
                "file_size": result["file_size"],
                "mime_type": result["mime_type"],
                "file_ext": result["file_ext"],
                "file_hash": result["file_hash"],
                "storage_type": result.get("storage_type", "local"),
                "file_type": file_type,
                "width": result["width"],
                "height": result["height"],
                "thumbnail_filename": result["thumbnail_filename"],
                "thumbnail_path": result["thumbnail_path"],
                "url": base_url + result.get("url", ""),
            }
            # 如果有缩略图，添加缩略图URL
            if result["thumbnail_path"]:
                # 缩略图URL需要根据存储类型生成
                storage_type = result.get("storage_type", "local")
                if storage_type == "local":
                    url_prefix = Config.get("upload.url_prefix", "/uploads").lstrip("/")
                    result_data["thumbnail_url"] = (
                        f"{base_url}/{url_prefix}/{result['thumbnail_path']}"
                    )
                else:
                    # 云存储的缩略图URL
                    result_data["thumbnail_url"] = result["thumbnail_path"]
                result_data["thumbnail_filename"] = result["thumbnail_filename"]
                result_data["thumbnail_path"] = result["thumbnail_path"]

            return success(result_data, message="上传成功")

        except Exception as e:
            return error(f"上传失败: {str(e)}")

    async def index(self, data: dict[str, Any], request: Request) -> JSONResponse:
        """获取文件列表或搜索文件（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)
        # 文本搜索字段（模糊匹配）
        data["text_fields"] = ["original_name"]
        # 精确匹配字段字典
        data["exact_fields"] = ["file_type", "storage_type"]
        # 应用范围筛选
        data["range_fields"] = ["created_at"]
        base_url = get_base_url(request)
        url_prefix = Config.get("upload.url_prefix", "/uploads").lstrip("/")
        async with get_async_session() as session:
            # 构建基础查询，使用关系映射加载AdminUpload
            query = select(AdminUpload)
            # 搜索
            query = await self.apply_search_filters(query, AdminUpload, data)

            # 应用排序
            query = await self.apply_sorting(query, AdminUpload, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for upload in page_data.items:
                d = upload.__dict__.copy()
                d["created_at"] = (
                    format_datetime(upload.created_at) if upload.created_at else None
                )
                storage_type = d.get("storage_type", "local")
                if storage_type == "local":
                    d["url"] = f"{base_url}/{url_prefix}/{d['file_path']}"
                else:
                    # 云存储的缩略图URL
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

                items.append(d)
            return success(
                jsonable_encoder(
                    {
                        "items": items,
                        "total": page_data.total,
                        "page": page_data.page,
                        "size": page_data.size,
                        "pages": page_data.pages,
                    }
                )
            )

    async def destroy(self, id: int) -> JSONResponse:
        """文件删除"""
        return await self.common_destroy(id=id, model_class=AdminUpload)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """文件批量删除"""
        return await self.common_destroy_all(id_array=id_array, model_class=AdminUpload)
