"""
基于ID的分表策略

支持按ID范围或ID取模进行分表。
"""

from typing import Any

from .base import ShardingStrategy


class IdBasedShardingStrategy(ShardingStrategy):
    """
    基于ID的分表策略

    支持按ID范围或ID取模进行分表，适用于用户数据、订单数据等。
    """

    # 分表方式
    MODE_RANGE = "range"  # 按范围分表
    MODE_MOD = "mod"  # 按取模分表

    def __init__(
        self,
        sharding_key: str,
        mode: str = "mod",
        mod_value: int | None = None,
        range_size: int | None = None,
    ):
        """
        初始化基于ID的分表策略

        Args:
            sharding_key: 分表键字段名（通常是ID字段，如 "user_id", "order_id"）
            mode: 分表方式（"range" 或 "mod"）
            mod_value: 取模值（mode="mod"时使用）
            range_size: 范围大小（mode="range"时使用）

        Raises:
            ValueError: 当参数不合法时
        """
        super().__init__(sharding_key)

        if mode not in [self.MODE_RANGE, self.MODE_MOD]:
            raise ValueError(f"不支持的分表方式: {mode}，支持的方式: range, mod")

        self.mode = mode

        if mode == self.MODE_MOD:
            if mod_value is None or mod_value <= 0:
                raise ValueError("mode='mod' 时必须指定 mod_value 且大于0")
            self.mod_value = mod_value
            self.range_size = None
        else:  # range
            if range_size is None or range_size <= 0:
                raise ValueError("mode='range' 时必须指定 range_size 且大于0")
            self.range_size = range_size
            self.mod_value = None

    def get_table_name(self, sharding_key_value: Any, table_prefix: str) -> str:
        """
        根据ID值获取表名

        Args:
            sharding_key_value: ID值（整数或可转换为整数的值）
            table_prefix: 表名前缀

        Returns:
            str: 完整的表名

        Examples:
            >>> strategy = IdBasedShardingStrategy("user_id", mode="mod", mod_value=10)
            >>> strategy.get_table_name(123, "users_")
            'users_3'

            >>> strategy = IdBasedShardingStrategy("user_id", mode="range", range_size=1000)
            >>> strategy.get_table_name(12345, "users_")
            'users_12'
        """
        # 转换为整数
        id_value = self._to_int(sharding_key_value)

        # 根据模式生成表名后缀
        if self.mode == self.MODE_MOD:
            assert self.mod_value is not None
            suffix = str(id_value % self.mod_value)
        else:  # range
            assert self.range_size is not None
            suffix = str(id_value // self.range_size)

        return f"{table_prefix}{suffix}"

    def get_table_names_by_range(
        self,
        start_value: Any,
        end_value: Any,
        table_prefix: str,
    ) -> list[str]:
        """
        根据ID范围获取涉及的表名列表

        Args:
            start_value: 起始ID
            end_value: 结束ID
            table_prefix: 表名前缀

        Returns:
            list[str]: 表名列表

        Examples:
            >>> strategy = IdBasedShardingStrategy("user_id", mode="mod", mod_value=10)
            >>> strategy.get_table_names_by_range(15, 35, "users_")
            ['users_0', 'users_1', 'users_2', 'users_3', 'users_4', 'users_5']

            >>> strategy = IdBasedShardingStrategy("user_id", mode="range", range_size=1000)
            >>> strategy.get_table_names_by_range(1500, 3500, "users_")
            ['users_1', 'users_2', 'users_3']
        """
        # 转换为整数
        start_id = self._to_int(start_value)
        end_id = self._to_int(end_value)

        # 确保start_id <= end_id
        if start_id > end_id:
            start_id, end_id = end_id, start_id

        # 收集所有涉及的表名
        table_names = set()

        if self.mode == self.MODE_MOD:
            # 取模模式：遍历所有可能的余数
            assert self.mod_value is not None
            for i in range(self.mod_value):
                # 检查这个余数对应的ID范围是否与查询范围有交集
                # 余数为i的ID范围：[i, i + mod_value, i + 2*mod_value, ...]
                # 找到第一个 >= start_id 且余数为i的ID
                first_id = start_id
                if first_id % self.mod_value != i:
                    first_id = (
                        start_id + (i - start_id % self.mod_value) % self.mod_value
                    )

                # 如果第一个ID <= end_id，则说明有交集
                if first_id <= end_id:
                    table_name = f"{table_prefix}{i}"
                    table_names.add(table_name)

        else:  # range
            # 范围模式：计算涉及的range数量
            assert self.range_size is not None
            start_range = start_id // self.range_size
            end_range = end_id // self.range_size

            for i in range(start_range, end_range + 1):
                table_name = f"{table_prefix}{i}"
                table_names.add(table_name)

        # 按表名排序（按数字排序）
        return sorted(table_names, key=lambda x: int(x.replace(table_prefix, "")))

    def _to_int(self, value: Any) -> int:
        """
        将值转换为整数

        Args:
            value: 值（整数或可转换为整数的值）

        Returns:
            int: 整数

        Raises:
            ValueError: 当无法转换为整数时
        """
        if isinstance(value, int):
            return value

        if isinstance(value, str):
            try:
                return int(value)
            except ValueError as err:
                raise ValueError(f"无法将字符串转换为整数: {value}") from err

        try:
            return int(value)
        except (ValueError, TypeError) as err:
            raise ValueError(f"无法将 {type(value)} 转换为整数") from err

    def validate_sharding_key_value(self, value: Any) -> bool:
        """
        验证分表键值是否为有效的ID

        Args:
            value: 分表键的值

        Returns:
            bool: 是否有效
        """
        try:
            self._to_int(value)
            return True
        except (ValueError, TypeError):
            return False
