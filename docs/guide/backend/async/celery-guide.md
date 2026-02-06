# Celery 使用指南

本文档介绍了项目中 Celery 的配置和使用方法。

## 简介

Celery 是一个强大的分布式任务队列，用于处理异步任务和定时任务。

## 项目集成

项目已集成 Celery，通过 `CeleryService` 类管理 Celery 应用。

### 获取 Celery 实例

```python
from Modules.common.libs.celery.celery_service import get_celery_service

# 获取 Celery 服务实例
celery_service = get_celery_service()
celery_app = celery_service.app
```

### FastAPI 集成

```python
from fastapi import FastAPI
from Modules.common.libs.celery.celery_service import init_fastapi_celery

app = FastAPI()
init_fastapi_celery(app)
```

## 定义任务

### 基本任务定义

```python
from Modules.common.libs.celery.celery_service import celery_app

@celery_app().task
def send_email(to: str, subject: str, body: str):
    """发送邮件任务"""
    # 发送邮件逻辑
    return {"status": "sent", "to": to}
```

### 带装饰器的任务

```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def process_data(self, data_id: int):
    """处理数据任务，支持重试"""
    try:
        # 处理逻辑
        return {"status": "success"}
    except Exception as exc:
        # 重试
        raise self.retry(exc=exc, countdown=60)
```

## 调用任务

### 异步调用

```python
from Modules.admin.tasks.default_tasks import send_email

# 异步调用任务
result = send_email.delay("user@example.com", "Hello", "Body")

# 获取任务 ID
task_id = result.id
```

### 延迟调用

```python
from datetime import datetime, timedelta

# 10 秒后执行
result = send_email.apply_async(
    args=["user@example.com", "Hello", "Body"],
    countdown=10
)

# 指定时间执行
result = send_email.apply_async(
    args=["user@example.com", "Hello", "Body"],
    eta=datetime(2024, 1, 1, 12, 0)
)
```

### 等待结果

```python
# 等待任务完成
result = send_email.apply_async(args=[...])
result.wait()  # 阻塞等待

# 获取结果
value = result.get(timeout=10)
```

## 任务配置

### 任务装饰器参数

```python
@celery_app().task(
    name="custom.task.name",      # 任务名称
    bind=True,                     # 绑定任务实例
    max_retries=3,                 # 最大重试次数
    default_retry_delay=60,        # 重试延迟（秒）
    time_limit=3600,               # 任务超时时间（秒）
    soft_time_limit=3000,          # 软超时时间（秒）
    autoretry_for=(Exception,),    # 自动重试的异常类型
    retry_backoff=True,            # 指数退避重试
    retry_backoff_max=700,         # 最大退避时间
    retry_jitter=True,             # 添加随机抖动
)
def my_task():
    pass
```

### 路由配置

```python
# 配置任务路由
task_routes = {
    "Modules.admin.*": {"queue": "admin"},
    "Modules.quant.*": {"queue": "quant"},
    "Modules.email.*": {"queue": "email"},
}
```

## 定时任务

### 配置定时任务

在配置文件中配置 `beat_schedule`：

```python
beat_schedule = {
    # 每天凌晨执行数据同步
    "sync-daily-data": {
        "task": "Modules.quant.tasks.sync_stock_data",
        "schedule": crontab(hour=0, minute=0),
    },
    # 每 5 分钟执行一次
    "check-status": {
        "task": "Modules.admin.tasks.check_system_status",
        "schedule": 300.0,
    },
}
```

### 启动 Beat

```bash
celery -A Modules.common.libs.celery.celery_service beat --loglevel=info
```

## 启动 Worker

### 项目架构说明

本项目采用**分组 Worker 架构**，将不同业务模块的任务分配到独立的 Worker 中：

| Worker | 监听队列 | 说明 |
|--------|----------|------|
| celery-worker | default, email_queues | Admin 模块任务 |
| celery-worker-quant | quant_concept_queues, quant_industry_queues, quant_stock_queues | Quant 模块任务 |

### 基本启动

```bash
celery -A Modules.common.libs.celery.app worker --loglevel=info
```

### 指定队列

```bash
# 启动 Admin Worker（处理 default, email_queues）
celery -A Modules.common.libs.celery.app worker --loglevel=info \
  --queues=default,email_queues -n worker-admin@%h

# 启动 Quant Worker（处理 quant_* 队列）
celery -A Modules.common.libs.celery.app worker --loglevel=info \
  --queues=quant_concept_queues,quant_industry_queues,quant_stock_queues -n worker-quant@%h
```

### 指定并发数

```bash
# 使用 -c 参数指定并发数
celery -A Modules.common.libs.celery.app worker --loglevel=info \
  --queues=default,email_queues -c 4 -n worker-admin@%h
```

### 分组启动（推荐）

```bash
# 启动 Admin Worker
celery -A Modules.common.libs.celery.app worker --loglevel=info \
  --queues=default,email_queues -n worker-admin@%h &

# 启动 Quant Worker
celery -A Modules.common.libs.celery.app worker --loglevel=info \
  --queues=quant_concept_queues,quant_industry_queues,quant_stock_queues -n worker-quant@%h &

# 启动 Beat
celery -A Modules.common.libs.celery.app beat --loglevel=info &
```

### Docker 环境启动

```bash
# 启动所有 Celery 服务
cd server/docker
docker-compose up -d celery-worker celery-worker-quant celery-beat

# 扩展 Quant Worker
docker-compose up -d --scale celery-worker-quant=3
```

## 监控

### Flower 监控

```bash
celery -A Modules.common.libs.celery.celery_service flower
```

访问 http://localhost:5555 查看 Flower 监控界面。

### 命令行监控

```bash
# 查看活跃任务
celery -A Modules.common.libs.celery.celery_service inspect active

# 查看已注册任务
celery -A Modules.common.libs.celery.celery_service inspect registered

# 查看统计信息
celery -A Modules.common.libs.celery.celery_service inspect stats
```

## 最佳实践

### 1. 任务幂等性

任务应该是幂等的，即多次执行结果相同：

```python
@celery_app().task
def update_user(user_id: int, data: dict):
    # 使用 update_time 避免重复更新
    update_time = datetime.now()
    # 更新逻辑...
```

### 2. 避免大参数传递

不要传递大量数据给任务，使用 ID 引用：

```python
# 不推荐
@celery_app().task
def process_large_data(data: list):
    pass

# 推荐
@celery_app().task
def process_data_ids(data_ids: list[int]):
    data = load_data_by_ids(data_ids)
    # 处理逻辑...
```

### 3. 任务结果存储

```python
@celery_app().task(bind=True)
def long_task(self):
    # 更新任务状态
    self.update_state(state='PROGRESS', meta={'progress': 50})
    # 继续处理...
    return {'status': 'completed'}
```

### 4. 错误处理

```python
@celery_app().task(bind=True, max_retries=3)
def risky_task(self):
    try:
        # 可能失败的操作
        pass
    except Exception as exc:
        # 记录日志
        logger.error(f"Task failed: {exc}")
        # 重试
        raise self.retry(exc=exc)
```

## 配置说明

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| broker_url | Broker 地址 | redis://localhost:6379/0 |
| result_backend | 结果存储 | redis://localhost:6379/1 |
| task_serializer | 任务序列化 | json |
| result_serializer | 结果序列化 | json |
| timezone | 时区 | Asia/Shanghai |
| worker_concurrency | Worker 并发数 | CPU 核心数 |
| task_default_queue | 默认队列 | default |
