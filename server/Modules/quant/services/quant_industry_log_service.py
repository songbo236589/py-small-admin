"""
行业日志业务服务 - 负责行业日志相关的业务逻辑
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import select

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import success
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.quant.models.quant_industry_log import QuantIndustryLog


class QuantIndustryLogService(BaseService):
    """行业日志业务服务 - 负责行业日志相关的业务逻辑"""

    def __init__(self):
        """初始化行业日志服务"""
        super().__init__()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """
        获取行业日志列表（支持搜索、筛选、分页）

        支持的筛选条件：
        - page: 页码，从1开始（默认1）
        - limit: 每页返回的记录数量（默认20）
        - industry_id: 行业ID，精确匹配
        - record_date: 记录日期，区间匹配
        - name: 行业名称，支持模糊匹配
        - code: 行业代码，支持模糊匹配
        - description: 行业描述，支持模糊匹配
        - status: 启用状态，精确匹配（1-启用，0-禁用）
        - latest_price: 最新价，区间匹配
        - change_amount: 涨跌额，区间匹配
        - change_percent: 涨跌幅，区间匹配
        - total_market_cap: 总市值，区间匹配
        - turnover_rate: 换手率，区间匹配
        - up_count: 上涨家数，区间匹配
        - down_count: 下跌家数，区间匹配
        - leading_stock: 领涨股票，支持模糊匹配
        - leading_stock_change: 领涨股票涨跌幅，区间匹配
        - sort: 排序规则，支持两种格式：
          * JSON格式：{"id":"desc"} 或 {"created_at":"asc"}
          * 字符串格式："id desc" 或 "created_at asc"
          支持多字段排序，如："id desc,created_at asc"
        - created_at[start]: 创建时间范围查询的开始时间（格式：YYYY-MM-DD HH:mm:ss）
        - created_at[end]: 创建时间范围查询的结束时间（格式：YYYY-MM-DD HH:mm:ss）
        - updated_at[start]: 更新时间范围查询的开始时间（格式：YYYY-MM-DD HH:mm:ss）
        - updated_at[end]: 更新时间范围查询的结束时间（格式：YYYY-MM-DD HH:mm:ss）

        Args:
            data: 查询参数

        Returns:
            JSONResponse: 行业日志列表数据
        """
        page = data.get("page", 1)
        size = data.get("limit", 20)

        # 设置文本搜索字段
        data["text_fields"] = ["name", "code", "description", "leading_stock"]
        # 精确匹配字段
        data["exact_fields"] = ["status", "industry_id"]
        # 应用范围筛选
        data["range_fields"] = [
            "latest_price",
            "change_amount",
            "change_percent",
            "total_market_cap",
            "turnover_rate",
            "up_count",
            "down_count",
            "leading_stock_change",
            "record_date",
            "created_at",
            "updated_at",
        ]

        # 转换单位：将搜索参数从显示单位（亿元）转换回数据库单位（元）
        if data.get("total_market_cap_start") is not None:
            data["total_market_cap_start"] = (
                float(data["total_market_cap_start"]) * 100000000
            )
        if data.get("total_market_cap_end") is not None:
            data["total_market_cap_end"] = (
                float(data["total_market_cap_end"]) * 100000000
            )

        async with get_async_session() as session:
            # 构建基础查询
            query = select(QuantIndustryLog)

            # 搜索
            query = await self.apply_search_filters(query, QuantIndustryLog, data)

            # 应用排序（默认按记录日期和创建时间降序排序）
            sort_param = data.get("sort")
            if not sort_param:
                sort_param = {"record_date": "desc", "id": "desc"}
            query = await self.apply_sorting(query, QuantIndustryLog, sort_param)

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for log in page_data.items:
                d = log.__dict__.copy()
                # 格式化日期字段
                if d.get("record_date"):
                    d["record_date"] = d["record_date"].isoformat()
                if d.get("created_at"):
                    d["created_at"] = d["created_at"].isoformat()
                if d.get("updated_at"):
                    d["updated_at"] = d["updated_at"].isoformat()
                # 转换 Decimal 为字符串
                for key in [
                    "latest_price",
                    "change_amount",
                    "change_percent",
                    "total_market_cap",
                    "turnover_rate",
                    "up_count",
                    "down_count",
                    "leading_stock_change",
                ]:
                    if d.get(key) is not None:
                        d[key] = str(d[key])
                # 转换总市值单位：从数据库单位（元）转换为显示单位（亿元）
                if d.get("total_market_cap"):
                    d["total_market_cap"] = (
                        f"{float(d['total_market_cap']) / 100000000:.4f}"
                    )
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

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """
        批量删除行业日志

        Args:
            id_array: 行业日志ID列表

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_destroy_all(
            id_array=id_array, model_class=QuantIndustryLog
        )
