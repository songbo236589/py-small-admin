"""
概念业务服务 - 负责概念相关的业务逻辑
"""

import asyncio
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlmodel import delete, select

from Modules.common.libs.database.sql.session import (
    get_async_session,
    get_sync_session,
)
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import now
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.quant.models.quant_concept import QuantConcept
from Modules.quant.models.quant_concept_log import QuantConceptLog
from Modules.quant.models.quant_stock import QuantStock
from Modules.quant.models.quant_stock_concept import QuantStockConcept
from Modules.quant.services.quant_data_fetch_service import QuantDataFetchService


class QuantConceptService(BaseService):
    """概念业务服务 - 负责概念相关的业务逻辑"""

    def __init__(self):
        """初始化概念服务"""
        super().__init__()
        self.data_fetch_service = QuantDataFetchService()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """
        获取概念列表（支持搜索、筛选、分页）

        支持的筛选条件：
        - page: 页码，从1开始（默认1）
        - limit: 每页返回的记录数量（默认20）
        - name: 概念名称，支持模糊匹配
        - code: 概念代码，支持模糊匹配
        - description: 概念描述，支持模糊匹配
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
            JSONResponse: 概念列表数据
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
            query = select(QuantConcept)

            # 搜索
            query = await self.apply_search_filters(query, QuantConcept, data)

            # 应用排序（默认按总市值由大到小排序）
            sort_param = data.get("sort")
            if not sort_param:
                sort_param = {"sort": "asc"}
            query = await self.apply_sorting(query, QuantConcept, sort_param)

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for concept in page_data.items:
                d = concept.__dict__.copy()
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
        添加概念

        Args:
            data: 概念数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_add(
            data=data,
            model_class=QuantConcept,
            pre_operation_callback=self._concept_add_pre_operation,
        )

    async def _concept_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """
        概念添加前置操作

        Args:
            data: 概念数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        code = data.get("code")
        name = data.get("name")

        # 检查概念代码是否已存在
        existing_concept = await session.execute(
            select(QuantConcept).where(QuantConcept.code == code)
        )
        if existing_concept.scalar_one_or_none():
            return error("概念代码已存在")

        # 检查概念名称是否已存在
        existing_concept = await session.execute(
            select(QuantConcept).where(QuantConcept.name == name)
        )
        if existing_concept.scalar_one_or_none():
            return error("概念名称已存在")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """
        获取概念信息（用于编辑）

        Args:
            id: 概念ID

        Returns:
            JSONResponse: 概念信息
        """
        async with get_async_session() as session:
            # 查询概念信息
            result = await session.execute(
                select(
                    *[
                        QuantConcept.id,
                        QuantConcept.name,
                        QuantConcept.code,
                        QuantConcept.sort,
                        QuantConcept.latest_price,
                        QuantConcept.change_amount,
                        QuantConcept.change_percent,
                        QuantConcept.total_market_cap,
                        QuantConcept.turnover_rate,
                        QuantConcept.up_count,
                        QuantConcept.down_count,
                        QuantConcept.leading_stock,
                        QuantConcept.leading_stock_change,
                        QuantConcept.description,
                        QuantConcept.status,
                    ]
                ).where(QuantConcept.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("概念不存在")

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
        更新概念信息

        Args:
            id: 概念ID
            data: 更新数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_update(
            id=id,
            data=data,
            model_class=QuantConcept,
            pre_operation_callback=self._concept_update_pre_operation,
        )

    async def _concept_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """
        概念更新前置操作

        Args:
            id: 概念ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        code = data.get("code")
        name = data.get("name")

        # 检查概念代码是否已被其他概念使用
        if code:
            existing_concept = await session.execute(
                select(QuantConcept).where(QuantConcept.code == code)
            )
            concept_with_code = existing_concept.scalar_one_or_none()

            if concept_with_code and concept_with_code.id != id:
                return error("概念代码已存在")

        # 检查概念名称是否已被其他概念使用
        if name:
            existing_concept = await session.execute(
                select(QuantConcept).where(QuantConcept.name == name)
            )
            concept_with_name = existing_concept.scalar_one_or_none()

            if concept_with_name and concept_with_name.id != id:
                return error("概念名称已存在")

        return data, session

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """
        概念状态

        Args:
            id: 概念ID
            data: 状态数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_update(id=id, data=data, model_class=QuantConcept)

    async def set_sort(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """概念排序"""
        return await self.common_update(id=id, data=data, model_class=QuantConcept)

    async def destroy(self, id: int) -> JSONResponse:
        """
        删除概念

        Args:
            id: 概念ID

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_destroy(id=id, model_class=QuantConcept)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """
        批量删除概念

        Args:
            id_array: 概念ID列表

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_destroy_all(
            id_array=id_array, model_class=QuantConcept
        )

    async def sync_list(self) -> JSONResponse:
        """
        同步概念列表（手动触发）

        Returns:
            JSONResponse: 同步结果统计
        """
        try:
            # 获取概念列表
            df = await self.data_fetch_service.fetch_concept_list()

            if df.empty:
                return error("未获取到概念数据")

            # 转换数据格式
            concept_list = []
            for _, row in df.iterrows():
                concept_data = {
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
                concept_list.append(concept_data)

            # 批量插入或更新数据库
            async with get_async_session() as session:
                added_count = 0
                updated_count = 0

                for concept_data in concept_list:
                    concept_code = concept_data["code"]

                    # 检查是否存在
                    existing = await session.execute(
                        select(QuantConcept).where(QuantConcept.code == concept_code)
                    )
                    existing_concept = existing.scalar_one_or_none()

                    if existing_concept:
                        # 更新
                        existing_concept.name = concept_data["name"]
                        existing_concept.sort = concept_data["sort"]
                        existing_concept.latest_price = concept_data["latest_price"]
                        existing_concept.change_amount = concept_data["change_amount"]
                        existing_concept.change_percent = concept_data["change_percent"]
                        existing_concept.total_market_cap = concept_data[
                            "total_market_cap"
                        ]
                        existing_concept.turnover_rate = concept_data["turnover_rate"]
                        existing_concept.up_count = concept_data["up_count"]
                        existing_concept.down_count = concept_data["down_count"]
                        existing_concept.leading_stock = concept_data["leading_stock"]
                        existing_concept.leading_stock_change = concept_data[
                            "leading_stock_change"
                        ]
                        existing_concept.updated_at = now()
                        updated_count += 1
                    else:
                        # 插入
                        concept = QuantConcept(
                            code=concept_data["code"],
                            name=concept_data["name"],
                            sort=concept_data["sort"],
                            latest_price=concept_data["latest_price"],
                            change_amount=concept_data["change_amount"],
                            change_percent=concept_data["change_percent"],
                            total_market_cap=concept_data["total_market_cap"],
                            turnover_rate=concept_data["turnover_rate"],
                            up_count=concept_data["up_count"],
                            down_count=concept_data["down_count"],
                            leading_stock=concept_data["leading_stock"],
                            leading_stock_change=concept_data["leading_stock_change"],
                            status=1,
                            created_at=now(),
                        )
                        session.add(concept)
                        added_count += 1

                await session.commit()

            # 记录日志（在主事务提交后）
            logs_created_count = 0
            logs_updated_count = 0
            current_date = now().date()

            async with get_async_session() as log_session:
                for concept_data in concept_list:
                    # 获取概念ID和description
                    concept = await log_session.execute(
                        select(QuantConcept.id, QuantConcept.description).where(
                            QuantConcept.code == concept_data["code"]
                        )
                    )
                    concept_result = concept.mappings().one_or_none()
                    concept_id = concept_result["id"] if concept_result else None
                    concept_description = (
                        concept_result["description"] if concept_result else None
                    )

                    if concept_id:
                        # 查询当天是否已有该概念的日志记录
                        existing_log = await log_session.execute(
                            select(QuantConceptLog).where(
                                QuantConceptLog.concept_id == concept_id,
                                QuantConceptLog.record_date == current_date,
                            )
                        )
                        log_record = existing_log.scalar_one_or_none()

                        if log_record:
                            # 更新现有记录
                            log_record.name = concept_data["name"]
                            log_record.code = concept_data["code"]
                            log_record.sort = concept_data["sort"]
                            log_record.latest_price = concept_data["latest_price"]
                            log_record.change_amount = concept_data["change_amount"]
                            log_record.change_percent = concept_data["change_percent"]
                            log_record.total_market_cap = concept_data[
                                "total_market_cap"
                            ]
                            log_record.turnover_rate = concept_data["turnover_rate"]
                            log_record.up_count = concept_data["up_count"]
                            log_record.down_count = concept_data["down_count"]
                            log_record.leading_stock = concept_data["leading_stock"]
                            log_record.leading_stock_change = concept_data[
                                "leading_stock_change"
                            ]
                            log_record.description = concept_description
                            log_record.status = 1
                            log_record.updated_at = now()
                            logs_updated_count += 1
                        else:
                            # 创建新记录
                            log_record = QuantConceptLog(
                                concept_id=concept_id,
                                record_date=current_date,
                                name=concept_data["name"],
                                code=concept_data["code"],
                                sort=concept_data["sort"],
                                latest_price=concept_data["latest_price"],
                                change_amount=concept_data["change_amount"],
                                change_percent=concept_data["change_percent"],
                                total_market_cap=concept_data["total_market_cap"],
                                turnover_rate=concept_data["turnover_rate"],
                                up_count=concept_data["up_count"],
                                down_count=concept_data["down_count"],
                                leading_stock=concept_data["leading_stock"],
                                leading_stock_change=concept_data[
                                    "leading_stock_change"
                                ],
                                description=concept_description,
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
                    "total": len(concept_list),
                    "logs_created": logs_created_count,
                    "logs_updated": logs_updated_count,
                },
                message=f"同步完成，新增 {added_count} 条，更新 {updated_count} 条，日志新增 {logs_created_count} 条，日志更新 {logs_updated_count} 条。",
            )
        except Exception as e:
            return error(f"同步失败: {str(e)}")

    async def sync_relation(self) -> JSONResponse:
        """
        同步概念-股票关联关系（手动触发）

        Returns:
            JSONResponse: 同步结果统计
        """

        # a = await self.sync_single_concept_relation(3, "BK0957")
        # return success(a)
        # 异步同步所有概念的关联关系
        from Modules.quant.queues.concept_queues import sync_concept_relation_queue

        try:
            async with get_async_session() as session:
                # 查询所有概念，用于同步关联关系
                all_concepts_result = await session.execute(select(QuantConcept))
                all_concepts = all_concepts_result.scalars().all()

                for index, concept in enumerate(all_concepts):
                    # 设置延时，避免同时执行太多任务（每个任务间隔2秒）
                    countdown = index * 5
                    sync_concept_relation_queue.apply_async(
                        args=[concept.id, concept.code],
                        countdown=countdown,
                    )

                return success(
                    {
                        "total": len(all_concepts),
                    },
                    message=f"同步任务已提交，共 {len(all_concepts)} 个概念，任务将在后台异步执行。",
                )
        except Exception as e:
            return error(f"同步失败: {str(e)}")

    async def simple_list(self, data: dict[str, Any] | None = None) -> JSONResponse:
        """
        获取概念简单列表（不分页，只返回 id 和 name）

        Args:
            data: 查询参数，可选参数：
                - status: 状态筛选（1-启用，0-禁用）
                - sort: 排序规则（如：{"name":"asc"} 或 "name asc"）

        Returns:
            JSONResponse: 概念简单列表
        """
        if data is None:
            data = {}

        async with get_async_session() as session:
            # 构建基础查询，只查询 id 和 name 字段
            query = select(QuantConcept.id, QuantConcept.name)

            # 应用状态筛选
            status = data.get("status")
            if status is not None:
                query = query.where(QuantConcept.status == status)

            # 应用排序（默认按 id 升序）
            sort_param = data.get("sort")
            if sort_param:
                query = await self.apply_sorting(query, QuantConcept, sort_param)
            else:
                query = await self.apply_sorting(query, QuantConcept, {"id": "asc"})

            # 执行查询
            result = await session.execute(query)
            concepts = result.mappings().all()

            # 转换为列表格式
            items = [
                {"id": concept["id"], "name": concept["name"]} for concept in concepts
            ]

            return success(items)

    def sync_single_concept_relation_sync(
        self, concept_id: int, concept_code: str
    ) -> dict:
        """
        同步单个概念的股票关联关系（同步版本，用于 Celery 任务）

        Args:
            concept_id: 概念ID
            concept_code: 概念代码

        Returns:
            dict: 同步结果统计
        """
        with get_sync_session() as session:
            try:
                # 验证概念是否存在
                concept_result = session.execute(
                    select(QuantConcept).where(QuantConcept.id == concept_id)
                )
                concept = concept_result.scalar_one_or_none()

                if not concept:
                    logger.error(
                        f"概念不存在: concept_id={concept_id}, concept_code={concept_code}"
                    )
                    return {
                        "success": False,
                        "concept_id": concept_id,
                        "concept_code": concept_code,
                        "error": "概念不存在",
                        "added": 0,
                    }

                # 获取所有股票（构建股票代码到ID的映射）
                stock_result = session.execute(select(QuantStock))
                stocks = stock_result.scalars().all()
                stock_code_to_id = {stock.stock_code: stock.id for stock in stocks}

                # 先删除该概念的所有关联关系（批量删除）
                session.execute(
                    delete(QuantStockConcept).where(
                        QuantStockConcept.concept_id == concept_id  # type: ignore
                    )
                )

                # 获取概念的成分股（使用 asyncio.to_thread 包装异步调用）
                stock_codes = asyncio.run(
                    self.data_fetch_service.fetch_concept_stocks(concept_code)
                )

                # 建立关联关系
                added_count = 0
                for stock_code in stock_codes:
                    stock_id = stock_code_to_id.get(stock_code)
                    if stock_id:
                        relation = QuantStockConcept(
                            stock_id=stock_id, concept_id=concept_id, created_at=now()
                        )
                        session.add(relation)
                        added_count += 1

                session.commit()

                logger.info(
                    f"概念关联同步成功: concept_id={concept_id}, "
                    f"concept_name={concept.name}, added={added_count}"
                )

                return {
                    "success": True,
                    "concept_id": concept_id,
                    "concept_code": concept_code,
                    "concept_name": concept.name,
                    "added": added_count,
                }

            except Exception as e:
                session.rollback()
                logger.error(
                    f"概念关联同步失败: concept_id={concept_id}, "
                    f"concept_code={concept_code}, error={str(e)}"
                )
                raise
