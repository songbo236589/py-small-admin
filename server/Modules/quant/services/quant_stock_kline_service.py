"""
股票K线数据业务服务 - 负责股票K线数据同步相关的业务逻辑
"""

from datetime import timedelta

from fastapi.responses import JSONResponse
from loguru import logger
from sqlmodel import select

from Modules.common.libs.database.sharding import (
    ShardingManager,
    TimeBasedShardingStrategy,
)
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import now
from Modules.common.services.base_service import BaseService
from Modules.quant.models.quant_stock import QuantStock
from Modules.quant.models.quant_stock_klines_1d import QuantStockKline1d
from Modules.quant.services.quant_data_fetch_service import QuantDataFetchService


class QuantStockKlineService(BaseService):
    """股票K线数据业务服务 - 负责股票K线数据同步相关的业务逻辑"""

    def __init__(self):
        """初始化股票K线服务"""
        super().__init__()
        self.data_fetch_service = QuantDataFetchService()

        # 初始化日K线分表管理器（按年分表）
        # 同步管理器：用于同步方法（Celery 任务）
        self.kline_sharding_manager_sync = ShardingManager(
            model=QuantStockKline1d,
            sharding_strategy=TimeBasedShardingStrategy(
                "trade_date", granularity="year"
            ),
        )

    async def sync_kline_1d(self) -> JSONResponse:
        """
        同步所有股票日K线数据（异步队列版本）

        Returns:
            JSONResponse: 同步结果统计
        """
        from Modules.quant.queues.stock_queues import sync_stock_kline_1d_queue

        try:
            async with get_async_session() as session:
                # A股：上海、深圳、北交所
                query = select(QuantStock).where(QuantStock.status == 1)
                result = await session.execute(query)
                all_stocks = result.scalars().all()
                # 过滤出A股市场
                stocks = [s for s in all_stocks if s.market in [1, 2, 3]]

                if not stocks:
                    return error("未找到股票数据")

                total_stocks = len(stocks)

                # 为每只股票提交队列任务
                for index, stock in enumerate(stocks):
                    # 设置延时，避免同时执行太多任务（每个任务间隔2秒）
                    countdown = index * 60
                    sync_stock_kline_1d_queue.apply_async(
                        args=[stock.id, stock.stock_code, stock.stock_name],
                        countdown=countdown,
                    )

                return success(
                    {
                        "total_stocks": total_stocks,
                    },
                    message=f"同步任务已提交，共 {total_stocks} 只股票，任务将在后台异步执行。",
                )

        except Exception as e:
            logger.error(f"同步日K线数据失败: {e}")
            return error(f"同步失败: {str(e)}")

    async def sync_single_kline_1d(self, stock_id: int) -> JSONResponse:
        """
        同步单个股票日K线数据

        Args:
            stock_id: 股票ID

        Returns:
            JSONResponse: 同步结果统计
        """
        try:
            # 查询股票信息
            async with get_async_session() as session:
                query = select(QuantStock).where(QuantStock.id == stock_id)
                result = await session.execute(query)
                stock = result.scalar_one_or_none()

                if not stock:
                    return error("股票不存在")

                # 验证是否为A股市场
                if stock.market not in [1, 2, 3]:
                    return error("只支持A股市场股票的同步")

                stock_code = stock.stock_code
                stock_name = stock.stock_name

                # 检查股票代码和名称是否为空
                if not stock_code or not stock_name:
                    return error("股票代码或名称为空")
            # 调用异步同步方法
            result = await self.sync_single_stock_kline_1d_async(
                stock_id, stock_code, stock_name
            )

            if result.get("success"):
                return success(
                    {
                        "stock_id": stock_id,
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "records": result.get("records", 0),
                        "processed": result.get("processed", 0),
                    },
                    message=f"同步完成，共 {result.get('records', 0)} 条记录，"
                    f"成功处理 {result.get('processed', 0)} 条。",
                )
            else:
                return error(f"同步失败: {result.get('error', '未知错误')}")

        except Exception as e:
            logger.error(f"同步股票ID {stock_id} 日K线数据失败: {e}")
            return error(f"同步失败: {str(e)}")

    async def sync_single_stock_kline_1d_async(
        self, stock_id: int, stock_code: str, stock_name: str
    ) -> dict:
        """
        同步单个股票的日K线数据（异步版本，用于直接调用）

        Args:
            stock_id: 股票ID
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            dict: 同步结果统计
        """
        try:
            # 获取当前日期
            current_date = now().strftime("%Y%m%d")

            # 计算30年前的日期
            thirty_years_ago = (now() - timedelta(days=30 * 365)).strftime("%Y%m%d")

            # 检查股票代码是否有效
            if not stock_code:
                logger.warning(f"股票 {stock_name} 的股票代码为空，跳过")
                return {
                    "success": False,
                    "stock_id": stock_id,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "error": "股票代码为空",
                    "records": 0,
                }

            thirty_years_ago_date = (now() - timedelta(days=30 * 365)).date()
            current_date_obj = now().date()

            logger.debug(
                f"[股票K线同步-查询最新记录-异步] 股票代码: {stock_code}, 股票ID: {stock_id}, 查询范围: {thirty_years_ago_date} - {current_date_obj}"
            )

            # 跨表查询最新记录（使用同步版本）
            latest_records = self.kline_sharding_manager_sync.query_multi_tables(
                sharding_key_range=(thirty_years_ago_date, current_date_obj),
                conditions={"stock_id": stock_id},
                limit=1,
                order_by="trade_date DESC",
            )

            latest_kline = latest_records[0] if latest_records else None

            logger.debug(
                f"[股票K线同步-查询结果-异步] 股票代码: {stock_code}, 查询到记录数: {len(latest_records)}, 最新记录: {latest_kline}"
            )

            if latest_kline and latest_kline.get("trade_date"):
                # 已有数据，获取增量数据
                latest_date = latest_kline["trade_date"]
                # 计算最新日期+1天
                next_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")

                # 检查是否需要获取增量数据
                if next_date > current_date:
                    # 最新日期已经是今天或未来，数据已是最新
                    logger.info(
                        f"股票 {stock_code} 数据已是最新，最新日期: {latest_date}，无需同步"
                    )
                    return {
                        "success": True,
                        "stock_id": stock_id,
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "records": 0,
                        "processed": 0,
                    }

                start_date = next_date
                end_date = current_date
                logger.info(
                    f"股票 {stock_code} 已有数据，最新日期: {latest_date}，"
                    f"获取增量数据: {start_date} - {end_date}"
                )
            else:
                # 没有数据，获取30年历史数据
                start_date = thirty_years_ago
                end_date = current_date
                logger.info(
                    f"股票 {stock_code} 无数据，获取历史数据: {start_date} - {end_date}"
                )

            # 调用AkShare获取日K线数据（异步版本）
            logger.debug(
                f"[股票K线同步-获取数据-异步] 股票代码: {stock_code}, 开始日期: {start_date}, 结束日期: {end_date}"
            )
            df = self.data_fetch_service.fetch_stock_kline(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                period="daily",
                adjust="qfq",
            )

            if df.empty:
                logger.warning(
                    f"[股票K线同步-获取数据失败-异步] 股票代码: {stock_code}, 未获取到数据"
                )
                return {
                    "success": False,
                    "stock_id": stock_id,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "error": "未获取到数据",
                    "records": 0,
                }

            logger.debug(
                f"[股票K线同步-获取数据成功-异步] 股票代码: {stock_code}, 获取到记录数: {len(df)}"
            )

            # 收集所有数据用于批量插入
            data_list = []
            for _, row in df.iterrows():
                data_list.append(
                    {
                        "stock_id": stock_id,
                        "trade_date": row["日期"],
                        "open_price": row.get("开盘"),
                        "high_price": row.get("最高"),
                        "low_price": row.get("最低"),
                        "close_price": row.get("收盘"),
                        "volume": row.get("成交量"),
                        "amount": row.get("成交额"),
                        "turnover_rate": row.get("换手率"),
                        "change_percent": row.get("涨跌幅"),
                        "amplitude": row.get("振幅"),
                        "change_amount": row.get("涨跌额"),
                        "status": 1,
                    }
                )

            logger.debug(
                f"[股票K线同步-批量插入-异步] 股票代码: {stock_code}, 准备插入记录数: {len(data_list)}"
            )

            # 批量插入数据（使用ON DUPLICATE KEY UPDATE自动处理重复）
            success_count = self.kline_sharding_manager_sync.batch_insert(
                data_list, on_duplicate="UPDATE"
            )

            logger.info(
                f"[股票K线同步-完成-异步] 股票代码: {stock_code}, "
                f"共 {len(df)} 条记录，"
                f"成功处理 {success_count} 条"
            )

            return {
                "success": True,
                "stock_id": stock_id,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "records": len(df),
                "processed": success_count,
            }

        except Exception as e:
            logger.error(f"股票 {stock_code} 同步失败: {e}")
            raise

    def sync_single_stock_kline_1d_sync(
        self, stock_id: int, stock_code: str, stock_name: str
    ) -> dict:
        """
        同步单个股票的日K线数据（同步版本，用于 Celery 任务）

        Args:
            stock_id: 股票ID
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            dict: 同步结果统计
        """

        try:
            # 获取当前日期
            current_date = now().strftime("%Y%m%d")

            # 计算30年前的日期
            thirty_years_ago = (now() - timedelta(days=30 * 365)).strftime("%Y%m%d")

            # 检查股票代码是否有效
            if not stock_code:
                logger.warning(f"股票 {stock_name} 的股票代码为空，跳过")
                return {
                    "success": False,
                    "stock_id": stock_id,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "error": "股票代码为空",
                    "records": 0,
                }

            thirty_years_ago_date = (now() - timedelta(days=30 * 365)).date()
            current_date_obj = now().date()

            logger.debug(
                f"[股票K线同步-查询最新记录-异步] 股票代码: {stock_code}, 股票ID: {stock_id}, 查询范围: {thirty_years_ago_date} - {current_date_obj}"
            )

            # 跨表查询最新记录（使用同步版本）
            latest_records = self.kline_sharding_manager_sync.query_multi_tables(
                sharding_key_range=(thirty_years_ago_date, current_date_obj),
                conditions={"stock_id": stock_id},
                limit=1,
                order_by="trade_date DESC",
            )

            latest_kline = latest_records[0] if latest_records else None

            logger.debug(
                f"[股票K线同步-查询结果-异步] 股票代码: {stock_code}, 查询到记录数: {len(latest_records)}, 最新记录: {latest_kline}"
            )

            if latest_kline and latest_kline.get("trade_date"):
                # 已有数据，获取增量数据
                latest_date = latest_kline["trade_date"]
                # 计算最新日期+1天
                next_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")

                # 检查是否需要获取增量数据
                if next_date > current_date:
                    # 最新日期已经是今天或未来，数据已是最新
                    logger.info(
                        f"股票 {stock_code} 数据已是最新，最新日期: {latest_date}，无需同步"
                    )
                    return {
                        "success": True,
                        "stock_id": stock_id,
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "records": 0,
                        "processed": 0,
                    }

                start_date = next_date
                end_date = current_date
                logger.info(
                    f"股票 {stock_code} 已有数据，最新日期: {latest_date}，"
                    f"获取增量数据: {start_date} - {end_date}"
                )
            else:
                # 没有数据，获取30年历史数据
                start_date = thirty_years_ago
                end_date = current_date
                logger.info(
                    f"股票 {stock_code} 无数据，获取历史数据: {start_date} - {end_date}"
                )

            # 调用AkShare获取日K线数据
            logger.debug(
                f"[股票K线同步-获取数据-同步] 股票代码: {stock_code}, 开始日期: {start_date}, 结束日期: {end_date}"
            )
            df = self.data_fetch_service.fetch_stock_kline(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                period="daily",
                adjust="qfq",
            )

            if df.empty:
                logger.warning(
                    f"[股票K线同步-获取数据失败-同步] 股票代码: {stock_code}, 未获取到数据"
                )
                return {
                    "success": False,
                    "stock_id": stock_id,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "error": "未获取到数据",
                    "records": 0,
                }

            logger.debug(
                f"[股票K线同步-获取数据成功-同步] 股票代码: {stock_code}, 获取到记录数: {len(df)}"
            )

            # 收集所有数据用于批量插入
            data_list = []
            for _, row in df.iterrows():
                data_list.append(
                    {
                        "stock_id": stock_id,
                        "trade_date": row["日期"],
                        "open_price": row.get("开盘"),
                        "high_price": row.get("最高"),
                        "low_price": row.get("最低"),
                        "close_price": row.get("收盘"),
                        "volume": row.get("成交量"),
                        "amount": row.get("成交额"),
                        "turnover_rate": row.get("换手率"),
                        "change_percent": row.get("涨跌幅"),
                        "amplitude": row.get("振幅"),
                        "change_amount": row.get("涨跌额"),
                        "status": 1,
                    }
                )

            logger.debug(
                f"[股票K线同步-批量插入-同步] 股票代码: {stock_code}, 准备插入记录数: {len(data_list)}"
            )

            # 批量插入数据（使用ON DUPLICATE KEY UPDATE自动处理重复）
            success_count = self.kline_sharding_manager_sync.batch_insert(
                data_list, on_duplicate="UPDATE"
            )

            logger.info(
                f"[股票K线同步-完成-同步] 股票代码: {stock_code}, "
                f"共 {len(df)} 条记录，"
                f"成功处理 {success_count} 条"
            )

            return {
                "success": True,
                "stock_id": stock_id,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "records": len(df),
                "processed": success_count,
            }

        except Exception as e:
            logger.error(f"股票 {stock_code} 同步失败: {e}")
            raise
