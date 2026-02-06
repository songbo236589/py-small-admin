# 异步任务开发

本文档介绍了如何使用 Celery 开发异步任务。

## Celery 简介

Celery 是一个强大的分布式任务队列，用于处理异步任务和定时任务。

### 项目集成

项目通过 `CeleryService` 类集成 Celery，支持：

- 异步任务执行
- 定时任务调度
- 任务监控和日志
- 任务重试和错误处理
- 多队列支持

## 架构设计

### 任务架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  FastAPI    │────▶│   Redis     │────▶│  Celery     │
│  应用       │     │  (Broker)   │     │  Worker     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                         │
       │                                         ▼
       │                                  ┌─────────────┐
       │                                  │  Database   │
       └─────────────────────────────────┴─────────────┘
```

### 任务目录结构

```
Modules/
├── admin/
│   ├── tasks/           # 任务定义
│   │   └── default_tasks.py
│   └── queues/          # 队列定义
│       └── email_queues.py
└── quant/
    ├── tasks/           # 任务定义
    │   └── sync_tasks.py
    └── queues/          # 队列定义
        └── data_queues.py
```

## 任务定义

### 基本任务

```python
from Modules.common.libs.celery.celery_service import celery_app

@celery_app().task(name="app.tasks.print_hello")
def print_hello():
    """打印 Hello"""
    print("Hello, World!")
    return {"status": "success"}
```

### 带参数的任务

```python
@celery_app().task(name="app.tasks.send_email")
def send_email(to: str, subject: str, body: str):
    """发送邮件"""
    # 发送邮件逻辑
    return {"status": "sent", "to": to}
```

### 绑定任务

```python
@celery_app().task(bind=True, name="app.tasks.process_data")
def process_data(self, data_id: int):
    """处理数据任务（可以访问任务实例）"""
    # 更新任务状态
    self.update_state(state='PROGRESS', meta={'progress': 50})

    # 处理数据
    result = do_process(data_id)

    return {"status": "completed", "result": result}
```

### 任务配置

```python
@celery_app().task(
    name="app.tasks.heavy_task",
    max_retries=3,              # 最大重试次数
    default_retry_delay=60,     # 重试延迟（秒）
    time_limit=3600,            # 任务超时（秒）
    soft_time_limit=3000,       # 软超时（秒）
    autoretry_for=(Exception,), # 自动重试的异常
)
def heavy_task(param: str):
    """重型任务"""
    # 任务逻辑
    pass
```

## 任务调用

### 异步调用

```python
from Modules.admin.tasks.default_tasks import send_email

# 异步调用
result = send_email.delay("user@example.com", "Hello", "Body")

# 获取任务 ID
task_id = result.id
print(f"任务 ID: {task_id}")

# 检查任务状态
print(f"任务状态: {result.state}")
print(f"任务结果: {result.result}")
```

### 延迟执行

```python
from datetime import timedelta

# 10 秒后执行
result = send_email.apply_async(
    args=["user@example.com", "Hello", "Body"],
    countdown=10
)

# 1 小时后执行
result = send_email.apply_async(
    args=["user@example.com", "Hello", "Body"],
    countdown=3600
)
```

### 定时执行

```python
from datetime import datetime

# 在指定时间执行
result = send_email.apply_async(
    args=["user@example.com", "Hello", "Body"],
    eta=datetime(2024, 1, 1, 12, 0)
)
```

## 定时任务

### 配置定时任务

```python
from celery.schedules import crontab

beat_schedule = {
    # 每 30 秒执行一次
    'task-every-30s': {
        'task': 'app.tasks.print_hello',
        'schedule': 30.0,
    },

    # 每天凌晨 2 点执行
    'task-daily': {
        'task': 'app.tasks.sync_stock_list',
        'schedule': crontab(hour=2, minute=0),
    },

    # 每周一早上 8 点执行
    'task-weekly': {
        'task': 'app.tasks.weekly_report',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),
    },
}
```

### 启动 Beat

```bash
celery -A Modules.common.libs.celery.celery_service beat --loglevel=info
```

## 任务队列

### 配置队列

```python
task_queues = [
    Queue('default', routing_key='default'),
    Queue('admin', routing_key='admin'),
    Queue('quant', routing_key='quant'),
    Queue('email', routing_key='email'),
]

