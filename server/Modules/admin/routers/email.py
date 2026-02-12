"""
邮件发送路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.admin.controllers.v1.email_controller import EmailController

# 创建路由器
router = APIRouter(prefix="/email", tags=["邮件管理"])
# 创建控制器实例
controller = EmailController()

router.post(
    "/send_batch",
    response_model=dict[str, Any],
    summary="批量发送邮件",
    description="使用表单数据批量发送邮件，支持HTML内容和附件",
)(controller.send_batch)
