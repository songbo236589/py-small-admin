# 任务开发指南

本指南将详细介绍如何在 Py Small Admin 项目中开发和优化 Celery 任务。

## 任务基础

### 创建任务文件

在模块目录下创建 `tasks` 目录：

```
Modules/
├── admin/
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── email_task.py
│   │   └── report_task.py
```

### 基础任务定义

```python
# Modules/admin/tasks/__init__.py
from .email_task import send_email_task
from .report_task import generate_report_task

__all__ = ['send_email_task', 'generate_report_task']
```

```python
# Modules/admin/tasks/email_task.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(name='admin.send_email')
def send_email_task(to_email: str, subject: str, content: str) -> dict:
    """
    发送邮件任务

    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        content: 邮件内容

    Returns:
        dict: 执行结果
    """
    logger.info(f"开始发送邮件: {to_email}")

    try:
        # 邮件发送逻辑
        result = send_email(to_email, subject, content)

        logger.info(f"邮件发送成功: {to_email}")
        return {
            'status': 'success',
            'email': to_email,
            'message': '邮件发送成功'
        }
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        raise
```

## 任务类型

### 1. 简单任务

```python
@shared_task
def simple_task(data: dict) -> dict:
    """
    简单任务 - 无状态、无重试
    """
    result = process(data)
    return result
```

### 2. 绑定任务

```python
@shared_task(bind=True)
def bound_task(self, data_id: int) -> dict:
    """
    绑定任务 - 可以访问任务实例
    """
    logger.info(f"任务 ID: {self.request.id}")
    logger.info(f"重试次数: {self.request.retries}")

    try:
        result = process_data(data_id)
        return result
    except Exception as exc:
        # 可以使用 self.retry() 重试
        raise self.retry(exc=exc, countdown=60)
```

### 3. 重试任务

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def retry_task(self, url: str) -> dict:
    """
    带重试的任务
    """
    try:
        response = requests.get(url, timeout=30)
        return response.json()
    except Exception as exc:
        logger.warning(f"请求失败，准备重试: {exc}")
        raise self.retry(exc=exc)
```

### 4. 定时任务

```python
@shared_task
def scheduled_cleanup():
    """
    定时清理任务
    """
    logger.info("开始执行定时清理")

    # 清理逻辑
    cleanup_expired_data()
    cleanup_temp_files()

    logger.info("定时清理完成")
    return {'status': 'completed'}
```

### 5. 批量任务

```python
@shared_task
def batch_process_task(item_ids: list[int]) -> dict:
    """
    批量处理任务
    """
    results = []
    failed = []

    for item_id in item_ids:
        try:
            result = process_item(item_id)
            results.append(result)
        except Exception as e:
            logger.error(f"处理失败 {item_id}: {e}")
            failed.append(item_id)

    return {
        'total': len(item_ids),
        'success': len(results),
        'failed': len(failed),
        'failed_ids': failed
    }
```

## 任务参数

### 基础参数

```python
@shared_task(
    name='custom.task_name',           # 任务名称
    bind=True,                         # 绑定任务实例
    max_retries=3,                     # 最大重试次数
    default_retry_delay=60,             # 默认重试延迟
    time_limit=300,                    # 硬超时时间（秒）
    soft_time_limit=240,               # 软超时时间（秒）
    autoretry_for=(Exception,),        # 自动重试的异常类型
    retry_backoff=True,                # 指数退避
    retry_backoff_max=600,             # 最大退避时间
    retry_jitter=True,                 # 添加随机抖动
    rate_limit='10/m',                 # 速率限制
    ignore_result=False,               # 是否忽略结果
    serializer='json',                 # 序列化方式
    compression='gzip',                 # 压缩方式
)
def advanced_task(self, data: dict) -> dict:
    """
    高级任务配置示例
    """
    # 任务逻辑
    return process(data)
```

### 任务路由

```python
@shared_task(
    name='admin.process_data',
    queue='admin',                     # 指定队列
    routing_key='admin.process_data'   # 路由键
)
def admin_task(data: dict) -> dict:
    """管理员任务 - 使用 admin 队列"""
    return process(data)
```

## 任务调用

### 基础调用

```python
from Modules.admin.tasks.email_task import send_email_task

# 异步调用
task = send_email_task.delay('user@example.com', '主题', '内容')