task_routes = {
    'Modules.admin.*': {'queue': 'admin'},
    'Modules.quant.*': {'queue': 'quant'},
    'Modules.admin.queues.email_queues.*': {'queue': 'email'},
}
```

### 指定队列启动 Worker

```bash
# 只处理 admin 队列
celery -A Modules.common.libs.celery.celery_service worker --loglevel=info -Q admin

# 处理多个队列
celery -A Modules.common.libs.celery.celery_service worker --loglevel=info -Q admin,quant
```

## 任务监控

### Flower 监控

```bash
# 启动 Flower
celery -A Modules.common.libs.celery.celery_service flower

# 访问 http://localhost:5555
```

Fliber 提供以下功能：

- 实时任务状态
- Worker 状态
- 任务执行时间
- 任务成功率
- 任务重试情况

### 命令行监控

```bash
# 查看活跃任务
celery -A Modules.common.libs.celery.celery_service inspect active

# 查看已注册任务
celery -A Modules.common.libs.celery.celery_service inspect registered

# 查看统计信息
celery -A Modules.common.libs.celery.celery_service inspect stats

# 查看计划任务
celery -A Modules.common.libs.celery.celery_service inspect scheduled
```

## 任务重试

### 自动重试

```python
@celery_app().task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
)
def risky_task(self):
    """会自动重试的任务"""
    try:
        # 可能失败的操作
        pass
    except Exception as exc:
        # 记录日志
        logger.error(f"任务失败: {exc}")
        # 触发重试
        raise self.retry(exc=exc, countdown=60)
```

### 手动重试

```python
@celery_app().task(bind=True)
def manual_retry_task(self):
    """手动重试的任务"""
    try:
        result = do_something()
        return result
    except Exception as exc:
        # 重试，使用指数退避
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

## 最佳实践

### 1. 任务幂等性

任务应该是幂等的，多次执行结果相同：

```python
@celery_app().task
def update_user(user_id: int, data: dict):
    """更新用户（幂等）"""
    user = db.get_user(user_id)
    if user and user.updated_at < data['updated_at']:
        db.update_user(user_id, data)
    return {"status": "success"}
```

### 2. 避免大参数传递

使用 ID 引用而非大对象：

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

### 3. 使用任务进度

```python
@celery_app().task(bind=True)
def long_task(self):
    """长任务，报告进度"""
    for i in range(100):
        # 处理逻辑
        time.sleep(0.1)

        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={'progress': i + 1, 'total': 100}
        )

    return {'status': 'completed'}
```

### 4. 合理设置超时

```python
@celery_app().task(
    time_limit=3600,        # 硬超时（强制终止）
    soft_time_limit=3000,    # 软超时（抛出异常）
)
def long_running_task():
    """长运行任务"""
    pass
```

### 5. 任务结果存储

```python
@celery_app().task(bind=True)
def task_with_result(self):
    """有结果存储的任务"""
    result = do_work()

    # 存储结果
    self.update_state(
        state='SUCCESS',
        meta={'result': result}
    )

    return result
```

## 常见问题

### 任务一直处于 PENDING 状态

**原因**：Worker 没有运行或队列配置错误

**解决方案**：
1. 确认 Worker 正在运行
2. 检查队列名称是否匹配
3. 确认 Redis 连接正常

### 任务执行失败但没重试

**原因**：异常类型不在 `autoretry_for` 中

**解决方案**：
```python
@celery_app().task(
    autoretry_for=(ConnectionError, TimeoutError),  # 指定自动重试的异常
    retry_backoff=True,                             # 启用指数退避
)
```

### 内存泄漏

**原因**：长时间运行的 Worker 可能积累内存

**解决方案**：
```bash
# 限制每个 Worker 处理的任务数
celery worker --max-tasks-per-child=1000
```

## 相关文档

- [Celery 使用指南](./celery-guide.md)
- [任务列表](./task-list.md)
- [配置指南](../config/index.md)
