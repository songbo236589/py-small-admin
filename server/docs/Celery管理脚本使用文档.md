# Celery 管理脚本使用文档

## 📋 概述

`celery_manager.py` 是一个统一的 Celery 组件管理脚本，用于管理 Celery Worker、Beat、Flower 的启动、停止、重启等操作。

**文件位置：** `commands/celery_manager.py`

## 🚀 快速开始

### 1. 启动所有组件

```bash
python -m commands.celery_manager start all
```

### 2. 查看组件状态

```bash
python -m commands.celery_manager status
```

### 3. 停止所有组件

```bash
python -m commands.celery_manager stop all
```

---

## 📖 详细使用说明

### Worker 操作

Worker 是 Celery 的任务执行器，负责从队列中获取并执行任务。

#### 启动 Worker

```bash
# 启动 Worker（使用默认队列）
python -m commands.celery_manager worker start

# 启动 Worker 并指定队列
python -m commands.celery_manager worker start -q email_queues,default

# 启动 Worker 并指定多个队列
python -m commands.celery_manager worker start --queues email_queues,image_queue
```

**参数说明：**

- `-q, --queues`: 队列名称，多个队列用逗号分隔
- 默认使用配置文件中的 `task_default_queue`

#### 停止 Worker

```bash
python -m commands.celery_manager worker stop
```

#### 重启 Worker

```bash
# 重启 Worker（使用默认队列）
python -m commands.celery_manager worker restart

# 重启 Worker 并指定队列
python -m commands.celery_manager worker restart -q high_priority,default
```

---

### Beat 操作

Beat 是 Celery 的定时任务调度器，负责按照配置的时间规则触发定时任务。

#### 启动 Beat

```bash
python -m commands.celery_manager beat start
```

#### 停止 Beat

```bash
python -m commands.celery_manager beat stop
```

#### 重启 Beat

```bash
python -m commands.celery_manager beat restart
```

---

### Flower 操作

Flower 是 Celery 的 Web 监控界面，提供实时监控和管理功能。

#### 启动 Flower

```bash
python -m commands.celery_manager flower start
```

启动后，可以通过浏览器访问 Flower 监控界面：

- 默认地址: `http://localhost:5555`
- 如果配置了认证，需要输入用户名和密码

#### 停止 Flower

```bash
python -m commands.celery_manager flower stop
```

#### 重启 Flower

```bash
python -m commands.celery_manager flower restart
```

---

### 批量操作

#### 启动所有组件

```bash
python -m commands.celery_manager start all
```

此命令会依次启动：

1. Worker
2. Beat
3. Flower

#### 停止所有组件

```bash
python -m commands.celery_manager stop all
```

此命令会依次停止：

1. Flower
2. Beat
3. Worker

#### 重启所有组件

```bash
python -m commands.celery_manager restart all
```

---

### 状态查看

#### 查看所有组件状态

```bash
python -m commands.celery_manager status
```

输出示例：

```
📊 Celery 组件状态

==================================================
✅ WORKER     - 运行中 (PID: 12345)
   日志: d:\python\project\py-small-admin\server\logs\celery_worker.log
✅ BEAT       - 运行中 (PID: 12346)
   日志: d:\python\project\py-small-admin\server\logs\celery_beat.log
✅ FLOWER     - 运行中 (PID: 12347)
   日志: d:\python\project\py-small-admin\server\logs\celery_flower.log
==================================================

🌸 Flower 监控界面:
   地址: http://0.0.0.0:5555
   认证: admin:password
```

---

## ⚙️ 配置说明

脚本会从 `config/celery.py` 中的 `CeleryConfig` 类读取配置参数。

### Worker 配置


| 配置项                       | 说明              | 默认值  |
| ---------------------------- | ----------------- | ------- |
| `worker_pool`                | Worker 执行池类型 | prefork |
| `worker_concurrency`         | Worker 并发数     | 4       |
| `worker_prefetch_multiplier` | 预取倍数          | 4       |
| `worker_max_tasks_per_child` | 每进程最大任务数  | 1000    |
| `task_default_queue`         | 默认队列名称      | default |
| `beat_loglevel`              | 日志级别          | INFO    |

