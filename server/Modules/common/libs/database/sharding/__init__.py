"""
通用分表管理模块

提供基于ORM模型的通用分表功能,支持多种分表策略。
"""

from .cache_utils import ShardingCacheManager
from .manager import ShardingManager
from .strategies.base import ShardingStrategy
from .strategies.hash_based import HashBasedShardingStrategy
from .strategies.id_based import IdBasedShardingStrategy
from .strategies.time_based import TimeBasedShardingStrategy
from .table_creator import ShardingTableCreator

__all__ = [
    # 管理器
    "ShardingManager",
    "ShardingTableCreator",
    # 分表策略
    "ShardingStrategy",
    "TimeBasedShardingStrategy",
    "IdBasedShardingStrategy",
    "HashBasedShardingStrategy",
    # 缓存工具
    "ShardingCacheManager",
]
