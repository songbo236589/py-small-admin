"""
Celery 应用实例

供 Celery CLI 使用的应用实例入口

使用示例:
    # 启动 Worker
    celery -A Modules.common.libs.celery.app worker --loglevel=info

    # 启动 Beat (定时任务)
    celery -A Modules.common.libs.celery.app beat --loglevel=info

    # 启动 Flower (监控)
    celery -A Modules.common.libs.celery.app flower

    # 查看已注册的任务
    celery -A Modules.common.libs.celery.app inspect registered

    # 查看定时任务配置
    celery -A Modules.common.libs.celery.app inspect beat
"""

# Celery Worker 启动时需要初始化数据库等资源
# 这里执行与 FastAPI 应用相同的初始化流程

# ========== gevent Monkey Patch（必须在所有其他导入之前）==========
# gevent.monkey.patch_all() 必须在其他模块导入之前执行
# 只在 Worker 进程中应用，避免影响 FastAPI/Flower/Beat 应用
# ==================================================================

# 1. 首先只导入必要的模块用于检查环境
import os
import sys

# 2. 检查是否为 Worker 进程且使用 gevent pool
service_type = os.getenv("SERVICE_TYPE", "")
is_gevent_worker = (
    service_type.startswith("celery-worker")  # 是 Worker
    and (
        "--pool=gevent" in " ".join(sys.argv) or "-P gevent" in " ".join(sys.argv)
    )  # 使用 gevent
)

# 3. 应用 gevent monkey patch（必须在所有其他导入之前）
if is_gevent_worker:
    try:
        from gevent.monkey import patch_all

        patch_all()
        print("[celery.app] ✅ gevent monkey patch applied")
    except ImportError:
        print("[celery.app] ⚠️ gevent not available, monkey patch skipped")
    except Exception as e:
        print(f"[celery.app] ⚠️ gevent monkey patch failed: {e}")

# ==================================================================
# 4. 现在才导入其他所有模块（它们会被 gevent patch）
from ..config.registry import ConfigRegistry  # noqa: E402
from ..database import (  # noqa: E402
    # close_db_engine,
    # close_redis_clients,
    init_db_engine,
    init_redis_clients,
    init_session_maker,
)
from ..log import setup_logging  # noqa: E402
from ..time import init_timezone  # noqa: E402
from .celery_service import get_celery_service  # noqa: E402

# 按顺序执行初始化
# 1. 加载所有配置
ConfigRegistry.load()

# 2. 初始化日志
setup_logging()

# 3. 初始化数据库引擎
init_db_engine()

# 4. 初始化数据库会话工厂
init_session_maker()

# 5. 初始化 Redis 客户端
init_redis_clients()

# 6. 初始化时区
init_timezone()

# 7. 创建 Celery 应用实例供 CLI 使用
celery = get_celery_service().app


# # 8. 注册 Celery Worker 退出时的资源清理函数
# def cleanup_resources():
#     """
#     Celery Worker 退出时的资源清理函数

#     关闭数据库连接和 Redis 客户端，避免资源泄漏
#     """
#     try:
#         # 获取当前事件循环
#         loop = asyncio.get_event_loop()

#         # 如果事件循环未关闭，则执行清理
#         if not loop.is_closed():
#             # 关闭数据库引擎
#             loop.run_until_complete(close_db_engine())

#             # 关闭 Redis 客户端
#             loop.run_until_complete(close_redis_clients())

#     except Exception:
#         # 捕获异常，避免清理失败影响 Worker 退出
#         import traceback

#         traceback.print_exc()


# # 注册 worker_shutdown 信号处理


# @worker_shutdown.connect
# def on_worker_shutdown(sender, **kwargs):
#     """
#     Celery Worker 退出时的信号处理函数

#     当 Worker 接收到 shutdown 信号时，执行资源清理
#     """
#     cleanup_resources()


# # 注册系统信号处理（用于强制退出场景）
# def signal_handler(signum, frame):
#     """
#     系统信号处理函数

#     当收到 SIGTERM 或 SIGINT 信号时，执行资源清理并退出
#     """
#     cleanup_resources()
#     sys.exit(0)


# # 注册系统信号
# signal.signal(signal.SIGTERM, signal_handler)
# signal.signal(signal.SIGINT, signal_handler)

# # 注册 atexit 钩子（作为最后的保障）


# atexit.register(cleanup_resources)
