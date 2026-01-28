"""
存储策略抽象基类

定义所有存储策略必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseStorage(ABC):
    """
    存储策略抽象基类

    所有具体的存储策略都必须继承此类并实现所有抽象方法
    """

    def __init__(self, config: dict[str, Any]):
        """
        初始化存储策略

        Args:
            config: 存储配置字典
        """
        self.config = config

    @abstractmethod
    async def upload(self, file_content: bytes, file_path: str) -> dict[str, Any]:
        """
        上传文件

        Args:
            file_content: 文件内容（字节数据）
            file_path: 文件存储路径（相对路径）

        Returns:
            dict: 上传结果
                {
                    "success": bool,      # 是否成功
                    "error": str | None,  # 错误信息
                    "file_size": int,     # 文件大小
                    "url": str,           # 文件访问URL
                }
        """
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 文件存储路径（相对路径）

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """
        获取文件访问URL

        Args:
            file_path: 文件存储路径（相对路径）

        Returns:
            str: 文件访问URL
        """
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            file_path: 文件存储路径（相对路径）

        Returns:
            bool: 文件是否存在
        """
        pass
