"""
股票控制器 - 负责股票相关的API接口
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
    ListStatusRequest,
    PaginationRequest,
)
from Modules.quant.services.quant_stock_service import QuantStockService
from Modules.quant.validators.quant_stock_validator import (
    QuantStockAddUpdateRequest,
    QuantStockSyncRequest,
)


class QuantStockController:
    """股票控制器 - 负责股票相关的API接口"""

    def __init__(self):
        """初始化股票控制器"""
        self.service = QuantStockService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录，用于控制每页显示数量"),
        concept_id: int | None = Query(None, description="概念id"),
        stock_code: str | None = Query(None, description="股票代码"),
        stock_name: str | None = Query(None, description="股票名称"),
        market: int | None = Query(None, description="市场类型"),
        exchange: int | None = Query(None, description="交易所"),
        industry_id: int | None = Query(None, description="行业ID"),
        list_status: int | None = Query(None, description="上市状态"),
        trade_status: int | None = Query(None, description="交易状态"),
        is_st: int | None = Query(None, description="是否ST股"),
        stock_type: int | None = Query(None, description="股票类型"),
        total_market_cap_start: float | None = Query(
            None, alias="total_market_cap[start]", description="总市值开始"
        ),
        total_market_cap_end: float | None = Query(
            None, alias="total_market_cap[end]", description="总市值结束"
        ),
        circulating_market_cap_start: float | None = Query(
            None, alias="circulating_market_cap[start]", description="流通市值开始"
        ),
        circulating_market_cap_end: float | None = Query(
            None, alias="circulating_market_cap[end]", description="流通市值结束"
        ),
        pe_ratio_start: float | None = Query(
            None, alias="pe_ratio[start]", description="市盈率开始"
        ),
        pe_ratio_end: float | None = Query(
            None, alias="pe_ratio[end]", description="市盈率结束"
        ),
        pb_ratio_start: float | None = Query(
            None, alias="pb_ratio[start]", description="市净率开始"
        ),
        pb_ratio_end: float | None = Query(
            None, alias="pb_ratio[end]", description="市净率结束"
        ),
        total_shares_start: float | None = Query(
            None, alias="total_shares[start]", description="总股本开始"
        ),
        total_shares_end: float | None = Query(
            None, alias="total_shares[end]", description="总股本结束"
        ),
        circulating_shares_start: float | None = Query(
            None, alias="circulating_shares[start]", description="流通股本开始"
        ),
        circulating_shares_end: float | None = Query(
            None, alias="circulating_shares[end]", description="流通股本结束"
        ),
        ipo_price_start: float | None = Query(
            None, alias="ipo_price[start]", description="发行价格开始"
        ),
        ipo_price_end: float | None = Query(
            None, alias="ipo_price[end]", description="发行价格结束"
        ),
        ipo_shares_start: float | None = Query(
            None, alias="ipo_shares[start]", description="发行数量开始"
        ),
        ipo_shares_end: float | None = Query(
            None, alias="ipo_shares[end]", description="发行数量结束"
        ),
        latest_price_start: float | None = Query(
            None, alias="latest_price[start]", description="最新价开始"
        ),
        latest_price_end: float | None = Query(
            None, alias="latest_price[end]", description="最新价结束"
        ),
        open_price_start: float | None = Query(
            None, alias="open_price[start]", description="今开开始"
        ),
        open_price_end: float | None = Query(
            None, alias="open_price[end]", description="今开结束"
        ),
        close_price_start: float | None = Query(
            None, alias="close_price[start]", description="昨收开始"
        ),
        close_price_end: float | None = Query(
            None, alias="close_price[end]", description="昨收结束"
        ),
        high_price_start: float | None = Query(
            None, alias="high_price[start]", description="最高开始"
        ),
        high_price_end: float | None = Query(
            None, alias="high_price[end]", description="最高结束"
        ),
        low_price_start: float | None = Query(
            None, alias="low_price[start]", description="最低开始"
        ),
        low_price_end: float | None = Query(
            None, alias="low_price[end]", description="最低结束"
        ),
        change_percent_start: float | None = Query(
            None, alias="change_percent[start]", description="涨跌幅开始"
        ),
        change_percent_end: float | None = Query(
            None, alias="change_percent[end]", description="涨跌幅结束"
        ),
        change_amount_start: float | None = Query(
            None, alias="change_amount[start]", description="涨跌额开始"
        ),
        change_amount_end: float | None = Query(
            None, alias="change_amount[end]", description="涨跌额结束"
        ),
        change_speed_start: float | None = Query(
            None, alias="change_speed[start]", description="涨速开始"
        ),
        change_speed_end: float | None = Query(
            None, alias="change_speed[end]", description="涨速结束"
        ),
        volume_start: float | None = Query(
            None, alias="volume[start]", description="成交量开始"
        ),
        volume_end: float | None = Query(
            None, alias="volume[end]", description="成交量结束"
        ),
        amount_start: float | None = Query(
            None, alias="amount[start]", description="成交额开始"
        ),
        amount_end: float | None = Query(
            None, alias="amount[end]", description="成交额结束"
        ),
        volume_ratio_start: float | None = Query(
            None, alias="volume_ratio[start]", description="量比开始"
        ),
        volume_ratio_end: float | None = Query(
            None, alias="volume_ratio[end]", description="量比结束"
        ),
        turnover_rate_start: float | None = Query(
            None, alias="turnover_rate[start]", description="换手率开始"
        ),
        turnover_rate_end: float | None = Query(
            None, alias="turnover_rate[end]", description="换手率结束"
        ),
        amplitude_start: float | None = Query(
            None, alias="amplitude[start]", description="振幅开始"
        ),
        amplitude_end: float | None = Query(
            None, alias="amplitude[end]", description="振幅结束"
        ),
        change_5min_start: float | None = Query(
            None, alias="change_5min[start]", description="5分钟涨跌开始"
        ),
        change_5min_end: float | None = Query(
            None, alias="change_5min[end]", description="5分钟涨跌结束"
        ),
        change_60day_start: float | None = Query(
            None, alias="change_60day[start]", description="60日涨跌幅开始"
        ),
        change_60day_end: float | None = Query(
            None, alias="change_60day[end]", description="60日涨跌幅结束"
        ),
        change_ytd_start: float | None = Query(
            None, alias="change_ytd[start]", description="年初至今涨跌幅开始"
        ),
        change_ytd_end: float | None = Query(
            None, alias="change_ytd[end]", description="年初至今涨跌幅结束"
        ),
        description: str | None = Query(None, description="股票描述"),
        website: str | None = Query(None, description="官方网站"),
        list_date_start: str | None = Query(
            None, alias="list_date[start]", description="上市日期开始"
        ),
        list_date_end: str | None = Query(
            None, alias="list_date[end]", description="上市日期结束"
        ),
        delist_date_start: str | None = Query(
            None, alias="delist_date[start]", description="退市日期开始"
        ),
        delist_date_end: str | None = Query(
            None, alias="delist_date[end]", description="退市日期结束"
        ),
        status: int | None = Query(None, description="状态"),
        sort: str | None = Query(None, description="排序规则"),
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
        获取股票列表

        支持的查询参数：
        - page: 页码，从1开始（默认1）
        - limit: 每页返回的记录数量（默认20）
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
        """
        return await self.service.index(
            {
                "page": page,
                "limit": limit,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "market": market,
                "exchange": exchange,
                "industry_id": industry_id,
                "list_status": list_status,
                "trade_status": trade_status,
                "is_st": is_st,
                "stock_type": stock_type,
                "total_market_cap_start": total_market_cap_start,
                "total_market_cap_end": total_market_cap_end,
                "circulating_market_cap_start": circulating_market_cap_start,
                "circulating_market_cap_end": circulating_market_cap_end,
                "pe_ratio_start": pe_ratio_start,
                "pe_ratio_end": pe_ratio_end,
                "pb_ratio_start": pb_ratio_start,
                "pb_ratio_end": pb_ratio_end,
                "total_shares_start": total_shares_start,
                "total_shares_end": total_shares_end,
                "circulating_shares_start": circulating_shares_start,
                "circulating_shares_end": circulating_shares_end,
                "ipo_price_start": ipo_price_start,
                "ipo_price_end": ipo_price_end,
                "ipo_shares_start": ipo_shares_start,
                "ipo_shares_end": ipo_shares_end,
                "latest_price_start": latest_price_start,
                "latest_price_end": latest_price_end,
                "open_price_start": open_price_start,
                "open_price_end": open_price_end,
                "close_price_start": close_price_start,
                "close_price_end": close_price_end,
                "high_price_start": high_price_start,
                "high_price_end": high_price_end,
                "low_price_start": low_price_start,
                "low_price_end": low_price_end,
                "change_percent_start": change_percent_start,
                "change_percent_end": change_percent_end,
                "change_amount_start": change_amount_start,
                "change_amount_end": change_amount_end,
                "change_speed_start": change_speed_start,
                "change_speed_end": change_speed_end,
                "volume_start": volume_start,
                "volume_end": volume_end,
                "amount_start": amount_start,
                "amount_end": amount_end,
                "volume_ratio_start": volume_ratio_start,
                "volume_ratio_end": volume_ratio_end,
                "turnover_rate_start": turnover_rate_start,
                "turnover_rate_end": turnover_rate_end,
                "amplitude_start": amplitude_start,
                "amplitude_end": amplitude_end,
                "change_5min_start": change_5min_start,
                "change_5min_end": change_5min_end,
                "change_60day_start": change_60day_start,
                "change_60day_end": change_60day_end,
                "change_ytd_start": change_ytd_start,
                "change_ytd_end": change_ytd_end,
                "description": description,
                "website": website,
                "list_date_start": list_date_start,
                "list_date_end": list_date_end,
                "delist_date_start": delist_date_start,
                "delist_date_end": delist_date_end,
                "status": status,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
                "concept_id": concept_id,
            }
        )

    @validate_request_data(QuantStockAddUpdateRequest)
    async def add(
        self,
        stock_code: str = Form(..., description="股票代码"),
        stock_name: str = Form(..., description="股票名称"),
        market: int = Form(..., description="市场类型"),
        exchange: int | None = Form(None, description="交易所"),
        industry_id: int | None = Form(None, description="行业ID"),
        list_status: int | None = Form(1, description="上市状态"),
        trade_status: int | None = Form(1, description="交易状态"),
        is_st: int | None = Form(0, description="是否ST股"),
        stock_type: int | None = Form(None, description="股票类型"),
        total_market_cap: float | None = Form(None, description="总市值"),
        circulating_market_cap: float | None = Form(None, description="流通市值"),
        pe_ratio: float | None = Form(None, description="市盈率"),
        pb_ratio: float | None = Form(None, description="市净率"),
        total_shares: float | None = Form(None, description="总股本"),
        circulating_shares: float | None = Form(None, description="流通股本"),
        list_date: str | None = Form(None, description="上市日期"),
        delist_date: str | None = Form(None, description="退市日期"),
        ipo_price: float | None = Form(None, description="发行价格"),
        ipo_shares: float | None = Form(None, description="发行数量"),
        description: str | None = Form(None, description="股票描述"),
        website: str | None = Form(None, description="官方网站"),
        logo_url: str | None = Form(None, description="Logo URL"),
        status: int = Form(1, description="状态"),
    ) -> JSONResponse:
        """添加股票"""
        return await self.service.add(
            {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "market": market,
                "exchange": exchange,
                "industry_id": industry_id,
                "list_status": list_status,
                "trade_status": trade_status,
                "is_st": is_st,
                "stock_type": stock_type,
                "total_market_cap": total_market_cap,
                "circulating_market_cap": circulating_market_cap,
                "pe_ratio": pe_ratio,
                "pb_ratio": pb_ratio,
                "total_shares": total_shares,
                "circulating_shares": circulating_shares,
                "list_date": list_date,
                "delist_date": delist_date,
                "ipo_price": ipo_price,
                "ipo_shares": ipo_shares,
                "description": description,
                "website": website,
                "logo_url": logo_url,
                "status": status,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="股票ID")) -> JSONResponse:
        """获取股票详情"""
        return await self.service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(QuantStockAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="股票ID"),
        stock_code: str | None = Form(None, description="股票代码"),
        stock_name: str | None = Form(None, description="股票名称"),
        market: int | None = Form(None, description="市场类型"),
        exchange: int | None = Form(None, description="交易所"),
        industry_id: int | None = Form(None, description="行业ID"),
        list_status: int | None = Form(None, description="上市状态"),
        trade_status: int | None = Form(None, description="交易状态"),
        is_st: int | None = Form(None, description="是否ST股"),
        stock_type: int | None = Form(None, description="股票类型"),
        total_market_cap: float | None = Form(None, description="总市值"),
        circulating_market_cap: float | None = Form(None, description="流通市值"),
        pe_ratio: float | None = Form(None, description="市盈率"),
        pb_ratio: float | None = Form(None, description="市净率"),
        total_shares: float | None = Form(None, description="总股本"),
        circulating_shares: float | None = Form(None, description="流通股本"),
        list_date: str | None = Form(None, description="上市日期"),
        delist_date: str | None = Form(None, description="退市日期"),
        ipo_price: float | None = Form(None, description="发行价格"),
        ipo_shares: float | None = Form(None, description="发行数量"),
        description: str | None = Form(None, description="股票描述"),
        website: str | None = Form(None, description="官方网站"),
        logo_url: str | None = Form(None, description="Logo URL"),
        status: int | None = Form(None, description="状态"),
    ) -> JSONResponse:
        """更新股票信息"""
        return await self.service.update(
            id,
            {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "market": market,
                "exchange": exchange,
                "industry_id": industry_id,
                "list_status": list_status,
                "trade_status": trade_status,
                "is_st": is_st,
                "stock_type": stock_type,
                "total_market_cap": total_market_cap,
                "circulating_market_cap": circulating_market_cap,
                "pe_ratio": pe_ratio,
                "pb_ratio": pb_ratio,
                "total_shares": total_shares,
                "circulating_shares": circulating_shares,
                "list_date": list_date,
                "delist_date": delist_date,
                "ipo_price": ipo_price,
                "ipo_shares": ipo_shares,
                "description": description,
                "website": website,
                "logo_url": logo_url,
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="股票ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """更新股票状态"""
        return await self.service.set_status(id, {"status": status})

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="股票ID"),
    ) -> JSONResponse:
        """删除股票"""
        return await self.service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """批量删除股票"""
        return await self.service.delete_all(request.id_array)

    @validate_request_data(QuantStockSyncRequest)
    async def sync_stock_list(
        self, market: int = Form(1, description="市场类型")
    ) -> JSONResponse:
        """手动同步股票列表"""
        return await self.service.sync_stock_list(market)
