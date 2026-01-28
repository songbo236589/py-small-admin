"""
股票业务服务 - 负责股票相关的业务逻辑
"""

import math
from typing import Any

import pandas as pd
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import selectinload
from sqlmodel import select

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import now
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.quant.models.quant_concept import QuantConcept
from Modules.quant.models.quant_industry import QuantIndustry
from Modules.quant.models.quant_stock import QuantStock
from Modules.quant.services.quant_data_fetch_service import QuantDataFetchService


class QuantStockService(BaseService):
    """股票业务服务 - 负责股票相关的业务逻辑"""

    def __init__(self):
        """初始化股票服务"""
        super().__init__()
        self.data_fetch_service = QuantDataFetchService()

    def _clean_nan_values(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        清理字典中的 nan 值，将其转换为 None

        Args:
            data: 待清理的字典

        Returns:
            dict[str, Any]: 清理后的字典
        """
        cleaned_data = {}
        for key, value in data.items():
            # 检查是否为 nan 值
            if isinstance(value, float) and math.isnan(value):
                cleaned_data[key] = None
            else:
                cleaned_data[key] = value
        return cleaned_data

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """
        获取股票列表（支持搜索、筛选、分页）

        支持的筛选条件：
        - page: 页码，从1开始（默认1）
        - limit: 每页返回的记录数量（默认20）
        - concept_id: 概念ID，精确匹配，筛选属于该概念的股票
        - stock_code: 股票代码，支持模糊匹配
        - stock_name: 股票名称，支持模糊匹配
        - market: 市场类型，精确匹配
        - exchange: 交易所，精确匹配
        - industry_id: 行业ID，精确匹配
        - list_status: 上市状态，精确匹配
        - trade_status: 交易状态，精确匹配
        - is_st: 是否ST股，精确匹配
        - stock_type: 股票类型，精确匹配
        - total_market_cap: 总市值，区间匹配
        - circulating_market_cap: 流通市值，区间匹配
        - pe_ratio: 市盈率，区间匹配
        - pb_ratio: 市净率，区间匹配
        - total_shares: 总股本，区间匹配
        - circulating_shares: 流通股本，区间匹配
        - ipo_price: 发行价格，区间匹配
        - ipo_shares: 发行数量，区间匹配
        - latest_price: 最新价，区间匹配
        - open_price: 今开，区间匹配
        - close_price: 昨收，区间匹配
        - high_price: 最高，区间匹配
        - low_price: 最低，区间匹配
        - change_percent: 涨跌幅，区间匹配
        - change_amount: 涨跌额，区间匹配
        - change_speed: 涨速，区间匹配
        - volume: 成交量，区间匹配
        - amount: 成交额，区间匹配
        - volume_ratio: 量比，区间匹配
        - turnover_rate: 换手率，区间匹配
        - amplitude: 振幅，区间匹配
        - change_5min: 5分钟涨跌，区间匹配
        - change_60day: 60日涨跌幅，区间匹配
        - change_ytd: 年初至今涨跌幅，区间匹配
        - description: 股票描述，支持模糊匹配
        - website: 官方网站，支持模糊匹配
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
            JSONResponse: 股票列表数据
        """
        page = data.get("page", 1)
        size = data.get("limit", 20)

        # 转换单位：将搜索参数从显示单位（亿元/万股）转换回数据库单位（元/股）
        if data.get("total_market_cap_start") is not None:
            data["total_market_cap_start"] = (
                float(data["total_market_cap_start"]) * 100000000
            )
        if data.get("total_market_cap_end") is not None:
            data["total_market_cap_end"] = (
                float(data["total_market_cap_end"]) * 100000000
            )

        if data.get("circulating_market_cap_start") is not None:
            data["circulating_market_cap_start"] = (
                float(data["circulating_market_cap_start"]) * 100000000
            )
        if data.get("circulating_market_cap_end") is not None:
            data["circulating_market_cap_end"] = (
                float(data["circulating_market_cap_end"]) * 100000000
            )

        if data.get("total_shares_start") is not None:
            data["total_shares_start"] = float(data["total_shares_start"]) * 10000
        if data.get("total_shares_end") is not None:
            data["total_shares_end"] = float(data["total_shares_end"]) * 10000

        if data.get("circulating_shares_start") is not None:
            data["circulating_shares_start"] = (
                float(data["circulating_shares_start"]) * 10000
            )
        if data.get("circulating_shares_end") is not None:
            data["circulating_shares_end"] = (
                float(data["circulating_shares_end"]) * 10000
            )

        if data.get("total_shares_start") is not None:
            data["total_shares_start"] = float(data["total_shares_start"]) * 10000
        if data.get("total_shares_end") is not None:
            data["total_shares_end"] = float(data["total_shares_end"]) * 10000

        if data.get("circulating_shares_start") is not None:
            data["circulating_shares_start"] = (
                float(data["circulating_shares_start"]) * 10000
            )
        if data.get("circulating_shares_end") is not None:
            data["circulating_shares_end"] = (
                float(data["circulating_shares_end"]) * 10000
            )

        # 转换单位：将搜索参数从显示单位（亿元）转换回数据库单位（元）
        if data.get("volume_start") is not None:
            data["volume_start"] = float(data["volume_start"]) * 100000000
        if data.get("volume_end") is not None:
            data["volume_end"] = float(data["volume_end"]) * 100000000

        if data.get("amount_start") is not None:
            data["amount_start"] = float(data["amount_start"]) * 100000000
        if data.get("amount_end") is not None:
            data["amount_end"] = float(data["amount_end"]) * 100000000

        # 设置文本搜索字段
        data["text_fields"] = [
            "stock_code",
            "stock_name",
            "description",
            "website",
        ]
        # 精确匹配字段
        data["exact_fields"] = [
            "market",
            "exchange",
            "industry_id",
            "list_status",
            "trade_status",
            "is_st",
            "stock_type",
            "status",
        ]
        # 应用范围筛选
        data["range_fields"] = [
            "created_at",
            "updated_at",
            "list_date",
            "delist_date",
            "total_market_cap",
            "circulating_market_cap",
            "pe_ratio",
            "pb_ratio",
            "total_shares",
            "circulating_shares",
            "ipo_price",
            "ipo_shares",
            # 价格行情字段
            "latest_price",
            "open_price",
            "close_price",
            "high_price",
            "low_price",
            "change_percent",
            "change_amount",
            "change_speed",
            # 交易指标字段
            "volume",
            "amount",
            "volume_ratio",
            "turnover_rate",
            "amplitude",
            "change_5min",
            "change_60day",
            "change_ytd",
        ]

        async with get_async_session() as session:
            # 构建基础查询
            query = select(QuantStock)

            # 处理概念ID筛选
            concept_id = data.get("concept_id")
            if concept_id:
                from Modules.quant.models.quant_stock_concept import QuantStockConcept

                # 使用 JOIN 查询关联表
                query = query.join(
                    QuantStockConcept,
                    QuantStock.id == QuantStockConcept.stock_id,  # type: ignore
                )
                query = query.filter(QuantStockConcept.concept_id == concept_id)

            query = query.options(
                selectinload(QuantStock.concepts).load_only(
                    *[QuantConcept.id, QuantConcept.name]
                ),
                selectinload(QuantStock.industry).load_only(
                    *[QuantIndustry.id, QuantIndustry.name]
                ),
            )

            # 搜索
            query = await self.apply_search_filters(query, QuantStock, data)

            # 应用排序（默认按总市值由大到小排序）
            sort_param = data.get("sort")
            if not sort_param:
                sort_param = {"total_market_cap": "desc"}
            query = await self.apply_sorting(query, QuantStock, sort_param)

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for stock in page_data.items:
                d = stock.__dict__.copy()
                # 格式化日期字段
                if d.get("list_date"):
                    d["list_date"] = d["list_date"].isoformat()
                if d.get("delist_date"):
                    d["delist_date"] = d["delist_date"].isoformat()
                if d.get("created_at"):
                    d["created_at"] = d["created_at"].isoformat()
                if d.get("updated_at"):
                    d["updated_at"] = d["updated_at"].isoformat()
                # 转换 Decimal 为字符串
                if d.get("total_market_cap"):
                    d["total_market_cap"] = (
                        f"{float(d['total_market_cap']) / 100000000:.4f}"
                    )
                if d.get("circulating_market_cap"):
                    d["circulating_market_cap"] = (
                        f"{float(d['circulating_market_cap']) / 100000000:.4f}"
                    )
                if d.get("pe_ratio"):
                    d["pe_ratio"] = str(d["pe_ratio"])
                if d.get("pb_ratio"):
                    d["pb_ratio"] = str(d["pb_ratio"])
                if d.get("total_shares"):
                    d["total_shares"] = f"{float(d['total_shares']) / 10000:.4f}"
                if d.get("circulating_shares"):
                    d["circulating_shares"] = (
                        f"{float(d['circulating_shares']) / 10000:.4f}"
                    )
                if d.get("ipo_price"):
                    d["ipo_price"] = str(d["ipo_price"])
                if d.get("ipo_shares"):
                    d["ipo_shares"] = str(d["ipo_shares"])
                # 价格行情字段
                if d.get("latest_price"):
                    d["latest_price"] = str(d["latest_price"])
                if d.get("open_price"):
                    d["open_price"] = str(d["open_price"])
                if d.get("close_price"):
                    d["close_price"] = str(d["close_price"])
                if d.get("high_price"):
                    d["high_price"] = str(d["high_price"])
                if d.get("low_price"):
                    d["low_price"] = str(d["low_price"])
                if d.get("change_percent"):
                    d["change_percent"] = str(d["change_percent"])
                if d.get("change_amount"):
                    d["change_amount"] = str(d["change_amount"])
                if d.get("change_speed"):
                    d["change_speed"] = str(d["change_speed"])
                # 交易指标字段
                if d.get("volume"):
                    d["volume"] = f"{float(d['volume']) / 100000000:.4f}"
                if d.get("amount"):
                    d["amount"] = f"{float(d['amount']) / 100000000:.4f}"
                if d.get("volume_ratio"):
                    d["volume_ratio"] = str(d["volume_ratio"])
                if d.get("turnover_rate"):
                    d["turnover_rate"] = str(d["turnover_rate"])
                if d.get("amplitude"):
                    d["amplitude"] = str(d["amplitude"])
                if d.get("change_5min"):
                    d["change_5min"] = str(d["change_5min"])
                if d.get("change_60day"):
                    d["change_60day"] = str(d["change_60day"])
                if d.get("change_ytd"):
                    d["change_ytd"] = str(d["change_ytd"])
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
        添加股票

        Args:
            data: 股票数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_add(
            data=data,
            model_class=QuantStock,
            pre_operation_callback=self._stock_add_pre_operation,
        )

    async def _stock_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """
        股票添加前置操作

        Args:
            data: 股票数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        stock_code = data.get("stock_code")

        # 检查股票代码是否已存在
        existing_stock = await session.execute(
            select(QuantStock).where(QuantStock.stock_code == stock_code)
        )
        if existing_stock.scalar_one_or_none():
            return error("股票代码已存在")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """
        获取股票信息（用于编辑）

        Args:
            id: 股票ID

        Returns:
            JSONResponse: 股票信息
        """
        async with get_async_session() as session:
            result = await session.execute(
                select(
                    *[
                        QuantStock.id,
                        QuantStock.stock_code,
                        QuantStock.stock_name,
                        QuantStock.market,
                        QuantStock.exchange,
                        QuantStock.industry_id,
                        QuantStock.list_status,
                        QuantStock.trade_status,
                        QuantStock.is_st,
                        QuantStock.stock_type,
                        # 价格行情字段
                        QuantStock.latest_price,
                        QuantStock.open_price,
                        QuantStock.close_price,
                        QuantStock.high_price,
                        QuantStock.low_price,
                        QuantStock.change_percent,
                        QuantStock.change_amount,
                        QuantStock.change_speed,
                        # 交易指标字段
                        QuantStock.volume,
                        QuantStock.amount,
                        QuantStock.volume_ratio,
                        QuantStock.turnover_rate,
                        QuantStock.amplitude,
                        QuantStock.change_5min,
                        QuantStock.change_60day,
                        QuantStock.change_ytd,
                        # 财务与估值字段
                        QuantStock.total_market_cap,
                        QuantStock.circulating_market_cap,
                        QuantStock.pe_ratio,
                        QuantStock.pb_ratio,
                        QuantStock.total_shares,
                        QuantStock.circulating_shares,
                        QuantStock.list_date,
                        QuantStock.delist_date,
                        QuantStock.ipo_price,
                        QuantStock.ipo_shares,
                        QuantStock.description,
                        QuantStock.website,
                        QuantStock.logo_url,
                        QuantStock.status,
                    ]
                ).where(QuantStock.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("股票不存在")

            # 转换为字典并格式化日期和 Decimal 字段
            data = dict(info)
            # 格式化日期字段
            if data.get("list_date"):
                data["list_date"] = data["list_date"].isoformat()
            if data.get("delist_date"):
                data["delist_date"] = data["delist_date"].isoformat()

            # 转换 Decimal 为字符串
            for key in [
                "total_market_cap",
                "circulating_market_cap",
                "pe_ratio",
                "pb_ratio",
                "total_shares",
                "circulating_shares",
                "ipo_price",
                "ipo_shares",
                # 价格行情字段
                "latest_price",
                "open_price",
                "close_price",
                "high_price",
                "low_price",
                "change_percent",
                "change_amount",
                "change_speed",
                # 交易指标字段
                "volume",
                "amount",
                "volume_ratio",
                "turnover_rate",
                "amplitude",
                "change_5min",
                "change_60day",
                "change_ytd",
            ]:
                if data.get(key) is not None:
                    data[key] = str(data[key])

            return success(data)

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """
        更新股票信息

        Args:
            id: 股票ID
            data: 更新数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_update(
            id=id,
            data=data,
            model_class=QuantStock,
            pre_operation_callback=self._stock_update_pre_operation,
        )

    async def _stock_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """
        股票更新前置操作

        Args:
            id: 股票ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        stock_code = data.get("stock_code")

        # 检查股票代码是否已被其他股票使用
        if stock_code:
            existing_stock = await session.execute(
                select(QuantStock).where(QuantStock.stock_code == stock_code)
            )
            stock_with_code = existing_stock.scalar_one_or_none()

            if stock_with_code and stock_with_code.id != id:
                return error("股票代码已存在")

        return data, session

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """
        股票状态

        Args:
            id: 股票ID
            data: 状态数据

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_update(id=id, data=data, model_class=QuantStock)

    async def destroy(self, id: int) -> JSONResponse:
        """
        删除股票

        Args:
            id: 股票ID

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_destroy(id=id, model_class=QuantStock)

    async def delete_all(self, id_array: list[int]) -> JSONResponse:
        """
        批量删除股票

        Args:
            id_array: 股票ID列表

        Returns:
            JSONResponse: 操作结果
        """
        return await self.common_destroy_all(id_array=id_array, model_class=QuantStock)

    def _process_a_stock_data(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """
        处理A股股票数据

        A股数据来源：stock_zh_a_spot_em
        A股数据字段：23个字段，包含完整的交易指标和财务估值数据
        ['序号', '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额',
         '振幅', '最高', '最低', '今开', '昨收', ' 量比', '换手率', '市盈率-动态',
         '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']

        Args:
            df: A股股票数据DataFrame

        Returns:
            list[dict[str, Any]]: 处理后的股票数据列表
        """
        stock_list = []
        for _, row in df.iterrows():
            code = row["代码"]
            name = row["名称"]

            # 根据股票代码前缀判断市场类型
            # 沪市主板：600 / 601 / 603 / 605
            # 深市主板：000 / 001 / 002 / 003
            # 创业板：  300 / 301
            # 科创板：  688
            # 北交所：  43 / 83 / 87 / 88
            if code.startswith(("600", "601", "603", "605", "688")):
                stock_market = 1  # 上海（主板 + 科创板）
                exchange = 1  # 上海证券交易所(SSE)
            elif code.startswith(("000", "001", "002", "003", "300", "301")):
                stock_market = 2  # 深圳（主板 + 创业板）
                exchange = 2  # 深圳证券交易所(SZSE)
            elif code.startswith(("43", "83", "87", "88")):
                stock_market = 3  # 北交所
                exchange = 3  # 北京证券交易所(BSE)
            else:
                continue  # 跳过其他代码格式的股票

            # 判断股票类型
            if code.startswith(
                ("600", "601", "603", "605", "000", "001", "002", "003")
            ):
                stock_type = 1  # 主板
            elif code.startswith(("300", "301")):
                stock_type = 2  # 创业板
            elif code.startswith("688"):
                stock_type = 3  # 科创板
            elif code.startswith(("43", "83", "87", "88")):
                stock_type = 4  # 北交所
            else:
                stock_type = None

            # 判断交易状态（根据最新价判断）
            latest_price = row.get("最新价")
            if latest_price is None or latest_price == "" or latest_price == "-":
                trade_status = 0  # 停牌
            else:
                trade_status = 1  # 正常交易

            # 判断是否为ST股（根据股票名称判断）
            is_st = 1 if "ST" in name else 0

            # 提取完整信息
            stock_data = {
                "code": code,
                "name": name,
                "market": stock_market,
                "exchange": exchange,
                "stock_type": stock_type,
                # 状态字段
                "trade_status": trade_status,
                "is_st": is_st,
                # 价格行情字段
                "latest_price": row.get("最新价"),
                "open_price": row.get("今开"),
                "close_price": row.get("昨收"),
                "high_price": row.get("最高"),
                "low_price": row.get("最低"),
                "change_percent": row.get("涨跌幅"),
                "change_amount": row.get("涨跌额"),
                "change_speed": row.get("涨速"),
                # 交易指标字段
                "volume": row.get("成交量"),
                "amount": row.get("成交额"),
                "volume_ratio": row.get("量比"),
                "turnover_rate": row.get("换手率"),
                "amplitude": row.get("振幅"),
                "change_5min": row.get("5分钟涨跌"),
                "change_60day": row.get("60日涨跌幅"),
                "change_ytd": row.get("年初至今涨跌幅"),
                # 财务与估值字段
                "pe_ratio": row.get("市盈率-动态"),
                "pb_ratio": row.get("市净率"),
                "total_market_cap": row.get("总市值"),
                "circulating_market_cap": row.get("流通市值"),
            }
            stock_list.append(stock_data)

        return stock_list

    def _process_hk_stock_data(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """
        处理港股股票数据

        港股数据来源：stock_hk_spot_em
        港股数据字段：12个字段，缺少所有交易指标和财务估值数据
        ['序号', '代码', '名称', '最新价', '涨跌额', '涨跌幅', '今开', '最高', '最低', '昨收', '成交量', '成交额']

        注意：港股数据不包含以下字段（全部返回None）：
        - 交易指标：涨速、量比、换手率、振幅、5分钟涨跌、60日涨跌幅、年初至今涨跌幅
        - 财务估值：市盈率、市净率、总市值、流通市值

        Args:
            df: 港股股票数据DataFrame

        Returns:
            list[dict[str, Any]]: 处理后的股票数据列表
        """
        stock_list = []
        for _, row in df.iterrows():
            # 港股代码和名称字段
            code = row.get("代码")
            name = row.get("名称")

            if not code or not name:
                continue

            # 港股市场固定为4，交易所固定为4（HKEX）
            stock_market = 4
            exchange = 4

            # 港股没有主板/创业板之分，设置为None
            stock_type = None

            # 判断交易状态（根据最新价判断）
            latest_price = row.get("最新价")
            if latest_price is None or latest_price == "" or latest_price == "-":
                trade_status = 0  # 停牌
            else:
                trade_status = 1  # 正常交易

            # 港股没有ST制度
            is_st = 0

            # 提取完整信息（港股接口只有12个字段，缺少所有交易指标和财务估值字段）
            stock_data = {
                "code": code,
                "name": name,
                "market": stock_market,
                "exchange": exchange,
                "stock_type": stock_type,
                # 状态字段
                "trade_status": trade_status,
                "is_st": is_st,
                # 价格行情字段（港股有这些字段）
                "latest_price": row.get("最新价"),
                "open_price": row.get("今开"),
                "close_price": row.get("昨收"),
                "high_price": row.get("最高"),
                "low_price": row.get("最低"),
                "change_percent": row.get("涨跌幅"),
                "change_amount": row.get("涨跌额"),
                "change_speed": None,  # 港股无此字段
                # 交易指标字段（港股只有成交量和成交额）
                "volume": row.get("成交量"),
                "amount": row.get("成交额"),
                "volume_ratio": None,  # 港股无此字段
                "turnover_rate": None,  # 港股无此字段
                "amplitude": None,  # 港股无此字段
                "change_5min": None,  # 港股无此字段
                "change_60day": None,  # 港股无此字段
                "change_ytd": None,  # 港股无此字段
                # 财务与估值字段（港股无这些字段）
                "pe_ratio": None,  # 港股无此字段
                "pb_ratio": None,  # 港股无此字段
                "total_market_cap": None,  # 港股无此字段
                "circulating_market_cap": None,  # 港股无此字段
            }
            stock_list.append(stock_data)

        return stock_list

    def _process_us_stock_data(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """
        处理美股股票数据

        美股数据来源：stock_us_spot_em
        美股数据字段：16个字段，字段名与A股不同
        ['序号', '名称', '最新价', '涨跌额', '涨跌幅', '开盘价', '最高价', '最低价',
         '昨收价', '总市值', '市盈率', '成交量', '成交额', '振幅', '换手率', '代码']

        注意：
        1. 美股字段名与A股不同（如：开盘价 vs 今开，最高价 vs 最高等）
        2. 美股数据不包含以下字段（全部返回None）：
           - 交易指标：涨速、量比、5分钟涨跌、60日涨跌幅、年初至今涨跌幅
           - 财务估值：市净率、流通市值
        3. 美股包含但港股不包含的字段：总市值、市盈率、振幅、换手率

        Args:
            df: 美股股票数据DataFrame

        Returns:
            list[dict[str, Any]]: 处理后的股票数据列表
        """
        stock_list = []
        for _, row in df.iterrows():
            # 美股代码和名称字段
            code = row.get("代码")
            name = row.get("名称")

            if not code or not name:
                continue

            # 美股市场固定为5
            stock_market = 5

            # 根据股票代码前缀判断交易所
            # AkShare返回的美股代码格式：交易所代码.股票代码
            # 105. → NASDAQ (纳斯达克)
            # 106. → NYSE (纽约证券交易所)
            # 107. → AMEX (美国证券交易所)
            if isinstance(code, str) and "." in code:
                # 提取交易所前缀
                prefix = code.split(".")[0]
                if prefix == "105":
                    exchange = 5  # NASDAQ
                elif prefix == "106":
                    exchange = 6  # NYSE
                elif prefix == "107":
                    exchange = 7  # AMEX
                else:
                    exchange = 6  # NYSE (默认)

                # 去掉交易所前缀，只保留股票代码
                code = code.split(".")[1]
            else:
                exchange = 6  # NYSE (默认)

            # 美股没有主板/创业板之分，设置为None
            stock_type = None

            # 判断交易状态（根据最新价判断）
            latest_price = row.get("最新价")
            if latest_price is None or latest_price == "" or latest_price == "-":
                trade_status = 0  # 停牌
            else:
                trade_status = 1  # 正常交易

            # 美股没有ST制度
            is_st = 0

            # 提取完整信息（美股接口缺少的字段会自动返回None）
            stock_data = {
                "code": code,
                "name": name,
                "market": stock_market,
                "exchange": exchange,
                "stock_type": stock_type,
                # 状态字段
                "trade_status": trade_status,
                "is_st": is_st,
                # 价格行情字段（美股字段名与A股不同）
                "latest_price": row.get("最新价"),
                "open_price": row.get("开盘价"),  # 美股字段名：开盘价
                "close_price": row.get("昨收价"),  # 美股字段名：昨收价
                "high_price": row.get("最高价"),  # 美股字段名：最高价
                "low_price": row.get("最低价"),  # 美股字段名：最低价
                "change_percent": row.get("涨跌幅"),
                "change_amount": row.get("涨跌额"),
                "change_speed": None,  # 美股无此字段
                # 交易指标字段
                "volume": row.get("成交量"),
                "amount": row.get("成交额"),
                "volume_ratio": None,  # 美股无此字段
                "turnover_rate": row.get("换手率"),  # 美股有此字段
                "amplitude": row.get("振幅"),  # 美股有此字段
                "change_5min": None,  # 美股无此字段
                "change_60day": None,  # 美股无此字段
                "change_ytd": None,  # 美股无此字段
                # 财务与估值字段
                "pe_ratio": row.get("市盈率"),  # 美股字段名：市盈率
                "pb_ratio": None,  # 美股无此字段
                "total_market_cap": row.get("总市值"),  # 美股有此字段
                "circulating_market_cap": None,  # 美股无此字段
            }
            stock_list.append(stock_data)

        return stock_list

    async def sync_stock_list(self, market: int = 1) -> JSONResponse:
        """
        同步股票列表（手动触发）

        Args:
            market: 市场类型（1=上海、2=深圳、3=北交所、4=港股、5=美股）

        Returns:
            JSONResponse: 同步结果统计
        """
        try:
            # 根据市场类型获取股票列表
            if market == 1 or market == 2 or market == 3:
                df = await self.data_fetch_service.fetch_a_stock_list()
            elif market == 4:
                df = await self.data_fetch_service.fetch_hk_stock_list()
            elif market == 5:
                df = await self.data_fetch_service.fetch_us_stock_list()
            else:
                return error("不支持的市场类型")

            if df.empty:
                return error("未获取到股票数据")

            # 根据市场类型处理数据
            if market == 4:
                stock_list = self._process_hk_stock_data(df)
            elif market == 5:
                stock_list = self._process_us_stock_data(df)
            else:
                stock_list = self._process_a_stock_data(df)

            # 批量插入或更新数据库
            async with get_async_session() as session:
                added_count = 0
                updated_count = 0

                for stock_data in stock_list:
                    stock_code = stock_data.get("code")

                    # 检查是否存在
                    existing = await session.execute(
                        select(QuantStock).where(QuantStock.stock_code == stock_code)
                    )
                    existing_stock = existing.scalar_one_or_none()
                    # 清理 nan 值
                    cleaned_data = self._clean_nan_values(stock_data)
                    if existing_stock:
                        # 更新基础信息
                        existing_stock.stock_name = cleaned_data.get("name")
                        existing_stock.stock_type = cleaned_data.get("stock_type")
                        existing_stock.exchange = cleaned_data.get("exchange")
                        # 状态字段
                        existing_stock.trade_status = cleaned_data.get("trade_status")
                        existing_stock.is_st = cleaned_data.get("is_st")
                        # 价格行情字段
                        existing_stock.latest_price = cleaned_data.get("latest_price")
                        existing_stock.open_price = cleaned_data.get("open_price")
                        existing_stock.close_price = cleaned_data.get("close_price")
                        existing_stock.high_price = cleaned_data.get("high_price")
                        existing_stock.low_price = cleaned_data.get("low_price")
                        existing_stock.change_percent = cleaned_data.get(
                            "change_percent"
                        )
                        existing_stock.change_amount = cleaned_data.get("change_amount")
                        existing_stock.change_speed = cleaned_data.get("change_speed")
                        # 交易指标字段
                        existing_stock.volume = cleaned_data.get("volume")
                        existing_stock.amount = cleaned_data.get("amount")
                        existing_stock.volume_ratio = cleaned_data.get("volume_ratio")
                        existing_stock.turnover_rate = cleaned_data.get("turnover_rate")
                        existing_stock.amplitude = cleaned_data.get("amplitude")
                        existing_stock.change_5min = cleaned_data.get("change_5min")
                        existing_stock.change_60day = cleaned_data.get("change_60day")
                        existing_stock.change_ytd = cleaned_data.get("change_ytd")
                        # 财务与估值字段
                        existing_stock.pe_ratio = cleaned_data.get("pe_ratio")
                        existing_stock.pb_ratio = cleaned_data.get("pb_ratio")
                        existing_stock.total_market_cap = cleaned_data.get(
                            "total_market_cap"
                        )
                        existing_stock.circulating_market_cap = cleaned_data.get(
                            "circulating_market_cap"
                        )
                        existing_stock.updated_at = now()
                        updated_count += 1
                    else:
                        # 插入完整信息
                        stock = QuantStock(
                            stock_code=cleaned_data["code"],
                            stock_name=cleaned_data["name"],
                            market=cleaned_data["market"],
                            exchange=cleaned_data["exchange"],
                            stock_type=cleaned_data["stock_type"],
                            # 状态字段
                            list_status=1,
                            trade_status=cleaned_data.get("trade_status"),
                            is_st=cleaned_data.get("is_st"),
                            status=1,
                            # 价格行情字段
                            latest_price=cleaned_data.get("latest_price"),
                            open_price=cleaned_data.get("open_price"),
                            close_price=cleaned_data.get("close_price"),
                            high_price=cleaned_data.get("high_price"),
                            low_price=cleaned_data.get("low_price"),
                            change_percent=cleaned_data.get("change_percent"),
                            change_amount=cleaned_data.get("change_amount"),
                            change_speed=cleaned_data.get("change_speed"),
                            # 交易指标字段
                            volume=cleaned_data.get("volume"),
                            amount=cleaned_data.get("amount"),
                            volume_ratio=cleaned_data.get("volume_ratio"),
                            turnover_rate=cleaned_data.get("turnover_rate"),
                            amplitude=cleaned_data.get("amplitude"),
                            change_5min=cleaned_data.get("change_5min"),
                            change_60day=cleaned_data.get("change_60day"),
                            change_ytd=cleaned_data.get("change_ytd"),
                            # 财务与估值字段
                            pe_ratio=cleaned_data.get("pe_ratio"),
                            pb_ratio=cleaned_data.get("pb_ratio"),
                            total_market_cap=cleaned_data.get("total_market_cap"),
                            circulating_market_cap=cleaned_data.get(
                                "circulating_market_cap"
                            ),
                            created_at=now(),
                        )
                        session.add(stock)
                        added_count += 1

                await session.commit()

            return success(
                {
                    "added": added_count,
                    "updated": updated_count,
                    "total": len(stock_list),
                },
                message=f"同步完成，新增 {added_count} 条，更新 {updated_count} 条。",
            )
        except Exception as e:
            return error(f"同步失败: {str(e)}")
