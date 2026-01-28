"""
行业业务服务 - 负责行业相关的业务逻辑
"""

import asyncio
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlmodel import select

from Modules.common.libs.database.sql.session import (
    get_async_session,
    get_sync_session,
)
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import now
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.quant.models.quant_industry import QuantIndustry
from Modules.quant.models.quant_industry_log import QuantIndustryLog
from Modules.quant.models.quant_stock import QuantStock
from Modules.quant.services.quant_data_fetch_service import QuantDataFetchService


class QuantIndustryService(BaseService):
    """行业业务服务 - 负责行业相关的业务逻辑"""

    def __init__(self):
        """初始化行业服务"""
        super().__init__()
        self.data_fetch_service = QuantDataFetchService()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """
        获取行业列表（支持搜索、筛选、分页）

        支持的筛选条件：
        - page: 页码，从1开始（默认1）
        - limit: 每页返回的记录数量（默认20）
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
            JSONResponse: 行业列表数据
        """
        page = data.get("page", 1)
        size = data.get("limit", 20)

        # 设置文本搜索字段
        data["text_fields"] = ["name", "code", "description", "leading_stock"]
        # 精确匹配字段
        data["exact_fields"] = ["status"]
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
            query = select(QuantIndustry)

            # 搜索
            query = await self.apply_search_filters(query, QuantIndustry, data)

            # 应用排序（默认按总市值由大到小排序）
            sort_param = data.get("sort")
            if not sort_param:
                sort_param = {"sort": "asc"}
            query = await self.apply_sorting(query, QuantIndustry, sort_param)

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for industry in page_data.items:
                d = industry.__dict__.copy()
                # 格式化日期字段
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

    async def add(self, data: dict[str, Any]) -> JSONResponse:
        """
        添加行业

        Args:
            data: 行业数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_add(
            data=data,
            model_class=QuantIndustry,
            pre_operation_callback=self._industry_add_pre_operation,
        )

    async def _industry_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """
        行业添加前置操作

        Args:
            data: 行业数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        code = data.get("code")
        name = data.get("name")

        # 检查行业代码是否已存在
        existing_industry = await session.execute(
            select(QuantIndustry).where(QuantIndustry.code == code)
        )
        if existing_industry.scalar_one_or_none():
            return error("行业代码已存在")

        # 检查行业名称是否已存在
        existing_industry = await session.execute(
            select(QuantIndustry).where(QuantIndustry.name == name)
        )
        if existing_industry.scalar_one_or_none():
            return error("行业名称已存在")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """
        获取行业信息（用于编辑）

        Args:
            id: 行业ID

        Returns:
            JSONResponse: 行业信息
        """
        async with get_async_session() as session:
            # 查询行业信息
            result = await session.execute(
                select(
                    *[
                        QuantIndustry.id,
                        QuantIndustry.name,
                        QuantIndustry.code,
                        QuantIndustry.sort,
                        QuantIndustry.latest_price,
                        QuantIndustry.change_amount,
                        QuantIndustry.change_percent,
                        QuantIndustry.total_market_cap,
                        QuantIndustry.turnover_rate,
                        QuantIndustry.up_count,
                        QuantIndustry.down_count,
                        QuantIndustry.leading_stock,
                        QuantIndustry.leading_stock_change,
                        QuantIndustry.description,
                        QuantIndustry.status,
                    ]
                ).where(QuantIndustry.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("行业不存在")

            # 转换为字典
            data = dict(info)

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
                if data.get(key) is not None:
                    data[key] = str(data[key])

            return success(data)

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """
        更新行业信息

        Args:
            id: 行业ID
            data: 更新数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_update(
            id=id,
            data=data,
            model_class=QuantIndustry,
            pre_operation_callback=self._industry_update_pre_operation,
        )

    async def _industry_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """
        行业更新前置操作

        Args:
            id: 行业ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        code = data.get("code")
        name = data.get("name")

        # 检查行业代码是否已被其他行业使用
        if code:
            existing_industry = await session.execute(
                select(QuantIndustry).where(QuantIndustry.code == code)
            )
            industry_with_code = existing_industry.scalar_one_or_none()

            if industry_with_code and industry_with_code.id != id:
                return error("行业代码已存在")

        # 检查行业名称是否已被其他行业使用
        if name:
            existing_industry = await session.execute(
                select(QuantIndustry).where(QuantIndustry.name == name)
            )
            industry_with_name = existing_industry.scalar_one_or_none()

            if industry_with_name and industry_with_name.id != id:
                return error("行业名称已存在")

        return data, session

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """
        行业状态

        Args:
            id: 行业ID
            data: 状态数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_update(id=id, data=data, model_class=QuantIndustry)

    async def set_sort(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """行业排序"""
        return await self.common_update(id=id, data=data, model_class=QuantIndustry)

    async def destroy(self, id: int) -> JSONResponse:
        """
        删除行业

        Args:
            id: 行业ID

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_destroy(id=id, model_class=QuantIndustry)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """
        批量删除行业

        Args:
            id_array: 行业ID列表

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_destroy_all(
            id_array=id_array, model_class=QuantIndustry
        )

    async def sync_list(self) -> JSONResponse:
        """
        同步行业列表（手动触发）

        Returns:
            JSONResponse: 同步结果统计
        """
        try:
            # 获取行业列表
            df = await self.data_fetch_service.fetch_industry_list()

            if df.empty:
                return error("未获取到行业数据")

            # 转换数据格式
            industry_list = []
            for _, row in df.iterrows():
                industry_data = {
                    "code": row.get("板块代码", ""),
                    "name": row.get("板块名称", ""),
                    "sort": int(row.get("排名", 0)) if row.get("排名") else 0,
                    "latest_price": float(row.get("最新价", 0))
                    if row.get("最新价")
                    else 0,
                    "change_amount": float(row.get("涨跌额", 0))
                    if row.get("涨跌额")
                    else 0,
                    "change_percent": float(row.get("涨跌幅", 0))
                    if row.get("涨跌幅")
                    else 0,
                    "total_market_cap": float(row.get("总市值", 0))
                    if row.get("总市值")
                    else 0,
                    "turnover_rate": float(row.get("换手率", 0))
                    if row.get("换手率")
                    else 0,
                    "up_count": int(row.get("上涨家数", 0))
                    if row.get("上涨家数")
                    else 0,
                    "down_count": int(row.get("下跌家数", 0))
                    if row.get("下跌家数")
                    else 0,
                    "leading_stock": str(row.get("领涨股票", ""))
                    if row.get("领涨股票")
                    else "",
                    "leading_stock_change": float(row.get("领涨股票-涨跌幅", 0))
                    if row.get("领涨股票-涨跌幅")
                    else 0,
                }
                industry_list.append(industry_data)

            # 批量插入或更新数据库
            async with get_async_session() as session:
                added_count = 0
                updated_count = 0

                for industry_data in industry_list:
                    industry_code = industry_data["code"]

                    # 检查是否存在
                    existing = await session.execute(
                        select(QuantIndustry).where(QuantIndustry.code == industry_code)
                    )
                    existing_industry = existing.scalar_one_or_none()

                    if existing_industry:
                        # 更新
                        existing_industry.name = industry_data["name"]
                        existing_industry.sort = industry_data["sort"]
                        existing_industry.latest_price = industry_data["latest_price"]
                        existing_industry.change_amount = industry_data["change_amount"]
                        existing_industry.change_percent = industry_data[
                            "change_percent"
                        ]
                        existing_industry.total_market_cap = industry_data[
                            "total_market_cap"
                        ]
                        existing_industry.turnover_rate = industry_data["turnover_rate"]
                        existing_industry.up_count = industry_data["up_count"]
                        existing_industry.down_count = industry_data["down_count"]
                        existing_industry.leading_stock = industry_data["leading_stock"]
                        existing_industry.leading_stock_change = industry_data[
                            "leading_stock_change"
                        ]
                        existing_industry.updated_at = now()
                        updated_count += 1
                    else:
                        # 插入
                        industry = QuantIndustry(
                            code=industry_data["code"],
                            name=industry_data["name"],
                            sort=industry_data["sort"],
                            latest_price=industry_data["latest_price"],
                            change_amount=industry_data["change_amount"],
                            change_percent=industry_data["change_percent"],
                            total_market_cap=industry_data["total_market_cap"],
                            turnover_rate=industry_data["turnover_rate"],
                            up_count=industry_data["up_count"],
                            down_count=industry_data["down_count"],
                            leading_stock=industry_data["leading_stock"],
                            leading_stock_change=industry_data["leading_stock_change"],
                            status=1,
                            created_at=now(),
                        )
                        session.add(industry)
                        added_count += 1

                await session.commit()

            # 记录日志（在主事务提交后）
            logs_created_count = 0
            logs_updated_count = 0
            current_date = now().date()

            async with get_async_session() as log_session:
                for industry_data in industry_list:
                    # 获取行业ID和description
                    industry = await log_session.execute(
                        select(QuantIndustry.id, QuantIndustry.description).where(
                            QuantIndustry.code == industry_data["code"]
                        )
                    )
                    industry_result = industry.mappings().one_or_none()
                    industry_id = industry_result["id"] if industry_result else None
                    industry_description = (
                        industry_result["description"] if industry_result else None
                    )

                    if industry_id:
                        # 查询当天是否已有该行业的日志记录
                        existing_log = await log_session.execute(
                            select(QuantIndustryLog).where(
                                QuantIndustryLog.industry_id == industry_id,
                                QuantIndustryLog.record_date == current_date,
                            )
                        )
                        log_record = existing_log.scalar_one_or_none()

                        if log_record:
                            # 更新现有记录
                            log_record.name = industry_data["name"]
                            log_record.code = industry_data["code"]
                            log_record.sort = industry_data["sort"]
                            log_record.latest_price = industry_data["latest_price"]
                            log_record.change_amount = industry_data["change_amount"]
                            log_record.change_percent = industry_data["change_percent"]
                            log_record.total_market_cap = industry_data[
                                "total_market_cap"
                            ]
                            log_record.turnover_rate = industry_data["turnover_rate"]
                            log_record.up_count = industry_data["up_count"]
                            log_record.down_count = industry_data["down_count"]
                            log_record.leading_stock = industry_data["leading_stock"]
                            log_record.leading_stock_change = industry_data[
                                "leading_stock_change"
                            ]
                            log_record.description = industry_description
                            log_record.status = 1
                            log_record.updated_at = now()
                            logs_updated_count += 1
                        else:
                            # 创建新记录
                            log_record = QuantIndustryLog(
                                industry_id=industry_id,
                                record_date=current_date,
                                name=industry_data["name"],
                                code=industry_data["code"],
                                sort=industry_data["sort"],
                                latest_price=industry_data["latest_price"],
                                change_amount=industry_data["change_amount"],
                                change_percent=industry_data["change_percent"],
                                total_market_cap=industry_data["total_market_cap"],
                                turnover_rate=industry_data["turnover_rate"],
                                up_count=industry_data["up_count"],
                                down_count=industry_data["down_count"],
                                leading_stock=industry_data["leading_stock"],
                                leading_stock_change=industry_data[
                                    "leading_stock_change"
                                ],
                                description=industry_description,
                                status=1,
                                created_at=now(),
                            )
                            log_session.add(log_record)
                            logs_created_count += 1

                await log_session.commit()

            return success(
                {
                    "added": added_count,
                    "updated": updated_count,
                    "total": len(industry_list),
                    "logs_created": logs_created_count,
                    "logs_updated": logs_updated_count,
                },
                message=f"同步完成，新增 {added_count} 条，更新 {updated_count} 条，日志新增 {logs_created_count} 条，日志更新 {logs_updated_count} 条。",
            )
        except Exception as e:
            return error(f"同步失败: {str(e)}")

    async def sync_relation(self) -> JSONResponse:
        """
        同步行业-股票关联关系（手动触发）

        Returns:
            JSONResponse: 同步结果统计
        """
        # 异步同步所有行业的关联关系
        from Modules.quant.queues.industry_queues import sync_industry_relation_queue

        try:
            async with get_async_session() as session:
                # 查询所有行业，用于同步关联关系
                all_industries_result = await session.execute(select(QuantIndustry))
                all_industries = all_industries_result.scalars().all()

                for index, industry in enumerate(all_industries):
                    # 设置延时，避免同时执行太多任务（每个任务间隔2秒）
                    countdown = index * 5
                    sync_industry_relation_queue.apply_async(
                        args=[industry.id, industry.code],
                        countdown=countdown,
                    )

                return success(
                    {
                        "total": len(all_industries),
                    },
                    message=f"同步任务已提交，共 {len(all_industries)} 个行业，任务将在后台异步执行。",
                )
        except Exception as e:
            return error(f"同步失败: {str(e)}")

    async def simple_list(self, data: dict[str, Any] | None = None) -> JSONResponse:
        """
        获取行业简单列表（不分页，只返回 id 和 name）

        Args:
            data: 查询参数，可选参数：
                - status: 状态筛选（1-启用，0-禁用）
                - sort: 排序规则（如：{"name":"asc"} 或 "name asc"）

        Returns:
            JSONResponse: 行业简单列表
        """
        if data is None:
            data = {}

        async with get_async_session() as session:
            # 构建基础查询，只查询 id 和 name 字段
            query = select(QuantIndustry.id, QuantIndustry.name)

            # 应用状态筛选
            status = data.get("status")
            if status is not None:
                query = query.where(QuantIndustry.status == status)

            # 应用排序（默认按 id 升序）
            sort_param = data.get("sort")
            if sort_param:
                query = await self.apply_sorting(query, QuantIndustry, sort_param)
            else:
                query = await self.apply_sorting(query, QuantIndustry, {"id": "asc"})

            # 执行查询
            result = await session.execute(query)
            industries = result.mappings().all()

            # 转换为列表格式
            items = [
                {"id": industry["id"], "name": industry["name"]}
                for industry in industries
            ]

            return success(items)

    def sync_single_industry_relation_sync(
        self, industry_id: int, industry_code: str
    ) -> dict:
        """
        同步单个行业的股票关联关系（同步版本，用于 Celery 任务）

        Args:
            industry_id: 行业ID
            industry_code: 行业代码

        Returns:
            dict: 同步结果统计
        """
        with get_sync_session() as session:
            try:
                # 验证行业是否存在
                industry_result = session.execute(
                    select(QuantIndustry).where(QuantIndustry.id == industry_id)
                )
                industry = industry_result.scalar_one_or_none()

                if not industry:
                    logger.error(
                        f"行业不存在: industry_id={industry_id}, industry_code={industry_code}"
                    )
                    return {
                        "success": False,
                        "industry_id": industry_id,
                        "industry_code": industry_code,
                        "error": "行业不存在",
                        "added": 0,
                    }

                # 获取所有股票（构建股票代码到ID的映射）
                stock_result = session.execute(select(QuantStock))
                stocks = stock_result.scalars().all()
                stock_code_to_id = {stock.stock_code: stock.id for stock in stocks}

                # 获取行业的成分股（使用 asyncio.to_thread 包装异步调用）
                stock_codes = asyncio.run(
                    self.data_fetch_service.fetch_industry_stocks(industry_code)
                )

                # 更新股票的行业ID（覆盖更新，不是追加）
                updated_count = 0
                for stock_code in stock_codes:
                    stock_id = stock_code_to_id.get(stock_code)
                    if stock_id:
                        stock_result = session.execute(
                            select(QuantStock).where(QuantStock.id == stock_id)
                        )
                        stock = stock_result.scalar_one_or_none()
                        if stock:
                            stock.industry_id = industry_id
                            updated_count += 1

                session.commit()

                logger.info(
                    f"行业关联同步成功: industry_id={industry_id}, "
                    f"industry_name={industry.name}, updated={updated_count}"
                )

                return {
                    "success": True,
                    "industry_id": industry_id,
                    "industry_code": industry_code,
                    "industry_name": industry.name,
                    "updated": updated_count,
                }

            except Exception as e:
                session.rollback()
                logger.error(
                    f"行业关联同步失败: industry_id={industry_id}, "
                    f"industry_code={industry_code}, error={str(e)}"
                )
                raise
