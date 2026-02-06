# Flower 监控指南

本文档介绍如何使用 Flower 监控和管理 Celery 任务队列。

## Flower 简介

Flower 是一个用于监控和管理 Celery 的 Web 工具，提供以下功能：

- 实时查看任务执行状态
- 查看 Worker 状态和统计信息
- 查看任务执行时间、参数和结果
- 重试失败的任务
- 查看任务队列状态
- 监控系统资源使用

## 快速开始

### 1. 安装 Flower

```bash
pip install flower
```

### 2. 启动 Flower

```bash
# 基本启动
celery -A Modules.common.libs.celery.celery_service.celery flower

# 指定端口
celery -A Modules.common.libs.celery.celery_service.celery flower --port=5555

# 指定 broker
celery -A Modules.common.libs.celery.celery_service.celery flower \
    --broker=redis://localhost:6379/1
```

### 3. 访问 Flower

打开浏览器访问：http://localhost:5555

## 配置选项

### 命令行参数

```bash
celery -A Modules.common.libs.celery.celery_service.celery flower \
    --port=5555 \
    --broker=redis://localhost:6379/1 \
    --basic_auth=admin:password \
    --max_tasks=10000 \
    --purge_offline_workers=3600 \
    --format_json=True
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--port` | 监听端口 | 5555 |
| `--broker` | Broker URL | 从 Celery 配置读取 |
| `--basic_auth` | 基本认证 `user:password` | 无 |
| `--max_tasks` | 保留的最大任务数 | 10000 |
| `--purge_offline_workers` | 离线 Worker 保留时间（秒） | 3600 |
| `--format_json` | 格式化 JSON 输出 | False |
| `--db` | 持久化数据库路径 | 无 |
| `--ssl` | 启用 SSL | False |
| `--certfile` | SSL 证书文件 | 无 |
| `--keyfile` | SSL 密钥文件 | 无 |

### 配置文件

在 `celery_service.py` 中配置：

```python
from celery import Celery

celery = Celery('py_small_admin')

# Flower 配置
celery_conf = {
    'flower_port': 5555,
    'flower_basic_auth': ['admin:your_password'],
    'flower_max_tasks': 10000,
    'flowerpurge_offline_workers': 3600,
}
```

## Systemd 服务配置

创建 `/etc/systemd/system/py-small-admin-flower.service`：

```ini
[Unit]
Description=Flower for Py Small Admin
After=network.target redis.service rabbitmq.service
Requires=py-small-admin-celery.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/py-small-admin/server
Environment="PATH=/opt/py-small-admin/server/venv/bin"
EnvironmentFile=/opt/py-small-admin/server/.env

ExecStart=/opt/py-small-admin/server/venv/bin/celery -A Modules.common.libs.celery.celery_service.celery flower \
    --port=5555 \
    --broker=$CELERY_BROKER_URL \
    --basic_auth=admin:$FLOWER_PASSWORD \
    --max_tasks=10000

Restart=always
RestartSec=10

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start py-small-admin-flower
sudo systemctl enable py-small-admin-flower
sudo systemctl status py-small-admin-flower
```

## Nginx 反向代理

### HTTP 配置

```nginx
upstream flower_backend {
    server localhost:5555;
}

server {
    listen 80;
    server_name your-domain.com;

    location /flower {
        proxy_pass http://flower_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location /flower {
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Docker 部署

### Docker Compose 配置

```yaml
services:
  flower:
    build: ../
    command: celery -A Modules.common.libs.celery.celery_service.celery flower \
      --port=5555 \
      --broker=redis://redis:6379/1 \
      --basic_auth=admin:${FLOWER_PASSWORD}
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - FLOWER_PASSWORD=${FLOWER_PASSWORD}
    depends_on:
      - redis
    restart: unless-stopped
```

### 独立 Docker 容器

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flower

COPY . .

CMD ["celery", "-A", "Modules.common.libs.celery.celery_service.celery", "flower", \
     "--port=5555", \
     "--broker=redis://redis:6379/1", \
     "--basic_auth=admin:password"]
```

## Web 界面功能

### 1. Dashboard 概览

主页显示整体状态：
- Worker 数量和状态
- 任务执行统计
- 队列信息
- 系统资源使用

### 2. Workers 页面

查看每个 Worker 的详细信息：
- Worker 状态（在线/离线）
- 正在执行的任务
- 已处理的任务数
- 失败的任务数
- 负载情况

### 3. Tasks 页面

