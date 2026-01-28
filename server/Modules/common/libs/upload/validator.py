"""
文件上传验证器 - 负责验证文件大小、扩展名等
"""

from typing import Any

from config.upload import UploadConfig


class UploadValidator:
    """文件上传验证器"""

    # 默认最大文件大小（MB）
    DEFAULT_MAX_SIZES = {
        "image": 5,
        "document": 20,
        "video": 50,
        "audio": 20,
    }

    # 默认支持的扩展名
    DEFAULT_EXTENSIONS = {
        "image": {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"},
        "document": {
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "txt",
            "csv",
        },
        "video": {"mp4", "avi", "mov", "wmv", "flv", "mkv", "webm"},
        "audio": {"mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"},
    }

    # 配置键映射
    CONFIG_KEY_MAP = {
        "image": {
            "max_size": "upload_image_max_size",
            "allowed_types": "upload_image_allowed_types",
        },
        "document": {
            "max_size": "upload_document_max_size",
            "allowed_types": "upload_document_allowed_types",
        },
        "video": {
            "max_size": "upload_video_max_size",
            "allowed_types": "upload_video_allowed_types",
        },
        "audio": {
            "max_size": "upload_audio_max_size",
            "allowed_types": "upload_audio_allowed_types",
        },
    }

    def __init__(self, upload_config: dict[str, Any] | UploadConfig | None = None):
        """
        初始化验证器

        Args:
            upload_config: 上传配置字典或UploadConfig对象
        """
        self.upload_config = upload_config or {}

    def validate_file_size(self, file_type: str, file_size: int) -> dict[str, Any]:
        """
        验证文件大小是否超过配置的限制

        Args:
            file_type: 文件类型 (image/document/video/audio)
            file_size: 文件大小（字节）

        Returns:
            dict: 包含验证结果和最大文件大小
                {
                    "valid": bool,  # 是否验证通过
                    "max_size_mb": int  # 最大文件大小（MB）
                }
        """
        # 获取配置键
        config_keys = self.CONFIG_KEY_MAP.get(file_type, {})
        max_size_key = config_keys.get("max_size")

        max_size_mb = 0

        # 从配置中获取最大文件大小
        if max_size_key and self.upload_config:
            if isinstance(self.upload_config, dict):
                max_size_mb = self.upload_config.get(max_size_key, 0)
            else:
                # UploadConfig 对象，从 sys_config 获取（因为 UploadConfig 不包含这些字段）
                # 这些字段来自数据库配置，不是 UploadConfig 的字段
                max_size_mb = 0

        # 如果配置不存在，使用默认值
        if max_size_mb == 0:
            max_size_mb = self.DEFAULT_MAX_SIZES.get(file_type, 10)

        # 如果配置为0，表示不限制大小
        if max_size_mb == 0:
            return {"valid": True, "max_size_mb": 0}

        # 转换为字节进行比较
        max_size_bytes = max_size_mb * 1024 * 1024
        is_valid = file_size <= max_size_bytes

        return {"valid": is_valid, "max_size_mb": max_size_mb}

    def validate_file_extension(self, file_type: str, file_ext: str) -> dict[str, Any]:
        """
        验证文件扩展名是否与文件类型匹配

        Args:
            file_type: 文件类型 (image/document/video/audio)
            file_ext: 文件扩展名（带点号，如 .jpg）

        Returns:
            dict: 包含验证结果和支持的扩展名列表
                {
                    "valid": bool,  # 是否验证通过
                    "supported": list  # 支持的扩展名列表
                }
        """
        # 获取配置键
        config_keys = self.CONFIG_KEY_MAP.get(file_type, {})
        allowed_types_key = config_keys.get("allowed_types")

        extensions_set = None

        # 从配置中获取允许的扩展名
        if allowed_types_key and self.upload_config:
            if isinstance(self.upload_config, dict):
                extensions_list = self.upload_config.get(allowed_types_key)
                if isinstance(extensions_list, list):
                    extensions_set = set(extensions_list)
            else:
                # UploadConfig 对象，从 sys_config 获取（因为 UploadConfig 不包含这些字段）
                # 这些字段来自数据库配置，不是 UploadConfig 的字段
                extensions_set = None

        # 如果配置不存在，使用默认扩展名
        if extensions_set is None:
            extensions_set = self.DEFAULT_EXTENSIONS.get(file_type, set())

        # 将文件扩展名转换为不带点号的形式（如 .jpg -> jpg）
        file_ext_without_dot = file_ext.lstrip(".")

        # 验证扩展名
        is_valid = file_ext_without_dot in extensions_set

        return {"valid": is_valid, "supported": sorted(extensions_set)}

    def get_allowed_extensions(self, file_type: str) -> list[str]:
        """
        获取指定文件类型支持的扩展名列表

        Args:
            file_type: 文件类型

        Returns:
            list: 支持的扩展名列表
        """
        result = self.validate_file_extension(file_type, "")
        return result["supported"]

    def get_max_size(self, file_type: str) -> int:
        """
        获取指定文件类型的最大文件大小

        Args:
            file_type: 文件类型

        Returns:
            int: 最大文件大小（MB）
        """
        result = self.validate_file_size(file_type, 0)
        return result["max_size_mb"]
