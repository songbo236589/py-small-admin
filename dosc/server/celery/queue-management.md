# 队列管理指南

本指南将详细介绍如何管理和优化 Celery 队列，包括队列配置、任务路由、性能调优等。

## 队列基础

### 队列概念

Celery 队列用于组织和分发任务，通过合理的队列设计可以实现：

- **任务优先级**: 重要任务优先处理
- **资源隔离**: 不同类型任务使用不同队列
- **负载均衡**: 多个 worker 处理不同队列
- **故障隔离**: 单个队列问题不影响其他队列

### 队列类型

```python
# 1. 默认队列
celery_app.conf.task_default_queue = 'default'
celery_app.conf.task_default_exchange = 'default'
celery_app.conf.task_default_routing_key = 'default'

# 2. 专用队列
celery_app.conf.task_queues = [
    Queue('high_priority', routing_key='high_priority.#'),
    Queue('normal', routing_key='normal.#'),
    Queue('low_priority', routing_key='low_priority.#'),
]

# 3. 混合队列
celery_app.conf.task_queues = (
    Queue('default', routing_key='default.#'),
    Queue('admin', routing_key='admin.#'),
    Queue('quant', routing_key='quant.#'),
    Queue('common', routing_key='common.#'),
)
```

## 队列配置

### 基础配置

```python
# config/celery_config.py
from kombu import Queue, Exchange

# 定义交换机
default_exchange = Exchange('default', type='direct')
admin_exchange = Exchange('admin', type='direct')
quant_exchange = Exchange('quant', type='direct')

# 定义队列
celery_app.conf.task_queues = [
    # 默认队列
    Queue('default', default_exchange, routing_key='default'),

    # 管理员队列
    Queue('admin', admin_exchange, routing_key='admin'),

    # 量化数据队列
    Queue('quant', quant_exchange, routing_key='quant'),

    # 高优先级队列
    Queue('high_priority', default_exchange, routing_key='high'),

    # 低优先级队列
    Queue('low_priority', default_exchange, routing_key='low'),
]

# 任务路由配置
celery_app.conf.task_routes = {
    # 管理员任务路由到 admin 队列
    'Modules.admin.tasks.*': {
        'queue': 'admin',
        'routing_key': 'admin',
    },

    # 量化任务路由到 quant 队列
    'Modules.quant.tasks.*': {
        'queue': 'quant',
        'routing_key': 'quant',
    },

    # 高优先级任务
    'Modules.common.tasks.urgent_*': {
        'queue': 'high_priority',
        'routing_key': 'high',
    },

    # 低优先级任务
    'Modules.common.tasks.background_*': {
        'queue': 'low_priority',
        'routing_key': 'low',
    },

    # 其他任务使用默认队列
    'Modules.common.tasks.*': {
        'queue': 'default',
        'routing_key': 'default',
    },
}
```

### 队列优先级

```python
# 创建优先级队列
celery_app.conf.task_queues = [
    Queue('high', routing_key='high', queue_arguments={
        'x-max-priority': 10,
    }),
    Queue('normal', routing_key='normal', queue_arguments={
        'x-max-priority': 5,
    }),
    Queue('low', routing_key='low', queue_arguments={
        'x-max-priority': 1,
    }),
]

# 任务指定优先级
@shared_task(queue='high')
def high_priority_task(data):
    """高优先级任务"""
    return process(data)

# 调用时指定优先级
task = high_priority_task.apply_async(
    args=[data],
    priority=10
)
```

## Worker 配置

### 基础 Worker 启动

```bash
# 启动 worker 处理默认队列
celery -A config.celery_config worker -l info

# 启动 worker 处理多个队列
celery -A config.celery_config worker -l info -Q admin,quant,common

# 启动 worker 处理所有队列
celery -A config.celery_config worker -l info -Q *

# 指定并发数
celery -A config.celery_config worker -l info -c 4

# 指定 worker 名称
celery -A config.celery_config worker -l info -n worker1@%h
```

### 专用 Worker 配置

```bash
# 管理员队列专用 worker
celery -A config.celery_config worker -l info -Q admin -n admin_worker@%h

# 量化队列专用 worker
celery -A config.celery_config worker -l info -Q quant -n quant_worker@%h

# 高优先级队列专用 worker
celery -A config.celery_config worker -l info -Q high_priority -n high_worker@%h -c 2

# 低优先级队列专用 worker（低并发）
celery -A config.celery_config worker -l info -Q low_priority -n low_worker@%h -c 1
```

### Worker 优化参数

```bash
# 完整的 worker 启动命令
celery -A config.celery_config worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=admin,quant \
    --hostname=worker1@%h \
    --max-tasks-per-child=1000 \
    --max-memory-per-child=200000 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --prefetch-multiplier=4 \
    --autoscale=10,2 \
    --pidfile=/var/run/celery/worker1.pid \
    --logfile=/var/log/celery/worker1.log
```

参数说明：

