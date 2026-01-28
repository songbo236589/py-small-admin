"""
文件名和路径生成器 - 负责生成存储文件名和文件路径
"""

import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path


class FilenameGenerator:
    """文件名和路径生成器"""

    def __init__(self, upload_dir: str):
        """
        初始化文件名生成器

        Args:
            upload_dir: 上传根目录
        """
        self.upload_dir = upload_dir

    def generate_filename(
        self,
        file_ext: str,
        original_filename: str = "",
        filename_rule: str = "uuid",
    ) -> str:
        """
        根据配置生成存储文件名

        Args:
            file_ext: 文件扩展名（包含点号，如 .jpg）
            original_filename: 原始文件名
            filename_rule: 文件名规则 (uuid/timestamp/md5/original)

        Returns:
            str: 生成的文件名
        """
        # 如果提供了原始文件名且规则为 original，使用原始文件名
        if filename_rule == "original" and original_filename:
            # 提取文件名（不含扩展名）
            base_name = os.path.splitext(original_filename)[0]

            # 检查文件是否已存在，如果存在则添加数字后缀
            counter = 1
            while True:
                if counter == 1:
                    new_filename = f"{base_name}{file_ext}"
                else:
                    new_filename = f"{base_name}_{counter}{file_ext}"

                # 检查文件是否已存在（需要生成完整路径）
                # 这里暂时返回，实际使用时需要传入 file_type 来生成完整路径
                # 或者由调用者处理文件存在性检查
                return new_filename

        if filename_rule == "uuid":
            return f"{uuid.uuid4().hex}{file_ext}"
        elif filename_rule == "timestamp":
            return f"{int(datetime.now().timestamp())}{file_ext}"
        elif filename_rule == "md5":
            return f"{hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()}{file_ext}"
        else:
            # 默认使用 UUID
            return f"{uuid.uuid4().hex}{file_ext}"

    def check_filename_exists(
        self, file_type: str, filename: str, path_rule: str = "Y-m-d"
    ) -> bool:
        """
        检查文件名是否已存在

        Args:
            file_type: 文件类型
            filename: 文件名
            path_rule: 路径规则

        Returns:
            bool: 文件是否存在
        """
        file_path = self.generate_file_path(file_type, filename, path_rule)
        full_path = Path(self.upload_dir) / file_path
        return full_path.exists()

    def generate_unique_filename(
        self,
        file_type: str,
        file_ext: str,
        original_filename: str = "",
        filename_rule: str = "uuid",
        path_rule: str = "Y-m-d",
    ) -> str:
        """
        生成唯一的文件名（处理文件名冲突）

        Args:
            file_type: 文件类型
            file_ext: 文件扩展名
            original_filename: 原始文件名
            filename_rule: 文件名规则
            path_rule: 路径规则

        Returns:
            str: 唯一的文件名
        """
        if filename_rule == "original" and original_filename:
            # 提取文件名（不含扩展名）
            base_name = os.path.splitext(original_filename)[0]

            # 检查文件是否已存在，如果存在则添加数字后缀
            counter = 1
            while True:
                if counter == 1:
                    new_filename = f"{base_name}{file_ext}"
                else:
                    new_filename = f"{base_name}_{counter}{file_ext}"

                # 检查文件是否已存在
                if not self.check_filename_exists(file_type, new_filename, path_rule):
                    return new_filename

                counter += 1
                # 防止无限循环，最多尝试 1000 次
                if counter > 1000:
                    # 超过最大尝试次数，使用 UUID
                    return f"{uuid.uuid4().hex}{file_ext}"
        else:
            # 其他规则直接生成
            return self.generate_filename(file_ext, original_filename, filename_rule)

    def generate_file_path(
        self, file_type: str, filename: str, path_rule: str = "Y-m-d"
    ) -> str:
        """
        根据配置生成文件存储路径

        Args:
            file_type: 文件类型
            filename: 文件名
            path_rule: 路径规则 (Y-m-d/Y-m/Y)

        Returns:
            str: 文件存储路径（相对路径）
        """
        if path_rule == "Y-m-d":
            date_str = datetime.now().strftime("%Y-%m-%d")
            return f"{file_type}/{date_str}/{filename}"
        elif path_rule == "Y-m":
            date_str = datetime.now().strftime("%Y-%m")
            return f"{file_type}/{date_str}/{filename}"
        elif path_rule == "Y":
            year_str = datetime.now().strftime("%Y")
            return f"{file_type}/{year_str}/{filename}"
        else:
            # 默认使用年-月-日
            date_str = datetime.now().strftime("%Y-%m-%d")
            return f"{file_type}/{date_str}/{filename}"

    def get_full_path(self, file_path: str) -> Path:
        """
        获取文件的完整路径

        Args:
            file_path: 相对路径

        Returns:
            Path: 完整路径
        """
        return Path(self.upload_dir) / file_path

    def ensure_directory_exists(self, file_path: str) -> None:
        """
        确保文件所在目录存在

        Args:
            file_path: 相对路径
        """
        full_path = self.get_full_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
