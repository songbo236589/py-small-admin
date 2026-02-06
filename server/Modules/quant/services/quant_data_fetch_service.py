"""
量化数据获取服务 - 负责从 AkShare 获取金融数据
"""

import asyncio

import akshare as ak
import pandas as pd
from loguru import logger


class QuantDataFetchService:
    """量化数据获取服务 - 负责从 AkShare 获取金融数据"""

    # ==================== 股票数据获取 ====================

    async def fetch_a_stock_list(self) -> pd.DataFrame:
        """
        获取A股股票实时行情列表

        Returns:
            pd.DataFrame: 股票实时行情数据，包含代码、名称、价格、市值等字段
        """
        try:
            logger.info("开始获取A股股票实时行情列表")
            # df = await asyncio.to_thread(ak.stock_zh_a_spot_em)
            df = await asyncio.to_thread(ak.stock_zh_a_spot)

            logger.info(f"成功获取A股股票实时行情列表，共 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"获取A股股票实时行情列表失败: {e}")
            raise

    async def fetch_hk_stock_list(self) -> pd.DataFrame:
        """
        获取港股股票列表

        Returns:
            pd.DataFrame: 港股列表数据
        """
        try:
            logger.info("开始获取港股股票列表")
            df = await asyncio.to_thread(ak.stock_hk_spot_em)
            logger.info(f"成功获取港股股票列表，共 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"获取港股股票列表失败: {e}")
            raise

    async def fetch_us_stock_list(self) -> pd.DataFrame:
        """
        获取美股股票列表

        Returns:
            pd.DataFrame: 美股列表数据
        """
        try:
            logger.info("开始获取美股股票列表")
            df = await asyncio.to_thread(ak.stock_us_spot_em)
            logger.info(f"成功获取美股股票列表，共 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"获取美股股票列表失败: {e}")
            raise

    # ==================== 概念数据获取 ====================

    async def fetch_concept_list(self) -> pd.DataFrame:
        """
        获取概念板块列表

        Returns:
            pd.DataFrame: 概念列表数据，包含概念代码、概念名称等字段
        """
        try:
            logger.info("开始获取概念板块列表")
            df = await asyncio.to_thread(ak.stock_board_concept_name_em)
            logger.info(f"成功获取概念板块列表，共 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"获取概念板块列表失败: {e}")
            raise

    async def fetch_concept_stocks(self, concept_code: str | None) -> list[str]:
        """
        获取概念成分股

        Args:
            concept_code: 概念代码

        Returns:
            list[str]: 股票代码列表
        """
        if concept_code is None:
            logger.warning(f"无效的概念成分股: {concept_code}")
            return []
        try:
            logger.info(f"开始获取概念成分股: {concept_code}")
            df = await asyncio.to_thread(
                ak.stock_board_concept_cons_em, symbol=concept_code
            )

            if df.empty:
                logger.warning(f"未找到概念成分股: {concept_code}")
                return []

            # 提取股票代码列表
            stock_codes = df["代码"].tolist()
            logger.info(
                f"成功获取概念成分股: {concept_code}, 共 {len(stock_codes)} 只股票"
            )
            return stock_codes
        except Exception as e:
            logger.error(f"获取概念成分股失败: {concept_code}, 错误: {e}")
            return []

    # ==================== 行业数据获取 ====================

    async def fetch_industry_list(self) -> pd.DataFrame:
        """
        获取行业板块列表

        Returns:
            pd.DataFrame: 行业列表数据，包含行业代码、行业名称等字段
        """
        try:
            logger.info("开始获取行业板块列表")
            df = await asyncio.to_thread(ak.stock_board_industry_name_em)
            logger.info(f"成功获取行业板块列表，共 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"获取行业板块列表失败: {e}")
            raise

    async def fetch_industry_stocks(self, industry_code: str | None) -> list[str]:
        """
        获取行业成分股

        Args:
            industry_code: 行业代码

        Returns:
            list[str]: 股票代码列表
        """
        if industry_code is None:
            logger.warning(f"无效的行业成分股: {industry_code}")
            return []
        try:
            logger.info(f"开始获取行业成分股: {industry_code}")
            df = await asyncio.to_thread(
                ak.stock_board_industry_cons_em, symbol=industry_code
            )

            if df.empty:
                logger.warning(f"未找到行业成分股: {industry_code}")
                return []

            # 提取股票代码列表
            stock_codes = df["代码"].tolist()
            logger.info(
                f"成功获取行业成分股: {industry_code}, 共 {len(stock_codes)} 只股票"
            )
            return stock_codes
        except Exception as e:
            logger.error(f"获取行业成分股失败: {industry_code}, 错误: {e}")
            return []

    # ==================== K线数据获取 ====================

    def fetch_stock_kline(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        """
        获取股票K线数据（支持日K、周K、月K）

        Args:
            stock_code: 股票代码（如：000001）
            start_date: 开始日期（格式：YYYYMMDD）
            end_date: 结束日期（格式：YYYYMMDD）
            period: K线周期（daily=日K、weekly=周K、monthly=月K）
            adjust: 复权方式（qfq=前复权、hfq=后复权、空字符串=不复权）

        Returns:
            pd.DataFrame: K线数据
        """
        try:
            logger.info(
                f"开始获取股票K线数据: {stock_code}, "
                f"start_date={start_date}, end_date={end_date}, period={period}, adjust={adjust}"
            )

            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                adjust=adjust,
                start_date=start_date,
                end_date=end_date,
            )

            logger.info(f"成功获取股票K线数据: {stock_code}, 共 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"获取股票K线数据失败: {stock_code}, 错误: {e}")
            raise