- `--concurrency`: 并发进程数
- `--queues`: 监听的队列
- `--hostname`: worker 名称
- `--max-tasks-per-child`: 每个 worker 处理的任务数
- `--max-memory-per-child`: 最大内存限制（KB）
- `--time-limit`: 硬超时时间
- `--soft-time-limit`: 软超时时间
- `--prefetch-multiplier`: 预取倍数
- `--autoscale`: 自动扩展（最大,最小）
- `--pidfile`: PID 文件路径
- `--logfile`: 日志文件路径

## 队列监控

### 使用 Flower 监控

```bash
# 启动 flower
celery -A config.celery_config flower --port=5555

# 指定 broker
celery -A config.celery_config flower --broker=redis://localhost:6379/0

# 持久化配置
celery -A config.celery_config flower \
    --port=5555 \
    --broker=redis://localhost:6379/0 \
    --basic_auth=user:password \
    --flower_port=5555
```

### 使用命令行监控

```bash
# 查看活动任务
celery -A config.celery_config inspect active

# 查看预定任务
celery -A config.celery_config inspect scheduled

# 查看已注册任务
celery -A config.celery_config inspect registered

# 查看队列统计
celery -A config.celery_config inspect stats

# 查看队列长度
celery -A config.celery_config inspect active_queues

# 清除队列
celery -A config.celery_config purge

# 撤销任务
celery -A config.celery_config control revoke <task_id>
```

### 自定义监控脚本

```python
# scripts/monitor_queues.py
import redis
from celery import Celery

def monitor_queues():
    """监控队列状态"""
    r = redis.Redis(host='localhost', port=6379, db=0)

    queues = ['default', 'admin', 'quant', 'high_priority', 'low_priority']

    print("队列状态监控:")
    print("-" * 50)

    for queue in queues:
        # 获取队列长度
        queue_key = f'celery:{queue}'
        length = r.llen(queue_key)

        # 获取队列详情
        print(f"队列: {queue}")
        print(f"  长度: {length}")
        print(f"  状态: {'正常' if length < 1000 else '繁忙'}")
        print()

if __name__ == '__main__':
    monitor_queues()
```

## 队列优化

### 1. 合理分配队列

```python
# 根据任务特性分配队列
celery_app.conf.task_routes = {
    # CPU 密集型任务
    'Modules.quant.tasks.process_*': {
        'queue': 'cpu_intensive',
        'routing_key': 'cpu',
    },

    # I/O 密集型任务
    'Modules.admin.tasks.send_*': {
        'queue': 'io_intensive',
        'routing_key': 'io',
    },

    # 批量任务
    'Modules.common.tasks.batch_*': {
        'queue': 'batch',
        'routing_key': 'batch',
    },

    # 定时任务
    'Modules.common.tasks.scheduled_*': {
        'queue': 'scheduled',
        'routing_key': 'scheduled',
    },
}
```

### 2. Worker 并发优化

```bash
# CPU 密集型任务 - 低并发
celery -A config.celery_config worker -Q cpu_intensive -c 2

# I/O 密集型任务 - 高并发
celery -A config.celery_config worker -Q io_intensive -c 10

# 批量任务 - 中等并发
celery -A config.celery_config worker -Q batch -c 4

# 定时任务 - 低并发
celery -A config.celery_config worker -Q scheduled -c 1
```

### 3. 预取优化

```python
# I/O 密集型任务 - 增加预取
celery_app.conf.worker_prefetch_multiplier = 8

# CPU 密集型任务 - 减少预取
celery_app.conf.worker_prefetch_multiplier = 1

# 混合任务 - 中等预取
celery_app.conf.worker_prefetch_multiplier = 4
```

### 4. 自动扩展

```bash
# 自动扩展 worker
celery -A config.celery_config worker \
    --autoscale=10,2 \
    --queues=default

# 参数说明：
# --autoscale=10,2
#   10: 最大 worker 数
#   2: 最小 worker 数
```

## 队列管理

### 清空队列

```python
from celery import current_app

def clear_queue(queue_name):
    """清空指定队列"""
    with current_app.pool.acquire(block=True) as conn:
        conn.default_channel.queue_purge(queue_name)
    print(f"队列 {queue_name} 已清空")

# 清空所有队列
def clear_all_queues():
    """清空所有队列"""
    queues = ['default', 'admin', 'quant']
    for queue in queues:
        clear_queue(queue)
```

### 查询队列状态

```python
def get_queue_status(queue_name):
    """获取队列状态"""
    import redis

    r = redis.Redis(host='localhost', port=6379, db=0)
    queue_key = f'celery:{queue_name}'

    # 队列长度
    length = r.llen(queue_key)

    # 队列详情
    return {
        'queue': queue_name,
        'length': length,
        'status': 'busy' if length > 100 else 'normal'
    }
```

### 任务重试管理

