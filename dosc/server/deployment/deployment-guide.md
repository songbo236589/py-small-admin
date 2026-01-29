# 部署指南

本指南将详细介绍 Py Small Admin 项目的部署流程，包括开发环境、测试环境和生产环境的部署。

## 部署概述

### 部署架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│  Gunicorn   │────▶│   FastAPI   │
│  (反向代理)  │     │  (WSGI)     │     │  (应用)     │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Redis     │     │   MySQL     │     │   Celery    │
│  (缓存)     │     │  (数据库)   │     │  (任务队列) │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 部署环境

| 环境     | 用途     | 配置               |
| -------- | -------- | ------------------ |
| 开发环境 | 本地开发 | 单机部署，调试模式 |
| 测试环境 | 功能测试 | 模拟生产，小规模   |
| 生产环境 | 正式运行 | 高可用，负载均衡   |

## 环境准备

### 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **Python**: 3.9+
- **MySQL**: 5.7+
- **Redis**: 6.0+
- **Nginx**: 1.18+
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 20GB，推荐 50GB+

### 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3-pip \
    nginx \
    mysql-server \
    redis-server \
    supervisor \
    git

# CentOS/RHEL
sudo yum update
sudo yum install -y \
    python39 \
    python39-devel \
    nginx \
    mysql-server \
    redis \
    supervisor \
    git
```

### 创建部署用户

```bash
# 创建专用部署用户
sudo useradd -m -s /bin/bash deploy

# 设置密码
sudo passwd deploy

# 添加到 sudo 组（可选）
sudo usermod -aG sudo deploy
```

## 项目部署

### 1. 克隆项目

```bash
# 切换到部署用户
sudo su - deploy

# 克隆项目
git clone https://github.com/songbo236589/py-small-admin.git
cd py-small-admin

# 进入 server 目录
cd server
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3.9 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 3. 安装依赖

```bash
# 安装生产环境依赖
pip install -r requirements.txt

# 或使用国内镜像源加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 配置环境变量

```bash
# 复制生产环境配置
cp .env.production.example .env

# 编辑配置文件
nano .env
```

生产环境配置示例：

```bash
# 应用配置
APP_NAME=Py Small Admin
APP_ENV=production
APP_DEBUG=False
APP_HOST=0.0.0.0
APP_PORT=8000

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=py_small_admin
DB_USER=py_admin
DB_PASSWORD=your_secure_password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT 配置
JWT_SECRET_KEY=your_jwt_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=/var/log/py-small-admin
```

### 5. 初始化数据库

```bash
# 创建数据库
mysql -u root -p

CREATE DATABASE py_small_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'py_admin'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON py_small_admin.* TO 'py_admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 运行数据库迁移
python -m commands.migrate

# 填充初始数据（可选）
python -m commands.seed
```

### 6. 配置日志目录

```bash
# 创建日志目录
sudo mkdir -p /var/log/py-small-admin

# 设置权限
sudo chown -R deploy:deploy /var/log/py-small-admin
sudo chmod -R 755 /var/log/py-small-admin
```

## Gunicorn 配置

### 安装 Gunicorn

```bash
pip install gunicorn
```

### 创建 Gunicorn 配置文件

```python
# config/gunicorn_config.py
import multiprocessing
import os

# 服务器 socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker 进程数
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型
worker_class = "uvicorn.workers.UvicornWorker"

# Worker 连接数
worker_connections = 1000

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 超时设置
timeout = 30
keepalive = 2

# 日志配置
accesslog = "/var/log/py-small-admin/gunicorn_access.log"
errorlog = "/var/log/py-small-admin/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "py_small_admin"

# 进程文件
pidfile = "/var/run/py-small-admin/gunicorn.pid"

# 用户和组
user = "deploy"
group = "deploy"

# 临时目录
tmp_upload_dir = None

# 启用预加载
preload_app = True

