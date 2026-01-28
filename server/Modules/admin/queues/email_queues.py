"""
邮件发送队列任务

包含邮件发送相关的异步队列任务
"""

from typing import Any

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail,
)
from loguru import logger

from Modules.common.libs.celery.celery_service import get_celery_service

# 获取 Celery 应用实例
celery_app = get_celery_service().app


@celery_app.task(
    name="Modules.admin.queues.email_queues.send_batch_email_queue",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 600},
)
def send_batch_email_queue(
    self,
    to_emails: list[str],
    subject: str,
    content: str,
    content_type: str = "html",
    email_config: dict[str, Any] | None = None,
):
    """
    批量发送邮件任务

    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        content: 邮件内容
        content_type: 内容类型（html/plain）
        email_config: 邮件配置字典

    Returns:
        dict: 发送结果统计
    """
    import asyncio

    if not email_config:
        logger.error("邮件配置为空，无法发送邮件")
        return {"success": 0, "failed": len(to_emails), "errors": ["邮件配置为空"]}

    smtp_port = email_config.get("smtp_port", 587)
    use_ssl_tls = smtp_port == 465
    use_starttls = smtp_port == 587
    # 配置邮件连接
    conf = ConnectionConfig(
        MAIL_SERVER=email_config.get("smtp_host", ""),
        MAIL_PORT=email_config.get("smtp_port", 587),
        MAIL_USERNAME=email_config.get("smtp_username", ""),
        MAIL_PASSWORD=email_config.get("smtp_password", ""),
        MAIL_FROM=email_config.get("mail_from_address", ""),
        MAIL_FROM_NAME=email_config.get("mail_from_name", "Py Small Admin"),
        MAIL_STARTTLS=use_starttls,  # 587端口启用STARTTLS
        MAIL_SSL_TLS=use_ssl_tls,  # 465端口启用SSL/TLS
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=False,  # 关闭证书验证（解决部分环境的SSL证书问题）
        TIMEOUT=30,  # 添加超时时间，避免卡壳
    )

    # 创建FastMail实例
    fm = FastMail(conf)

    # 统计发送结果
    success_count = 0
    failed_count = 0
    errors = []

    for email in to_emails:
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[NameEmail(name=email, email=email)],
                body=content,
                subtype=MessageType.html
                if content_type == "html"
                else MessageType.plain,
            )
            asyncio.run(fm.send_message(message))
            success_count += 1
            logger.info(f"邮件发送成功: {email}")
        except Exception as e:
            # 过滤QQ邮箱的非致命SMTP响应格式错误
            error_msg = str(e)
            if "Malformed SMTP response line" in error_msg:
                success_count += 1
                logger.warning(
                    f"QQ邮箱SMTP响应格式异常（邮件已发送）: {email} - {error_msg}"
                )
            else:
                # 真正的发送失败错误
                failed_count += 1
                err = f"{email}: {error_msg}"
                errors.append(err)
                logger.error(f"邮件发送失败: {err}")
    return {
        "success": success_count,
        "failed": failed_count,
        "total": len(to_emails),
        "errors": errors,
    }