查看任务详情：
- 任务 UUID
- 任务名称
- 执行状态
- 执行时间
- 参数和结果
- 异常信息（如果失败）

### 4. 任务操作

- **重试任务**：点击失败任务的重试按钮
- **终止任务**：终止正在运行的任务
- **清理任务**：删除已完成任务的历史记录

### 5. 队列监控

查看队列状态：
- 队列长度
- 等待中的任务
- 预定任务

## 高级配置

### 1. 启用持久化

```bash
celery -A Modules.common.libs.celery.celery_service.celery flower \
    --db=/var/lib/flower/flower.db
```

### 2. 配置 CORS

```python
# 在 flower 启动命令中添加
--cors_enabled=True
```

### 3. 自定义认证

```python
# 创建自定义认证模块
# flower_auth.py

def auth_handler(username, password):
    # 实现自定义认证逻辑
    # 可以从数据库验证
    return True

# 启动时指定
celery -A Modules.common.libs.celery.celery_service.celery flower \
    --auth_module=flower_auth
```

### 4. 配置邮件告警

```python
# flower_config.py
from flower.utils.broker import Broker

class EmailBroker(Broker):
    def send_event(self, event):
        # 发送邮件通知
        pass

# 启动时指定
celery -A Modules.common.libs.celery.celery_service.celery flower \
    --broker_class=flower_config.EmailBroker
```

## 监控最佳实践

### 1. 设置告警阈值

```python
# 定期检查任务状态
import requests

def check_flower_status():
    response = requests.get('http://localhost:5555/api/workers')
    workers = response.json()

    for worker, stats in workers.items():
        if stats.get('status') != 'online':
            send_alert(f'Worker {worker} is offline')

        if stats.get('pool', {}).get('max-concurrency'):
            active = stats.get('pool', {}).get('max-concurrency', 0)
            if active > 80:
                send_alert(f'Worker {worker} is nearly full')
```

### 2. 任务超时监控

```python
def check_stuck_tasks():
    response = requests.get('http://localhost:5555/api/tasks')
    tasks = response.json()

    for task_id, task in tasks.items():
        if task.get('state') == 'STARTED':
            started = task.get('started')
            if started and (time.time() - started) > 3600:
                send_alert(f'Task {task_id} may be stuck')
```

### 3. 失败任务监控

```python
def check_failed_tasks():
    response = requests.get('http://localhost:5555/api/tasks?state=FAILURE')
    tasks = response.json()

    if len(tasks) > 10:
        send_alert(f'Too many failed tasks: {len(tasks)}')
```

## API 接口

Flower 提供 RESTful API：

### 获取 Workers 信息

```bash
curl http://localhost:5555/api/workers
```

### 获取任务信息

```bash
# 所有任务
curl http://localhost:5555/api/tasks

# 特定状态的任务
curl http://localhost:5555/api/tasks?state=SUCCESS
curl http://localhost:5555/api/tasks?state=FAILURE
curl http://localhost:5555/api/tasks?state=PENDING

# 特定任务
curl http://localhost:5555/api/tasks/<task_id>
```

### 获取队列信息

```bash
curl http://localhost:5555/api/queues
```

### 获取统计信息

```bash
curl http://localhost:5555/api/stats
```

## 故障排查

### 1. Flower 无法启动

```bash
# 检查端口占用
netstat -tulpn | grep 5555

# 检查日志
journalctl -u py-small-admin-flower -n 50

# 检查 broker 连接
celery -A Modules.common.libs.celery.celery_service.celery inspect active
```

### 2. 无法显示任务

```bash
# 确认 Celery 正在运行
ps aux | grep celery

# 检查任务路由配置
celery -A Modules.common.libs.celery.celery_service.celery inspect active_queues

# 重启 Flower
sudo systemctl restart py-small-admin-flower
```

### 3. 认证问题

```bash
# 测试基本认证
curl -u admin:password http://localhost:5555/api/workers

# 重置密码
vim /opt/py-small-admin/server/.env
sudo systemctl restart py-small-admin-flower
```

## 安全建议

1. **启用认证**：始终配置基本认证
2. **使用 HTTPS**：生产环境必须启用 SSL
3. **限制访问**：通过防火墙限制访问来源
4. **定期更新**：保持 Flower 版本最新
5. **监控日志**：定期审查访问日志

## 性能优化

1. **限制任务历史**：设置 `--max_tasks` 避免内存溢出
2. **清理离线 Worker**：设置 `--purge_offline_workers`
3. **使用持久化**：避免重启后丢失数据
4. **配置缓存**：使用 Redis 缓存统计数据
