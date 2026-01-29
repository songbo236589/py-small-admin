# Celery 基础指南

Celery 是一个强大的分布式任务队列，用于处理异步任务和定时任务。本指南将帮助您在 Py Small Admin 项目中配置和使用 Celery。

## 概述

Celery 是一个简单、灵活且可靠的分布式系统，用于处理大量消息，同时为操作提供维护此类系统所需的工具。它是一个任务队列，专注于实时操作，但也支持调度。

### 核心概念

- **Broker（消息代理）**: 用于传递消息的中间件，如 RabbitMQ、Redis
- **Worker（工作进程）**: 执行任务的进程
- **Task（任务）**: 需要异步执行的函数
- **Queue（队列）**: 存储待处理任务的队列
- **Result Backend（结果存储）**: 存储任务执行结果的存储后端

### 为什么使用 Celery

- **异步处理**: 将耗时操作从主流程中分离
- **定时任务**: 支持周期性任务调度
- **分布式**: 支持多台机器协同工作
- **可靠性**: 任务失败自动重试，消息持久化
- **监控**: 提供丰富的监控和管理工具

## 环境准备

### 1. 安装依赖

```bash
# 基础依赖
pip install celery[redis]

# 或使用 RabbitMQ
pip install celery[rabbitmq]

# 监控工具
pip install flower
```

### 2. 配置消息代理

#### 使用 Redis

```bash
# 安装 Redis
# Windows: 下载并安装 Redis
# Linux/Mac: 使用包管理器安装

# 启动 Redis
redis-server
```

#### 使用 RabbitMQ

```bash
# 安装 RabbitMQ
# Ubuntu/Debian:
sudo apt-get install rabbitmq-server

# Mac:
brew install rabbitmq

# 启动 RabbitMQ
sudo rabbitmq-server
```

## 配置 Celery

### 基础配置

在项目配置文件中添加 Celery 配置：

```python
# config/celery_config.py
from celery import Celery
import os

# Celery 实例
celery_app = Celery('py_small_admin')

# 配置消息代理
# 使用 Redis
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# 或使用 RabbitMQ
# celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')

# 配置结果存储
celery_app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# 时区设置
celery_app.conf.timezone = 'Asia/Shanghai'
celery_app.conf.enable_utc = True

# 任务序列化
celery_app.conf.task_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_serializer = 'json'

# 任务结果过期时间（秒）
celery_app.conf.result_expires = 3600

# 任务接收设置
celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 30 * 60  # 30分钟硬限制
celery_app.conf.task_soft_time_limit = 25 * 60  # 25分钟软限制

# 任务路由配置
celery_app.conf.task_routes = {
    'Modules.admin.tasks.*': {'queue': 'admin'},
    'Modules.quant.tasks.*': {'queue': 'quant'},
    'Modules.common.tasks.*': {'queue': 'common'},
}

# 自动发现任务
celery_app.conf.autodiscover_tasks = [
    'Modules.admin',
    'Modules.quant',
    'Modules.common',
]
```

### 环境变量配置

在 `.env` 文件中添加：

```bash
# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_LOG_LEVEL=INFO
```

## 创建第一个任务

### 定义任务

```python
# Modules/admin/tasks/email_task.py
from celery import shared_task
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task(name='send_email')
def send_email_task(to_email, subject, content):
    """
    发送邮件任务

    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        content: 邮件内容

    Returns:
        dict: 发送结果
    """
    logger.info(f"开始发送邮件到: {to_email}")

    try:
        # 模拟邮件发送
        import time
        time.sleep(2)

        logger.info(f"邮件发送成功: {to_email}")

        return {
            'status': 'success',
            'email': to_email,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        raise
```

### 调用任务

```python
# 在 API 中调用任务
from fastapi import APIRouter, HTTPException
from Modules.admin.tasks.email_task import send_email_task

router = APIRouter()

@router.post("/send-email")
async def send_email(to_email: str, subject: str, content: str):
    """
    发送邮件 API
    """
    try:
        # 异步调用任务
        task = send_email_task.delay(to_email, subject, content)

        return {
            'code': 200,
            'message': '邮件已加入发送队列',
            'data': {
                'task_id': task.id,
                'status': task.status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 启动 Worker

### 基础启动

```bash
# 启动 worker
celery -A config.celery_config worker --loglevel=info

# 指定队列
celery -A config.celery_config worker -l info -Q admin,quant

# 指定并发数
celery -A config.celery_config worker -l info -c 4

# 后台运行（生产环境）
celery -A config.celery_config worker -l info --detach
```

### 启动 Beat（定时任务）

```bash
# 启动 beat 调度器
celery -A config.celery_config beat --loglevel=info

# 同时启动 worker 和 beat
celery -A config.celery_config worker --beat --loglevel=info
```

### 常用启动参数

```bash
# 常用参数说明
-l, --loglevel          # 日志级别
-c, --concurrency       # 并发数
-Q, --queues            # 指定队列
-n, --hostname          # worker 名称
--detach                # 后台运行
--pidfile               # PID 文件路径
--logfile               # 日志文件路径
--max-tasks-per-child   # 每个 worker 处理的任务数限制
```

## 任务配置

### 任务装饰器选项

```python
from celery import shared_task

@shared_task(
    name='process_data',           # 任务名称
    bind=True,                     # 绑定任务实例
    max_retries=3,                 # 最大重试次数
    default_retry_delay=60,         # 重试延迟（秒）
    time_limit=300,                # 任务超时时间
    soft_time_limit=240,           # 软超时时间
    autoretry_for=(Exception,),    # 自动重试的异常
    retry_backoff=True,            # 指数退避
    retry_backoff_max=600,         # 最大退避时间
    retry_jitter=True,             # 添加随机抖动
)
def process_data_task(self, data_id):
    """
    处理数据任务
    """
    try:
        # 处理逻辑
        result = process_data(data_id)
        return result
    except Exception as exc:
        # 记录重试信息
        logger.error(f"任务失败，准备重试: {exc}")
        raise self.retry(exc=exc)
