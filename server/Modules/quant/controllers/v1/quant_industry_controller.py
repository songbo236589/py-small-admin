"""
行业控制器 - 负责行业相关的API接口
"""

from fastapi import Body, Form, Path, Query
from fastapi.responses import JSONResponse

from Modules.common.libs.validation.decorators import (
    validate_body_data,
    validate_request_data,
)
from Modules.common.libs.validation.pagination_validator import (
    IdArrayRequest,
    IdRequest,
    ListSortRequest,
    ListStatusRequest,
    PaginationRequest,
)
from Modules.quant.services.quant_industry_service import QuantIndustryService
from Modules.quant.validators.quant_industry_validator import (
    QuantIndustryAddUpdateRequest,
)


class QuantIndustryController:
    """行业控制器 - 负责行业相关的API接口"""

    def __init__(self):
        """初始化行业控制器"""
        self.service = QuantIndustryService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录，用于控制每页显示数量"),
        name: str | None = Query(None, description="行业名称"),
        code: str | None = Query(None, description="行业代码"),
        description: str | None = Query(None, description="行业描述"),
        status: int | None = Query(None, description="状态"),
        sort: str | None = Query(None, description="排序规则"),
        latest_price_start: float | None = Query(
            None, alias="latest_price[start]", description="最新价开始"
        ),
        latest_price_end: float | None = Query(
            None, alias="latest_price[end]", description="最新价结束"
        ),
        change_amount_start: float | None = Query(
            None, alias="change_amount[start]", description="涨跌额开始"
        ),
        change_amount_end: float | None = Query(
            None, alias="change_amount[end]", description="涨跌额结束"
        ),
        change_percent_start: float | None = Query(
            None, alias="change_percent[start]", description="涨跌幅开始"
        ),
        change_percent_end: float | None = Query(
            None, alias="change_percent[end]", description="涨跌幅结束"
        ),
        total_market_cap_start: float | None = Query(
            None, alias="total_market_cap[start]", description="总市值开始"
        ),
        total_market_cap_end: float | None = Query(
            None, alias="total_market_cap[end]", description="总市值结束"
        ),
        turnover_rate_start: float | None = Query(
            None, alias="turnover_rate[start]", description="换手率开始"
        ),
        turnover_rate_end: float | None = Query(
            None, alias="turnover_rate[end]", description="换手率结束"
        ),
        up_count_start: int | None = Query(
            None, alias="up_count[start]", description="上涨家数开始"
        ),
        up_count_end: int | None = Query(
            None, alias="up_count[end]", description="上涨家数结束"
        ),
        down_count_start: int | None = Query(
            None, alias="down_count[start]", description="下跌家数开始"
        ),
        down_count_end: int | None = Query(
            None, alias="down_count[end]", description="下跌家数结束"
        ),
        leading_stock: str | None = Query(None, description="领涨股票"),
        leading_stock_change_start: float | None = Query(
            None, alias="leading_stock_change[start]", description="领涨股票涨跌幅开始"
        ),
        leading_stock_change_end: float | None = Query(
            None, alias="leading_stock_change[end]", description="领涨股票涨跌幅结束"
        ),
        created_at_start: str | None = Query(
            None, alias="created_at[start]", description="创建时间开始"
        ),
        created_at_end: str | None = Query(
            None, alias="created_at[end]", description="创建时间结束"
        ),
        updated_at_start: str | None = Query(
            None, alias="updated_at[start]", description="更新时间开始"
        ),
        updated_at_end: str | None = Query(
            None, alias="updated_at[end]", description="更新时间结束"
        ),
    ) -> JSONResponse:
        """
        获取行业列表

        支持的查询参数：
        - page: 页码，从1开始（默认1）
        - limit: 每页返回的记录数量（默认20）
        - name: 行业名称，支持模糊匹配
        - code: 行业代码，支持模糊匹配
        - description: 行业描述，支持模糊匹配
        - status: 启用状态，精确匹配（1-启用，0-禁用）
        - sort: 排序规则，支持两种格式：
          * JSON格式：{"id":"desc"} 或 {"created_at":"asc"}
          * 字符串格式："id desc" 或 "created_at asc"
          支持多字段排序，如："id desc,created_at asc"
        - latest_price[start]: 最新价范围查询的开始值
        - latest_price[end]: 最新价范围查询的结束值
        - change_amount[start]: 涨跌额范围查询的开始值
        - change_amount[end]: 涨跌额范围查询的结束值
        - change_percent[start]: 涨跌幅范围查询的开始值
        - change_percent[end]: 涨跌幅范围查询的结束值
        - total_market_cap[start]: 总市值范围查询的开始值
        - total_market_cap[end]: 总市值范围查询的结束值
        - turnover_rate[start]: 换手率范围查询的开始值
        - turnover_rate[end]: 换手率范围查询的结束值
        - up_count[start]: 上涨家数范围查询的开始值
        - up_count[end]: 上涨家数范围查询的结束值
        - down_count[start]: 下跌家数范围查询的开始值
        - down_count[end]: 下跌家数范围查询的结束值
        - leading_stock: 领涨股票，支持模糊匹配
        - leading_stock_change[start]: 领涨股票涨跌幅范围查询的开始值
        - leading_stock_change[end]: 领涨股票涨跌幅范围查询的结束值
        - created_at[start]: 创建时间范围查询的开始时间（格式：YYYY-MM-DD HH:mm:ss）
        - created_at[end]: 创建时间范围查询的结束时间（格式：YYYY-MM-DD HH:mm:ss）
        - updated_at[start]: 更新时间范围查询的开始时间（格式：YYYY-MM-DD HH:mm:ss）
        - updated_at[end]: 更新时间范围查询的结束时间（格式：YYYY-MM-DD HH:mm:ss）
        """
        return await self.service.index(
            {
                "page": page,
                "limit": limit,
                "name": name,
                "code": code,
                "description": description,
                "status": status,
                "sort": sort,
                "latest_price_start": latest_price_start,
                "latest_price_end": latest_price_end,
                "change_amount_start": change_amount_start,
                "change_amount_end": change_amount_end,
                "change_percent_start": change_percent_start,
                "change_percent_end": change_percent_end,
                "total_market_cap_start": total_market_cap_start,
                "total_market_cap_end": total_market_cap_end,
                "turnover_rate_start": turnover_rate_start,
                "turnover_rate_end": turnover_rate_end,
                "up_count_start": up_count_start,
                "up_count_end": up_count_end,
                "down_count_start": down_count_start,
                "down_count_end": down_count_end,
                "leading_stock": leading_stock,
                "leading_stock_change_start": leading_stock_change_start,
                "leading_stock_change_end": leading_stock_change_end,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(QuantIndustryAddUpdateRequest)
    async def add(
        self,
        name: str = Form(..., description="行业名称"),
        code: str | None = Form(None, description="行业代码"),
        description: str | None = Form(None, description="行业描述"),
        sort: int | None = Form(0, description="排名"),
        latest_price: float | None = Form(None, description="最新价"),
        change_amount: float | None = Form(None, description="涨跌额"),
        change_percent: float | None = Form(None, description="涨跌幅"),
        total_market_cap: float | None = Form(None, description="总市值"),
        turnover_rate: float | None = Form(None, description="换手率"),
        up_count: int | None = Form(None, description="上涨家数"),
        down_count: int | None = Form(None, description="下跌家数"),
        leading_stock: str | None = Form(None, description="领涨股票"),
        leading_stock_change: float | None = Form(None, description="领涨股票涨跌幅"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """
        添加行业
        """
        return await self.service.add(
            {
                "name": name,
                "code": code,
                "description": description,
                "sort": sort,
                "latest_price": latest_price,
                "change_amount": change_amount,
                "change_percent": change_percent,
                "total_market_cap": total_market_cap,
                "turnover_rate": turnover_rate,
                "up_count": up_count,
                "down_count": down_count,
                "leading_stock": leading_stock,
                "leading_stock_change": leading_stock_change,
                "status": status,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="行业ID")) -> JSONResponse:
        """获取行业信息（用于编辑）"""
        return await self.service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(QuantIndustryAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="行业ID"),
        name: str | None = Form(None, description="行业名称"),
        code: str | None = Form(None, description="行业代码"),
        description: str | None = Form(None, description="行业描述"),
        sort: int | None = Form(None, description="排名"),
        latest_price: float | None = Form(None, description="最新价"),
        change_amount: float | None = Form(None, description="涨跌额"),
        change_percent: float | None = Form(None, description="涨跌幅"),
        total_market_cap: float | None = Form(None, description="总市值"),
        turnover_rate: float | None = Form(None, description="换手率"),
        up_count: int | None = Form(None, description="上涨家数"),
        down_count: int | None = Form(None, description="下跌家数"),
        leading_stock: str | None = Form(None, description="领涨股票"),
        leading_stock_change: float | None = Form(None, description="领涨股票涨跌幅"),
        status: int | None = Form(None, description="状态"),
    ) -> JSONResponse:
        """
        更新行业信息
        """

        return await self.service.update(
            id,
            {
                "name": name,
                "code": code,
                "description": description,
                "sort": sort,
                "latest_price": latest_price,
                "change_amount": change_amount,
                "change_percent": change_percent,
                "total_market_cap": total_market_cap,
                "turnover_rate": turnover_rate,
                "up_count": up_count,
                "down_count": down_count,
                "leading_stock": leading_stock,
                "leading_stock_change": leading_stock_change,
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="行业ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """
        更新行业状态
        """
        return await self.service.set_status(id, {"status": status})

    @validate_request_data(IdRequest)
    @validate_request_data(ListSortRequest)
    async def set_sort(
        self,
        id: int = Path(..., description="行业ID"),
        sort: int = Form(..., description="排序"),
    ) -> JSONResponse:
        """行业排序"""
        return await self.service.set_sort(
            id,
            {
                "sort": sort,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="行业ID"),
    ) -> JSONResponse:
        """
        删除行业
        """
        return await self.service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """
        批量删除行业
        """
        return await self.service.destroy_all(request.id_array)

    async def sync_list(self) -> JSONResponse:
        """
        手动同步行业列表
        """
        return await self.service.sync_list()

    async def sync_relation(self) -> JSONResponse:
        """
        手动同步行业-股票关联关系
        """
        return await self.service.sync_relation()

    async def simple_list(
        self,
        status: int | None = Query(None, description="状态（1-启用，0-禁用）"),
        sort: str | None = Query(None, description="排序规则"),
    ) -> JSONResponse:
        """
        获取行业简单列表（不分页，只返回 id 和 name）

        Args:
            status: 状态筛选（1-启用，0-禁用）
            sort: 排序规则，支持两种格式：
              * JSON格式：{"name":"asc"} 或 {"id":"desc"}
              * 字符串格式："name asc" 或 "id desc"

        Returns:
            JSONResponse: 行业简单列表
        """
        return await self.service.simple_list(
            {
                "status": status,
                "sort": sort,
            }
        )
