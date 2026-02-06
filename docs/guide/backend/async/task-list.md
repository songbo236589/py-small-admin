# 异步任务列表

本文档列出了项目中定义的所有异步任务。

## Admin 模块任务

### 默认任务

| 任务名称 | 说明 | 队列 |
|----------|------|------|
| `Modules.admin.tasks.default_tasks.send_email` | 发送邮件 | email |
| `Modules.admin.tasks.default_tasks.clear_cache` | 清除缓存 | default |

### 邮件任务

```python
from Modules.admin.tasks.default_tasks import send_email

# 异步发送邮件
result = send_email.delay(
    to="user@example.com",
    subject="邮件主题",
    body="邮件内容"
)

# 获取任务 ID
task_id = result.id
```

### 缓存任务

```python
from Modules.admin.tasks.default_tasks import clear_cache

# 清除指定缓存
result = clear_cache.delay(key_prefix="user:*")
```

## Email 队列任务

| 任务名称 | 说明 | 队列 |
|----------|------|------|
| `Modules.admin.queues.email_queues.send_welcome_email` | 发送欢迎邮件 | email |
| `Modules.admin.queues.email_queues.send_notification_email` | 发送通知邮件 | email |

```python
from Modules.admin.queues.email_queues import send_welcome_email

# 发送欢迎邮件
result = send_welcome_email.delay(
    user_id=1,
    username="newuser"
)
```

## Quant 模块任务

### 数据同步任务

| 任务名称 | 说明 | 队列 |
|----------|------|------|
| `Modules.quant.tasks.sync_stock_data` | 同步股票数据 | quant |
| `Modules.quant.tasks.sync_industry_data` | 同步行业数据 | quant |
| `Modules.quant.tasks.sync_concept_data` | 同步概念数据 | quant |

```python
from Modules.quant.tasks import sync_stock_data

# 同步股票数据
result = sync_stock_data.delay()
```

## 定时任务

| 任务名称 | 调度时间 | 说明 |
|----------|----------|------|
| `sync-daily-data` | 每天凌晨 | 同步每日数据 |
| `check-system-status` | 每 5 分钟 | 检查系统状态 |
| `clean-temp-files` | 每周 | 清理临时文件 |
| `send-daily-report` | 每天早上 | 发送每日报告 |

## 任务状态查询

### 通过任务 ID 查询

```python
from celery.result import AsyncResult

task_id = "xxx-xxx-xxx"
result = AsyncResult(task_id)

# 查询状态
if result.state == 'PENDING':
    print("任务等待中")
elif result.state == 'STARTED':
    print("任务已开始")
elif result.state == 'SUCCESS':
    print(f"任务成功: {result.result}")
elif result.state == 'FAILURE':
    print(f"任务失败: {result.info}")
```

### 通过 Celery Inspector 查询

```python
from Modules.common.libs.celery.celery_service import get_celery_service

celery_app = get_celery_service().app

# 查询活跃任务
active = celery_app.control.inspect().active()

# 查询已注册任务
registered = celery_app.control.inspect().registered()

# 查询计划任务
scheduled = celery_app.control.inspect().scheduled()
```

## 任务重试配置

### 自动重试

```python
@celery_app().task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError)
)
def retry_task(self):
    # 会自动重试的任务
    pass
```

### 手动重试

```python
@celery_app().task(bind=True)
def manual_retry_task(self):
    try:
        # 可能失败的操作
        pass
    except Exception as exc:
        # 手动触发重试
        raise self.retry(exc=exc, countdown=60)
```

## 任务优先级

```python
# 高优先级任务
result = high_priority_task.apply_async(priority=9)

# 低优先级任务
result = low_priority_task.apply_async(priority=1)
```

## 任务链 (Chain)

```python
from celery import chain

# 顺序执行多个任务
result = chain(
    task1.s(arg1, arg2),
    task2.s(),
    task3.s()
).apply_async()
```

## 任务组 (Group)

```python
from celery import group

# 并行执行多个任务
result = group([
    task1.s(arg1),
    task2.s(arg2),
    task3.s(arg3)
]).apply_async()
```

## 任务回调

```python
# 成功回调
@celery_app().task
def on_success(result):
    print(f"任务成功: {result}")

# 失败回调
@celery_app().task
def on_failure(request, exc, traceback):
    print(f"任务失败: {exc}")

# 主任务
@celery_app().task(
    link=on_success.s(),        # 成功时执行
    link_error=on_failure.s()   # 失败时执行
)
def main_task():
    pass
```
