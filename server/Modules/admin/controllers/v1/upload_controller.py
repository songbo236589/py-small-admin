"""
Admin 文件管理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Body, Form, Path, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from Modules.admin.services.upload_service import UploadService
from Modules.admin.validators.common_validator import FileTypeRequest
from Modules.common.libs.validation.decorators import (
    validate_body_data,
    validate_request_data,
)
from Modules.common.libs.validation.pagination_validator import (
    IdArrayRequest,
    IdRequest,
    PaginationRequest,
)


class UploadController:
    """Admin文件管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化文件管理控制器"""
        self.upload_service = UploadService()

    @validate_request_data(FileTypeRequest)
    async def file(
        self,
        request: Request,
        file_type: str = Form(..., description="文件类型"),
        file: UploadFile = Form(..., description="上传的文件"),
    ) -> JSONResponse:
        """文件上传接口"""
        return await self.upload_service.file(
            {
                "file_type": file_type,
                "file": file,
            },
            request,
        )

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        request: Request,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录，用于控制每页显示数量"),
        original_name: str | None = Query(None, description="原始文件名"),
        file_type: str | None = Query(
            None, description="文件分类:image/document/video/audio/other"
        ),
        storage_type: str | None = Query(
            None, description="存储类型(local/aliyun_oss/tencent_oss/qiniu_oss)"
        ),
        sort: str | None = Query(None, description="排序规则"),
        created_at_start: str | None = Query(
            None, alias="created_at[start]", description="创建时间开始"
        ),
        created_at_end: str | None = Query(
            None, alias="created_at[end]", description="创建时间结束"
        ),
    ) -> JSONResponse:
        """获取文件列表或搜索文件（统一接口）"""
        return await self.upload_service.index(
            {
                "page": page,
                "limit": limit,
                "original_name": original_name,
                "file_type": file_type,
                "storage_type": storage_type,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
            },
            request,
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="文件ID"),
    ) -> JSONResponse:
        """文件删除"""
        return await self.upload_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """文件批量删除"""
        return await self.upload_service.destroy_all(request.id_array)
