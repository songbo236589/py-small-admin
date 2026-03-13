# Celery 异步任务

本文档介绍项目中 Celery 异步任务的配置、使用和监控。

## 目录

- [概述](#概述)
- [架构说明](#架构说明)
- [环境配置](#环境配置)
- [Celery 配置](#celery-配置)
- [启动服务](#启动服务)
- [任务定义](#任务定义)
- [定时任务](#定时任务)
- [任务队列](#任务队列)
- [Flower 监控](#flower-监控)
- [常见问题](#常见问题)

## 概述

Celery 是一个强大的分布式任务队列，用于处理异步任务和定时任务。本项目使用 Celery 来处理：

- **异步任务**：如文章发布、话题抓取、邮件发送等耗时操作
- **定时任务**：如数据同步、日志清理、统计报表等周期性任务

### 核心组件

```mermaid
graph TB
    A[FastAPI 应用] -->|发送任务| B[RabbitMQ/Redis]
    B -->|分发任务| C[Celery Worker]
    C -->|执行任务| D[任务函数]
    D -->|返回结果| E[Redis Backend]
    F[Celery Beat] -->|调度定时任务| B
    G[Flower] -->|监控| C
    G -->|监控| E
```

### 主要优势

- **异步执行**：不阻塞主线程，提高系统响应速度
- **任务重试**：自动重试失败任务，提高任务成功率
- **任务调度**：支持定时任务和周期性任务
- **任务监控**：通过 Flower 实时监控任务状态
- **任务队列**：支持多队列，实现任务优先级和隔离

## 架构说明

### 服务架构

本项目采用以下架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI 应用                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  业务逻辑层                                          │  │
│  │  - 文章发布 API                                       │  │
│  │  - 话题抓取 API                                       │  │
│  │  - 邮件发送 API                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Celery 集成层                                        │  │
│  │  - CeleryService                                     │  │
│  │  - 任务发送                                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    消息队列（Broker）                         │
│                    RabbitMQ / Redis                          │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Celery Worker  │ │  Celery Worker  │ │  Celery Worker  │
│  - 文章发布     │ │  - 话题抓取     │ │  - 邮件发送     │
│  - 数据同步     │ │  - 图片处理     │ │  - 日志清理     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    结果存储（Backend）                        │
│                        Redis                                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flower 监控                              │
│              http://localhost:5555                           │
└─────────────────────────────────────────────────────────────┘
```

### 模块说明

| 模块          | 路径                                       | 说明                           |
| ------------- | ------------------------------------------ | ------------------------------ |
| Celery 服务   | `server/Modules/common/libs/celery/`       | Celery 应用实例管理和配置      |
| Celery 配置   | `server/config/celery.py`                  | Celery 配置类（基于 Pydantic） |
| Celery 应用   | `server/Modules/common/libs/celery/app.py` | Celery 应用入口                |
| 任务模块      | `server/Modules/*/tasks/`                  | 各模块的任务定义               |
| Celery 管理器 | `server/commands/celery_manager.py`        | Celery 服务管理命令            |

## 环境配置

### 依赖安装

```bash
# 安装 Celery 核心依赖
pip install celery

# 安装 Redis 支持（如果使用 Redis）
pip install redis

# 安装 RabbitMQ 支持（如果使用 RabbitMQ）
pip install kombu

# 安装 Flower 监控工具
pip install flower

# 安装 gevent（可选，用于高并发 I/O 任务）
pip install gevent
```

### Broker 选择

#### RabbitMQ（推荐生产环境）

```bash
# Docker 启动 RabbitMQ
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management

# 访问管理界面
# http://localhost:15672
# 默认账号: guest / guest
```

**环境变量配置**：

```bash
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
```

#### Redis（推荐开发环境）

```bash
# Docker 启动 Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine

# 或使用本地 Redis
redis-server
```

**环境变量配置**：

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# ========== Broker 配置 ==========
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_BROKER_CONNECTION_RETRY=true
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP=true

# ========== Result Backend 配置 ==========
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_RESULT_EXPIRES=3600
CELERY_RESULT_EXTENDED=true

# ========== Worker 配置 ==========
CELERY_WORKER__CONCURRENCY=4
CELERY_WORKER__PREFETCH_MULTIPLIER=4
CELERY_WORKER__MAX_TASKS_PER_CHILD=1000

# ========== 任务配置 ==========
CELERY_TASK_DEFAULT_QUEUE=default
CELERY_TASK_DEFAULT_TIME_LIMIT=3600
CELERY_TASK_DEFAULT_SOFT_TIME_LIMIT=3000
CELERY_TASK_DEFAULT_MAX_RETRIES=3
CELERY_TASK_DEFAULT_RETRY_DELAY=60
CELERY_TASK_TRACK_STARTED=true
CELERY_TASK_ACKS_LATE=true

# ========== 序列化配置 ==========
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=json

# ========== 时区配置 ==========
CELERY_TIMEZONE=Asia/Shanghai
CELERY_ENABLE_UTC=true

# ========== 任务模块配置 ==========
CELERY_INCLUDE_JSON='["Modules.admin.tasks.default_tasks"]'

# ========== 定时任务配置 ==========
CELERY_BEAT_SCHEDULE_JSON='{
  "task_print_hello": {
    "task": "Modules.admin.tasks.default_tasks.print_hello_task",
    "schedule": 60.0
  }
}'

# ========== Flower 监控配置 ==========
CELERY_FLOWER__PORT=5555
CELERY_FLOWER__HOST=0.0.0.0
```

## Celery 配置

### 配置类说明

项目使用 `CeleryConfig` 类（位于 `server/config/celery.py`）来管理 Celery 配置。该类基于 Pydantic Settings，支持从环境变量读取配置。

### 主要配置项

#### Broker 配置

| 配置项                               | 默认值                                | 说明                   |
| ------------------------------------ | ------------------------------------- | ---------------------- |
| `broker_url`                         | `amqp://guest:guest@localhost:5672//` | 消息代理 URL           |
| `broker_connection_retry`            | `true`                                | 连接失败时是否自动重试 |
| `broker_connection_retry_on_startup` | `true`                                | 启动时连接失败是否重试 |
| `broker_connection_max_retries`      | `5`                                   | 最大重试次数           |
| `broker_connection_retry_delay`      | `5`                                   | 重试延迟时间（秒）     |
| `broker_use_ssl`                     | `false`                               | 是否使用 SSL 连接      |

#### Result Backend 配置

| 配置项            | 默认值                     | 说明                   |
| ----------------- | -------------------------- | ---------------------- |
| `result_backend`  | `redis://localhost:6379/2` | 任务结果存储 URL       |
| `result_expires`  | `3600`                     | 任务结果过期时间（秒） |
| `result_extended` | `true`                     | 是否扩展结果格式       |

#### Worker 配置

| 配置项                       | 默认值    | 说明                         |
| ---------------------------- | --------- | ---------------------------- |
| `worker_pool`                | `threads` | Worker 执行池类型            |
| `worker_concurrency`         | `4`       | Worker 并发数                |
| `worker_prefetch_multiplier` | `4`       | 预取倍数                     |
| `worker_max_tasks_per_child` | `1000`    | 每个 Worker 处理的最大任务数 |
| `worker_disable_rate_limits` | `false`   | 是否禁用速率限制             |

#### 任务配置

| 配置项                         | 默认值    | 说明                 |
| ------------------------------ | --------- | -------------------- |
| `task_default_queue`           | `default` | 默认队列名称         |
| `task_default_rate_limit`      | `""`      | 默认速率限制         |
| `task_default_time_limit`      | `3600`    | 默认硬超时时间（秒） |
| `task_default_soft_time_limit` | `3000`    | 默认软超时时间（秒） |
| `task_default_max_retries`     | `3`       | 默认最大重试次数     |
| `task_default_retry_delay`     | `60`      | 默认重试延迟（秒）   |
| `task_track_started`           | `true`    | 是否跟踪任务开始时间 |
| `task_acks_late`               | `true`    | 是否延迟确认         |

#### 时区配置

| 配置项       | 默认值          | 说明              |
| ------------ | --------------- | ----------------- |
| `timezone`   | `Asia/Shanghai` | 时区设置          |
| `enable_utc` | `true`          | 是否使用 UTC 时间 |

#### Flower 配置

| 配置项              | 默认值    | 说明                            |
| ------------------- | --------- | ------------------------------- |
| `flower.port`       | `5555`    | 监控端口                        |
| `flower.host`       | `0.0.0.0` | 监听地址                        |
| `flower.basic_auth` | `""`      | 基本认证（格式: user:password） |
| `flower.broker_api` | `""`      | RabbitMQ 管理接口 URL           |

### 配置示例

#### 开发环境配置

```bash
# 使用 Redis 作为 Broker（简单快速）
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Worker 使用线程池（适合 Windows）
CELERY_WORKER__POOL=threads
CELERY_WORKER__CONCURRENCY=2

# 任务重试次数较少
CELERY_TASK_DEFAULT_MAX_RETRIES=1
CELERY_TASK_DEFAULT_RETRY_DELAY=30
```

#### 生产环境配置

```bash
# 使用 RabbitMQ 作为 Broker（可靠性高）
CELERY_BROKER_URL=amqp://user:password@rabbitmq.example.com:5672//
CELERY_BROKER_USE_SSL=true

# 使用 Redis 作为 Backend（性能好）
CELERY_RESULT_BACKEND=redis://redis.example.com:6379/2

# Worker 使用进程池（充分利用多核）
CELERY_WORKER__POOL=prefork
CELERY_WORKER__CONCURRENCY=8

# 任务重试次数较多
CELERY_TASK_DEFAULT_MAX_RETRIES=5
CELERY_TASK_DEFAULT_RETRY_DELAY=60

# 启用任务压缩
CELERY_TASK_COMPRESSION=gzip
CELERY_TASK_COMPRESSION_THRESHOLD=1024
```

## 启动服务

### 启动 Worker

```bash
# 基础启动
celery -A Modules.common.libs.celery.app worker --loglevel=info

# 指定并发数
celery -A Modules.common.libs.celery.app worker --loglevel=info --concurrency=4

# 指定队列
celery -A Modules.common.libs.celery.app worker --loglevel=info -Q high_priority,default

# 指定 Worker 名称
celery -A Modules.common.libs.celery.app worker --loglevel=info -n worker1@%h

# 使用项目命令
python -m commands.celery_manager worker start
```

### 启动 Beat（定时任务）

```bash
# 基础启动
celery -A Modules.common.libs.celery.app beat --loglevel=info

# 指定调度器文件
celery -A Modules.common.libs.celery.app beat --loglevel=info --schedule=celerybeat-schedule

# 使用项目命令
python -m commands.celery_manager beat start
```

### 启动 Flower（监控）

```bash
# 基础启动
celery -A Modules.common.libs.celery.app flower

# 指定端口
celery -A Modules.common.libs.celery.app flower --port=5555

# 指定认证
celery -A Modules.common.libs.celery.app flower --basic_auth=admin:password

# 指定 Broker API（RabbitMQ 管理接口）
celery -A Modules.common.libs.celery.app flower --broker_api=http://localhost:15672/api/

# 使用项目命令
python -m commands.celery_manager flower start
```

### 同时启动 Worker 和 Beat

```bash
# 使用 -B 参数同时启动 Beat
celery -A Modules.common.libs.celery.app worker --beat --loglevel=info
```

### Windows 系统注意事项

::: warning
在 Windows 系统上，Celery Beat 不支持 `-B` 参数（同时启动 Worker 和 Beat）。需要分别启动：
:::

```bash
# 终端 1：启动 Worker
celery -A Modules.common.libs.celery.app worker --loglevel=info --pool=solo

# 终端 2：启动 Beat
celery -A Modules.common.libs.celery.app beat --loglevel=info
```

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY . .

# 启动命令
CMD ["celery", "-A", "Modules.common.libs.celery.app", "worker", "--loglevel=info"]
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery-worker:
    build: .
    command: celery -A Modules.common.libs.celery.app worker --loglevel=info
    depends_on:
      - rabbitmq
      - redis
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379/2

  celery-beat:
    build: .
    command: celery -A Modules.common.libs.celery.app beat --loglevel=info
    depends_on:
      - rabbitmq
      - redis
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379/2

  flower:
    build: .
    command: celery -A Modules.common.libs.celery.app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - rabbitmq
      - redis
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
```

## 任务定义

### 基础任务定义

```python
# server/Modules/admin/tasks/default_tasks.py

from Modules.common.libs.celery.celery_service import get_celery_service

# 获取 Celery 服务实例
celery_service = get_celery_service()

# 定义任务
@celery_service.app.task
def print_hello_task():
    """打印 Hello 世界的任务"""
    print("Hello, World!")
    return "Hello, World!"
```

### 带参数的任务

```python
@celery_service.app.task
def add_task(x, y):
    """加法任务"""
    result = x + y
    print(f"{x} + {y} = {result}")
    return result
```

### 任务配置选项

```python
@celery_service.app.task(
    name="tasks.send_email",  # 任务名称（可选，默认使用函数名）
    bind=True,  # 绑定任务实例，可以访问 self
    max_retries=3,  # 最大重试次数
    default_retry_delay=60,  # 默认重试延迟（秒）
    autoretry_for=(Exception,),  # 自动重试的异常类型
    retry_backoff=True,  # 启用指数退避
    retry_backoff_max=600,  # 最大退避时间（秒）
    retry_jitter=True,  # 添加随机抖动
    time_limit=3600,  # 硬超时时间（秒）
    soft_time_limit=3000,  # 软超时时间（秒）
    rate_limit="100/m",  # 速率限制
)
def send_email_task(to, subject, body):
    """发送邮件任务"""
    # 发送邮件逻辑
    print(f"发送邮件到 {to}: {subject}")
    return f"邮件已发送到 {to}"
```

### 任务重试

```python
from celery.exceptions import Retry

@celery_service.app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def fetch_data_task(self, url):
    """抓取数据任务（带重试）"""
    try:
        # 抓取数据逻辑
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        # 重试逻辑
        raise self.retry(exc=exc, countdown=60)
```

### 任务进度报告

```python
@celery_service.app.task(bind=True)
def long_running_task(self, total_steps):
    """长时间运行的任务（带进度报告）"""
    for i in range(total_steps):
        # 执行步骤
        time.sleep(1)

        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_steps,
                'status': f'正在处理第 {i + 1} 步'
            }
        )

    return {'status': '完成', 'total': total_steps}
```

### 任务链（Chain）

```python
from celery import chain

# 定义任务链
task_chain = chain(
    add_task.s(2, 2),  # 2 + 2 = 4
    add_task.s(4),     # 4 + 4 = 8
    add_task.s(8)      # 8 + 8 = 16
)

# 执行任务链
result = task_chain.delay()
```

### 任务组（Group）

```python
from celery import group

# 定义任务组
task_group = group(
    add_task.s(1, 1),
    add_task.s(2, 2),
    add_task.s(3, 3),
)

# 执行任务组
result = task_group.delay()

# 等待所有任务完成
results = result.get()
```

### 任务回调

```python
@celery_service.app.task
def on_success_task(result):
    """任务成功回调"""
    print(f"任务成功，结果: {result}")

@celery_service.app.task
def on_failure_task(request, exc, traceback):
    """任务失败回调"""
    print(f"任务失败: {exc}")

# 使用回调
result = add_task.apply_async(
    args=(2, 2),
    link=on_success_task.s(),  # 成功回调
    link_error=on_failure_task.s()  # 失败回调
)
```

### 调用任务

#### 在 FastAPI 中调用

```python
from fastapi import FastAPI
from Modules.common.libs.celery.celery_service import get_celery_service

app = FastAPI()
celery_service = get_celery_service()

@app.post("/api/tasks/add")
async def create_add_task(x: int, y: int):
    """创建加法任务"""
    # 异步调用任务
    result = add_task.delay(x, y)

    return {
        "task_id": result.id,
        "status": result.status
    }

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    result = celery_service.app.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

#### 同步调用（仅用于测试）

```python
# 同步调用（不推荐用于生产环境）
result = add_task.apply(args=(2, 2))
print(result.get())
```

#### 异步调用

```python
# 异步调用
result = add_task.delay(2, 2)

# 等待结果
result.wait()
print(result.get())

# 检查状态
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE, RETRY

# 获取结果
if result.ready():
    print(result.get())
```

## 定时任务

### 配置定时任务

在 `.env` 文件中配置定时任务：

```bash
CELERY_BEAT_SCHEDULE_JSON='{
  "task_print_hello": {
    "task": "Modules.admin.tasks.default_tasks.print_hello_task",
    "schedule": 60.0
  },
  "task_cleanup_data": {
    "task": "Modules.tasks.data_tasks.cleanup_data",
    "schedule": "crontab(hour=2, minute=0)"
  },
  "task_sync_stock": {
    "task": "Modules.quant.tasks.stock_tasks.sync_stock_list",
    "schedule": "crontab(hour=9, minute=30, day_of_week=1-5)"
  }
}'
```

### 定时任务格式

#### 间隔调度（秒）

```json
{
  "task_name": {
    "task": "module.path.to.task",
    "schedule": 60.0
  }
}
```

#### Crontab 调度

```json
{
  "task_name": {
    "task": "module.path.to.task",
    "schedule": "crontab(hour=2, minute=0)"
  }
}
```

**Crontab 参数**：

| 参数            | 说明                | 示例                           |
| --------------- | ------------------- | ------------------------------ |
| `minute`        | 分钟（0-59）        | `0, 30`（每小时的 0 和 30 分） |
| `hour`          | 小时（0-23）        | `2`（凌晨 2 点）               |
| `day_of_month`  | 日期（1-31）        | `1`（每月 1 号）               |
| `month_of_year` | 月份（1-12）        | `1`（1 月份）                  |
| `day_of_week`   | 星期（0-6，0=周日） | `1-5`（周一到周五）            |

**Crontab 示例**：

```python
# 每天凌晨 2 点执行
crontab(hour=2, minute=0)

# 每周一到周五的 9:30 执行
crontab(hour=9, minute=30, day_of_week=1-5)

# 每小时的 0 和 30 分执行
crontab(minute="0,30")

# 每 5 分钟执行一次
crontab(minute="*/5")

# 每月 1 号的凌晨 2 点执行
crontab(hour=2, minute=0, day_of_month=1)

# 每季度的第一天执行
crontab(hour=2, minute=0, day_of_month=1, month_of_year="1,4,7,10")
```

### 定时任务示例

```python
# server/Modules/admin/tasks/default_tasks.py

@celery_service.app.task
def print_hello_task():
    """每分钟打印 Hello"""
    print("Hello, World!")
    return "Hello, World!"

@celery_service.app.task
def cleanup_data_task():
    """每天凌晨 2 点清理数据"""
    print("清理数据...")
    # 清理逻辑
    return "数据清理完成"

@celery_service.app.task
def sync_stock_list_task():
    """每个工作日的 9:30 同步股票列表"""
    print("同步股票列表...")
    # 同步逻辑
    return "股票列表同步完成"
```

### 定时任务配置示例

```bash
CELERY_BEAT_SCHEDULE_JSON='{
  "task_print_hello": {
    "task": "Modules.admin.tasks.default_tasks.print_hello_task",
    "schedule": 60.0,
    "options": {
      "expires": 3600
    }
  },
  "task_cleanup_data": {
    "task": "Modules.admin.tasks.default_tasks.cleanup_data_task",
    "schedule": "crontab(hour=2, minute=0)",
    "options": {
      "expires": 7200
    }
  },
  "task_sync_stock": {
    "task": "Modules.quant.tasks.stock_tasks.sync_stock_list_task",
    "schedule": "crontab(hour=9, minute=30, day_of_week=1-5)",
    "options": {
      "expires": 3600
    }
  }
}'
```

### 定时任务高级选项

```json
{
  "task_name": {
    "task": "module.path.to.task",
    "schedule": 60.0,
    "args": [], // 任务参数
    "kwargs": {}, // 任务关键字参数
    "options": {
      "expires": 3600, // 任务过期时间（秒）
      "queue": "high_priority", // 指定队列
      "exchange": "high_priority", // 指定交换机
      "routing_key": "high_priority", // 指定路由键
      "priority": 9 // 任务优先级（0-9，9 最高）
    }
  }
}
```

## 任务队列

### 配置多队列

在 `.env` 文件中配置多个队列：

```bash
CELERY_TASK_QUEUES_JSON='[
  {"name": "default", "exchange": "default", "routing_key": "default"},
  {"name": "high_priority", "exchange": "high_priority", "routing_key": "high_priority"},
  {"name": "low_priority", "exchange": "low_priority", "routing_key": "low_priority"}
]'
```

### 任务路由配置

```bash
CELERY_TASK_ROUTES='{
  "Modules.content.tasks.publish_tasks.*": {
    "queue": "high_priority",
    "routing_key": "high_priority"
  },
  "Modules.quant.tasks.*": {
    "queue": "default",
    "routing_key": "default"
  },
  "Modules.admin.tasks.*": {
    "queue": "low_priority",
    "routing_key": "low_priority"
  }
}'
```

### 启动指定队列的 Worker

```bash
# 只处理 high_priority 队列
celery -A Modules.common.libs.celery.app worker -Q high_priority --loglevel=info

# 处理多个队列（按优先级）
celery -A Modules.common.libs.celery.app worker -Q high_priority,default,low_priority --loglevel=info

# 处理所有队列
celery -A Modules.common.libs.celery.app worker --loglevel=info
```

### 队列使用场景

| 队列            | 用途         | 任务类型           |
| --------------- | ------------ | ------------------ |
| `high_priority` | 高优先级任务 | 文章发布、紧急通知 |
| `default`       | 默认任务     | 数据同步、常规处理 |
| `low_priority`  | 低优先级任务 | 日志清理、数据归档 |

## Flower 监控

### 启动 Flower

```bash
# 基础启动
celery -A Modules.common.libs.celery.app flower

# 指定端口
celery -A Modules.common.libs.celery.app flower --port=5555

# 指定认证
celery -A Modules.common.libs.celery.app flower --basic_auth=admin:password

# 指定 Broker API
celery -A Modules.common.libs.celery.app flower --broker_api=http://localhost:15672/api/
```

### 访问 Flower

启动后访问：http://localhost:5555

### Flower 功能

#### 1. Dashboard（仪表盘）

- 任务统计：成功、失败、重试、等待
- Worker 统计：在线 Worker 数、任务吞吐量
- 队列统计：队列长度、任务处理速度

#### 2. Tasks（任务）

- 查看所有任务
- 任务详情：参数、结果、执行时间
- 任务状态：PENDING、STARTED、SUCCESS、FAILURE、RETRY
- 任务过滤：按状态、时间、Worker 过滤

#### 3. Workers（Worker）

- 查看 Worker 列表
- Worker 详情：并发数、队列、任务统计
- Worker 操作：关闭、重启

#### 4. Broker（消息队列）

- 查看队列信息
- 查看消息数量
- 查看消息详情

#### 5. Monitor（监控）

- 实时监控任务执行
- 查看任务日志
- 查看任务追踪

### Flower API

Flower 提供 RESTful API：

```bash
# 获取任务列表
curl http://localhost:5555/api/tasks

# 获取 Worker 列表
curl http://localhost:5555/api/workers

# 获取队列信息
curl http://localhost:5555/api/queues

# 获取任务详情
curl http://localhost:5555/api/tasks/task-id

# 获取统计信息
curl http://localhost:5555/api/stats
```

## 常见问题

### 1. Worker 启动失败

**问题**：启动 Worker 时报错 "Connection refused"

**原因**：Broker 服务未启动或连接配置错误

**解决方案**：

```bash
# 检查 RabbitMQ 是否启动
docker ps | grep rabbitmq

# 检查 Redis 是否启动
docker ps | grep redis

# 检查连接配置
echo $CELERY_BROKER_URL
echo $CELERY_RESULT_BACKEND
```

### 2. 任务不执行

**问题**：任务发送成功，但一直处于 PENDING 状态

**原因**：Worker 未订阅任务队列

**解决方案**：

```bash
# 检查 Worker 是否订阅了正确的队列
celery -A Modules.common.libs.celery.app inspect active_queues

# 确保任务路由配置正确
celery -A Modules.common.libs.celery.app inspect registered
```

### 3. 任务重试失败

**问题**：任务一直重试，无法成功

**原因**：任务逻辑有问题或依赖服务不可用

**解决方案**：

```python
# 检查任务日志
celery -A Modules.common.libs.celery.app inspect active

# 查看任务详情
celery -A Modules.common.libs.celery.app inspect stats

# 修改任务重试配置
@celery_service.app.task(
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,)
)
def my_task():
    pass
```

### 4. 内存泄漏

**问题**：Worker 运行一段时间后内存占用持续增长

**原因**：任务处理过程中存在内存泄漏

**解决方案**：

```bash
# 设置 max_tasks_per_child，定期重启 Worker
CELERY_WORKER__MAX_TASKS_PER_CHILD=1000

# 或在代码中设置
@celery_service.app.task
def my_task():
    # 确保资源正确释放
    pass
```

### 5. 定时任务不执行

**问题**：Beat 启动后，定时任务不执行

**原因**：定时任务配置错误或时区问题

**解决方案**：

```bash
# 检查定时任务配置
celery -A Modules.common.libs.celery.app inspect beat

# 检查时区配置
echo $CELERY_TIMEZONE

# 查看日志
celery -A Modules.common.libs.celery.app beat --loglevel=debug
```

### 6. Windows 系统问题

**问题**：Windows 上启动 Worker 报错

**原因**：Windows 不支持 prefork 池

**解决方案**：

```bash
# 使用线程池或 solo 池
celery -A Modules.common.libs.celery.app worker --pool=threads --loglevel=info

# 或在配置中设置
CELERY_WORKER__POOL=threads
```

### 7. Flower 无法访问

**问题**：Flower 启动后无法访问

**原因**：端口被占用或防火墙阻止

**解决方案**：

```bash
# 检查端口是否被占用
netstat -ano | findstr :5555

# 使用其他端口
celery -A Modules.common.libs.celery.app flower --port=5556

# 检查防火墙设置
```

### 8. 任务结果丢失

**问题**：任务执行成功，但结果无法获取

**原因**：Result Backend 配置错误或结果过期

**解决方案**：

```bash
# 检查 Result Backend 配置
echo $CELERY_RESULT_BACKEND

# 延长结果过期时间
CELERY_RESULT_EXPIRES=86400

# 检查 Redis 是否正常
redis-cli ping
```

### 9. 任务执行超时

**问题**：任务执行时间过长，被强制终止

**原因**：任务超时配置过短

**解决方案**：

```python
# 增加任务超时时间
@celery_service.app.task(
    time_limit=7200,  # 2 小时
    soft_time_limit=6000  # 1 小时 40 分钟
)
def long_running_task():
    pass
```

### 10. 任务重复执行

**问题**：任务被重复执行多次

**原因**：`task_acks_late=True` 且 Worker 崩溃

**解决方案**：

```python
# 确保任务幂等性
@celery_service.app.task
def my_task(idempotent_id):
    # 检查是否已执行
    if is_already_executed(idempotent_id):
        return "已执行"

    # 执行任务
    result = do_work()

    # 标记为已执行
    mark_as_executed(idempotent_id)

    return result
```

## 参考资源

- [Celery 官方文档](https://docs.celeryq.dev/)
- [Flower 官方文档](https://flower.readthedocs.io/)
- [Celery 最佳实践](https://docs.celeryq.dev/en/stable/userguide/optimizing.html)
- [Celery 故障排查](https://docs.celeryq.dev/en/stable/userguide/task.html#task-results)