```

### 任务结果处理

```python
from celery.result import AsyncResult

# 获取任务结果
def get_task_result(task_id):
    """
    获取任务执行结果
    """
    result = AsyncResult(task_id)

    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None,
        'traceback': result.traceback if result.failed() else None
    }
```

## 定时任务

### 配置定时任务

```python
# config/celery_config.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # 每天凌晨 2 点执行
    'daily-data-cleanup': {
        'task': 'Modules.common.tasks.cleanup_data',
        'schedule': crontab(hour=2, minute=0),
    },

    # 每 5 分钟执行一次
    'every-5-minutes': {
        'task': 'Modules.quant.tasks.sync_data',
        'schedule': 300.0,  # 秒
    },

    # 每周一早上 9 点执行
    'weekly-report': {
        'task': 'Modules.admin.tasks.generate_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },

    # 每月 1 号凌晨 3 点执行
    'monthly-backup': {
        'task': 'Modules.common.tasks.backup_database',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),
    },
}
```

### Crontab 语法

```python
# crontab(minute, hour, day_of_month, month_of_year, day_of_week)

# 示例
crontab()                    # 每分钟
crontab(minute=0)            # 每小时
crontab(minute=0, hour=0)    # 每天午夜
crontab(minute=0, hour='*/3') # 每 3 小时
crontab(minute=30, hour=12)  # 每天 12:30
crontab(minute=0, hour=9, day_of_week='mon-fri') # 工作日早上 9 点
```

## 监控 Flower

### 启动 Flower

```bash
# 启动 flower
celery -A config.celery_config flower

# 指定端口
celery -A config.celery_config flower --port=5555

# 指定 broker
celery -A config.celery_config flower --broker=redis://localhost:6379/0

# 后台运行
celery -A config.celery_config flower --detach
```

### 访问 Flower UI

启动后访问：http://localhost:5555

Flower 提供的功能：

- Worker 状态监控
- 任务执行情况
- 任务队列状态
- 任务重试和撤销
- 实时日志查看

## 最佳实践

### 1. 任务设计原则

```python
# ✅ 好的设计
@shared_task
def process_user_data(user_id):
    """处理单个用户数据"""
    user = get_user(user_id)
    result = process(user)
    return result

# ❌ 不好的设计
@shared_task
def process_all_users():
    """处理所有用户数据"""
    users = get_all_users()  # 可能返回大量数据
    for user in users:
        process(user)
```

### 2. 幂等性设计

```python
@shared_task(bind=True, max_retries=3)
def process_payment(self, order_id):
    """
    处理支付任务 - 幂等性设计
    """
    # 检查订单状态
    order = get_order(order_id)
    if order.status == 'paid':
        logger.info(f"订单 {order_id} 已支付，跳过处理")
        return {'status': 'already_paid'}

    try:
        # 处理支付
        result = payment_gateway.charge(order)

        # 更新订单状态
        update_order_status(order_id, 'paid')

        return {'status': 'success', 'order_id': order_id}
    except Exception as exc:
        logger.error(f"支付处理失败: {exc}")
        raise self.retry(exc=exc)
```

### 3. 错误处理

```python
@shared_task(bind=True, max_retries=3)
def risky_task(self, data):
    """
    带错误处理的任务
    """
    try:
        result = process_data(data)
        return result
    except ValueError as e:
        # 业务逻辑错误，不重试
        logger.error(f"业务错误: {e}")
        raise
    except ConnectionError as e:
        # 网络错误，重试
        logger.warning(f"网络错误，准备重试: {e}")
        raise self.retry(exc=e, countdown=60)
    except Exception as e:
        # 未知错误，记录并重试
        logger.error(f"未知错误: {e}")
        raise self.retry(exc=e, countdown=60)
```

### 4. 任务链和组

```python
from celery import chain, group, chord

# 任务链：顺序执行
task_chain = chain(
    process_data.s(data_id),
    validate_result.s(),
    send_notification.s()
)
task_chain.delay()

# 任务组：并行执行
task_group = group(
    process_user_data.s(user_id)
    for user_id in user_ids
)
task_group.delay()

# 任务和弦：并行执行后汇总
task_chord = chord(
    (process_user_data.s(user_id) for user_id in user_ids),
    summarize_results.s()
)
task_chord.delay()
```

## 常见问题

### 1. Worker 不启动

**问题**：启动 worker 时报错

**解决方案**：

- 检查 broker 是否运行
- 检查配置文件路径是否正确
- 检查依赖是否安装完整

### 2. 任务不执行

**问题**：任务已提交但不执行

**解决方案**：

- 检查 worker 是否运行
- 检查队列配置是否正确
- 查看日志获取详细错误信息

### 3. 内存泄漏

**问题**：worker 内存持续增长

**解决方案**：

- 设置 `--max-tasks-per-child` 限制
- 检查任务代码是否有内存泄漏
- 使用 `--max-memory-per-child` 限制内存

## 相关文档

- [任务开发指南](./task-development.md)
- [队列管理](./queue-management.md)
- [监控指南](./monitoring.md)
- [部署指南](../deployment/deployment-guide.md)

## 参考资源

- [Celery 官方文档](https://docs.celeryproject.org/)
- [Flower 文档](https://flower.readthedocs.io/)
- [Celery 最佳实践](https://docs.celeryproject.org/en/stable/userguide/optimizing.html)