**Worker 执行池类型说明：**

- **prefork**（默认）：多进程模式，适合 CPU 密集型任务，充分利用多核 CPU，但内存占用较大
- **threads**：多线程模式，适合 I/O 密集型任务（如网络请求、文件读写），内存占用小，但受 Python GIL 限制
- **solo**：单线程模式，适合调试或需要串行执行的任务
- **gevent**：协程模式，适合高并发 I/O 密集型任务，需要安装 gevent 库
- **eventlet**：协程模式，适合高并发 I/O 密集型任务，需要安装 eventlet 库

**配置示例：**

```bash
# .env 文件中配置
CELERY_WORKER__POOL=threads
```

**选择建议：**

- CPU 密集型任务（如数据处理、图像处理）：使用 `prefork`
- I/O 密集型任务（如 HTTP 请求、数据库操作）：使用 `threads`
- 高并发 I/O 密集型任务（如 WebSocket、长连接）：使用 `gevent` 或 `eventlet`
- 调试环境：使用 `solo`

### Beat 配置


| 配置项                   | 说明               | 默认值              |
| ------------------------ | ------------------ | ------------------- |
| `beat_schedule_filename` | 调度器文件名       | celerybeat-schedule |
| `beat_max_loop_interval` | 最大循环间隔（秒） | 5                   |
| `beat_loglevel`          | 日志级别           | INFO                |

### Flower 配置


| 配置项              | 说明                  | 默认值  |
| ------------------- | --------------------- | ------- |
| `flower.port`       | 监控端口              | 5555    |
| `flower.host`       | 监听地址              | 0.0.0.0 |
| `flower.basic_auth` | 基本认证              | 空      |
| `flower.broker_api` | RabbitMQ 管理接口 URL | 空      |

---

## 📁 文件结构

脚本运行后会创建以下文件和目录：

```
server/
├── pids/                          # PID 文件目录
│   ├── celery_worker.pid          # Worker 进程 ID
│   ├── celery_beat.pid            # Beat 进程 ID
│   └── celery_flower.pid          # Flower 进程 ID
├── logs/                          # 日志文件目录
│   ├── celery_worker.log          # Worker 日志
│   ├── celery_beat.log            # Beat 日志
│   └── celery_flower.log          # Flower 日志
└── commands/
    └── celery_manager.py          # 管理脚本
```

---

## 🔧 高级用法

### 指定不同的队列

根据业务需求，可以启动多个 Worker 实例，每个实例处理不同的队列：

```bash
# 启动处理高优先级任务的 Worker
python -m commands.celery_manager worker start -q high_priority

# 启动处理邮件任务的 Worker
python -m commands.celery_manager worker start -q email_queue

# 启动处理多个队列的 Worker
python -m commands.celery_manager worker start -q high_priority,default,low_priority
```

### 查看实时日志

```bash
# 查看 Worker 日志
tail -f logs/celery_worker.log

# 查看 Beat 日志
tail -f logs/celery_beat.log

# 查看 Flower 日志
tail -f logs/celery_flower.log
```

### 手动清理 PID 文件

如果进程异常退出，可以手动删除 PID 文件：

```bash
# Windows
del pids\celery_worker.pid

# Linux/Mac
rm pids/celery_worker.pid
```

---

## 🐛 故障排查

### Worker 无法启动

**可能原因：**

1. RabbitMQ/Redis 未启动
2. 端口被占用
3. 配置错误

**解决方法：**

1. 检查 RabbitMQ/Redis 是否运行

   ```bash
   # 检查 RabbitMQ
   rabbitmqctl status

   # 检查 Redis
   redis-cli ping
   ```
2. 检查日志文件

   ```bash
   cat logs/celery_worker.log
   ```
3. 验证配置

   ```bash
   python -c "from config.celery import CeleryConfig; print(CeleryConfig().broker_url)"
   ```

### Beat 无法启动

**可能原因：**

1. 调度器文件被锁定
2. 定时任务配置错误

**解决方法：**

