"""
基于哈希的分表策略

支持按字段哈希值进行分表。
"""

import hashlib
from typing import Any

from .base import ShardingStrategy


class HashBasedShardingStrategy(ShardingStrategy):
    """
    基于哈希的分表策略

    支持按字段哈希值进行分表，适用于需要均匀分布数据的场景。
    """

    def __init__(
        self, sharding_key: str, bucket_count: int = 10, hash_algorithm: str = "md5"
    ):
        """
        初始化基于哈希的分表策略

        Args:
            sharding_key: 分表键字段名（如 "username", "email"）
            bucket_count: 分桶数量（分表数量）
            hash_algorithm: 哈希算法（"md5", "sha1", "sha256"）

        Raises:
            ValueError: 当参数不合法时
        """
        super().__init__(sharding_key)

        if bucket_count <= 0:
            raise ValueError("bucket_count 必须大于0")

        if hash_algorithm not in ["md5", "sha1", "sha256"]:
            raise ValueError(
                f"不支持的哈希算法: {hash_algorithm}，支持的算法: md5, sha1, sha256"
            )

        self.bucket_count = bucket_count
        self.hash_algorithm = hash_algorithm

    def get_table_name(self, sharding_key_value: Any, table_prefix: str) -> str:
        """
        根据分表键值获取表名

        Args:
            sharding_key_value: 分表键的值（任何可哈希的值）
            table_prefix: 表名前缀

        Returns:
            str: 完整的表名

        Examples:
            >>> strategy = HashBasedShardingStrategy("username", bucket_count=10)
            >>> strategy.get_table_name("user123", "users_")
            'users_5'
        """
        # 计算哈希值
        hash_value = self._calculate_hash(sharding_key_value)

        # 计算桶号
        bucket_index = hash_value % self.bucket_count

        return f"{table_prefix}{bucket_index}"

    def get_table_names_by_range(
        self,
        start_value: Any,
        end_value: Any,
        table_prefix: str,
    ) -> list[str]:
        """
        根据分表键范围获取涉及的表名列表

        注意：对于哈希分表，无法精确判断范围涉及哪些表，
        因此返回所有可能的表。

        Args:
            start_value: 起始值（此参数在哈希分表中不使用）
            end_value: 结束值（此参数在哈希分表中不使用）
            table_prefix: 表名前缀

        Returns:
            list[str]: 所有表名列表

        Examples:
            >>> strategy = HashBasedShardingStrategy("username", bucket_count=10)
            >>> strategy.get_table_names_by_range("a", "z", "users_")
            ['users_0', 'users_1', 'users_2', 'users_3', 'users_4',
             'users_5', 'users_6', 'users_7', 'users_8', 'users_9']
        """
        # 哈希分表无法根据范围判断，返回所有表
        return [f"{table_prefix}{i}" for i in range(self.bucket_count)]

    def _calculate_hash(self, value: Any) -> int:
        """
        计算值的哈希值

        Args:
            value: 值（任何可转换为字符串的值）

        Returns:
            int: 哈希值（整数）

        Raises:
            ValueError: 当无法计算哈希时
        """
        # 转换为字符串
        value_str = str(value)

        # 计算哈希
        if self.hash_algorithm == "md5":
            hash_obj = hashlib.md5(value_str.encode("utf-8"))
        elif self.hash_algorithm == "sha1":
            hash_obj = hashlib.sha1(value_str.encode("utf-8"))
        else:  # sha256
            hash_obj = hashlib.sha256(value_str.encode("utf-8"))

        # 转换为整数
        hash_hex = hash_obj.hexdigest()
        hash_int = int(hash_hex, 16)

        return hash_int

    def validate_sharding_key_value(self, value: Any) -> bool:
        """
        验证分表键值是否有效

        Args:
            value: 分表键的值

        Returns:
            bool: 是否有效

        默认实现：只要值不为None就认为有效
        """
        return value is not None
