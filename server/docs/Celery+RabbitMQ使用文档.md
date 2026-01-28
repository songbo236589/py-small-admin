# Celery + RabbitMQ 使用文档

## 目录

- [一、概述](#一概述)
- [二、技术栈介绍](#二技术栈介绍)
- [三、架构设计](#三架构设计)
- [四、环境准备](#四环境准备)
- [五、依赖安装](#五依赖安装)
- [六、配置说明](#六配置说明)
- [七、目录结构](#七目录结构)
- [八、核心概念](#八核心概念)
- [九、使用场景](#九使用场景)
- [十、最佳实践](#十最佳实践)
- [十一、监控和管理](#十一监控和管理)
- [十二、部署方案](#十二部署方案)
- [十三、常见问题](#十三常见问题)
- [十四、性能优化](#十四性能优化)
- [十五、安全建议](#十五安全建议)

---

## 一、概述

### 1.1 什么是 Celery

Celery 是一个强大的分布式任务队列，专注于实时操作，同时也支持调度。它使用消息队列（如 RabbitMQ、Redis）在分布式系统中的工作者之间传递任务。

### 1.2 什么是 RabbitMQ

RabbitMQ 是一个开源的消息代理软件，实现了高级消息队列协议（AMQP）。它提供可靠的消息传递、灵活的路由和多种消息模式。

### 1.3 为什么要使用 Celery + RabbitMQ

**优势：**

- ✅ **高可靠性**：消息持久化，任务不会丢失
- ✅ **分布式处理**：支持多台机器并行处理任务
- ✅ **定时任务**：内置 Celery Beat 支持复杂的定时任务
- ✅ **任务链**：支持任务链（Chain）和组（Group）操作
- ✅ **监控完善**：提供 Flower 等监控工具
- ✅ **灵活配置**：支持多种消息代理和结果后端
- ✅ **重试机制**：任务失败自动重试
- ✅ **优先级队列**：支持任务优先级

**适用场景：**

- 发送邮件、短信等耗时操作
- 数据报表生成
- 定时数据同步
- 图片/视频处理
- 批量数据处理
- 第三方 API 调用
- 定时清理任务

---

## 二、技术栈介绍

### 2.1 Celery 核心组件


| 组件               | 说明                                        |
| ------------------ | ------------------------------------------- |
| **Producer**       | 任务生产者，负责发送任务到消息队列          |
| **Broker**         | 消息代理，负责存储和传递消息（RabbitMQ）    |
| **Worker**         | 任务工作者，负责从队列中获取并执行任务      |
| **Beat**           | 定时任务调度器，负责按计划发送定时任务      |
| **Result Backend** | 结果存储后端，用于存储任务执行结果（Redis） |
| **Task**           | 任务单元，定义要执行的具体操作              |

### 2.2 RabbitMQ 核心概念


| 概念             | 说明                             |
| ---------------- | -------------------------------- |
| **Exchange**     | 交换机，负责接收消息并路由到队列 |
| **Queue**        | 队列，存储消息直到被消费者消费   |
| **Binding**      | 绑定，交换机和队列之间的关联关系 |
| **Routing Key**  | 路由键，决定消息路由到哪个队列   |
| **Virtual Host** | 虚拟主机，逻辑隔离不同的消息环境 |

### 2.3 消息模式

1. **Direct Exchange**：根据路由键精确匹配
2. **Topic Exchange**：根据路由键模式匹配
3. **Fanout Exchange**：广播到所有绑定的队列
4. **Headers Exchange**：根据消息头属性匹配

---

## 三、架构设计

### 3.1 整体架构

```
┌─────────────┐
│  FastAPI    │  (Web 应用)
│  Producer   │
└──────┬──────┘
       │ 发送任务
       ▼
┌─────────────────────────────────────┐
│         RabbitMQ (Broker)           │
│  ┌─────────────────────────────┐   │
│  │      Exchange              │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │      Queue                  │   │
│  └──────────┬──────────────────┘   │
└─────────────┼───────────────────────┘
              │ 消费任务
              ▼
┌─────────────────────────────────────┐
│      Celery Worker                  │
│  ┌─────────────────────────────┐   │
│  │      Task Executor          │   │
│  └──────────┬──────────────────┘   │
└─────────────┼───────────────────────┘
              │ 存储结果
              ▼
┌─────────────────────────────────────┐
│         Redis (Result Backend)      │
└─────────────────────────────────────┘
```

### 3.2 与现有架构的集成

```
server/
├── config/
│   ├── app.py              # 应用配置
│   ├── database.py         # 数据库配置（含 Redis）
│   └── celery.py           # Celery 配置（新增）
├── Modules/
│   └── common/
│       └── libs/
│           ├── celery/     # Celery 核心库（新增）
│           │   ├── __init__.py
│           │   ├── app.py         # Celery 实例
│           │   ├── config.py      # Celery 配置
│           │   ├── tasks.py       # 基础任务装饰器
│           │   └── beat.py        # 定时任务配置
│           ├── cache/      # Redis 缓存（已存在）
│           └── log/        # 日志系统（已存在）
├── tasks/                  # 任务目录（新增）
│   ├── __init__.py
│   ├── email_tasks.py
│   ├── data_tasks.py
│   └── report_tasks.py
├── worker.py               # Worker 启动脚本（新增）
└── beat.py                 # Beat 启动脚本（新增）
```

### 3.3 数据流

1. **任务提交**：FastAPI 应用通过 Celery 客户端发送任务到 RabbitMQ
2. **任务路由**：RabbitMQ 根据路由规则将任务分发到相应队列
3. **任务执行**：Celery Worker 从队列中获取任务并执行
4. **结果存储**：任务执行结果存储到 Redis
5. **结果查询**：FastAPI 应用可以从 Redis 查询任务结果

---

## 四、环境准备

### 4.1 RabbitMQ 安装

#### Windows

```powershell
# 使用 Chocolatey 安装
choco install rabbitmq

# 或下载安装包
# https://www.rabbitmq.com/download.html
```

#### macOS

```bash
# 使用 Homebrew 安装
brew install rabbitmq

# 启动服务
brew services start rabbitmq
```

#### Linux (Ubuntu/Debian)

```bash
# 安装 Erlang
sudo apt-get install erlang

# 添加 RabbitMQ 仓库
echo "deb https://dl.bintray.com/rabbitmq/debian $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/rabbitmq.list

# 安装 RabbitMQ
sudo apt-get update
sudo apt-get install rabbitmq-server

# 启动服务
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

#### Docker

```bash
# 拉取镜像
docker pull rabbitmq:3-management

# 运行容器
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=admin123 \
  rabbitmq:3-management
```

### 4.2 RabbitMQ 配置

#### 创建虚拟主机和用户

```bash
# 进入容器
docker exec -it rabbitmq /bin/bash

# 启用管理插件
rabbitmq-plugins enable rabbitmq_management

# 创建虚拟主机
rabbitmqctl add_vhost /celery

# 创建用户
rabbitmqctl add_user celery_user celery_password

# 设置用户权限
rabbitmqctl set_permissions -p /celery celery_user ".*" ".*" ".*"

# 设置用户标签
rabbitmqctl set_user_tags celery_user management

# 查看所有虚拟主机
rabbitmqctl list_vhosts

# 查看所有用户
rabbitmqctl list_users

# 查看用户权限
rabbitmqctl list_permissions -p /celery
```

#### 访问管理界面

- URL: `http://localhost:15672`
- 默认用户: `admin`
- 默认密码: `admin123`

#### 验证连接

```bash
# 退出容器
exit

# 测试连接
docker exec -it rabbitmq rabbitmqctl status
```

### 4.3 Redis 配置

项目已配置 Redis，无需额外安装。建议为 Celery 使用独立的数据库：

```
DB 0: 应用缓存
DB 1: Celery 结果存储
DB 2: Celery 锁和状态
```

---

## 五、依赖安装

### 5.1 Python 依赖

在 `requirements.txt` 中添加以下依赖：

```txt
# Celery - 分布式任务队列
celery==5.3.6

# Kombu - Celery 的消息库
kombu==5.3.5

# Billiard - Celery 的多进程库
billiard==4.2.0

# pytz - 时区支持
pytz==2024.1

# tzdata - 时区数据
tzdata==2024.1

# Flower - Celery 监控工具
flower==2.0.1
```

### 5.2 安装命令

```bash
# 安装依赖
pip install -r requirements.txt

# 或单独安装
pip install celery==5.3.6 flower==2.0.1
```

---

## 六、配置说明

### 6.1 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# ========== Celery 配置 ==========
# Celery Broker URL (RabbitMQ)
CELERY_BROKER_URL=amqp://celery_user:celery_password@localhost:5672/celery

# Celery Result Backend URL (Redis)
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1

# Celery 任务序列化方式
CELERY_TASK_SERIALIZER=json

# Celery 结果序列化方式
CELERY_RESULT_SERIALIZER=json

# Celery 接受的序列化方式
CELERY_ACCEPT_CONTENT=json

# Celery 时区设置
CELERY_TIMEZONE=Asia/Shanghai

# Celery 启用时区支持
CELERY_ENABLE_UTC=True

# Celery 任务结果过期时间（秒）
CELERY_RESULT_EXPIRES=86400

# Celery 任务最大重试次数
CELERY_TASK_MAX_RETRIES=3

# Celery 任务重试延迟（秒）
CELERY_TASK_RETRY_DELAY=60

# Celery 任务默认超时时间（秒）
CELERY_TASK_TIME_LIMIT=3600

# Celery Worker 并发数
CELERY_WORKER_CONCURRENCY=4

# Celery Worker 预取任务数
CELERY_WORKER_PREFETCH_MULTIPLIER=4

# Celery 任务路由配置
CELERY_TASK_ROUTES={
    "tasks.email_tasks.*": {"queue": "email"},
    "tasks.data_tasks.*": {"queue": "data"},
    "tasks.report_tasks.*": {"queue": "report"},
}

# ========== Flower 监控配置 ==========
# Flower 监控端口
FLOWER_PORT=5555

# Flower 访问地址
FLOWER_URL_PREFIX=flower

# Flower 基础认证
FLOWER_BASIC_AUTH=admin:admin123
```

### 6.2 Celery 配置类

创建 `config/celery.py` 配置文件：

```python
"""
Celery 配置类
基于 Pydantic Settings，从环境变量读取配置
"""
from typing import Any

from pydantic import Field

from config.base import BaseConfig


class CeleryConfig(BaseConfig):
    """
    Celery 配置类

    该配置类基于 Pydantic Settings，专门为 Celery 提供配置支持。
    所有环境变量都需要以 "CELERY_" 为前缀。

    设计特点：
    - 支持多种消息代理（RabbitMQ、Redis）
    - 灵活的任务路由配置
    - 完整的重试和超时机制
    - 支持任务结果缓存和查询
    - 可配置的序列化方式

    环境变量格式：
    - 简单配置：CELERY_BROKER_URL=amqp://...
    - 嵌套配置：CELERY_TASK_ROUTES__EMAIL__QUEUE=email
    - 嵌套配置使用双下划线 "__" 作为分隔符
    """

    model_config = BaseConfig.model_config | {"env_prefix": "CELERY_"}

    # ==================== Broker 配置 ====================

    # 消息代理 URL
    # 格式: amqp://user:password@host:port/vhost
    # 或: redis://:password@host:port/db
    broker_url: str = Field(
        default="amqp://guest:guest@localhost:5672//",
        description="Celery 消息代理 URL",
    )

    # ==================== Result Backend 配置 ====================

    # 结果后端 URL
    # 格式: redis://:password@host:port/db
    # 或: db+postgresql://user:password@host:port/dbname
    result_backend: str = Field(
        default="redis://127.0.0.1:6379/1",
        description="Celery 结果后端 URL",
    )

    # ==================== 序列化配置 ====================

    # 任务序列化方式
    # 可选值: json, pickle, msgpack, yaml
    task_serializer: str = Field(
        default="json",
        description="任务序列化方式",
    )

    # 结果序列化方式
    result_serializer: str = Field(
        default="json",
        description="结果序列化方式",
    )

    # 接受的序列化方式
    # 安全考虑，生产环境建议只接受 json
    accept_content: list[str] = Field(
        default=["json"],
        description="接受的序列化方式",
    )

    # ==================== 时区配置 ====================

    # 时区设置
    timezone: str = Field(
        default="Asia/Shanghai",
        description="时区设置",
    )

    # 是否启用 UTC
    enable_utc: bool = Field(
        default=True,
        description="是否启用 UTC",
    )

    # ==================== 结果配置 ====================

    # 结果过期时间（秒）
    # 0 表示永不过期
    result_expires: int = Field(
        default=86400,
        description="结果过期时间（秒）",
    )

    # 结果扩展
    # 是否扩展结果以包含任务参数
    result_extended: bool = Field(
        default=True,
        description="是否扩展结果",
    )

    # ==================== 任务配置 ====================

    # 任务最大重试次数
    task_max_retries: int = Field(
        default=3,
        description="任务最大重试次数",
    )

    # 任务重试延迟（秒）
    task_retry_delay: int = Field(
        default=60,
        description="任务重试延迟（秒）",
    )

    # 任务重试策略
    # 可选值: True, False, "jitter"
    task_retry_backoff: bool | str = Field(
        default=True,
        description="任务重试策略",
    )

    # 任务重试最大延迟（秒）
    task_retry_backoff_max: int = Field(
        default=600,
        description="任务重试最大延迟（秒）",
    )

    # 任务默认超时时间（秒）
    # None 表示无限制
    task_time_limit: int | None = Field(
        default=3600,
        description="任务默认超时时间（秒）",
    )

    # 任务软超时时间（秒）
    # 超时后抛出 SoftTimeLimitExceeded 异常，任务可以捕获并优雅退出
    task_soft_time_limit: int | None = Field(
        default=3000,
        description="任务软超时时间（秒）",
    )

    # 任务严格模式
    # True: 未知任务会抛异常
    # False: 未知任务会忽略
    task_strict: bool = Field(
        default=True,
        description="任务严格模式",
    )

    # ==================== Worker 配置 ====================

    # Worker 并发数
    # 建议设置为 CPU 核心数的 2 倍
    worker_concurrency: int = Field(
        default=4,
        description="Worker 并发数",
    )

    # Worker 预取任务数
    # 建议设置为并发数的 4 倍
    worker_prefetch_multiplier: int = Field(
        default=4,
        description="Worker 预取任务数",
    )

    # Worker 最大任务数
    # 达到此数量后 Worker 会重启
    worker_max_tasks_per_child: int | None = Field(
        default=1000,
        description="Worker 最大任务数",
    )

    # Worker 任务执行超时（秒）
    worker_task_time_limit: int | None = Field(
        default=None,
        description="Worker 任务执行超时（秒）",
    )

    # ==================== 任务路由配置 ====================

    # 任务路由配置
    # 格式: {"任务模式": {"queue": "队列名", "routing_key": "路由键"}}
    task_routes: dict[str, dict[str, Any]] = Field(
        default_factory=lambda: {
            "tasks.email_tasks.*": {"queue": "email"},
            "tasks.data_tasks.*": {"queue": "data"},
            "tasks.report_tasks.*": {"queue": "report"},
        },
        description="任务路由配置",
    )

    # ==================== 队列配置 ====================

    # 默认队列
    task_default_queue: str = Field(
        default="default",
        description="默认队列",
    )

    # 默认路由键
    task_default_routing_key: str = Field(
        default="default",
        description="默认路由键",
    )

    # 队列配置
    task_queues: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {"name": "default", "routing_key": "default"},
            {"name": "email", "routing_key": "email"},
            {"name": "data", "routing_key": "data"},
            {"name": "report", "routing_key": "report"},
        ],
        description="队列配置",
    )

    # ==================== 安全配置 ====================

    # 任务发送确认
    # True: 等待消息代理确认
    task_send_sent_event: bool = Field(
        default=True,
        description="任务发送确认",
    )

    # 任务执行追踪
    # True: 追踪任务执行状态
    task_track_started: bool = Field(
        default=True,
        description="任务执行追踪",
    )

    # ==================== 日志配置 ====================

    # 日志级别
    worker_log_level: str = Field(
        default="INFO",
        description="Worker 日志级别",
    )

    # 日志格式
    worker_log_format: str = Field(
        default="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        description="日志格式",
    )

    # 任务日志格式
    worker_task_log_format: str = Field(
        default="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
        description="任务日志格式",
    )
```

---

## 七、目录结构

### 7.1 推荐目录结构

```
server/
├── config/
│   ├── __init__.py
│   ├── base.py              # 基础配置
│   ├── app.py               # 应用配置
│   ├── database.py          # 数据库配置
│   ├── cache.py             # 缓存配置
│   └── celery.py            # Celery 配置（新增）
│
├── Modules/
│   └── common/
│       └── libs/
│           ├── celery/      # Celery 核心库（新增）
│           │   ├── __init__.py
│           │   ├── app.py              # Celery 实例
│           │   ├── config.py           # Celery 配置加载
│           │   ├── tasks.py            # 基础任务装饰器
│           │   ├── beat.py             # 定时任务配置
│           │   └── utils.py            # 工具函数
│           │
│           ├── cache/      # Redis 缓存（已存在）
│           │   ├── __init__.py
│           │   ├── cache.py
│           │   └── init.py
│           │
│           └── log/        # 日志系统（已存在）
│               ├── __init__.py
│               └── setup_logging.py
│
├── tasks/                   # 任务目录（新增）
│   ├── __init__.py
│   ├── email_tasks.py       # 邮件任务
│   ├── data_tasks.py        # 数据任务
│   ├── report_tasks.py      # 报表任务
│   ├── notification_tasks.py # 通知任务
│   └── cleanup_tasks.py     # 清理任务
│
├── worker.py                # Worker 启动脚本（新增）
├── beat.py                  # Beat 启动脚本（新增）
├── flower.py                # Flower 启动脚本（新增）
│
├── run.py                   # FastAPI 应用启动脚本
├── requirements.txt         # Python 依赖
└── .env                     # 环境变量配置
```

### 7.2 文件职责说明


| 文件                                   | 职责                                    |
| -------------------------------------- | --------------------------------------- |
| `config/celery.py`                     | Celery 配置类，定义所有 Celery 相关配置 |
| `Modules/common/libs/celery/app.py`    | Celery 实例初始化                       |
| `Modules/common/libs/celery/config.py` | 加载和应用 Celery 配置                  |
| `Modules/common/libs/celery/tasks.py`  | 基础任务装饰器和工具函数                |
| `Modules/common/libs/celery/beat.py`   | 定时任务调度配置                        |
| `tasks/*.py`                           | 具体任务实现                            |
| `worker.py`                            | Worker 进程启动脚本                     |
| `beat.py`                              | Beat 进程启动脚本                       |
| `flower.py`                            | Flower 监控服务启动脚本                 |

---

## 八、核心概念

### 8.1 任务（Task）

任务是 Celery 的基本单元，是一个可调用的 Python 函数，通过 `@app.task` 装饰器注册。

**任务类型：**

- **普通任务**：异步执行的任务
- **定时任务**：按计划执行的任务
- **链式任务**：按顺序执行的任务
- **组任务**：并行执行的任务
- **回调任务**：任务完成后执行的任务

### 8.2 任务状态


| 状态        | 说明           |
| ----------- | -------------- |
| **PENDING** | 任务等待执行   |
| **STARTED** | 任务已开始执行 |
| **SUCCESS** | 任务执行成功   |
| **FAILURE** | 任务执行失败   |
| **RETRY**   | 任务正在重试   |
| **REVOKED** | 任务被撤销     |

### 8.3 任务结果

任务执行结果存储在 Redis 中，可以通过任务 ID 查询。

**结果类型：**

- **普通结果**：任务返回的值
- **异常结果**：任务抛出的异常
- **链式结果**：任务链的最终结果
- **组结果**：任务组的结果集合

### 8.4 任务路由

任务路由决定任务发送到哪个队列。

**路由方式：**

- **基于任务名称**：根据任务模式匹配
- **基于任务参数**：根据任务参数动态路由
- **自定义路由器**：实现自定义路由逻辑

### 8.5 任务优先级

Celery 支持任务优先级，优先级高的任务优先执行。

**优先级范围：** 0-9（0 最高，9 最低）

### 8.6 任务重试

任务失败后可以自动重试。

**重试策略：**

- **固定延迟**：每次重试间隔固定
- **指数退避**：重试间隔逐渐增加
- **随机抖动**：避免多个任务同时重试

---

## 九、使用场景

### 9.1 异步任务

**场景：** 发送邮件、短信通知

**优势：**

- 不阻塞主线程
- 提高响应速度
- 支持批量发送

**示例：**

```python
# 发送邮件任务
@app.task(bind=True, max_retries=3)
def send_email_task(self, to_email, subject, content):
    try:
        # 发送邮件逻辑
        send_email(to_email, subject, content)
        return {"status": "success", "email": to_email}
    except Exception as exc:
        # 自动重试
        raise self.retry(exc=exc, countdown=60)
```

### 9.2 定时任务

**场景：** 数据同步、报表生成、数据清理

**优势：**

- 灵活的调度规则
- 支持 Cron 表达式
- 可动态添加/修改任务

**示例：**

```python
# 每天凌晨 2 点执行数据同步
@app.task
def sync_data_task():
    # 数据同步逻辑
    sync_data()

# 每小时执行一次数据清理
@app.task
def cleanup_data_task():
    # 数据清理逻辑
    cleanup_data()
```

### 9.3 批量任务

**场景：** 批量导入数据、批量处理图片

**优势：**

- 并行处理
- 提高效率
- 支持进度追踪

**示例：**

```python
# 批量导入数据
@app.task
def batch_import_task(data_list):
    # 批量导入逻辑
    for data in data_list:
        import_data(data)
    return {"status": "success", "count": len(data_list)}
```

### 9.4 任务链

**场景：** 多步骤任务，按顺序执行

**优势：**

- 任务依赖管理
- 数据传递
- 错误处理

**示例：**

```python
# 数据处理链：下载 -> 处理 -> 上传
@app.task
def download_task(url):
    # 下载数据
    return download_data(url)

@app.task
def process_task(data):
    # 处理数据
    return process_data(data)

@app.task
def upload_task(data):
    # 上传数据
    return upload_data(data)

# 创建任务链
chain(
    download_task.s(url),
    process_task.s(),
    upload_task.s()
).apply_async()
```

### 9.5 任务组

**场景：** 并行执行多个独立任务

**优势：**

- 并行处理
- 提高效率
- 结果聚合

**示例：**

```python
# 并行发送多个邮件
@app.task
def send_email_task(email):
    # 发送邮件
    return send_email(email)

# 创建任务组
group(
    send_email_task.s(email1),
    send_email_task.s(email2),
    send_email_task.s(email3)
).apply_async()
```

---

## 十、最佳实践

### 10.1 任务设计原则

1. **幂等性**：任务可以安全地重复执行
2. **原子性**：任务要么全部成功，要么全部失败
3. **可重试**：任务失败后可以安全重试
4. **超时控制**：设置合理的超时时间
5. **错误处理**：完善的异常捕获和处理

### 10.2 任务命名规范

```
格式: {模块}_{功能}_task

示例:
- tasks.email_tasks.send_email_task
- tasks.data_tasks.sync_data_task
- tasks.report_tasks.generate_report_task
```

### 10.3 任务参数设计

1. **使用简单类型**：优先使用基本类型（str, int, float, bool）
2. **避免大对象**：不要传递大对象，使用 ID 或 URL
3. **序列化友好**：确保参数可以 JSON 序列化
4. **参数验证**：在任务开始时验证参数

### 10.4 错误处理

```python
@app.task(bind=True, max_retries=3)
def example_task(self, param):
    try:
        # 任务逻辑
        result = do_something(param)
        return result
    except TemporaryError as exc:
        # 临时错误，重试
        raise self.retry(exc=exc, countdown=60)
    except PermanentError as exc:
        # 永久错误，记录日志
        logger.error(f"任务失败: {exc}")
        raise
    except Exception as exc:
        # 未知错误，记录日志并重试
        logger.exception(f"未知错误: {exc}")
        raise self.retry(exc=exc, countdown=60)
```

### 10.5 日志记录

```python
from loguru import logger

@app.task(bind=True)
def example_task(self, param):
    logger.info(f"任务开始执行: {self.request.id}")
    try:
        result = do_something(param)
        logger.info(f"任务执行成功: {self.request.id}")
        return result
    except Exception as exc:
        logger.error(f"任务执行失败: {self.request.id}, 错误: {exc}")
        raise
```

### 10.6 性能优化

1. **合理设置并发数**：根据 CPU 核心数调整
2. **使用任务路由**：不同类型任务使用不同队列
3. **批量处理**：合并多个小任务为一个大任务
4. **避免阻塞操作**：使用异步或线程池
5. **合理设置预取数**：避免任务堆积

### 10.7 监控和告警

1. **使用 Flower**：实时监控任务执行情况
2. **记录关键指标**：任务数量、执行时间、成功率
3. **设置告警规则**：任务失败率、执行时间过长
4. **定期检查日志**：及时发现潜在问题

---

## 十一、监控和管理

### 11.1 Flower 监控

Flower 是 Celery 的实时监控工具，提供 Web 界面。

**功能特性：**

- 实时监控任务执行情况
- 查看 Worker 状态
- 查看任务详情
- 管理任务（撤销、重试）
- 查看任务统计

**启动命令：**

```bash
celery -A Modules.common.libs.celery.app flower --port=5555
```

**访问地址：**

- URL: `http://localhost:5555`

### 11.2 命令行管理

**查看 Worker 状态：**

```bash
celery -A Modules.common.libs.celery.app inspect active
celery -A Modules.common.libs.celery.app inspect registered
celery -A Modules.common.libs.celery.app inspect stats
```

**管理任务：**

```bash
# 撤销任务
celery -A Modules.common.libs.celery.app control revoke <task_id>

# 清空队列
celery -A Modules.common.libs.celery.app purge

# 重启 Worker
celery -A Modules.common.libs.celery.app control shutdown
```

### 11.3 日志分析

**关键日志指标：**

- 任务执行时间
- 任务成功率
- 任务失败原因
- Worker 资源使用

### 11.4 告警配置

**告警场景：**

- 任务失败率超过阈值
- 任务执行时间过长
- Worker 数量不足
- 队列积压严重

---

## 十二、部署方案

### 12.1 开发环境

**启动顺序：**

1. 启动 RabbitMQ
2. 启动 Redis
3. 启动 Celery Worker
4. 启动 Celery Beat
5. 启动 FastAPI 应用

**启动命令：**

```bash
# 启动 Worker
celery -A Modules.common.libs.celery.app worker --loglevel=info

# 启动 Beat
celery -A Modules.common.libs.celery.app beat --loglevel=info

# 启动 Flower
celery -A Modules.common.libs.celery.app flower --port=5555

# 启动 FastAPI
uvicorn run:app --reload
```

### 12.2 生产环境

#### Docker Compose 部署

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: celery_user
      RABBITMQ_DEFAULT_PASS: celery_password
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build: .
    command: celery -A Modules.common.libs.celery.app worker --loglevel=info
    depends_on:
      - rabbitmq
      - redis
    environment:
      CELERY_BROKER_URL: amqp://celery_user:celery_password@rabbitmq:5672/celery
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    volumes:
      - .:/app

  celery_beat:
    build: .
    command: celery -A Modules.common.libs.celery.app beat --loglevel=info
    depends_on:
      - rabbitmq
      - redis
    environment:
      CELERY_BROKER_URL: amqp://celery_user:celery_password@rabbitmq:5672/celery
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    volumes:
      - .:/app

  flower:
    build: .
    command: celery -A Modules.common.libs.celery.app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - rabbitmq
      - redis
    environment:
      CELERY_BROKER_URL: amqp://celery_user:celery_password@rabbitmq:5672/celery
      CELERY_RESULT_BACKEND: redis://redis:6379/1

  fastapi:
    build: .
    command: uvicorn run:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - rabbitmq
      - redis
    environment:
      CELERY_BROKER_URL: amqp://celery_user:celery_password@rabbitmq:5672/celery
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    volumes:
      - .:/app

volumes:
  rabbitmq_data:
  redis_data:
```

#### Kubernetes 部署

使用 Kubernetes 部署可以实现：

- 自动扩缩容
- 滚动更新
- 健康检查
- 资源限制

### 12.3 高可用部署

**RabbitMQ 集群：**

- 使用 RabbitMQ 镜像队列
- 配置负载均衡
- 实现故障转移

**Redis 集群：**

- 使用 Redis Sentinel
- 或 Redis Cluster
- 实现高可用

**Celery Worker 集群：**

- 多个 Worker 实例
- 使用相同的队列
- 实现负载均衡

---

## 十三、常见问题

### 13.1 任务不执行

**可能原因：**

1. Worker 未启动
2. 队列名称不匹配
3. 任务未注册
4. Broker 连接失败

**解决方案：**

1. 检查 Worker 是否正常运行
2. 确认队列配置正确
3. 确认任务已注册
4. 检查 Broker 连接

### 13.2 任务执行失败

**可能原因：**

1. 任务代码错误
2. 依赖服务不可用
3. 超时时间过短
4. 资源不足

**解决方案：**

1. 检查任务日志
2. 检查依赖服务状态
3. 增加超时时间
4. 增加 Worker 资源

### 13.3 任务执行缓慢

**可能原因：**

1. Worker 并发数不足
2. 任务逻辑复杂
3. 阻塞操作过多
4. 网络延迟

**解决方案：**

1. 增加 Worker 并发数
2. 优化任务逻辑
3. 使用异步操作
4. 优化网络配置

### 13.4 内存泄漏

**可能原因：**

1. 任务未释放资源
2. 循环引用
3. 大对象未清理
4. Worker 长时间运行

**解决方案：**

1. 设置 worker_max_tasks_per_child
2. 及时释放资源
3. 避免大对象
4. 定期重启 Worker

### 13.5 任务重复执行

**可能原因：**

1. 任务非幂等
2. 网络问题导致重复发送
3. Worker 重启

**解决方案：**

1. 确保任务幂等
2. 使用任务去重
3. 检查网络配置

---

## 十四、性能优化

### 14.1 Worker 优化

**并发数设置：**

```python
# 建议：CPU 核心数的 2 倍
worker_concurrency = cpu_count() * 2
```

**预取数设置：**

```python
# 建议：并发数的 4 倍
worker_prefetch_multiplier = 4
```

**任务数限制：**

```python
# 建议：1000-5000
worker_max_tasks_per_child = 1000
```

### 14.2 任务优化

**批量处理：**

```python
# 不推荐：多次调用
for item in items:
    process_item_task.delay(item)

# 推荐：批量处理
process_items_task.delay(items)
```

**避免阻塞：**

```python
# 不推荐：阻塞操作
def task():
    time.sleep(10)

# 推荐：异步操作
def task():
    await asyncio.sleep(10)
```

### 14.3 Broker 优化

**RabbitMQ 优化：**

- 增加连接池大小
- 使用持久化队列
- 优化队列数量
- 使用镜像队列

**Redis 优化：**

- 增加连接池大小
- 使用合适的数据库
- 设置合理的过期时间
- 使用 Pipeline

### 14.4 网络优化

- 使用内网通信
- 减少网络延迟
- 增加带宽
- 使用 CDN

---

## 十五、安全建议

### 15.1 认证和授权

**RabbitMQ：**

- 使用强密码
- 创建专用用户
- 限制用户权限
- 使用 SSL/TLS

**Redis：**

- 设置密码
- 限制访问 IP
- 使用 SSL/TLS
- 禁用危险命令

### 15.2 数据加密

**传输加密：**

- 使用 SSL/TLS
- 加密敏感数据
- 使用安全的序列化方式

**存储加密：**

- 加密结果数据
- 使用安全的存储后端
- 定期清理过期数据

### 15.3 访问控制

**网络隔离：**

- 使用防火墙
- 限制访问 IP
- 使用 VPN

**应用隔离：**

- 使用虚拟主机
- 使用独立的数据库
- 限制队列访问

### 15.4 审计和监控

**日志审计：**

- 记录所有操作
- 定期检查日志
- 设置告警规则

**安全监控：**

- 监控异常访问
- 监控资源使用
- 监控任务执行

---

## 总结

Celery + RabbitMQ 是一个强大的分布式任务队列解决方案，适合处理异步任务和定时任务。通过本文档，您可以了解：

1. **技术栈**：Celery 和 RabbitMQ 的核心概念
2. **架构设计**：如何集成到现有项目中
3. **配置管理**：如何配置 Celery 和 RabbitMQ
4. **任务开发**：如何开发和管理任务
5. **监控管理**：如何监控和管理任务执行
6. **部署方案**：如何部署到生产环境
7. **最佳实践**：如何优化性能和安全性

建议在实际使用中：

- 从简单场景开始，逐步扩展
- 充分测试后再部署到生产环境
- 建立完善的监控和告警机制
- 定期优化和调整配置

如有疑问，请参考官方文档：

- Celery: https://docs.celeryproject.org/
- RabbitMQ: https://www.rabbitmq.com/docs
