"""
邮件发送服务 - 负责邮件发送相关的业务逻辑
"""

from typing import Any

from fastapi.responses import JSONResponse
from loguru import logger

from Modules.admin.services.sys_config_service import SysConfigService
from Modules.common.libs.celery.celery_service import get_celery_service
from Modules.common.libs.responses.response import error, success
from Modules.common.services.base_service import BaseService


class EmailService(BaseService):
    """邮件发送服务 - 负责邮件发送相关的业务逻辑"""

    def __init__(self):
        super().__init__()
        self.sys_config_service = SysConfigService()

    async def send_batch_email(self, data: dict[str, Any]) -> JSONResponse:
        """
        批量发送邮件（异步）

        Args:
            data: 邮件数据，包含:
                - to_emails: 收件人邮箱列表
                - subject: 邮件主题
                - content: 邮件内容
                - content_type: 内容类型（html/plain）
                - attachments: 附件路径列表

        Returns:
            JSONResponse: 包含任务ID的响应
        """
        # 获取邮件配置
        email_config = await self._get_email_config()
        if not email_config:
            return error("邮件配置不完整，请先配置SMTP信息")

        # 获取Celery应用实例
        celery_service = get_celery_service()
        celery_app = celery_service.app

        # 调用Celery异步任务发送邮件
        try:
            task = celery_app.send_task(
                "Modules.admin.queues.email_queues.send_batch_email_queue",
                args=[
                    data.get("to_emails", "").split(","),
                    data.get("subject"),
                    data.get("content"),
                    data.get("content_type", "html"),
                    email_config,
                ],
            )

            logger.info(
                f"邮件发送任务已提交: task_id={task.id}, "
                f"recipients={len(data.get('to_emails', []))}"
            )

            return success(
                {
                    "task_id": task.id,
                    "total_recipients": len(data.get("to_emails", [])),
                    "status": "pending",
                },
                message="邮件发送任务已提交",
            )
        except Exception as e:
            logger.error(f"提交邮件发送任务失败: {e}")
            return error(f"提交邮件发送任务失败: {str(e)}")

    async def _get_email_config(self) -> dict[str, Any] | None:
        """
        获取邮件配置

        Returns:
            dict | None: 邮件配置字典，如果配置不完整则返回None
        """
        try:
            config = await self.sys_config_service.get_config_by_group("email")

            # 验证必需的配置项
            required_keys = [
                "smtp_host",
                "smtp_port",
                "smtp_username",
                "smtp_password",
                "mail_from_address",
                "mail_from_name",
            ]

            for key in required_keys:
                if key not in config or not config[key]:
                    logger.warning(f"邮件配置缺少必需项: {key}")
                    return None

            # 确保端口号是整数
            if isinstance(config["smtp_port"], str):
                config["smtp_port"] = int(config["smtp_port"])

            return config
        except Exception as e:
            logger.error(f"获取邮件配置失败: {e}")
            return None
