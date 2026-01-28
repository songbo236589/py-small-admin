"""
文件上传库 - 统一入口，一行代码完成文件上传
"""

import os
from typing import Any

from config.upload import UploadConfig
from Modules.common.libs.upload.storage import StorageFactory
from Modules.common.libs.upload.upload_handler import UploadHandler


class UploadLib:
    """文件上传库 - 统一入口类"""

    @staticmethod
    async def upload(
        upload_config: dict[str, Any] | UploadConfig,
        sys_config: dict[str, Any],
        file: Any,
        file_type: str,
    ) -> dict[str, Any]:
        """
        一行代码完成文件上传

        Args:
            upload_config: 上传配置 (Config.get("upload"))
            sys_config: 系统配置 (sys_config_service.get_config_by_group("upload"))
            file: FastAPI UploadFile 对象
            file_type: 文件类型 (image/document/video/audio)

        Returns:
            dict: 上传结果
                {
                    "success": bool,           # 是否成功
                    "error": str | None,       # 错误信息
                    "original_name": str,      # 原始文件名
                    "filename": str,           # 存储文件名
                    "file_path": str,          # 文件路径
                    "file_size": int,          # 文件大小
                    "file_hash": str,          # 文件哈希
                    "mime_type": str,          # MIME 类型
                    "file_ext": str,           # 文件扩展名
                    "width": int,              # 图片宽度
                    "height": int,             # 图片高度
                    "thumbnail_filename": str, # 缩略图文件名
                    "thumbnail_path": str,     # 缩略图路径
                    "thumbnail_size": int,     # 缩略图大小
                }
        """
        # 获取存储类型（从系统配置中获取）
        storage_type = (
            sys_config.get("upload_storage_type", "local") if sys_config else "local"
        )

        # 初始化处理器
        if isinstance(upload_config, dict):
            upload_dir = upload_config.get("dir", "./uploads")
        else:
            upload_dir = upload_config.dir
        handler = UploadHandler(upload_dir, sys_config)

        # 创建存储策略
        storage_config = (
            upload_config
            if isinstance(upload_config, dict)
            else upload_config.model_dump()
        )
        storage = StorageFactory.create_storage(storage_type, storage_config)

        # 获取原始文件名
        original_filename = file.filename or ""

        # 获取文件大小（在读取文件内容之前）
        file_size = file.size if hasattr(file, "size") else 0

        # 验证文件大小是否超过限制
        size_validation = handler.validate_file_size(file_type, file_size)
        if not size_validation["valid"]:
            max_size_mb = size_validation["max_size_mb"]
            current_size_mb = file_size / (1024 * 1024)
            return {
                "success": False,
                "error": f"文件大小超过限制，当前 {current_size_mb:.2f}MB，最大允许 {max_size_mb}MB",
            }

        # 读取文件内容
        file_content = await file.read()

        # 计算文件哈希值
        file_hash = handler.calculate_file_hash(file_content)

        # 获取文件扩展名
        file_ext = handler.get_file_extension(original_filename)

        # 验证文件扩展名是否与文件类型匹配
        validation_result = handler.validate_file_extension(file_type, file_ext)
        if not validation_result["valid"]:
            supported_extensions = ", ".join(validation_result["supported"])
            return {
                "success": False,
                "error": f"文件扩展名 {file_ext} 不支持，支持的扩展名有 {supported_extensions}",
            }

        # 生成存储文件名
        filename = handler.generate_filename(file_type, file_ext, original_filename)

        # 生成存储路径
        file_path = handler.generate_file_path(file_type, filename)

        # 处理文件内容（图片处理）
        processed_content = file_content
        width, height = 0, 0
        if file_type == "image":
            # 如果是图片，进行图片处理
            try:
                # 获取压缩配置
                compress_config = None
                if sys_config and sys_config.get("upload_compress_enabled", False):
                    compress_config = {
                        "enabled": True,
                        "max_width": sys_config.get("upload_compress_max_width", 1920),
                        "max_height": sys_config.get(
                            "upload_compress_max_height", 1080
                        ),
                        "quality": sys_config.get("upload_compress_quality", 85),
                    }

                # 获取水印配置
                watermark_config = None
                if sys_config and sys_config.get("upload_watermark_enabled", False):
                    watermark_config = UploadLib._get_watermark_config(sys_config)

                # 处理图片（压缩 + 水印）
                import io
                from pathlib import Path

                from PIL import Image

                img = Image.open(io.BytesIO(file_content))
                width, height = img.size

                # 如果有压缩或水印配置，处理图片
                if compress_config or watermark_config:
                    # 先保存到临时文件处理
                    temp_path = Path(handler.upload_dir) / ("temp_" + filename)
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    temp_width, temp_height, temp_size = (
                        handler.image_processor.process_image(
                            img,
                            str(temp_path),
                            compress_config,
                            watermark_config,
                        )
                    )
                    # 读取处理后的图片
                    with open(temp_path, "rb") as f:
                        processed_content = f.read()
                    # 删除临时文件
                    temp_path.unlink(missing_ok=True)
                    width, height = temp_width, temp_height
            except Exception as e:
                print(f"图片处理失败: {str(e)}")
                # 图片处理失败，使用原始内容
                try:
                    import io

                    from PIL import Image

                    img = Image.open(io.BytesIO(file_content))
                    width, height = img.size
                except Exception:
                    width, height = 0, 0

        # 使用存储策略上传文件
        upload_result = await storage.upload(processed_content, file_path)
        if not upload_result["success"]:
            return {
                "success": False,
                "error": upload_result["error"],
            }

        file_size = upload_result["file_size"]
        file_url = upload_result["url"]

        # 生成缩略图（仅图片类型）
        thumbnail_filename = ""
        thumbnail_path = ""
        thumbnail_size = 0
        if (
            file_type == "image"
            and sys_config
            and sys_config.get("upload_thumbnail_enabled", False)
        ):
            try:
                # 获取缩略图配置
                thumb_config = {
                    "width": sys_config.get("upload_thumbnail_width", 300),
                    "height": sys_config.get("upload_thumbnail_height", 300),
                    "quality": sys_config.get("upload_thumbnail_quality", 80),
                    "suffix": sys_config.get("upload_thumbnail_suffix", "_thumb"),
                }

                # 生成缩略图
                import io

                from PIL import Image

                # 打开原始图片生成缩略图
                img = Image.open(io.BytesIO(file_content))
                thumbnail_path, thumbnail_size = handler.generate_thumbnail(
                    file_path, thumb_config
                )

                # 获取缩略图文件名
                thumbnail_filename = os.path.basename(thumbnail_path)

                # 上传缩略图到存储
                if thumbnail_path:
                    # 读取缩略图内容
                    from pathlib import Path

                    thumb_full_path = Path(handler.upload_dir) / thumbnail_path
                    if thumb_full_path.exists():
                        with open(thumb_full_path, "rb") as f:
                            thumb_content = f.read()
                        # 上传缩略图
                        await storage.upload(thumb_content, thumbnail_path)

                print(f"缩略图生成成功: {thumbnail_filename} ({thumbnail_size} bytes)")
            except Exception as e:
                print(f"生成缩略图失败: {str(e)}")
                # 缩略图生成失败，不影响主文件上传

        # 获取 MIME 类型
        mime_type = file.content_type or ""

        # 如果是图片且未获取到宽高，重新获取
        if file_type == "image" and (width == 0 or height == 0):
            try:
                width, height = handler.get_image_size(file_path)
            except Exception:
                width, height = 0, 0

        # 返回成功结果
        return {
            "success": True,
            "error": None,
            "original_name": original_filename,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_hash": file_hash,
            "mime_type": mime_type,
            "file_ext": file_ext,
            "width": width,
            "height": height,
            "thumbnail_filename": thumbnail_filename,
            "thumbnail_path": thumbnail_path,
            "thumbnail_size": thumbnail_size,
            "url": file_url,
            "storage_type": storage_type,
        }

    @staticmethod
    def _get_watermark_config(sys_config: dict[str, Any]) -> dict[str, Any]:
        """
        获取水印配置

        Args:
            sys_config: 系统配置

        Returns:
            dict: 水印配置
        """

        # 获取透明度并转换为 float
        opacity_str = sys_config.get("upload_watermark_opacity", "0.5")
        try:
            opacity = float(opacity_str)
            # 确保透明度在 0-1 范围内
            opacity = max(0.0, min(1.0, opacity))
        except (ValueError, TypeError):
            opacity = 0.5

        # 获取图片缩放比例并转换为 float
        image_scale_str = sys_config.get("upload_watermark_image_scale", "0.2")
        try:
            image_scale = float(image_scale_str)
            # 确保缩放比例在 0-1 范围内
            image_scale = max(0.0, min(1.0, image_scale))
        except (ValueError, TypeError):
            image_scale = 0.2

        # 获取水印图片数据
        watermark_image_data = sys_config.get("upload_watermark_image_data", [])
        # 从 URL 转换为相对路径（去掉开头的 /）
        image_url = (
            watermark_image_data[0].get("url", "") if watermark_image_data else ""
        )
        image_path = image_url.lstrip("/") if image_url else ""
        return {
            "enabled": sys_config.get("upload_watermark_enabled", False),
            "type": sys_config.get("upload_watermark_type", "text"),
            "text": sys_config.get("upload_watermark_text", ""),
            "position": sys_config.get("upload_watermark_position", "bottom-right"),
            "opacity": opacity,
            "font_size": sys_config.get("upload_watermark_font_size", 20),
            "font_color": sys_config.get("upload_watermark_font_color", "#FFFFFF"),
            "font_path": sys_config.get("upload_watermark_font_path", ""),
            "image_path": image_path,
            "image_scale": image_scale,
            "margin": sys_config.get("upload_watermark_margin", 10),
        }
