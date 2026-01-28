"""
七牛云Kodo存储策略

将文件存储到七牛云对象存储Kodo
"""

from typing import Any

from qiniu import Auth, BucketManager, put_data

from .base_storage import BaseStorage


class QiniuKodoStrategy(BaseStorage):
    """
    七牛云Kodo存储策略

    将文件存储到七牛云对象存储Kodo，适用于生产环境
    """

    def __init__(self, config: dict[str, Any]):
        """
        初始化七牛云Kodo存储策略

        Args:
            config: 存储配置字典，必须包含:
                - kodo_access_key: Kodo Access Key
                - kodo_secret_key: Kodo Secret Key
                - kodo_bucket: Kodo Bucket名称
                - kodo_region: Kodo存储区域（如：z0, z1, z2等）
                - kodo_domain: 域名前缀（可选）
        """
        super().__init__(config)

        # 验证必要配置
        access_key = config.get("kodo_access_key", "")
        secret_key = config.get("kodo_secret_key", "")
        bucket_name = config.get("kodo_bucket", "")

        if not all([access_key, secret_key, bucket_name]):
            raise ValueError(
                "七牛云Kodo配置不完整，需要: kodo_access_key, kodo_secret_key, kodo_bucket"
            )

        # 创建认证对象
        self.auth = Auth(access_key, secret_key)

        # Bucket名称
        self.bucket_name = bucket_name

        # 创建Bucket管理器
        self.bucket_manager = BucketManager(self.auth)

        # 域名前缀（可选）
        self.domain = config.get("kodo_domain", "")

        # 存储区域（用于构建默认域名）
        self.region = config.get("kodo_region", "z0")

    async def upload(self, file_content: bytes, file_path: str) -> dict[str, Any]:
        """
        上传文件到七牛云Kodo

        Args:
            file_content: 文件内容（字节数据）
            file_path: 文件存储路径（相对路径，作为Kodo的Key）

        Returns:
            dict: 上传结果
        """
        try:
            # 生成上传Token
            token = self.auth.upload_token(self.bucket_name, file_path, 3600)

            # 上传文件
            ret, info = put_data(token, file_path, file_content)

            # 检查上传结果
            if info.status_code != 200:
                return {
                    "success": False,
                    "error": f"七牛云Kodo上传失败: {info.text_body}",
                    "file_size": 0,
                    "url": "",
                }

            # 获取访问URL
            url = self.get_url(file_path)

            return {
                "success": True,
                "error": None,
                "file_size": len(file_content),
                "url": url,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"七牛云Kodo上传失败: {str(e)}",
                "file_size": 0,
                "url": "",
            }

    async def delete(self, file_path: str) -> bool:
        """
        删除Kodo中的文件

        Args:
            file_path: 文件存储路径（相对路径，作为Kodo的Key）

        Returns:
            bool: 是否删除成功
        """
        try:
            # bucket_manager.delete() 返回 None，删除失败会抛出异常
            self.bucket_manager.delete(self.bucket_name, file_path)
            return True
        except Exception:
            return False

    def get_url(self, file_path: str) -> str:
        """
        获取Kodo文件访问URL

        Args:
            file_path: 文件存储路径（相对路径，作为Kodo的Key）

        Returns:
            str: 文件访问URL
        """
        # 如果配置了自定义域名，使用自定义域名
        if self.domain:
            return f"https://{self.domain}/{file_path}"

        # 否则使用七牛云默认域名
        # 格式: https://bucket-name.storage.qiniu.com/file-path
        # 注意：实际域名需要在七牛云控制台绑定，这里只是示例
        return f"https://{self.bucket_name}.cdn.qiniu.com/{file_path}"

    def exists(self, file_path: str) -> bool:
        """
        检查Kodo中的文件是否存在

        Args:
            file_path: 文件存储路径（相对路径，作为Kodo的Key）

        Returns:
            bool: 文件是否存在
        """
        try:
            # bucket_manager.stat() 返回 (ret, info) 元组
            # ret 是字典，包含文件信息；info 是 ResponseInfo 对象
            stat_result = self.bucket_manager.stat(self.bucket_name, file_path)
            # 如果文件存在，返回的元组第一个元素包含文件信息
            return stat_result is not None and stat_result[0] is not None
        except Exception:
            return False