1. 删除调度器文件

   ```bash
   # Windows
   del celerybeat-schedule.*

   # Linux/Mac
   rm celerybeat-schedule.*
   ```
2. 检查定时任务配置

   ```bash
   python -c "from config.celery import CeleryConfig; print(CeleryConfig().beat_schedule)"
   ```

### Flower 无法访问

**可能原因：**

1. 端口被占用
2. 防火墙阻止
3. 认证配置错误

**解决方法：**

1. 检查端口是否被占用

   ```bash
   # Windows
   netstat -ano | findstr 5555

   # Linux/Mac
   lsof -i :5555
   ```
2. 检查防火墙设置
3. 验证认证配置

   ```bash
   python -c "from config.celery import CeleryConfig; print(CeleryConfig().flower)"
   ```

---

## � Celery 原生命令

除了使用 `celery_manager.py` 管理脚本，您也可以直接使用 Celery 的原生命令来管理和监控 Celery 组件。

### Worker 命令

#### 启动 Worker

```bash
# 基本启动
celery -A Modules.common.libs.celery.app worker

# 指定日志级别
celery -A Modules.common.libs.celery.app worker --loglevel=info

# 指定队列
celery -A Modules.common.libs.celery.app worker -Q email_queues,default

# 指定并发数
celery -A Modules.common.libs.celery.app worker --concurrency=4

# 指定执行池类型
celery -A Modules.common.libs.celery.app worker --pool=threads

# 指定 Worker 名称
celery -A Modules.common.libs.celery.app worker -n worker1@%h

# 后台运行（需要安装 supervisor 或使用 nohup）
celery -A Modules.common.libs.celery.app worker --loglevel=info --detach
```

**常用参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-A, --app` | 应用程序路径 | - |
| `-n, --hostname` | Worker 名称 | celery@%h |
| `-Q, --queues` | 指定队列 | default |
| `-c, --concurrency` | 并发数 | CPU 核心数 |
| `-P, --pool` | 执行池类型 | prefork |
| `-l, --loglevel` | 日志级别 | WARNING |
| `-f, --logfile` | 日志文件 | - |
| `--pidfile` | PID 文件路径 | - |
| `--detach` | 后台运行 | False |

#### 停止 Worker

```bash
# 优雅停止（等待当前任务完成）
celery -A Modules.common.libs.celery.app control shutdown

# 强制停止
pkill -f "celery worker"
# 或
taskkill /F /IM celery.exe  # Windows
```

---

### Beat 命令

#### 启动 Beat

```bash
# 基本启动
celery -A Modules.common.libs.celery.app beat

# 指定调度器文件
celery -A Modules.common.libs.celery.app beat -s celerybeat-schedule

# 指定日志级别
celery -A Modules.common.libs.celery.app beat --loglevel=info

# 后台运行
celery -A Modules.common.libs.celery.app beat --loglevel=info --detach
```

**常用参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-A, --app` | 应用程序路径 | - |
| `-s, --schedule` | 调度器文件路径 | celerybeat-schedule |
| `--pidfile` | PID 文件路径 | celerybeat.pid |
| `-l, --loglevel` | 日志级别 | WARNING |
| `-f, --logfile` | 日志文件 | - |
| `--detach` | 后台运行 | False |

#### 停止 Beat

```bash
# 优雅停止
celery -A Modules.common.libs.celery.app control shutdown

# 强制停止
pkill -f "celery beat"
# 或
taskkill /F /IM celery.exe  # Windows
```

---

### Flower 命令

#### 启动 Flower

```bash
# 基本启动
celery -A Modules.common.libs.celery.app flower

# 指定端口
celery -A Modules.common.libs.celery.app flower --port=5555

# 指定监听地址
celery -A Modules.common.libs.celery.app flower --address=0.0.0.0

# 配置基本认证
celery -A Modules.common.libs.celery.app flower --basic_auth=admin:password

# 配置 RabbitMQ 管理接口
celery -A Modules.common.libs.celery.app flower --broker_api=http://guest:guest@localhost:15672/api/

# 后台运行
celery -A Modules.common.libs.celery.app flower --loglevel=info --detach
```

