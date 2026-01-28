"""
存储策略工厂

根据存储类型创建对应的存储策略实例
"""

from typing import Any

from .aliyun_oss_storage import AliyunOSSStorage
from .base_storage import BaseStorage
from .local_storage import LocalStorage
from .qiniu_kodo_storage import QiniuKodoStrategy
from .tencent_cos_storage import TencentCOSStrategy


class StorageFactory:
    """
    存储策略工厂

    根据存储类型动态创建对应的存储策略实例
    """

    # 存储类型映射表
    _strategies = {
        "local": LocalStorage,
        "aliyun_oss": AliyunOSSStorage,
        "tencent_oss": TencentCOSStrategy,
        "qiniu_oss": QiniuKodoStrategy,
    }

    @classmethod
    def create_storage(cls, storage_type: str, config: dict[str, Any]) -> BaseStorage:
        """
        根据存储类型创建对应的存储实例

        Args:
            storage_type: 存储类型（local/aliyun_oss/tencent_oss/qiniu_oss）
            config: 存储配置字典

        Returns:
            BaseStorage: 存储策略实例

        Raises:
            ValueError: 当存储类型不支持时抛出异常
        """
        strategy_class = cls._strategies.get(storage_type)

        if not strategy_class:
            supported_types = ", ".join(cls._strategies.keys())
            raise ValueError(
                f"不支持的存储类型: {storage_type}，支持的类型: {supported_types}"
            )

        return strategy_class(config)

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """
        获取所有支持的存储类型

        Returns:
            list: 支持的存储类型列表
        """
        return list(cls._strategies.keys())

    @classmethod
    def is_supported(cls, storage_type: str) -> bool:
        """
        检查存储类型是否支持

        Args:
            storage_type: 存储类型

        Returns:
            bool: 是否支持
        """
        return storage_type in cls._strategies