# 环境变量
raw_env = [
    'APP_ENV=production',
    'APP_DEBUG=False',
]
```

## Nginx 配置

### 创建 Nginx 配置文件

```nginx
# /etc/nginx/sites-available/py-small-admin
upstream py_small_admin {
    server 127.0.0.1:8000;
    # 多个 worker 时可以配置负载均衡
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    # 日志配置
    access_log /var/log/nginx/py-small-admin_access.log;
    error_log /var/log/nginx/py-small-admin_error.log;

    # 客户端上传大小限制
    client_max_body_size 100M;

    # 静态文件
    location /static {
        alias /home/deploy/py-small-admin/server/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件
    location /uploads {
        alias /home/deploy/py-small-admin/server/uploads;
        expires 7d;
    }

    # API 代理
    location / {
        proxy_pass http://py_small_admin;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # WebSocket 支持（如果需要）
    location /ws {
        proxy_pass http://py_small_admin;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/py-small-admin /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 设置开机自启
sudo systemctl enable nginx
```

## Supervisor 配置

### 安装 Supervisor

```bash
# Ubuntu/Debian
sudo apt-get install supervisor

# CentOS/RHEL
sudo yum install supervisor
```

### 创建 Gunicorn 配置

```ini
# /etc/supervisor/conf.d/py-small-admin.conf
[program:py-small-admin]
command=/home/deploy/py-small-admin/server/venv/bin/gunicorn -c config/gunicorn_config.py Modules.main:app
directory=/home/deploy/py-small-admin/server
user=deploy
autostart=true
autorestart=true
startretries=3
redirect_stderr=true
stdout_logfile=/var/log/py-small-admin/gunicorn_supervisor.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=APP_ENV="production",APP_DEBUG="False"
```

### 创建 Celery Worker 配置

```ini
# /etc/supervisor/conf.d/celery-worker.conf
[program:celery-worker]
command=/home/deploy/py-small-admin/server/venv/bin/celery -A config.celery_config worker -l info -Q default,admin,quant
directory=/home/deploy/py-small-admin/server
user=deploy
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/py-small-admin/celery_worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=APP_ENV="production"
```

### 创建 Celery Beat 配置

```ini
# /etc/supervisor/conf.d/celery-beat.conf
[program:celery-beat]
command=/home/deploy/py-small-admin/server/venv/bin/celery -A config.celery_config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/home/deploy/py-small-admin/server
user=deploy
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/py-small-admin/celery_beat.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=APP_ENV="production"
```

### 启动服务

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动所有服务
sudo supervisorctl start all

# 查看状态
sudo supervisorctl status

# 重启服务
sudo supervisorctl restart py-small-admin
sudo supervisorctl restart celery-worker
sudo supervisorctl restart celery-beat
```

## SSL 配置

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 手动配置 SSL

```nginx
# 编辑 Nginx 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其他配置...
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 部署脚本

### 部署脚本示例

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

PROJECT_DIR="/home/deploy/py-small-admin"
VENV_DIR="$PROJECT_DIR/server/venv"
LOG_DIR="/var/log/py-small-admin"

echo "开始部署 Py Small Admin..."

# 1. 备份当前版本
echo "备份当前版本..."
if [ -d "$PROJECT_DIR/server" ]; then
    BACKUP_DIR="$PROJECT_DIR/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$PROJECT_DIR/server" "$BACKUP_DIR/"
fi

# 2. 拉取最新代码
echo "拉取最新代码..."
cd "$PROJECT_DIR"
git pull origin main

# 3. 安装依赖
echo "安装依赖..."
cd "$PROJECT_DIR/server"
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

# 4. 运行数据库迁移
echo "运行数据库迁移..."
python -m commands.migrate

# 5. 重启服务
echo "重启服务..."
sudo supervisorctl restart py-small-admin
sudo supervisorctl restart celery-worker
sudo supervisorctl restart celery-beat

# 6. 清理旧备份
echo "清理旧备份..."
find "$PROJECT_DIR/backup" -type d -mtime +7 -exec rm -rf {} \;

echo "部署完成！"
```

### 回滚脚本

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

PROJECT_DIR="/home/deploy/py-small-admin"
BACKUP_DIR="$1"

if [ -z "$BACKUP_DIR" ]; then
    echo "请指定备份目录"
    exit 1
fi

echo "开始回滚到 $BACKUP_DIR..."

# 1. 停止服务
echo "停止服务..."
sudo supervisorctl stop py-small-admin celery-worker celery-beat

# 2. 恢复备份
echo "恢复备份..."
rm -rf "$PROJECT_DIR/server"
cp -r "$BACKUP_DIR/server" "$PROJECT_DIR/"

# 3. 重启服务
echo "重启服务..."
sudo supervisorctl start py-small-admin celery-worker celery-beat

echo "回滚完成！"
```

## Docker 部署

### Dockerfile

```dockerfile
# server/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p /var/log/py-small-admin

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "-c", "config/gunicorn_config.py", "Modules.main:app"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  app:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - APP_DEBUG=False
    volumes:
      - ./server:/app
      - /var/log/py-small-admin:/var/log/py-small-admin
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-worker:
    build: ./server
    command: celery -A config.celery_config worker -l info
    environment:
      - APP_ENV=production
    volumes:
      - ./server:/app
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-beat:
    build: ./server
    command: celery -A config.celery_config beat -l info
    environment:
      - APP_ENV=production
    volumes:
      - ./server:/app
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: mysql:5.7
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=py_small_admin
      - MYSQL_USER=py_admin
      - MYSQL_PASSWORD=password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### 启动 Docker

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_created_at ON orders(created_at);

-- 优化查询
-- 使用 EXPLAIN 分析查询
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

### 2. Redis 优化

```bash
# 编辑 Redis 配置
sudo nano /etc/redis/redis.conf

# 设置最大内存
maxmemory 256mb
maxmemory-policy allkeys-lru

# 重启 Redis
sudo systemctl restart redis
```

### 3. Nginx 优化

```nginx
# 启用 gzip 压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;

# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 302 10m;
    proxy_cache_valid 404 1m;
    proxy_pass http://py_small_admin;
}
```

## 安全加固

### 1. 防火墙配置

```bash
# 安装 UFW
sudo apt-get install ufw

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. SSH 安全

```bash
# 编辑 SSH 配置
sudo nano /etc/ssh/sshd_config

# 禁用 root 登录
PermitRootLogin no

# 禁用密码登录（使用密钥）
PasswordAuthentication no

# 重启 SSH
sudo systemctl restart sshd
```

### 3. 文件权限

```bash
# 设置正确的文件权限
chmod 600 .env
chmod 755 server
chmod -R 755 server/static
chmod -R 755 server/uploads
```

## 监控和维护

### 1. 日志轮转

```bash
# 创建日志轮转配置
sudo nano /etc/logrotate.d/py-small-admin

/var/log/py-small-admin/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 deploy deploy
    sharedscripts
    postrotate
        sudo supervisorctl restart py-small-admin
    endscript
}
```

### 2. 定期备份

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backup/py-small-admin"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR/$DATE"

# 备份数据库
mysqldump -u py_admin -p py_small_admin > "$BACKUP_DIR/$DATE/database.sql"

# 备份上传文件
tar -czf "$BACKUP_DIR/$DATE/uploads.tar.gz" /home/deploy/py-small-admin/server/uploads

# 清理旧备份（保留 30 天）
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} \;

echo "备份完成: $BACKUP_DIR/$DATE"
```

### 3. 健康检查

```bash
#!/bin/bash
# scripts/health_check.sh

# 检查应用状态
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)

if [ $HTTP_CODE -eq 200 ]; then
    echo "应用运行正常"
else
    echo "应用异常: HTTP $HTTP_CODE"
    # 发送告警
fi

# 检查 Celery Worker
CELERY_STATUS=$(sudo supervisorctl status celery-worker | awk '{print $2}')

if [ "$CELERY_STATUS" = "RUNNING" ]; then
    echo "Celery Worker 运行正常"
else
    echo "Celery Worker 异常"
    # 发送告警
fi
```

## 常见问题

### 1. 端口被占用

**问题**：启动时提示端口被占用

**解决方案**：

```bash
# 查找占用端口的进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 <PID>
```

### 2. 权限问题

**问题**：文件权限错误

**解决方案**：

```bash
# 设置正确的用户和组
sudo chown -R deploy:deploy /home/deploy/py-small-admin

# 设置正确的权限
chmod -R 755 /home/deploy/py-small-admin/server
```

### 3. 数据库连接失败

**问题**：无法连接数据库

**解决方案**：

- 检查数据库服务是否运行
- 验证连接配置
- 检查防火墙规则

## 相关文档

- [监控指南](./monitoring.md)
- [日志指南](./logging.md)
- [故障排查](./troubleshooting.md)
- [Celery 指南](../celery/celery-guide.md)
