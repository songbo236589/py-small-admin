"""
阿里云OSS存储策略

将文件存储到阿里云对象存储OSS
"""

from typing import Any

import oss2

from .base_storage import BaseStorage


class AliyunOSSStorage(BaseStorage):
    """
    阿里云OSS存储策略

    将文件存储到阿里云对象存储OSS，适用于生产环境
    """

    def __init__(self, config: dict[str, Any]):
        """
        初始化阿里云OSS存储策略

        Args:
            config: 存储配置字典，必须包含:
                - oss_access_key_id: OSS Access Key ID
                - oss_access_key_secret: OSS Access Key Secret
                - oss_region: OSS区域节点（如：oss-cn-hangzhou）
                - oss_bucket: OSS Bucket名称
                - oss_endpoint: OSS端点地址（可选，会根据region自动生成）
                - oss_cdn_domain: CDN域名（可选）
        """
        super().__init__(config)

        # 验证必要配置
        access_key_id = config.get("oss_access_key_id", "")
        access_key_secret = config.get("oss_access_key_secret", "")
        region = config.get("oss_region", "oss-cn-hangzhou")
        bucket_name = config.get("oss_bucket", "")

        if not all([access_key_id, access_key_secret, bucket_name]):
            raise ValueError(
                "阿里云OSS配置不完整，需要: oss_access_key_id, oss_access_key_secret, oss_bucket"
            )

        # 构建endpoint
        endpoint = config.get("oss_endpoint", f"https://{region}.aliyuncs.com")

        # 创建认证对象
        auth = oss2.Auth(access_key_id, access_key_secret)

        # 创建Bucket对象
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # CDN域名（可选）
        self.cdn_domain = config.get("oss_cdn_domain", "")

    async def upload(self, file_content: bytes, file_path: str) -> dict[str, Any]:
        """
        上传文件到阿里云OSS

        Args:
            file_content: 文件内容（字节数据）
            file_path: 文件存储路径（相对路径，作为OSS的Key）

        Returns:
            dict: 上传结果
        """
        try:
            # 上传文件到OSS
            self.bucket.put_object(file_path, file_content)

            # 获取访问URL
            url = self.get_url(file_path)

            return {
                "success": True,
                "error": None,
                "file_size": len(file_content),
                "url": url,
            }
        except oss2.exceptions.OssError as e:
            return {
                "success": False,
                "error": f"阿里云OSS上传失败: {e.message}",
                "file_size": 0,
                "url": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"阿里云OSS上传失败: {str(e)}",
                "file_size": 0,
                "url": "",
            }

    async def delete(self, file_path: str) -> bool:
        """
        删除OSS中的文件

        Args:
            file_path: 文件存储路径（相对路径，作为OSS的Key）

        Returns:
            bool: 是否删除成功
        """
        try:
            self.bucket.delete_object(file_path)
            return True
        except oss2.exceptions.OssError:
            return False
        except Exception:
            return False

    def get_url(self, file_path: str) -> str:
        """
        获取OSS文件访问URL

        Args:
            file_path: 文件存储路径（相对路径，作为OSS的Key）

        Returns:
            str: 文件访问URL
        """
        # 如果配置了CDN域名，使用CDN域名
        if self.cdn_domain:
            return f"https://{self.cdn_domain}/{file_path}"

        # 否则使用OSS默认域名
        # 格式: https://bucket-name.oss-region.aliyuncs.com/file-path
        bucket_name = self.bucket.bucket_name
        endpoint = self.bucket.endpoint
        # 从endpoint中提取域名部分
        domain = endpoint.replace("https://", "").replace("http://", "")
        return f"https://{bucket_name}.{domain}/{file_path}"

    def exists(self, file_path: str) -> bool:
        """
        检查OSS中的文件是否存在

        Args:
            file_path: 文件存储路径（相对路径，作为OSS的Key）

        Returns:
            bool: 文件是否存在
        """
        try:
            self.bucket.head_object(file_path)
            return True
        except oss2.exceptions.NoSuchKey:
            return False
        except Exception:
            return False
