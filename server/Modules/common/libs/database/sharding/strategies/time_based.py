"""
基于时间的分表策略

支持按年、月、日进行分表。
"""

from datetime import date, datetime, timedelta
from typing import Any

from .base import ShardingStrategy


class TimeBasedShardingStrategy(ShardingStrategy):
    """
    基于时间的分表策略

    支持按年、月、日进行分表，适用于时间序列数据。
    """

    # 支持的时间粒度
    GRANULARITY_YEAR = "year"
    GRANULARITY_MONTH = "month"
    GRANULARITY_DAY = "day"

    def __init__(self, sharding_key: str, granularity: str = "year"):
        """
        初始化基于时间的分表策略

        Args:
            sharding_key: 分表键字段名（通常是日期字段，如 "trade_date", "created_at"）
            granularity: 时间粒度（"year", "month", "day"）

        Raises:
            ValueError: 当granularity不支持时
        """
        super().__init__(sharding_key)

        if granularity not in [
            self.GRANULARITY_YEAR,
            self.GRANULARITY_MONTH,
            self.GRANULARITY_DAY,
        ]:
            raise ValueError(
                f"不支持的时间粒度: {granularity}，支持的粒度: year, month, day"
            )

        self.granularity = granularity

    def get_table_name(self, sharding_key_value: Any, table_prefix: str) -> str:
        """
        根据时间值获取表名

        Args:
            sharding_key_value: 时间值（date或datetime对象，或日期字符串）
            table_prefix: 表名前缀

        Returns:
            str: 完整的表名

        Examples:
            >>> strategy = TimeBasedShardingStrategy("trade_date", granularity="year")
            >>> strategy.get_table_name(date(2024, 1, 15), "quant_stock_klines_1d_")
            'quant_stock_klines_1d_2024'

            >>> strategy = TimeBasedShardingStrategy("trade_date", granularity="month")
            >>> strategy.get_table_name(date(2024, 1, 15), "quant_stock_klines_1d_")
            'quant_stock_klines_1d_202401'

            >>> strategy = TimeBasedShardingStrategy("trade_date", granularity="day")
            >>> strategy.get_table_name(date(2024, 1, 15), "quant_stock_klines_1d_")
            'quant_stock_klines_1d_20240115'
        """
        # 转换为date对象
        dt = self._to_date(sharding_key_value)

        # 根据粒度生成表名后缀
        if self.granularity == self.GRANULARITY_YEAR:
            suffix = dt.strftime("%Y")
        elif self.granularity == self.GRANULARITY_MONTH:
            suffix = dt.strftime("%Y%m")
        else:  # day
            suffix = dt.strftime("%Y%m%d")

        return f"{table_prefix}{suffix}"

    def get_table_names_by_range(
        self,
        start_value: Any,
        end_value: Any,
        table_prefix: str,
    ) -> list[str]:
        """
        根据时间范围获取涉及的表名列表

        Args:
            start_value: 起始时间
            end_value: 结束时间
            table_prefix: 表名前缀

        Returns:
            list[str]: 表名列表（按时间顺序）

        Examples:
            >>> strategy = TimeBasedShardingStrategy("trade_date", granularity="year")
            >>> strategy.get_table_names_by_range(
            ...     date(2023, 6, 1),
            ...     date(2024, 12, 31),
            ...     "quant_stock_klines_1d_"
            ... )
            ['quant_stock_klines_1d_2023', 'quant_stock_klines_1d_2024']

            >>> strategy = TimeBasedShardingStrategy("trade_date", granularity="month")
            >>> strategy.get_table_names_by_range(
            ...     date(2023, 12, 15),
            ...     date(2024, 2, 15),
            ...     "quant_stock_klines_1d_"
            ... )
            ['quant_stock_klines_1d_202312', 'quant_stock_klines_1d_202401', 'quant_stock_klines_1d_202402']
        """
        # 转换为date对象
        start_dt = self._to_date(start_value)
        end_dt = self._to_date(end_value)

        # 确保start_dt <= end_dt
        if start_dt > end_dt:
            start_dt, end_dt = end_dt, start_dt

        # 收集所有涉及的表名
        table_names = set()
        current_dt = start_dt

        if self.granularity == self.GRANULARITY_YEAR:
            # 按年遍历
            while current_dt.year <= end_dt.year:
                table_name = f"{table_prefix}{current_dt.strftime('%Y')}"
                table_names.add(table_name)
                current_dt = date(current_dt.year + 1, 1, 1)

        elif self.granularity == self.GRANULARITY_MONTH:
            # 按月遍历
            while (current_dt.year, current_dt.month) <= (
                end_dt.year,
                end_dt.month,
            ):
                table_name = f"{table_prefix}{current_dt.strftime('%Y%m')}"
                table_names.add(table_name)

                # 下个月
                if current_dt.month == 12:
                    current_dt = date(current_dt.year + 1, 1, 1)
                else:
                    current_dt = date(current_dt.year, current_dt.month + 1, 1)

        else:  # day
            # 按日遍历
            while current_dt <= end_dt:
                table_name = f"{table_prefix}{current_dt.strftime('%Y%m%d')}"
                table_names.add(table_name)
                current_dt += timedelta(days=1)

        # 按表名排序
        return sorted(table_names)

    def _to_date(self, value: Any) -> date:
        """
        将值转换为date对象

        Args:
            value: 值（date、datetime或字符串）

        Returns:
            date: date对象

        Raises:
            ValueError: 当无法转换为date时
        """
        if isinstance(value, date):
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, str):
            try:
                # 尝试解析ISO格式日期
                return date.fromisoformat(value)
            except ValueError:
                # 尝试其他格式
                try:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError as err:
                    raise ValueError(f"无法解析日期字符串: {value}") from err

        raise ValueError(f"无法将 {type(value)} 转换为date对象")

    def validate_sharding_key_value(self, value: Any) -> bool:
        """
        验证分表键值是否为有效的时间

        Args:
            value: 分表键的值

        Returns:
            bool: 是否有效
        """
        try:
            self._to_date(value)
            return True
        except (ValueError, TypeError):
            return False