# 立即调用（同步）
result = send_email_task.apply(args=['user@example.com', '主题', '内容'])

# 带参数调用
task = send_email_task.apply_async(
    args=['user@example.com', '主题', '内容'],
    kwargs={'priority': 'high'}
)
```

### 高级调用选项

```python
# 延迟执行
task = send_email_task.apply_async(
    args=['user@example.com', '主题', '内容'],
    countdown=60  # 60秒后执行
)

# 指定执行时间
from datetime import datetime, timedelta
eta = datetime.utcnow() + timedelta(hours=1)
task = send_email_task.apply_async(
    args=['user@example.com', '主题', '内容'],
    eta=eta
)

# 指定队列
task = send_email_task.apply_async(
    args=['user@example.com', '主题', '内容'],
    queue='high_priority'
)

# 设置过期时间
task = send_email_task.apply_async(
    args=['user@example.com', '主题', '内容'],
    expires=3600  # 1小时后过期
)

# 设置优先级
task = send_email_task.apply_async(
    args=['user@example.com', '主题', '内容'],
    priority=5
)

# 链式调用
from celery import chain
task_chain = chain(
    task1.s(arg1),
    task2.s(arg2),
    task3.s(arg3)
)
task_chain.delay()
```

## 任务结果处理

### 获取任务状态

```python
from celery.result import AsyncResult

def check_task_status(task_id: str) -> dict:
    """
    查询任务状态
    """
    result = AsyncResult(task_id)

    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None,
        'traceback': result.traceback if result.failed() else None,
        'info': result.info
    }
```

### 等待任务完成

```python
def wait_for_task(task_id: str, timeout: int = 30) -> dict:
    """
    等待任务完成
    """
    result = AsyncResult(task_id)

    try:
        # 等待任务完成
        result.get(timeout=timeout)
        return {
            'status': 'completed',
            'result': result.result
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
```

### 任务回调

```python
@shared_task
def task_with_callback(data: dict) -> dict:
    """
    带回调的任务
    """
    result = process(data)

    # 任务完成后执行回调
    callback_task.delay(result)

    return result

@shared_task
def callback_task(result: dict) -> None:
    """
    回调任务
    """
    logger.info(f"收到回调: {result}")
    # 处理回调逻辑
```

## 任务链和工作流

### 任务链（Chain）

```python
from celery import chain

# 顺序执行任务
workflow = chain(
    extract_data.s(source_url),
    transform_data.s(),
    load_data.s(destination_url)
)

# 执行
result = workflow.delay()
```

### 任务组（Group）

```python
from celery import group

# 并行执行任务
job = group(
    process_item.s(item_id)
    for item_id in item_ids
)

# 执行
result = job.delay()

# 等待所有任务完成
result.join()
```

### 任务和弦（Chord）

```python
from celery import chord

# 并行执行后汇总
header = [
    process_user_data.s(user_id)
    for user_id in user_ids
]
callback = summarize_results.s()

chord_task = chord(header)(callback)

# 执行
result = chord_task.delay()
```

### 任务图（Canvas）

```python
from celery import chain, group, chord

# 复杂工作流
workflow = chain(
    # 第一步：并行获取数据
    group([
        fetch_data.s(source1),
        fetch_data.s(source2),
        fetch_data.s(source3)
    ]),
    # 第二步：合并数据
    merge_data.s(),
    # 第三步：并行处理
    group([
        process_data.s('type1'),
        process_data.s('type2')
    ]),
    # 第四步：汇总
    summarize_results.s()
)

# 执行
result = workflow.delay()
```

## 任务优化

### 1. 减少任务参数大小

```python
# ❌ 不好的做法 - 传递大量数据
@shared_task
def process_large_data(large_data: list):
    """传递大量数据"""
    for item in large_data:
        process(item)

# ✅ 好的做法 - 传递 ID
@shared_task
def process_data_by_ids(data_ids: list[int]):
    """传递数据 ID"""
    for data_id in data_ids:
        data = get_data(data_id)
        process(data)
```

### 2. 使用批量处理

```python
# ❌ 不好的做法 - 多个小任务
for item_id in item_ids:
    process_item_task.delay(item_id)

# ✅ 好的做法 - 一个批量任务
batch_process_task.delay(item_ids)
```

### 3. 合理设置超时

```python
@shared_task(
    time_limit=300,        # 硬超时 5 分钟
    soft_time_limit=240    # 软超时 4 分钟
)
def long_running_task():
    """
    长时间运行的任务
    """
    # 在软超时时清理资源
    try:
        result = process()
        return result
    except SoftTimeLimitExceeded:
        logger.warning("任务超时，正在清理...")
        cleanup()
        raise
```

### 4. 使用连接池

```python
import redis
from redis import ConnectionPool

# 创建连接池
redis_pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=20
)

