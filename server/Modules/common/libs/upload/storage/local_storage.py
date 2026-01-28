"""
本地存储策略

将文件存储到本地文件系统
"""

from pathlib import Path
from typing import Any

from .base_storage import BaseStorage


class LocalStorage(BaseStorage):
    """
    本地存储策略

    将文件存储到本地文件系统，适用于开发环境和小规模应用
    """

    def __init__(self, config: dict[str, Any]):
        """
        初始化本地存储策略

        Args:
            config: 存储配置字典，必须包含:
                - dir: 上传根目录
                - url_prefix: URL访问前缀
        """
        super().__init__(config)
        self.upload_dir = Path(config.get("dir", "./uploads"))
        self.url_prefix = config.get("url_prefix", "/uploads").lstrip("/")

    async def upload(self, file_content: bytes, file_path: str) -> dict[str, Any]:
        """
        上传文件到本地文件系统

        Args:
            file_content: 文件内容（字节数据）
            file_path: 文件存储路径（相对路径）

        Returns:
            dict: 上传结果
        """
        try:
            # 构建完整路径
            full_path = self.upload_dir / file_path

            # 确保目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            with open(full_path, "wb") as f:
                f.write(file_content)

            # 返回成功结果
            return {
                "success": True,
                "error": None,
                "file_size": len(file_content),
                "url": f"/{self.url_prefix}/{file_path}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"本地存储上传失败: {str(e)}",
                "file_size": 0,
                "url": "",
            }

    async def delete(self, file_path: str) -> bool:
        """
        删除本地文件

        Args:
            file_path: 文件存储路径（相对路径）

        Returns:
            bool: 是否删除成功
        """
        try:
            full_path = self.upload_dir / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_url(self, file_path: str) -> str:
        """
        获取本地文件访问URL

        Args:
            file_path: 文件存储路径（相对路径）

        Returns:
            str: 文件访问URL
        """
        return f"/{self.url_prefix}/{file_path}"

    def exists(self, file_path: str) -> bool:
        """
        检查本地文件是否存在

        Args:
            file_path: 文件存储路径（相对路径）

        Returns:
            bool: 文件是否存在
        """
        full_path = self.upload_dir / file_path
        return full_path.exists()
