"""
邮件验证器

提供邮件发送相关的参数验证功能。
"""

import re

from pydantic import Field, field_validator

from ...common.models.base_model import BaseModel


class EmailBatchSendRequest(BaseModel):
    """批量发送邮件请求模型"""

    to_emails: str = Field(..., description="收件人邮箱列表（用逗号分隔）")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容（支持HTML）")
    content_type: str = Field(default="html", description="内容类型（html/plain）")

    @field_validator("to_emails")
    @classmethod
    def validate_to_emails(cls, v):
        """验证收件人邮箱列表"""
        if not v or len(v.strip()) == 0:
            raise ValueError("收件人列表不能为空")

        # 将逗号分隔的字符串转换为列表
        email_list = [email.strip() for email in v.split(",") if email.strip()]

        if len(email_list) == 0:
            raise ValueError("收件人列表不能为空")

        if len(email_list) > 100:
            raise ValueError("单次批量发送最多支持100个收件人")

        # 验证每个邮箱格式
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        for email in email_list:
            if not re.match(email_pattern, email):
                raise ValueError(f"邮箱格式不正确: {email}")

        return email_list

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v):
        """验证邮件主题"""
        if not v or len(v.strip()) == 0:
            raise ValueError("邮件主题不能为空")
        if len(v) > 200:
            raise ValueError("邮件主题长度不能超过200个字符")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        """验证邮件内容"""
        if not v or len(v.strip()) == 0:
            raise ValueError("邮件内容不能为空")
        if len(v) > 100000:
            raise ValueError("邮件内容长度不能超过100000个字符")
        return v.strip()

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        """验证内容类型"""
        if v not in ["html", "plain"]:
            raise ValueError("内容类型只能是html或plain")
        return v.lower()