```python
from celery.result import AsyncResult

def retry_failed_tasks(queue_name):
    """重试失败的任务"""
    # 获取失败的任务列表
    # 这里需要根据实际存储方式实现
    failed_tasks = get_failed_tasks(queue_name)

    for task_id in failed_tasks:
        task = AsyncResult(task_id)
        if task.failed():
            # 重新执行任务
            task.retry()
            print(f"任务 {task_id} 已重新提交")
```

### 任务优先级调整

```python
def adjust_task_priority(task_id, new_priority):
    """调整任务优先级"""
    # 撤销原任务
    from celery import current_app
    current_app.control.revoke(task_id, terminate=False)

    # 重新提交任务
    # 这里需要保存原任务参数，然后重新提交
    # 具体实现取决于任务类型
    print(f"任务 {task_id} 优先级已调整为 {new_priority}")
```

## 队列安全

### 访问控制

```python
# RabbitMQ 访问控制
celery_app.conf.broker_url = 'amqp://user:password@localhost:5672//'

# Redis 访问控制
celery_app.conf.broker_url = 'redis://:password@localhost:6379/0'
```

### 队列加密

```python
# 使用 SSL 连接 RabbitMQ
celery_app.conf.broker_url = 'amqp://user:password@localhost:5671//'
celery_app.conf.broker_use_ssl = {
    'ssl_version': 'PROTOCOL_TLSv1_2',
    'certfile': '/path/to/cert.pem',
    'keyfile': '/path/to/key.pem',
    'ca_certs': '/path/to/ca.pem',
}
```

### 任务签名

```python
from celery.security import disable_untrusted_serializers

# 禁用不信任的序列化器
celery_app.conf.task_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_serializer = 'json'

# 启用任务签名
celery_app.conf.task_send_sent_event = True
```

## 队列故障处理

### Worker 崩溃恢复

```bash
# 使用 systemd 管理 worker
# /etc/systemd/system/celery.service

[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=celery
Group=celery
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A config.celery_config worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=default \
    --pidfile=/var/run/celery/worker.pid
ExecStop=/path/to/venv/bin/celery -A config.celery_config control shutdown
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 队列积压处理

```python
def handle_queue_backlog(queue_name, max_workers=10):
    """处理队列积压"""
    import redis

    r = redis.Redis(host='localhost', port=6379, db=0)
    queue_key = f'celery:{queue_name}'
    length = r.llen(queue_key)

    if length > 1000:
        print(f"队列 {queue_name} 积压严重: {length} 个任务")

        # 启动额外的 worker
        for i in range(max_workers):
            celery_cmd = f"""
            celery -A config.celery_config worker \
                -Q {queue_name} \
                -n temp_worker{i}@%h \
                -c 4 \
                --max-tasks-per-child=100
            """
            # 执行命令启动临时 worker
            print(f"启动临时 worker {i}")
    else:
        print(f"队列 {queue_name} 状态正常: {length} 个任务")
```

### 死信队列

```python
# 配置死信队列
celery_app.conf.task_queues = [
    Queue('default', routing_key='default'),
    Queue('dead_letter', routing_key='dead_letter'),
]

# 任务路由到死信队列
celery_app.conf.task_routes = {
    'Modules.common.tasks.failed_*': {
        'queue': 'dead_letter',
        'routing_key': 'dead_letter',
    },
}
```

## 最佳实践

### 1. 队列命名规范

```python
# 使用有意义的队列名称
queues = [
    'admin_email',        # 管理员邮件队列
    'quant_data',         # 量化数据队列
    'user_notification',  # 用户通知队列
    'report_generation',  # 报表生成队列
    'data_cleanup',       # 数据清理队列
]
```

### 2. 监控告警

```python
# 设置队列监控告警
def queue_alert(queue_name, threshold=1000):
    """队列告警"""
    status = get_queue_status(queue_name)

    if status['length'] > threshold:
        # 发送告警
        send_alert(
            f"队列 {queue_name} 积压严重: {status['length']} 个任务",
            level='warning'
        )
```

### 3. 定期清理

```python
from celery.schedules import crontab

# 定期清理过期任务
celery_app.conf.beat_schedule = {
    'cleanup-expired-tasks': {
        'task': 'Modules.common.tasks.cleanup_expired_tasks',
        'schedule': crontab(hour=3, minute=0),  # 每天凌晨 3 点
    },
}
```

## 常见问题

### 1. 队列积压

**问题**：队列任务积压严重

**解决方案**：

- 增加并发数
- 启动临时 worker
- 优化任务逻辑
- 使用批量处理

### 2. Worker 饥饿

**问题**：某些队列任务无法及时处理

**解决方案**：

- 使用专用 worker
- 调整队列优先级
- 使用公平调度

### 3. 内存泄漏

**问题**：worker 内存持续增长

**解决方案**：

- 设置 `--max-tasks-per-child`
- 设置 `--max-memory-per-child`
- 检查任务代码

## 相关文档

- [Celery 基础指南](./celery-guide.md)
- [任务开发指南](./task-development.md)
- [监控指南](./monitoring.md)
- [部署指南](../deployment/deployment-guide.md)