**常用参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-A, --app` | 应用程序路径 | - |
| `--port` | 监听端口 | 5555 |
| `--address` | 监听地址 | 127.0.0.1 |
| `--basic_auth` | 基本认证（用户名:密码） | - |
| `--broker_api` | RabbitMQ 管理接口 URL | - |
| `--url_prefix` | URL 前缀 | - |
| `-l, --loglevel` | 日志级别 | WARNING |
| `-f, --logfile` | 日志文件 | - |
| `--detach` | 后台运行 | False |

#### 停止 Flower

```bash
# 优雅停止
pkill -f "celery flower"
# 或
taskkill /F /IM celery.exe  # Windows
```

---

### Inspect 命令（监控和诊断）

Inspect 命令用于监控和管理运行中的 Worker。

```bash
# 查看活跃的 Worker
celery -A Modules.common.libs.celery.app inspect active

# 查看已注册的任务
celery -A Modules.common.libs.celery.app inspect registered

# 查看已调度的任务
celery -A Modules.common.libs.celery.app inspect scheduled

# 查看保留的任务
celery -A Modules.common.libs.celery.app inspect reserved

# 查看统计信息
celery -A Modules.common.libs.celery.app inspect stats

# 查看已完成的任务
celery -A Modules.common.libs.celery.app inspect report

# 查看配置
celery -A Modules.common.libs.celery.app inspect conf

# 查看启用的队列
celery -A Modules.common.libs.celery.app inspect active_queues

# 指定特定的 Worker
celery -A Modules.common.libs.celery.app inspect active --destination=celery@hostname
```

**常用子命令：**

| 子命令 | 说明 |
|--------|------|
| `active` | 当前正在执行的任务 |
| `registered` | 已注册的任务列表 |
| `scheduled` | 已调度但未执行的任务 |
| `reserved` | 已接收但未开始执行的任务 |
| `stats` | Worker 统计信息 |
| `report` | Worker 详细报告 |
| `conf` | Worker 配置信息 |
| `active_queues` | Worker 监听的队列 |
| `ping` | 检查 Worker 是否在线 |

---

### Control 命令（控制 Worker）

Control 命令用于控制运行中的 Worker。

```bash
# 关闭 Worker
celery -A Modules.common.libs.celery.app control shutdown

# 重启 Worker
celery -A Modules.common.libs.celery.app control pool_restart

# 添加消费者
celery -A Modules.common.libs.celery.app control add_consumer queue_name

# 取消消费者
celery -A Modules.common.libs.celery.app control cancel_consumer queue_name

# 取消所有任务
celery -A Modules.common.libs.celery.app control purge

# 启用事件
celery -A Modules.common.libs.celery.app control enable_events

# 禁用事件
celery -A Modules.common.libs.celery.app control disable_events

# 限制任务速率
celery -A Modules.common.libs.celery.app control rate_limit task_name rate

# 重启特定任务
celery -A Modules.common.libs.celery.app control pool_restart --task=task_name

# 指定特定的 Worker
celery -A Modules.common.libs.celery.app control shutdown --destination=celery@hostname
```

**常用子命令：**

| 子命令 | 说明 |
|--------|------|
| `shutdown` | 优雅关闭 Worker |
| `pool_restart` | 重启 Worker 进程池 |
| `add_consumer` | 添加队列消费者 |
| `cancel_consumer` | 取消队列消费者 |
| `purge` | 清除所有待处理任务 |
| `enable_events` | 启用任务事件 |
| `disable_events` | 禁用任务事件 |
| `rate_limit` | 设置任务速率限制 |

---

### Purge 命令（清除任务）

```bash
# 清除所有队列中的待处理任务
celery -A Modules.common.libs.celery.app purge

# 清除指定队列的任务
celery -A Modules.common.libs.celery.app purge -Q email_queues

# 强制清除（不确认）
celery -A Modules.common.libs.celery.app purge -f
```

---

### Shell 命令（交互式 Shell）

```bash
# 启动 Celery 交互式 Shell
celery -A Modules.common.libs.celery.app shell

