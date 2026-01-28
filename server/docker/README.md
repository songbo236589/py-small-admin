# Py Small Admin Docker 部署文档

## 📋 目录

- [项目概述](#项目概述)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [常用命令](#常用命令)
- [服务说明](#服务说明)
- [配置说明](#配置说明)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

---

## 项目概述

本项目是一个基于 FastAPI 的管理系统，使用 Docker Compose 进行容器化部署。

### 技术栈

- **后端框架**: FastAPI 0.124.2
- **数据库**: MySQL 8.0
- **缓存**: Redis 7
- **消息队列**: RabbitMQ 3.12
- **异步任务**: Celery 5.6.2
- **任务监控**: Flower
- **反向代理**: Nginx (生产环境)

### 服务架构

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose 网络                   │
├─────────────────────────────────────────────────────────┤
│  1. FastAPI应用 (主服务) - 端口: 8009                   │
│  2. Celery Worker (异步任务)                            │
│  3. Celery Beat (定时任务)                              │
│  4. Flower监控 (可选) - 端口: 5555                      │
│  5. MySQL数据库 - 端口: 3306                           │
│  6. Redis缓存 - 端口: 6379                             │
│  7. RabbitMQ消息队列 - 端口: 5672, 15672                │
│  8. Nginx反向代理 (生产环境) - 端口: 80, 443            │
└─────────────────────────────────────────────────────────┘
```

---

## 环境要求

### 系统要求

- **操作系统**: Linux, macOS, Windows (with WSL2)
- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 10GB 可用空间

### 安装Docker

#### Linux (Ubuntu/Debian)

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y ca-certificates curl gnupg

# 添加Docker官方GPG密钥
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 设置Docker仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

#### macOS

```bash
# 使用Homebrew安装
brew install --cask docker

# 或下载Docker Desktop for Mac
# https://www.docker.com/products/docker-desktop
```

#### Windows

```bash
# 下载Docker Desktop for Windows
# https://www.docker.com/products/docker-desktop

# 确保启用WSL2
wsl --install
```

### 检查安装

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker-compose --version
```

### 系统资源建议

- **CPU**: 4核或以上
- **内存**: 8GB 或以上
- **磁盘**: 20GB 或以上

---

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd py-small-admin/server
```

### 2. 配置环境变量

```bash
# 进入 docker 目录
cd docker

# 复制环境变量示例文件
cp .env.example .env

# 根据需要修改 .env 文件
vim .env
```

### 3. 启动服务

```bash
# 使用启动脚本（推荐）
./start.sh

# 或使用docker-compose
docker-compose up -d
```

### 4. 验证服务

访问以下URL验证服务是否正常运行：

- FastAPI: http://localhost:8009
- API文档: http://localhost:8009/docs
- RabbitMQ管理界面: http://localhost:15672 (admin/admin123)
- Flower监控: http://localhost:5555 (admin/123456)

### 5. 停止服务

```bash
# 使用停止脚本
./stop.sh

# 或手动停止
docker-compose down

# 停止并删除数据卷（慎用）
docker-compose down -v
```

---

## 开发环境部署

### 步骤1: 准备配置

```bash
# 进入docker目录
cd docker

# 创建开发环境配置
cp .env.example .env

# 编辑配置文件（可选）
vim .env
```

### 步骤2: 启动服务

```bash
# 使用启动脚本
./start.sh dev

# 或手动启动
docker-compose up -d
```

### 步骤3: 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fastapi
docker-compose logs -f mysql
docker-compose logs -f redis
docker-compose logs -f rabbitmq
```

### 步骤4: 执行数据库迁移

```bash
# 进入 FastAPI 容器
docker-compose exec fastapi bash

# 执行迁移
alembic upgrade head

# 退出容器
exit
```

### 步骤5: 填充初始数据

```bash
# 进入 FastAPI 容器
docker-compose exec fastapi bash

# 填充数据
python commands/seed.py

# 退出容器
exit
```

### 步骤6: 停止服务

```bash
# 使用停止脚本
./stop.sh dev

# 或手动停止
docker-compose down
```

### 开发模式特性

- **自动重载**: 代码变更后自动重启（需在 .env 中设置 `APP_RELOAD=true`）
- **详细日志**: 显示所有调试信息
- **API 文档**: 默认开启
- **端口暴露**: 所有服务端口都暴露到主机

### 常用开发命令

```bash
# 查看某个服务的日志
docker-compose logs -f fastapi
docker-compose logs -f celery-worker

# 重启某个服务
docker-compose restart fastapi

# 进入某个服务的容器
docker-compose exec fastapi bash

# 重新构建某个服务
docker-compose build fastapi
docker-compose up -d fastapi
```

---

## 生产环境部署

### 步骤1: 准备生产环境配置

```bash
# 进入docker目录
cd docker

# 复制环境变量示例文件
cp .env.production.example .env.production

# 编辑生产环境配置（必须修改所有密码和密钥）
vim .env.production
```

**重要配置项**：

```bash
# 修改以下配置为强密码
DB_CONNECTIONS__MYSQL__PASSWORD=your_strong_password
DB_REDIS__DEFAULT__PASSWORD=your_strong_password
JWT_SECRET_KEY=your_very_long_secret_key_at_least_32_chars
APP_ADMIN_X_API_KEY=your_strong_api_key
CELERY_FLOWER_BASIC_AUTH=admin:your_strong_password
```

### 步骤2: 配置SSL证书

```bash
# 创建 SSL 证书目录
mkdir -p nginx/ssl

# 将证书文件复制到该目录
# cert.pem - SSL 证书
# key.pem - 私钥文件
```

#### 获取SSL证书的方式

##### 方式1: 使用Let's Encrypt（推荐，免费）

```bash
# 安装certbot
sudo apt-get update
sudo apt-get install certbot

# 生成证书（需要域名和DNS解析）
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 复制证书到此目录
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/key.pem

# 设置权限
chmod 644 docker/nginx/ssl/cert.pem
chmod 600 docker/nginx/ssl/key.pem
```

##### 方式2: 使用自签名证书（仅用于测试）

```bash
# 生成自签名证书（有效期365天）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/OU=IT/CN=localhost"

# 设置权限
chmod 644 docker/nginx/ssl/cert.pem
chmod 600 docker/nginx/ssl/key.pem
```

##### 方式3: 使用商业证书

1. 从CA机构购买SSL证书
2. 下载证书文件（通常是.crt或.pem格式）
3. 将证书文件重命名为 `cert.pem`
4. 将私钥文件重命名为 `key.pem`
5. 放置到此目录

#### SSL证书安全注意事项

1. **私钥保护**: 私钥文件（`key.pem`）权限应设置为 `600`，仅允许所有者读取
2. **不要提交到版本控制**: 将此目录添加到 `.gitignore`，避免私钥泄露
3. **定期更新**: Let's Encrypt证书有效期90天，需要定期更新
4. **备份**: 证书和私钥文件应妥善备份

#### 自动更新证书（Let's Encrypt）

使用cron定时任务自动更新证书：

```bash
# 编辑crontab
crontab -e

# 添加以下内容（每周一凌晨3点更新）
0 3 * * 1 certbot renew --quiet && cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /path/to/docker/nginx/ssl/cert.pem && cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /path/to/docker/nginx/ssl/key.pem && docker-compose -f docker-compose.prod.yml restart nginx
```

### 步骤3: 执行数据库迁移

```bash
# 进入MySQL容器
docker exec -it py-small-admin-mysql-prod mysql -uroot -p

# 执行迁移脚本
# 或使用Alembic
docker exec -it py-small-admin-fastapi-prod alembic upgrade head
```

### 步骤4: 启动服务

```bash
# 使用启动脚本
./start.sh prod

# 或手动启动
docker-compose -f docker-compose.prod.yml up -d
```

### 步骤5: 验证服务

```bash
# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 测试API
curl https://yourdomain.com/api/health
```

### 步骤6: 配置反向代理（可选）

如果使用Nginx作为反向代理：

```bash
# Nginx已在docker-compose.prod.yml中配置
# 确保SSL证书已正确放置
```

### 生产环境特性

- **资源限制**: 每个服务都有 CPU 和内存限制
- **日志管理**: 自动轮转，限制日志大小
- **健康检查**: 所有服务都有健康检查
- **自动重启**: 服务异常退出后自动重启
- **安全加固**: 不暴露数据库和缓存端口到主机
- **Nginx 反向代理**: 提供 SSL 终止和负载均衡

### 扩展 Celery Worker

```bash
# 扩展到 3 个 Worker 实例
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3

# 查看扩展后的状态
docker-compose -f docker-compose.prod.yml ps
```

---

## 常用命令

### Docker Compose 基础命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启所有服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]

# 查看所有服务日志
docker-compose logs -f

# 进入服务容器
docker-compose exec [service_name] bash

# 重新构建服务
docker-compose build [service_name]

# 删除所有容器和数据卷（慎用）
docker-compose down -v
```

### 服务管理

```bash
# 启动服务
./start.sh [dev|prod]

# 停止服务
./stop.sh [dev|prod]

# 重启服务
docker-compose restart [service_name]

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]
```

### 数据库相关命令

```bash
# 备份 MySQL 数据库
docker-compose exec mysql mysqldump -u root -proot123456 fastapi_db > backup.sql

# 恢复 MySQL 数据库
docker-compose exec -T mysql mysql -u root -proot123456 fastapi_db < backup.sql

# 进入 MySQL 命令行
docker-compose exec mysql mysql -u root -proot123456

# 执行数据库迁移
docker-compose exec fastapi alembic upgrade head

# 回滚数据库迁移
docker-compose exec fastapi alembic downgrade -1

# 使用备份脚本
./backup.sh backup [dev|prod]
./backup.sh restore [dev|prod] /path/to/backup.sql.gz
./backup.sh list [dev|prod]
```

### MySQL初始化说明

MySQL容器首次启动时会自动执行 `mysql-init/init.sql` 脚本。

**自动执行**：
```bash
# 启动MySQL容器
docker-compose up -d mysql

# 查看初始化日志
docker-compose logs mysql
```

**手动执行**（如果需要重新执行初始化脚本）：
```bash
# 方法1: 进入MySQL容器执行
docker exec -it py-small-admin-mysql mysql -uroot -proot123456 < docker/mysql-init/init.sql

# 方法2: 使用docker exec
docker exec -i py-small-admin-mysql mysql -uroot -proot123456 < docker/mysql-init/init.sql

# 方法3: 复制文件到容器后执行
docker cp docker/mysql-init/init.sql py-small-admin-mysql:/tmp/init.sql
docker exec -it py-small-admin-mysql mysql -uroot -proot123456 -e "source /tmp/init.sql"
```

**重新执行初始化脚本**：
```bash
# 停止容器
docker-compose down

# 删除数据卷（警告：会丢失所有数据）
docker volume rm docker_mysql_data

# 重新启动
docker-compose up -d mysql
```

### Redis 相关命令

```bash
# 进入 Redis 命令行
docker-compose exec redis redis-cli -a redis123456

# 清空 Redis 缓存
docker-compose exec redis redis-cli -a redis123456 FLUSHDB

# 清空所有 Redis 数据
docker-compose exec redis redis-cli -a redis123456 FLUSHALL
```

### Celery 相关命令

```bash
# 查看 Celery Worker 状态
docker-compose exec celery-worker celery -A Modules.common.libs.celery.celery_service.celery_app inspect active

# 查看 Celery 队列状态
docker-compose exec celery-worker celery -A Modules.common.libs.celery.celery_service.celery_app inspect registered

# 清空 Celery 队列
docker-compose exec celery-worker celery -A Modules.common.libs.celery.celery_service.celery_app purge
```

### 日志查看

```bash
# 查看 FastAPI 日志
docker-compose logs -f fastapi

# 查看 Celery Worker 日志
docker-compose logs -f celery-worker

# 查看 MySQL 日志
docker-compose logs -f mysql

# 查看最近 100 行日志
docker-compose logs --tail=100 fastapi

# 查看特定时间的日志
docker-compose logs --since="2024-01-01T00:00:00" fastapi
```

### 容器管理

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 进入容器
docker exec -it <container_name> /bin/bash

# 查看容器资源使用
docker stats

# 清理未使用的资源
./clean.sh

# 清理所有资源（包括数据）
./clean.sh --all
```

### 镜像管理

```bash
# 查看镜像
docker images

# 构建镜像
docker-compose build [service_name]

# 拉取最新镜像
docker-compose pull

# 删除未使用的镜像
docker image prune -a
```

---

## 服务说明

### FastAPI 应用

- **端口**: 8009
- **功能**: 提供 REST API 服务
- **依赖**: MySQL, Redis, RabbitMQ
- **健康检查**: http://localhost:8009/

### Celery Worker

- **功能**: 处理异步任务
- **依赖**: RabbitMQ, Redis, MySQL
- **队列**: default, email_queues, quant_concept_queues, quant_industry_queues, quant_stock_queues
- **并发数**: 4 (可配置)

### Celery Beat

- **功能**: 定时任务调度
- **依赖**: RabbitMQ
- **配置**: 支持 crontab 表达式

### Flower

- **端口**: 5555
- **功能**: Celery 任务监控 Web 界面
- **认证**: admin:123456
- **依赖**: RabbitMQ

### MySQL

- **端口**: 3306
- **版本**: 8.0
- **字符集**: utf8mb4
- **数据持久化**: 是

### Redis

- **端口**: 6379
- **版本**: 7
- **认证**: 需要密码
- **数据持久化**: 是

### RabbitMQ

- **端口**: 5672 (AMQP), 15672 (管理界面)
- **版本**: 3.12
- **管理界面**: http://localhost:15672
- **用户**: admin / admin123

### Nginx (生产环境)

- **端口**: 80 (HTTP), 443 (HTTPS)
- **功能**: 反向代理、SSL 终止、静态文件服务
- **依赖**: FastAPI

---

## 配置说明

### 环境变量文件

- **`.env`**: 开发环境配置
- **`.env.example`**: 环境变量示例
- **`.env.production`**: 生产环境配置

### MySQL 配置文件

MySQL 使用配置文件 [`mysql/my.cnf`](mysql/my.cnf:1) 进行高级配置，该文件已挂载到容器中。

**配置文件位置**: `docker/mysql/my.cnf`

**主要配置项**:
- **字符集**: utf8mb4
- **连接数**: 最大500个连接
- **InnoDB 缓冲池**: 512MB（开发环境），可根据服务器内存调整
- **慢查询日志**: 启用，阈值2秒
- **二进制日志**: 启用，保留7天
- **时区**: Asia/Shanghai

**修改配置后重启服务**:
```bash
docker-compose restart mysql
```

**生产环境优化建议**:
- 根据服务器内存调整 `innodb_buffer_pool_size`（建议为物理内存的50-70%）
- 根据业务需求调整 `max_connections`
- 定期检查慢查询日志优化SQL

### Redis 配置文件

Redis 使用配置文件 [`redis/redis.conf`](redis/redis.conf:1) 进行高级配置，该文件已挂载到容器中。

**配置文件位置**: `docker/redis/redis.conf`

**主要配置项**:
- **密码认证**: requirepass redis123456
- **持久化**: 启用AOF和RDB
- **内存限制**: 512MB，淘汰策略 allkeys-lru
- **慢查询日志**: 启用，阈值10毫秒
- **数据庂数量**: 16个

**修改配置后重启服务**:
```bash
docker-compose restart redis
```

**生产环境优化建议**:
- 根据服务器内存调整 `maxmemory`
- 根据业务需求选择合适的 `maxmemory-policy`
- 定期监控Redis内存使用情况

### RabbitMQ 配置文件

RabbitMQ 使用配置文件 [`rabbitmq/rabbitmq.conf`](rabbitmq/rabbitmq.conf:1) 进行高级配置，该文件已挂载到容器中。

**配置文件位置**: `docker/rabbitmq/rabbitmq.conf`

**主要配置项**:
- **网络配置**: 监听端口5672（AMQP）、15672（管理界面）
- **内存管理**: 内存高水位线40%，低水位线20%
- **磁盘管理**: 磁盘限制2GB，警报阈值50%
- **连接配置**: 最大连接数2048，心跳60秒
- **队列配置**: 默认队列模式，消息持久化
- **插件配置**: 管理界面、Shovel、联邦、STOMP、MQTT等
- **日志配置**: 日志级别info，文件轮转

**修改配置后重启服务**:
```bash
docker-compose restart rabbitmq
```

**生产环境优化建议**:
- 根据服务器性能调整`channel_max`
- 根据业务需求调整`vm_memory_high_watermark.relative`
- 定期检查磁盘空间，避免磁盘满导致消息丢失
- 考虑使用RabbitMQ Cluster提高可用性
- 启用SSL/TLS加密（生产环境强烈建议）

### 关键配置项

#### 应用配置

```bash
APP_ENV=development              # 运行环境
APP_DEBUG=true                   # 调试模式
APP_PORT=8009                    # 服务端口
APP_API_PREFIX=/api              # API 前缀
```

#### 数据库配置

```bash
# MySQL
DB_CONNECTIONS__MYSQL__HOST=mysql
DB_CONNECTIONS__MYSQL__PORT=3306
DB_CONNECTIONS__MYSQL__DATABASE=fastapi_db
DB_CONNECTIONS__MYSQL__USERNAME=root
DB_CONNECTIONS__MYSQL__PASSWORD=root123456

# Redis
DB_REDIS__DEFAULT__HOST=redis
DB_REDIS__DEFAULT__PORT=6379
DB_REDIS__DEFAULT__PASSWORD=redis123456
```

#### Celery 配置

```bash
CELERY_BROKER_URL=amqp://admin:admin123@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://:redis123456@redis:6379/0
CELERY_WORKER_CONCURRENCY=4
```

---

## 故障排查

### 常见问题

#### Q1: Docker命令找不到

**症状**: 执行`docker`或`docker-compose`命令时提示"command not found"

**原因**: Docker未安装或未添加到PATH

**解决方案**:

```bash
# 检查Docker是否安装
which docker
which docker-compose

# 如果未安装，请参考部署指南安装Docker
# https://docs.docker.com/get-docker/

# 如果已安装但找不到，重启终端或重新登录
```

#### Q2: 权限不足

**症状**: 执行Docker命令时提示"permission denied"

**原因**: 当前用户不在docker组中

**解决方案**:

```bash
# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker

# 验证
docker ps
```

#### Q3: 端口已被占用

**症状**: 启动服务时提示"port is already allocated"

**原因**: 端口已被其他服务占用

**解决方案**:

```bash
# 查看端口占用
netstat -tuln | grep <port>
# 或
lsof -i :<port>

# 方法1: 停止占用端口的服务
sudo systemctl stop <service_name>

# 方法2: 修改docker-compose.yml中的端口映射
vim docker-compose.yml
# 将 "8009:8009" 改为 "8010:8009"

# 方法3: 杀死占用端口的进程
sudo kill -9 <pid>
```

#### Q4: 内存不足

**症状**: 容器启动失败或被OOM Killer杀死

**原因**: 系统内存不足

**解决方案**:

```bash
# 查看内存使用
free -h

# 查看Docker资源使用
docker stats

# 方法1: 增加系统交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 方法2: 限制容器内存使用
# 编辑docker-compose.yml
services:
  fastapi:
    deploy:
      resources:
        limits:
          memory: 1G

# 方法3: 减少并发worker数量
# 编辑.env文件
FASTAPI_WORKERS=1
CELERY_WORKER_CONCURRENCY=2
```

### 服务问题

#### MySQL服务问题

##### 问题1: MySQL容器无法启动

**症状**: MySQL容器反复重启

**诊断**:

```bash
# 查看容器状态
docker-compose ps mysql

# 查看容器日志
docker-compose logs mysql

# 查看详细日志
docker-compose logs --tail=100 mysql
```

**常见原因及解决方案**:

1. **数据目录权限问题**

```bash
# 停止容器
docker-compose down

# 删除数据卷（警告：会丢失数据）
docker volume rm docker_mysql_data

# 重新启动
docker-compose up -d
```

2. **配置文件错误**

```bash
# 检查配置文件
cat docker/mysql/my.cnf

# 验证配置
docker run --rm -v $(pwd)/docker/mysql/my.cnf:/etc/mysql/conf.d/custom.cnf:ro mysql:8.0 --help
```

3. **内存不足**

```bash
# 检查系统内存
free -h

# 调整MySQL配置
vim docker/mysql/my.cnf
# 减少 innodb_buffer_pool_size
innodb_buffer_pool_size=256M
```

##### 问题2: 无法连接到MySQL

**症状**: 应用提示"Can't connect to MySQL server"

**诊断**:

```bash
# 测试MySQL连接
docker exec -it py-small-admin-mysql mysql -uroot -proot123456 -e "SELECT 1"

# 检查网络连接
docker network inspect py-small-admin-network

# 检查端口映射
docker port py-small-admin-mysql
```

**解决方案**:

1. **检查环境变量**

```bash
# 确认MySQL配置
cat .env | grep DB_CONNECTIONS__MYSQL

# 确保使用服务名而不是localhost
DB_CONNECTIONS__MYSQL__HOST=mysql
```

2. **检查防火墙**

```bash
# 检查防火墙状态
sudo ufw status

# 如果需要，开放端口
sudo ufw allow 3306
```

3. **检查MySQL用户权限**

```bash
# 进入MySQL容器
docker exec -it py-small-admin-mysql mysql -uroot -p

# 检查用户权限
SELECT user, host FROM mysql.user;
SHOW GRANTS FOR 'fastapi_user'@'%';

# 重新授权
GRANT ALL PRIVILEGES ON fastapi_db.* TO 'fastapi_user'@'%';
FLUSH PRIVILEGES;
```

#### Redis服务问题

##### 问题1: Redis容器无法启动

**症状**: Redis容器反复重启

**诊断**:

```bash
# 查看容器日志
docker-compose logs redis

# 查看详细日志
docker-compose logs --tail=100 redis
```

**解决方案**:

1. **配置文件错误**

```bash
# 检查配置文件
cat docker/redis/redis.conf

# 验证配置
docker run --rm -v $(pwd)/docker/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro redis:7-alpine redis-server /usr/local/etc/redis/redis.conf --test-memory 1
```

2. **数据目录权限问题**

```bash
# 停止容器
docker-compose down

# 删除数据卷
docker volume rm docker_redis_data

# 重新启动
docker-compose up -d
```

##### 问题2: 无法连接到Redis

**症状**: 应用提示"Error connecting to Redis"

**诊断**:

```bash
# 测试Redis连接
docker exec -it py-small-admin-redis redis-cli -a redis123456 ping

# 检查网络连接
docker network inspect py-small-admin-network
```

**解决方案**:

1. **检查密码配置**

```bash
# 确认Redis配置
cat .env | grep DB_REDIS

# 确保密码一致
DB_REDIS__DEFAULT__PASSWORD=redis123456
```

2. **检查Redis配置**

```bash
# 检查redis.conf中的密码设置
cat docker/redis/redis.conf | grep requirepass
```

#### RabbitMQ服务问题

##### 问题1: RabbitMQ容器无法启动

**症状**: RabbitMQ容器反复重启

**诊断**:

```bash
# 查看容器日志
docker-compose logs rabbitmq

# 查看详细日志
docker-compose logs --tail=100 rabbitmq
```

**解决方案**:

1. **配置文件错误**

```bash
# 检查配置文件
cat docker/rabbitmq/rabbitmq.conf

# 临时禁用配置文件测试
# 编辑docker-compose.yml，注释掉配置文件挂载
# volumes:
#   - ./rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
```

2. **数据目录权限问题**

```bash
# 停止容器
docker-compose down

# 删除数据卷
docker volume rm docker_rabbitmq_data

# 重新启动
docker-compose up -d
```

##### 问题2: 无法连接到RabbitMQ

**症状**: Celery提示"Error connecting to RabbitMQ"

**诊断**:

```bash
# 测试RabbitMQ连接
docker exec -it py-small-admin-rabbitmq rabbitmq-diagnostics -q ping

# 检查RabbitMQ状态
docker exec -it py-small-admin-rabbitmq rabbitmqctl status
```

**解决方案**:

1. **检查环境变量**

```bash
# 确认RabbitMQ配置
cat .env | grep CELERY_BROKER

# 确保使用服务名
CELERY_BROKER_HOST=rabbitmq
```

2. **检查RabbitMQ用户**

```bash
# 列出所有用户
docker exec -it py-small-admin-rabbitmq rabbitmqctl list_users

# 重新创建用户
docker exec -it py-small-admin-rabbitmq rabbitmqctl add_user admin admin123
docker exec -it py-small-admin-rabbitmq rabbitmqctl set_user_tags admin administrator
docker exec -it py-small-admin-rabbitmq rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

#### FastAPI服务问题

##### 问题1: FastAPI容器无法启动

**症状**: FastAPI容器反复重启

**诊断**:

```bash
# 查看容器日志
docker-compose logs fastapi

# 查看详细日志
docker-compose logs --tail=100 fastapi

# 进入容器查看
docker exec -it py-small-admin-fastapi /bin/bash
```

**解决方案**:

1. **依赖服务未就绪**

```bash
# 检查依赖服务状态
docker-compose ps mysql redis rabbitmq

# 等待依赖服务启动
# 或在.env中设置
WAIT_FOR_DEPENDENCIES=true
```

2. **应用代码错误**

```bash
# 查看应用日志
docker-compose logs fastapi

# 检查Python语法错误
docker exec -it py-small-admin-fastapi python -m py_compile Modules/main.py

# 检查导入错误
docker exec -it py-small-admin-fastapi python -c "from Modules.main import app"
```

3. **环境变量错误**

```bash
# 检查环境变量
docker exec -it py-small-admin-fastapi env | grep APP_

# 确认.env文件存在
ls -la .env
```

##### 问题2: API请求超时

**症状**: API请求响应慢或超时

**诊断**:

```bash
# 查看容器资源使用
docker stats py-small-admin-fastapi

# 查看应用日志
docker-compose logs -f fastapi

# 测试API响应
time curl http://localhost:8009/api/health
```

**解决方案**:

1. **增加worker数量**

```bash
# 编辑.env文件
FASTAPI_WORKERS=4
```

2. **优化数据库查询**

```bash
# 查看慢查询日志
docker exec -it py-small-admin-mysql mysql -uroot -p -e "SHOW VARIABLES LIKE 'slow_query_log';"
docker exec -it py-small-admin-mysql tail -f /var/log/mysql/slow.log
```

3. **启用缓存**

```bash
# 确认Redis缓存配置
cat .env | grep CACHE
```

#### Celery服务问题

##### 问题1: Celery Worker无法启动

**症状**: Celery Worker容器反复重启

**诊断**:

```bash
# 查看容器日志
docker-compose logs celery-worker

# 查看详细日志
docker-compose logs --tail=100 celery-worker
```

**解决方案**:

1. **RabbitMQ连接失败**

```bash
# 检查RabbitMQ状态
docker-compose ps rabbitmq

# 测试RabbitMQ连接
docker exec -it py-small-admin-rabbitmq rabbitmq-diagnostics -q ping
```

2. **Celery配置错误**

```bash
# 检查Celery配置
cat .env | grep CELERY

# 验证Celery应用
docker exec -it py-small-admin-celery-worker python -c "from Modules.common.libs.celery.celery_service import celery_app; print(celery_app)"
```

##### 问题2: 任务不执行

**症状**: Celery任务提交但不执行

**诊断**:

```bash
# 查看Celery Worker日志
docker-compose logs -f celery-worker

# 检查队列状态
docker exec -it py-small-admin-rabbitmq rabbitmqctl list_queues

# 检查Worker状态
docker exec -it py-small-admin-celery-worker celery -A Modules.common.libs.celery.celery_service.celery_app inspect active
```

**解决方案**:

1. **检查队列配置**

```bash
# 确认任务路由配置
cat .env | grep CELERY_TASK_ROUTES
```

2. **检查Worker队列**

```bash
# 确认Worker监听的队列
cat .env | grep CELERY_WORKER_QUEUES
```

3. **重启Celery Worker**

```bash
# 重启Worker
docker-compose restart celery-worker
```

### 网络问题

#### 问题1: 容器间无法通信

**症状**: 容器A无法访问容器B的服务

**诊断**:

```bash
# 检查网络
docker network ls
docker network inspect py-small-admin-network

# 检查容器网络
docker inspect py-small-admin-fastapi | grep -A 10 Networks
```

**解决方案**:

1. **确保容器在同一网络**

```bash
# 查看容器网络
docker inspect py-small-admin-fastapi | grep NetworkMode
docker inspect py-small-admin-mysql | grep NetworkMode

# 如果不在同一网络，重新创建
docker-compose down
docker-compose up -d
```

2. **使用服务名而不是IP**

```bash
# 错误：使用IP
DB_CONNECTIONS__MYSQL__HOST=172.18.0.2

# 正确：使用服务名
DB_CONNECTIONS__MYSQL__HOST=mysql
```

#### 问题2: 无法从主机访问容器

**症状**: 主机无法访问容器暴露的端口

**诊断**:

```bash
# 检查端口映射
docker port py-small-admin-fastapi

# 检查防火墙
sudo ufw status

# 测试端口连接
telnet localhost 8009
# 或
nc -zv localhost 8009
```

**解决方案**:

1. **检查端口映射**

```bash
# 确认docker-compose.yml中的端口映射
ports:
  - "8009:8009"
```

2. **检查防火墙**

```bash
# 开放端口
sudo ufw allow 8009

# 或临时关闭防火墙测试
sudo ufw disable
```

3. **检查容器监听地址**

```bash
# 确保应用监听0.0.0.0而不是127.0.0.1
APP_HOST=0.0.0.0
```

### 存储问题

#### 问题1: 磁盘空间不足

**症状**: Docker占用过多磁盘空间

**诊断**:

```bash
# 查看Docker磁盘使用
docker system df

# 查看各容器磁盘使用
docker ps -s
```

**解决方案**:

1. **清理未使用的资源**

```bash
# 使用清理脚本
./clean.sh

# 或手动清理
docker system prune -a --volumes
```

2. **清理日志**

```bash
# 清理容器日志
docker-compose down
docker volume prune

# 配置日志轮转（已在docker-compose.prod.yml中配置）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

3. **清理数据库**

```bash
# 备份数据库
./backup.sh backup

# 清理旧数据
docker exec -it py-small-admin-mysql mysql -uroot -p -e "DELETE FROM fa_admin_log WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);"
```

#### 问题2: 数据卷权限问题

**症状**: 容器无法写入数据卷

**诊断**:

```bash
# 查看数据卷
docker volume ls
docker volume inspect docker_mysql_data

# 查看数据卷挂载
docker inspect py-small-admin-mysql | grep -A 10 Mounts
```

**解决方案**:

1. **修复数据卷权限**

```bash
# 停止容器
docker-compose down

# 删除数据卷
docker volume rm docker_mysql_data

# 重新启动
docker-compose up -d
```

2. **调整挂载目录权限**

```bash
# 如果使用bind mount
sudo chown -R 999:999 ./mysql-data
# MySQL容器用户ID通常是999
```

### 性能问题

#### 问题1: 服务响应慢

**症状**: API请求响应时间长

**诊断**:

```bash
# 查看容器资源使用
docker stats

# 查看应用日志
docker-compose logs -f fastapi

# 测试API响应时间
time curl http://localhost:8009/api/health
```

**解决方案**:

1. **增加资源限制**

```yaml
# 编辑docker-compose.yml
services:
  fastapi:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

2. **优化数据库**

```bash
# 查看慢查询
docker exec -it py-small-admin-mysql mysql -uroot -p -e "SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;"

# 优化MySQL配置
vim docker/mysql/my.cnf
innodb_buffer_pool_size=1G
```

3. **启用缓存**

```bash
# 确认Redis缓存配置
cat .env | grep CACHE

# 检查Redis命中率
docker exec -it py-small-admin-redis redis-cli -a redis123456 INFO stats | grep keyspace
```

#### 问题2: 高CPU使用率

**症状**: 容器CPU使用率持续过高

**诊断**:

```bash
# 查看容器资源使用
docker stats

# 查看进程详情
docker exec -it py-small-admin-fastapi top
```

**解决方案**:

1. **减少worker数量**

```bash
# 编辑.env文件
FASTAPI_WORKERS=2
CELERY_WORKER_CONCURRENCY=2
```

2. **优化代码**

```bash
# 查看应用日志，查找耗时操作
docker-compose logs -f fastapi

# 使用性能分析工具
# 如：cProfile, py-spy
```

3. **启用连接池**

```bash
# 优化数据库连接池配置
DB_REDIS__DEFAULT__MAX_CONNECTIONS=50
```

### 安全问题

#### 问题1: 默认密码未修改

**症状**: 使用默认密码

**风险**: 高风险，容易被攻击

**解决方案**:

```bash
# 修改所有默认密码
vim .env.production

# 必须修改的密码：
# - DB_CONNECTIONS__MYSQL__PASSWORD
# - DB_REDIS__DEFAULT__PASSWORD
# - JWT_SECRET_KEY
# - APP_ADMIN_X_API_KEY
# - CELERY_FLOWER_BASIC_AUTH
```

#### 问题2: 端口暴露

**症状**: 数据库端口暴露到公网

**风险**: 数据泄露风险

**解决方案**:

```bash
# 生产环境不暴露数据库端口
# 编辑docker-compose.prod.yml
# 注释掉以下行：
# ports:
#   - "3306:3306"
#   - "6379:6379"
```

#### 问题3: 日志包含敏感信息

**症状**: 日志中包含密码、密钥等敏感信息

**风险**: 信息泄露风险

**解决方案**:

```bash
# 检查日志
docker-compose logs | grep -i password

# 确保不在日志中打印敏感信息
# 修改代码，使用环境变量而不是硬编码
```

---

## 最佳实践

### 1. 安全建议

- **修改默认密码**: 修改所有服务的默认密码
- **使用强密码**: 生产环境使用强密码
- **限制端口暴露**: 生产环境不暴露数据库和缓存端口
- **启用 SSL**: 生产环境必须启用 HTTPS
- **定期更新**: 定期更新 Docker 镜像和依赖包
- **备份数据**: 定期备份数据库和重要数据

### 2. 性能优化

- **调整 Worker 数量**: 根据任务负载调整 Celery Worker 数量
- **配置连接池**: 优化数据库和 Redis 连接池配置
- **启用缓存**: 合理使用 Redis 缓存
- **使用 CDN**: 静态文件使用 CDN 加速
- **数据库索引**: 确保数据库有合适的索引

### 3. 监控建议

- **监控服务状态**: 使用健康检查监控服务状态
- **监控资源使用**: 监控 CPU、内存、磁盘使用情况
- **监控任务队列**: 使用 Flower 监控 Celery 任务
- **日志收集**: 使用 ELK Stack 或类似工具收集日志
- **告警配置**: 配置告警规则，及时发现问题

### 4. 备份策略

- **数据库备份**: 每天备份 MySQL 数据库
- **配置文件备份**: 备份环境变量和配置文件
- **数据卷备份**: 定期备份 Docker 数据卷
- **异地备份**: 重要数据异地备份

### 5. 运维建议

- **版本管理**: 使用 Git 管理配置文件
- **文档更新**: 及时更新部署文档
- **变更记录**: 记录所有配置变更
- **测试环境**: 在测试环境验证后再部署到生产环境
- **灰度发布**: 使用灰度发布降低风险

---

## 附录

### 端口映射表

| 服务 | 开发环境端口 | 生产环境端口 | 说明 |
|------|-------------|-------------|------|
| FastAPI | 8009 | 8009 | API 服务 |
| Flower | 5555 | 5555 | Celery 监控 |
| MySQL | 3306 | 不暴露 | 数据库 |
| Redis | 6379 | 不暴露 | 缓存 |
| RabbitMQ | 5672, 15672 | 15672 | 消息队列 |
| Nginx | 不使用 | 80, 443 | 反向代理 |

### 目录结构

```
docker/
├── .env.example              # 环境变量示例
├── docker-compose.yml        # 开发环境编排
├── docker-compose.prod.yml   # 生产环境编排
├── Dockerfile               # 应用镜像构建文件
├── entrypoint.sh            # 容器启动脚本
├── mysql/
│   └── my.cnf            # MySQL 配置文件
├── mysql-init/
│   └── init.sql          # MySQL 初始化脚本
├── redis/
│   └── redis.conf         # Redis 配置文件
├── rabbitmq/
│   └── rabbitmq.conf      # RabbitMQ 配置文件
├── nginx/
│   ├── Dockerfile           # Nginx 镜像构建文件
│   └── nginx.conf          # Nginx 配置文件
└── README.md               # 本文档
```

### 数据卷

| 数据卷 | 说明 |
|--------|------|
| mysql_data | MySQL数据持久化 |
| redis_data | Redis数据持久化 |
| rabbitmq_data | RabbitMQ数据持久化 |
| uploads_prod | 上传文件存储 |
| logs_prod | 日志文件存储 |

### 网络配置

| 网络 | 说明 |
|------|------|
| py-small-admin-network | 开发环境网络 |
| py-small-admin-network-prod | 生产环境网络 |

### 参考链接

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Celery 文档](https://docs.celeryproject.org/)
- [Flower 文档](https://flower.readthedocs.io/)
- [MySQL官方文档](https://dev.mysql.com/doc/)
- [Redis文档](https://redis.io/documentation)
- [RabbitMQ文档](https://www.rabbitmq.com/documentation.html)

---

## 获取更多帮助

如有问题，请参考以下资源：

1. 收集诊断信息：

```bash
# 保存容器状态
docker-compose ps > docker_status.txt

# 保存容器日志
docker-compose logs > docker_logs.txt

# 保存系统信息
docker system df > docker_system.txt
```

2. 查看官方文档：

- [Docker文档](https://docs.docker.com/)
- [MySQL文档](https://dev.mysql.com/doc/)
- [Redis文档](https://redis.io/documentation)
- [RabbitMQ文档](https://www.rabbitmq.com/documentation.html)

3. 提交Issue：

- 在项目GitHub仓库提交Issue
- 附上诊断信息和错误日志

---

**最后更新**: 2026-01-27
