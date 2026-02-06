# Docker 部署指南

本文档介绍如何使用 Docker 和 Docker Compose 部署 Py Small Admin。

## 部署架构

Docker 部署包含以下容器：

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| mysql | mysql:8.0 | 3306 | 数据库 |
| redis | redis:7-alpine | 6379 | 缓存 |
| rabbitmq | rabbitmq:3.12-management | 5672, 15672 | 消息队列 |
| fastapi | 自定义 | 8009 | 后端 API |
| celery-worker | 自定义 | - | Admin 异步任务处理器 |
| celery-worker-quant | 自定义 | - | Quant 异步任务处理器 |
| celery-beat | 自定义 | - | 定时任务调度器 |
| flower | 自定义 | 5555 | Celery 监控界面 |

## 快速开始

### 1. 前置要求

确保已安装：
- Docker 20.10+
- Docker Compose 2.0+

### 2. 克隆项目

```bash
git clone https://github.com/songbo236589/py-small-admin.git
cd py-small-admin/server/docker
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**必须修改的配置**：

```bash
# 项目名称
PROJECT_NAME=py-small-admin

# MySQL 配置
MYSQL_ROOT_PASSWORD=your_root_password_change_this
MYSQL_DATABASE=py_small_admin
MYSQL_USER=py_admin
MYSQL_PASSWORD=your_mysql_password_change_this

# Redis 配置
REDIS_PASSWORD=your_redis_password_change_this

# RabbitMQ 配置
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password_change_this
RABBITMQ_DEFAULT_VHOST=/

# 应用配置
APP_ADMIN_X_API_KEY=your_admin_api_key_change_this
JWT_SECRET_KEY=your_jwt_secret_key_change_this

# 端口配置（可根据需要修改）
HOST_PORT_FASTAPI=8009
HOST_PORT_MYSQL=3306
HOST_PORT_REDIS=6379
HOST_PORT_RABBITMQ_AMQP=5672
HOST_PORT_RABBITMQ_MGMT=15672
HOST_PORT_FLOWER=5555
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 初始化数据库

```bash
# 进入 fastapi 容器
docker-compose exec fastapi bash

# 执行数据库迁移
alembic upgrade head

# 填充初始数据（可选）
python commands/seed.py

# 退出容器
exit
```

### 6. 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| FastAPI | http://localhost:8009 | 后端 API |
| API 文档 | http://localhost:8009/docs | Swagger 文档 |
| RabbitMQ 管理 | http://localhost:15672 | 用户名/密码：admin/配置的密码 |
| Flower 监控 | http://localhost:5555 | Celery 任务监控 |

## Celery 服务架构

项目采用**分组 Worker 架构**，将不同业务模块的任务分配到独立的 Worker 中处理。

### 架构图

```mermaid
graph TB
    subgraph "定时调度"
        BEAT[celery-beat]
    end

    subgraph "消息队列"
        MQ[RabbitMQ]
    end

    subgraph "Admin 任务处理"
        W1[celery-worker]
    end

    subgraph "Quant 任务处理"
        W2[celery-worker-quant]
    end

    subgraph "监控"
        FLOWER[flower]
    end

    BEAT --> MQ
    W1 --> MQ
    W2 --> MQ
    FLOWER --> MQ

    style W1 fill:#e1f5ff
    style W2 fill:#fff4e1
```

### Worker 说明

#### celery-worker (Admin Worker)

处理 Admin 模块相关的异步任务。

| 配置项 | 值 |
|--------|-----|
| 监听队列 | `default`, `email_queues` |
| Worker 名称 | `worker-admin@%h` |
| 处理任务 | 邮件发送、报表生成等 |

#### celery-worker-quant (Quant Worker)

处理 Quant 模块相关的异步任务。

| 配置项 | 值 |
|--------|-----|
| 监听队列 | `quant_concept_queues`, `quant_industry_queues`, `quant_stock_queues` |
| Worker 名称 | `worker-quant@%h` |
| 处理任务 | 概念同步、行业同步、股票K线同步 |

### 队列配置

在 `.env` 文件中配置队列相关参数：

```bash
# ========== 任务模块配置 ==========
CELERY_INCLUDE_JSON='["Modules.admin.tasks.default_tasks", "Modules.admin.queues.email_queues", "Modules.quant.queues.concept_queues", "Modules.quant.queues.industry_queues", "Modules.quant.queues.stock_queues"]'

# ========== 任务队列配置 ==========
CELERY_TASK_QUEUES_JSON='[
  {"name": "default", "exchange": "default", "routing_key": "default"},
  {"name": "email_queues", "exchange": "email_queues", "routing_key": "email_queues"},
  {"name": "quant_concept_queues", "exchange": "quant_concept_queues", "routing_key": "quant_concept_queues"},
  {"name": "quant_industry_queues", "exchange": "quant_industry_queues", "routing_key": "quant_industry_queues"},
  {"name": "quant_stock_queues", "exchange": "quant_stock_queues", "routing_key": "quant_stock_queues"}
]'

# ========== 任务路由配置 ==========
CELERY_TASK_ROUTES='{
  "Modules.admin.queues.email_queues.send_batch_email_queue": {"queue": "email_queues"},
  "Modules.quant.queues.concept_queues.sync_concept_relation_queue": {"queue": "quant_concept_queues"},
  "Modules.quant.queues.industry_queues.sync_industry_relation_queue": {"queue": "quant_industry_queues"},
  "Modules.quant.queues.stock_queues.sync_stock_kline_1d_queue": {"queue": "quant_stock_queues"}
}'
```

