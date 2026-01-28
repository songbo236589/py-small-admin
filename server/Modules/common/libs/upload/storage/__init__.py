"""
存储策略模块 - 支持多种存储后端

支持的存储类型：
- local: 本地存储
- aliyun_oss: 阿里云OSS
- tencent_oss: 腾讯云COS
- qiniu_oss: 七牛云Kodo
"""

from .base_storage import BaseStorage
from .storage_factory import StorageFactory

__all__ = ["BaseStorage", "StorageFactory"]
