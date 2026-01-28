"""
腾讯云COS存储策略

将文件存储到腾讯云对象存储COS
"""

from typing import Any

from qcloud_cos import CosConfig, CosS3Client

from .base_storage import BaseStorage


class TencentCOSStrategy(BaseStorage):
    """
    腾讯云COS存储策略

    将文件存储到腾讯云对象存储COS，适用于生产环境
    """

    def __init__(self, config: dict[str, Any]):
        """
        初始化腾讯云COS存储策略

        Args:
            config: 存储配置字典，必须包含:
                - cos_secret_id: COS Secret ID
                - cos_secret_key: COS Secret Key
                - cos_region: COS区域（如：ap-guangzhou）
                - cos_bucket: COS Bucket名称
                - cos_endpoint: COS端点地址（可选，会根据region自动生成）
                - cos_cdn_domain: CDN域名（可选）
        """
        super().__init__(config)

        # 验证必要配置
        secret_id = config.get("cos_secret_id", "")
        secret_key = config.get("cos_secret_key", "")
        region = config.get("cos_region", "ap-guangzhou")
        bucket_name = config.get("cos_bucket", "")

        if not all([secret_id, secret_key, bucket_name]):
            raise ValueError(
                "腾讯云COS配置不完整，需要: cos_secret_id, cos_secret_key, cos_bucket"
            )

        # 保存region（用于构建URL）
        self.region = region

        # 构建endpoint
        endpoint = config.get("cos_endpoint", f"cos.{region}.myqcloud.com")

        # 创建COS配置
        cos_config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Endpoint=endpoint,
        )

        # 创建COS客户端
        self.client = CosS3Client(cos_config)

        # Bucket名称（格式: bucket-name-appid）
        self.bucket_name = bucket_name

        # CDN域名（可选）
        self.cdn_domain = config.get("cos_cdn_domain", "")

    async def upload(self, file_content: bytes, file_path: str) -> dict[str, Any]:
        """
        上传文件到腾讯云COS

        Args:
            file_content: 文件内容（字节数据）
            file_path: 文件存储路径（相对路径，作为COS的Key）

        Returns:
            dict: 上传结果
        """
        try:
            # 上传文件到COS
            self.client.put_object(
                Bucket=self.bucket_name,
                Body=file_content,
                Key=file_path,
            )
            # put_object 返回 PutObjectResult，我们不需要使用它

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
                "error": f"腾讯云COS上传失败: {str(e)}",
                "file_size": 0,
                "url": "",
            }

    async def delete(self, file_path: str) -> bool:
        """
        删除COS中的文件

        Args:
            file_path: 文件存储路径（相对路径，作为COS的Key）

        Returns:
            bool: 是否删除成功
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception:
            return False

    def get_url(self, file_path: str) -> str:
        """
        获取COS文件访问URL

        Args:
            file_path: 文件存储路径（相对路径，作为COS的Key）

        Returns:
            str: 文件访问URL
        """
        # 如果配置了CDN域名，使用CDN域名
        if self.cdn_domain:
            return f"https://{self.cdn_domain}/{file_path}"

        # 否则使用COS默认域名
        # 格式: https://bucket-name.cos.region.myqcloud.com/file-path
        return f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{file_path}"

    def exists(self, file_path: str) -> bool:
        """
        检查COS中的文件是否存在

        Args:
            file_path: 文件存储路径（相对路径，作为COS的Key）

        Returns:
            bool: 文件是否存在
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception:
            return False
