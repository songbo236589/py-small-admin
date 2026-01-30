# 异步任务开发

本文档介绍了如何使用 Celery 开发异步任务。

## Celery 简介

Celery 是一个分布式任务队列，用于处理异步任务和定时任务。

## 任务定义

### 基本任务

```python
from Modules.common.libs.celery.celery_service import celery

@celery.task(name="myapp.task.print_hello")
def print_hello():
    """打印 Hello"""
    print("Hello, World!")
    return {"status": "success"}
```

### 带参数的任务

```python
@celery.task(name="myapp.task.send_email")
def send_email(to: str, subject: str, body: str):
    """发送邮件"""
    # 发送邮件逻辑
    return {"status": "success", "to": to}
```

## 任务调用

### 延迟执行

```python
from datetime import timedelta

# 10 秒后执行
result = print_hello.apply_async(countdown=10)
```

### 定时执行

```python
from celery.schedules import crontab

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # 每 30 秒执行一次
    sender.add_periodic_task(30.0, print_hello.s(), name='print-hello-every-30s')
    
    # 每天凌晨 2 点执行
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        sync_stock_list.s(),
        name='sync-stock-list-daily'
    )
```

## 任务监控

### 使用 Flower

```bash
celery -A Modules.common.libs.celery.celery_service.celery flower
```

访问 http://localhost:5555 查看任务状态。

## 最佳实践

1. 使用任务重试
2. 使用任务超时
3. 使用任务队列
4. 使用任务路由