# 使用 IPython
celery -A Modules.common.libs.celery.app shell --ipython
```

---

### Result 命令（查看任务结果）

```bash
# 查看任务结果
celery -A Modules.common.libs.celery.app result <task_id>

# 跟踪任务
celery -A Modules.common.libs.celery.app result --traceback <task_id>
```

---

### 其他有用命令

```bash
# 查看帮助
celery --help

# 查看 Worker 帮助
celery worker --help

# 查看 Beat 帮助
celery beat --help

# 查看 Flower 帮助
celery flower --help

# 查看版本
celery --version

# 测试连接
celery -A Modules.common.libs.celery.app inspect ping
```

---

### 原生命令 vs 管理脚本

| 特性 | 管理脚本 | 原生命令 |
|------|----------|----------|
| 易用性 | 简单统一 | 需要记住多个命令 |
| 后台运行 | 自动处理 | 需要手动配置 |
| 日志管理 | 自动管理 | 需要手动配置 |
| 进程管理 | 统一管理 | 需要手动管理 |
| 灵活性 | 受限 | 高度灵活 |
| 适用场景 | 快速开发 | 生产部署 |

**建议：**
- 开发环境：使用管理脚本 `celery_manager.py`
- 生产环境：使用原生命令配合 Supervisor 或 systemd

---

## �📝 命令速查表


| 命令                                               | 说明         |
| -------------------------------------------------- | ------------ |
| `python -m commands.celery_manager worker start`   | 启动 Worker  |
| `python -m commands.celery_manager worker stop`    | 停止 Worker  |
| `python -m commands.celery_manager worker restart` | 重启 Worker  |
| `python -m commands.celery_manager beat start`     | 启动 Beat    |
| `python -m commands.celery_manager beat stop`      | 停止 Beat    |
| `python -m commands.celery_manager beat restart`   | 重启 Beat    |
| `python -m commands.celery_manager flower start`   | 启动 Flower  |
| `python -m commands.celery_manager flower stop`    | 停止 Flower  |
| `python -m commands.celery_manager flower restart` | 重启 Flower  |
| `python -m commands.celery_manager start all`      | 启动所有组件 |
| `python -m commands.celery_manager stop all`       | 停止所有组件 |
| `python -m commands.celery_manager restart all`    | 重启所有组件 |
| `python -m commands.celery_manager status`         | 查看组件状态 |

---

## 🎯 最佳实践

### 开发环境

1. 使用默认配置启动所有组件
2. 查看日志进行调试
3. 使用 Flower 监控任务执行情况

```bash
python -m commands.celery_manager start all
python -m commands.celery_manager status
```

### 生产环境

1. 根据服务器配置调整并发数
2. 配置日志轮转
3. 使用守护进程管理工具（如 Supervisor、systemd）
4. 配置监控告警

```bash
# 启动 Worker 并指定队列
python -m commands.celery_manager worker start -q high_priority,default

# 启动 Beat
python -m commands.celery_manager beat start

# 启动 Flower（仅内网访问）
python -m commands.celery_manager flower start
```

### 高可用部署

1. 启动多个 Worker 实例
2. 使用负载均衡
3. 配置任务重试和超时
4. 定期检查组件状态

```bash
# 启动多个 Worker 实例
python -m commands.celery_manager worker start -q high_priority
python -m commands.celery_manager worker start -q default
python -m commands.celery_manager worker start -q low_priority
```

---

## 📚 相关文档

- [Celery+RabbitMQ使用文档.md](./Celery+RabbitMQ使用文档.md)
- [Redis使用文档.md](./Redis使用文档.md)

---

## 💡 提示

- 脚本支持 Windows、Linux、Mac 系统
- 所有组件都会在后台运行
- PID 文件和日志文件会自动创建
- 建议定期清理日志文件
- 生产环境建议使用专业的进程管理工具（如 Supervisor、systemd）

---

## 🆘 获取帮助

查看命令帮助：

```bash
python -m commands.celery_manager --help
```

查看特定组件的帮助：

```bash
python -m commands.celery_manager worker --help
python -m commands.celery_manager beat --help
python -m commands.celery_manager flower --help
```

