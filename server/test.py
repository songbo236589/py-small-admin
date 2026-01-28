import akshare as ak

# 直接测试（不使用异步）
df = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    adjust="qfq",
    start_date="20000101",
    end_date="20250101",
)
print(f"获取到 {len(df)} 条记录")


# import akshare as ak

# df = ak.stock_individual_info_em(symbol="600519")
# info = dict(zip(df["item"], df["value"], strict=False))
# print(info["行业"])


# print(info)
# import akshare as ak

# import akshare as ak

# df = ak.stock_zh_a_hist(
#     symbol="000001",
#     period="daily",  # daily / weekly / monthly
#     start_date="20230101",
#     end_date="20240101",
#     adjust="qfq",  # 前复权（回测必用）
# )
# print(df.columns.tolist())
# print(df)


# import asyncio

# from Modules.quant.services.quant_data_fetch_service import QuantDataFetchService


# async def test_update_stock_detail():
#     """测试更新股票详细信息"""
#     service = QuantDataFetchService()

#     # 测试获取一只股票的详细信息
#     # 使用一个常见的股票代码进行测试
#     # stock_code = "AAM_U"  # 浦发银行

#     # print(f"开始测试获取股票详细信息: {stock_code}")

#     result = await service.fetch_stock_kline(
#         stock_code="000001", start_date="20230101", end_date="20240101"
#     )

#     print(f"结果: {result}")


# if __name__ == "__main__":
#     asyncio.run(test_update_stock_detail())


# from datetime import date
# from decimal import Decimal

# from Modules.common.libs.database.sharding import (
#     SyncShardedTableManager,
#     TimeBasedShardingStrategy,
# )
# from Modules.common.libs.database.sql import init_db_engine
# from Modules.quant.models.quant_stock_klines_1d import QuantStockKline1d

# # 初始化数据库引擎
# init_db_engine()

# # 创建分表管理器
# manager = SyncShardedTableManager(
#     model=QuantStockKline1d,
#     sharding_strategy=TimeBasedShardingStrategy("trade_date", granularity="year"),
# )

# # 预热表（创建未来几年的表）
# manager.warm_up_tables(["2024", "2025", "2026"])

# # 插入单条数据
# manager.insert(
#     sharding_key_value=date(2024, 1, 15),
#     data={
#         "stock_id": 123,
#         "trade_date": date(2024, 1, 15),
#         "open_price": Decimal("100.00"),
#         "high_price": Decimal("105.00"),
#         "low_price": Decimal("98.00"),
#         "close_price": Decimal("103.00"),
#         "volume": Decimal("100000000"),
#         "amount": Decimal("10300000000"),
#     },
# )

# # 批量插入数据
# manager.batch_insert(
#     [
#         {
#             "stock_id": 123,
#             "trade_date": date(2024, 1, 16),
#             "open_price": Decimal("103.00"),
#             "close_price": Decimal("105.00"),
#             "volume": Decimal("120000000"),
#             "amount": Decimal("12600000000"),
#         },
#         {
#             "stock_id": 124,
#             "trade_date": date(2024, 1, 16),
#             "open_price": Decimal("50.00"),
#             "close_price": Decimal("52.00"),
#             "volume": Decimal("80000000"),
#             "amount": Decimal("4160000000"),
#         },
#     ]
# )

# # 查询单张表的数据
# data = manager.query_single_table(
#     table_name="quant_stock_klines_1d_2024",
#     conditions={"stock_id": 123},
#     limit=100,
#     order_by="trade_date DESC",
# )

# # 跨表查询（查询多张表的数据）
# data = manager.query_multi_tables(
#     sharding_key_range=(date(2023, 1, 1), date(2024, 12, 31)),
#     conditions={"stock_id": 123},
#     limit=100,
#     order_by="trade_date DESC",
# )

# # 统计数据数量
# count = manager.count(
#     sharding_key_range=(date(2023, 1, 1), date(2024, 12, 31)),
#     conditions={"stock_id": 123},
# )

# # 更新数据
# manager.update(
#     sharding_key_value=date(2024, 1, 15),
#     pk_values={"stock_id": 123, "trade_date": date(2024, 1, 15)},
#     data={"close_price": Decimal("104.00")},
# )

# # 插入或更新数据（upsert）
# manager.upsert(
#     sharding_key_value=date(2024, 1, 15),
#     data={
#         "stock_id": 123,
#         "trade_date": date(2024, 1, 15),
#         "open_price": Decimal("100.00"),
#         "close_price": Decimal("104.00"),
#     },
# )
