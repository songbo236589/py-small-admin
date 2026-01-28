"""
邮件发送控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Form
from fastapi.responses import JSONResponse

from Modules.admin.services.email_service import EmailService
from Modules.admin.validators.email_validator import EmailBatchSendRequest
from Modules.common.libs.validation.decorators import validate_request_data


class EmailController:
    """邮件发送控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化邮件发送控制器"""
        self.email_service = EmailService()

    @validate_request_data(EmailBatchSendRequest)
    async def send_batch(
        self,
        to_emails: str = Form(..., description="收件人邮箱列表（用逗号分隔）"),
        subject: str = Form(..., description="邮件主题"),
        content: str = Form(..., description="邮件内容（支持HTML）"),
        content_type: str = Form("html", description="内容类型（html/plain）"),
    ) -> JSONResponse:
        """批量发送邮件"""
        return await self.email_service.send_batch_email(
            {
                "to_emails": to_emails,
                "subject": subject,
                "content": content,
                "content_type": content_type,
            }
        )