@shared_task
def task_with_redis():
    """使用连接池的任务"""
    r = redis.Redis(connection_pool=redis_pool)
    # 使用连接
    r.set('key', 'value')
```

## 任务测试

### 单元测试

```python
import pytest
from Modules.admin.tasks.email_task import send_email_task

def test_send_email_task(mocker):
    """测试邮件发送任务"""
    # Mock 邮件发送函数
    mock_send_email = mocker.patch('Modules.admin.tasks.email_task.send_email')
    mock_send_email.return_value = {'status': 'sent'}

    # 执行任务
    result = send_email_task('test@example.com', '测试', '内容')

    # 验证结果
    assert result['status'] == 'success'
    assert result['email'] == 'test@example.com'
    mock_send_email.assert_called_once()
```

### 集成测试

```python
def test_task_integration():
    """测试任务集成"""
    # 创建任务
    task = send_email_task.delay('test@example.com', '测试', '内容')

    # 等待任务完成
    result = task.get(timeout=10)

    # 验证结果
    assert result['status'] == 'success'
```

## 最佳实践

### 1. 幂等性设计

```python
@shared_task
def idempotent_task(order_id: int) -> dict:
    """
    幂等任务 - 多次执行结果相同
    """
    order = get_order(order_id)

    # 检查是否已处理
    if order.status == 'processed':
        logger.info(f"订单 {order_id} 已处理，跳过")
        return {'status': 'already_processed'}

    # 处理订单
    process_order(order)

    # 更新状态
    update_order_status(order_id, 'processed')

    return {'status': 'success'}
```

### 2. 错误处理

```python
@shared_task(bind=True, max_retries=3)
def robust_task(self, data: dict) -> dict:
    """
    健壮的任务 - 完善的错误处理
    """
    try:
        # 验证输入
        if not validate_input(data):
            raise ValueError("输入数据无效")

        # 处理逻辑
        result = process(data)

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

### 3. 日志记录

```python
@shared_task(bind=True)
def logged_task(self, data_id: int) -> dict:
    """
    带详细日志的任务
    """
    task_id = self.request.id
    logger.info(f"任务 {task_id} 开始处理: {data_id}")

    try:
        # 处理逻辑
        result = process_data(data_id)

        logger.info(f"任务 {task_id} 处理成功")
        return result

    except Exception as e:
        logger.error(f"任务 {task_id} 处理失败: {e}", exc_info=True)
        raise
```

### 4. 资源清理

```python
@shared_task(bind=True)
def cleanup_task(self):
    """
    带资源清理的任务
    """
    resource = None
    try:
        # 获取资源
        resource = acquire_resource()

        # 处理逻辑
        result = process(resource)

        return result

    except Exception as e:
        logger.error(f"任务失败: {e}")
        raise

    finally:
        # 清理资源
        if resource:
            release_resource(resource)
```

## 常见问题

### 1. 任务参数序列化失败

**问题**：复杂对象无法序列化

**解决方案**：

- 使用简单数据类型（str, int, float, list, dict）
- 传递对象 ID 而不是对象本身
- 使用自定义序列化器

### 2. 任务执行超时

**问题**：长时间运行的任务超时

**解决方案**：

- 增加 `time_limit` 和 `soft_time_limit`
- 优化任务逻辑
- 将大任务拆分为小任务

### 3. 内存占用过高

**问题**：任务占用大量内存

**解决方案**：

- 使用批量处理
- 及时释放资源
- 设置 `--max-tasks-per-child` 限制

## 相关文档

- [Celery 基础指南](./celery-guide.md)
- [队列管理](./queue-management.md)
- [监控指南](./monitoring.md)
- [最佳实践](../guides/best-practices.md)
