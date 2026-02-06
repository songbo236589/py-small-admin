# Celery 管理

Celery 管理工具用于管理 Celery 组件（Worker、Beat、Flower）的启动、停止和重启。

## 基本用法

### 查看所有组件状态

```bash
python -m commands.celery_manager status
```

输出示例：

```
📊 Celery 组件状态

==================================================
✅ WORKER     - 运行中 (PID: 12345)
   日志: /path/to/logs/celery_worker.log
✅ BEAT       - 运行中 (PID: 12346)
   日志: /path/to/logs/celery_beat.log
✅ FLOWER     - 运行中 (PID: 12347)
   日志: /path/to/logs/celery_flower.log

🌸 Flower 监控界面:
   地址: http://localhost:5555
==================================================
```

### 启动所有组件

```bash
python -m commands.celery_manager start all
```

### 停止所有组件

```bash
python -m commands.celery_manager stop all
```

## Worker 管理

Worker 负责执行异步任务。

### 启动 Worker

```bash
# 使用默认队列
python -m commands.celery_manager worker start

# 指定队列
python -m commands.celery_manager worker start --queues email,sms
```

### 停止 Worker

```bash
python -m commands.celery_manager worker stop
```

### 重启 Worker

```bash
python -m commands.celery_manager worker restart
```

## Beat 管理

Beat 负责执行定时任务。

### 启动 Beat

```bash
python -m commands.celery_manager beat start
```

### 停止 Beat

```bash
python -m commands.celery_manager beat stop
```

### 重启 Beat

```bash
python -m commands.celery_manager beat restart
```

## Flower 管理

Flower 提供 Web 监控界面。

### 启动 Flower

```bash
python -m commands.celery_manager flower start
```

启动后访问 http://localhost:5555 查看监控界面。

### 停止 Flower

```bash
python -m commands.celery_manager flower stop
```

### 重启 Flower

```bash
python -m commands.celery_manager flower restart
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `worker start/stop/restart` | Worker 操作 |
| `beat start/stop/restart` | Beat 操作 |
| `flower start/stop/restart` | Flower 操作 |
| `start/stop all` | 启动/停止所有组件 |
| `status` | 查看组件状态 |

## 日志文件

各组件的日志文件位置：

```
logs/celery_worker.log   # Worker 日志
logs/celery_beat.log     # Beat 日志
logs/celery_flower.log   # Flower 日志
```

## 常见问题

### 组件已运行

**问题**：启动组件时提示"xxx 已经在运行中"

**解决方案**：
```bash
# 先停止组件
python -m commands.celery_manager worker stop

# 再重新启动
python -m commands.celery_manager worker start
```

### Flower 无法访问

**问题**：启动 Flower 后无法访问 Web 界面

**解决方案**：
1. 检查防火墙设置
2. 确认端口配置（默认 5555）
3. 查看日志文件排查错误

## 详细文档

更多详细用法请参考 [Celery管理脚本使用文档](../../../server/docs/Celery管理脚本使用文档.md)
