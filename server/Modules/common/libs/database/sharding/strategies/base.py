"""
分表策略抽象基类

定义分表策略的接口，所有分表策略都需要实现此接口。
"""

from abc import ABC, abstractmethod
from typing import Any


class ShardingStrategy(ABC):
    """
    分表策略抽象基类

    所有分表策略都需要继承此类并实现核心方法。
    """

    def __init__(self, sharding_key: str):
        """
        初始化分表策略

        Args:
            sharding_key: 分表键字段名（如 "trade_date", "user_id"）
        """
        self.sharding_key = sharding_key

    @abstractmethod
    def get_table_name(self, sharding_key_value: Any, table_prefix: str) -> str:
        """
        根据分表键值获取表名

        Args:
            sharding_key_value: 分表键的值
            table_prefix: 表名前缀

        Returns:
            str: 完整的表名

        Examples:
            >>> strategy = TimeBasedShardingStrategy("trade_date", granularity="year")
            >>> strategy.get_table_name(date(2024, 1, 15), "quant_stock_klines_1d_")
            'quant_stock_klines_1d_2024'
        """
        pass

    @abstractmethod
    def get_table_names_by_range(
        self,
        start_value: Any,
        end_value: Any,
        table_prefix: str,
    ) -> list[str]:
        """
        根据分表键范围获取涉及的表名列表

        Args:
            start_value: 起始值
            end_value: 结束值
            table_prefix: 表名前缀

        Returns:
            list[str]: 表名列表

        Examples:
            >>> strategy = TimeBasedShardingStrategy("trade_date", granularity="year")
            >>> strategy.get_table_names_by_range(
            ...     date(2023, 1, 1),
            ...     date(2024, 12, 31),
            ...     "quant_stock_klines_1d_"
            ... )
            ['quant_stock_klines_1d_2023', 'quant_stock_klines_1d_2024']
        """
        pass

    def extract_sharding_key_value(self, data: dict[str, Any]) -> Any:
        """
        从数据字典中提取分表键的值

        Args:
            data: 数据字典

        Returns:
            Any: 分表键的值

        Raises:
            ValueError: 当分表键不存在时
        """
        if self.sharding_key not in data:
            raise ValueError(f"分表键 '{self.sharding_key}' 不存在于数据中")

        return data[self.sharding_key]

    def validate_sharding_key_value(self, value: Any) -> bool:
        """
        验证分表键值是否有效

        Args:
            value: 分表键的值

        Returns:
            bool: 是否有效

        默认实现：只要值不为None就认为有效
        子类可以重写此方法以实现更严格的验证
        """
        return value is not None