### 扩展 Quant Worker

量化任务可能需要更多 Worker 来处理高负载场景。

```bash
# 扩展到 3 个 quant worker 实例
docker-compose up -d --scale celery-worker-quant=3

# 查看扩展后的实例
docker-compose ps | grep quant

# 重置为单实例
docker-compose up -d --scale celery-worker-quant=1
```

### Celery 日志

```bash
# Admin Worker 日志
docker-compose logs -f celery-worker

# Quant Worker 日志
docker-compose logs -f celery-worker-quant

# Beat 日志
docker-compose logs -f celery-beat

# 所有 Celery 服务日志
docker-compose logs -f celery-worker celery-worker-quant celery-beat
```

### Celery 命令

```bash
# 重启 Celery 服务
docker-compose restart celery-worker celery-worker-quant celery-beat

# 查看 Worker 状态
docker-compose exec celery-worker celery -A Modules.common.libs.celery.app inspect active

# 查看已注册任务
docker-compose exec celery-worker celery -A Modules.common.libs.celery.app inspect registered
```

## 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart fastapi

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]
```

### 数据库操作

```bash
# 进入 MySQL 容器
docker-compose exec mysql bash

# 连接 MySQL
mysql -u root -p

# 备份数据库
docker-compose exec mysql mysqldump -u root -p py_small_admin > backup.sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p py_small_admin < backup.sql
```

### Redis 操作

```bash
# 进入 Redis 容器
docker-compose exec redis bash

# 连接 Redis
redis-cli -a your_redis_password

# 查看 Redis 信息
INFO
```

### 清理和重建

```bash
# 停止并删除所有容器
docker-compose down

# 删除所有容器和数据卷（危险操作！）
docker-compose down -v

# 重新构建镜像
docker-compose build

# 强制重新构建并启动
docker-compose up -d --build
```

## 生产环境部署

### 1. 使用生产环境配置

创建 `docker-compose.prod.yml`：

```yaml
name: py-small-admin-prod

services:
  fastapi:
    environment:
      - APP_DEBUG=false
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  celery-worker:
    deploy:
      replicas: 2
```

启动生产环境：

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 2. 配置反向代理

使用 Nginx 作为反向代理：

```nginx
upstream fastapi_backend {
    server localhost:8009;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /flower {
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 配置 HTTPS

使用 Certbot 获取 SSL 证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. 配置日志

```yaml
services:
  fastapi:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 配置自动重启

```yaml
services:
  fastapi:
    restart: unless-stopped
```

## 数据持久化

数据卷自动挂载到宿主机：

| 容器路径 | 宿主机位置 | 说明 |
|----------|------------|------|
| /var/lib/mysql | Docker 卷 | MySQL 数据 |
| /data | Docker 卷 | Redis 数据 |
| /var/lib/rabbitmq | Docker 卷 | RabbitMQ 数据 |
| /app/uploads | ../uploads | 上传文件 |
| /app/logs | ../logs | 应用日志 |

### 备份数据卷

```bash
# 备份 MySQL 数据
docker run --rm --volumes-from py-small-admin-mysql -v $(pwd):/backup ubuntu tar czf /backup/mysql-backup.tar.gz /var/lib/mysql

# 备份上传文件
tar czf uploads-backup.tar.gz uploads/
```

## 故障排查

### 1. 容器启动失败

```bash
# 查看容器日志
docker-compose logs [service_name]

# 检查容器状态
docker-compose ps

# 进入容器排查
docker-compose exec [service_name] bash
```

### 2. 数据库连接失败

```bash
# 检查 MySQL 是否健康
docker-compose ps mysql

# 查看 MySQL 日志
docker-compose logs mysql

# 检查网络连接
docker-compose exec fastapi ping mysql -c 3
```

### 3. Redis 连接失败

```bash
# 检查 Redis 是否健康
docker-compose ps redis

# 测试 Redis 连接
docker-compose exec redis redis-cli -a your_password ping
```

### 4. 内存不足

```bash
# 查看容器资源使用
docker stats

# 限制容器内存
docker-compose up -d --scale fastapi=2
```

## 性能优化

### 1. 启用 Docker BuildKit

```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build
```

### 2. 使用多阶段构建

已在 Dockerfile 中配置，减小镜像体积。

### 3. 配置资源限制

```yaml
services:
  fastapi:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

### 4. 启用健康检查

所有服务已配置健康检查，确保服务可用性。

### 5. 使用外部数据库

生产环境建议使用外部托管数据库，修改 `.env`：

```bash
DB_DEFAULT=mysql://user:pass@external-host:3306/dbname
REDIS_DEFAULT=redis://external-host:6379/0
```
