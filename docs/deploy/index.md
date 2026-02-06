# 部署概览

本文档介绍了 Py Small Admin 的部署方案。

## 部署架构

### 推荐架构

```mermaid
graph TB
    subgraph "负载均衡"
        LB[Nginx]
    end

    subgraph "前端"
        FE[静态文件]
    end

    subgraph "后端"
        APP1[FastAPI 实例1]
        APP2[FastAPI 实例2]
        APP3[FastAPI 实例3]
    end

    subgraph "任务队列"
        WORKER1[Celery Worker 1]
        WORKER2[Celery Worker 2]
        BEAT[Celery Beat]
        FLOWER[Flower 监控]
    end

    subgraph "数据层"
        DB[(MySQL)]
        REDIS[(Redis)]
        MQ[(RabbitMQ)]
    end

    subgraph "存储"
        OSS[云存储 OSS/COS]
    end

    Client --> LB
    LB --> FE
    LB --> APP1
    LB --> APP2
    LB --> APP3
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    APP1 --> WORKER1
    APP2 --> WORKER2
    BEAT --> WORKER1
    BEAT --> WORKER2
    WORKER1 --> MQ
    WORKER2 --> MQ
    MQ --> WORKER1
    MQ --> WORKER2
    FLOWER --> MQ
    APP1 --> OSS
    APP2 --> OSS
    APP3 --> OSS
```

### 部署方式

#### 1. 传统部署

直接在服务器上部署，适合小型项目。

**优点**：
- 简单快速
- 资源占用少

**缺点**：
- 扩展性差
- 管理复杂

#### 2. Docker 部署

使用 Docker 容器化部署，适合中型项目。

**优点**：
- 环境一致
- 易于部署和扩展
- 便于管理

**缺点**：
- 需要学习 Docker
- 资源占用略高

#### 3. Kubernetes 部署

使用 Kubernetes 编排，适合大型项目。

**优点**：
- 高可用
- 自动扩缩容
- 滚动更新

**缺点**：
- 复杂度高
- 学习成本大

## 环境准备

### 系统要求

- **操作系统**：Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+
- **CPU**：2 核+
- **内存**：4 GB+
- **硬盘**：20 GB+
- **网络**：公网 IP 或内网

### 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 22.12+ | 前端构建环境 |
| MySQL | 5.7+ | 数据库 |
| Redis | 5.0+ | 缓存和消息队列 |
| RabbitMQ | 3.8+ | 消息队列（可选） |
| Nginx | 1.18+ | Web 服务器和反向代理 |
| Docker | 20.10+ | 容器化（可选） |

## 部署流程

### 1. 服务器准备

#### 更新系统

```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 安装基础软件

```bash
# Ubuntu/Debian
sudo apt install -y git curl vim

# CentOS/RHEL
sudo yum install -y git curl vim
```

### 2. 安装 Python

#### 方法 1：使用包管理器

```bash
# Ubuntu/Debian
sudo apt install -y python3.11 python3-pip python3-venv

# CentOS/RHEL
sudo yum install -y python3.11 python3-pip
```

#### 方法 2：使用 pyenv

```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 安装 Python 3.11
pyenv install 3.11.0
pyenv global 3.11.0
```

### 3. 安装 Node.js

#### 使用 nvm

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载配置
source ~/.bashrc

# 安装 Node.js 22
nvm install 22
nvm use 22
```

### 4. 安装 MySQL

```bash
# Ubuntu/Debian
sudo apt install -y mysql-server
sudo mysql_secure_installation

# CentOS/RHEL
sudo yum install -y mysql-server
sudo systemctl start mysqld
sudo mysql_secure_installation
```

创建数据库：

```sql
CREATE DATABASE py_small_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'py_admin'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON py_small_admin.* TO 'py_admin'@'localhost';
FLUSH PRIVILEGES;
```

### 5. 安装 Redis

```bash
# Ubuntu/Debian
sudo apt install -y redis-server
sudo systemctl start redis-server

# CentOS/RHEL
sudo yum install -y redis
sudo systemctl start redis
```

### 6. 安装 RabbitMQ（可选）

```bash
# Ubuntu/Debian
sudo apt install -y rabbitmq-server
sudo systemctl start rabbitmq-server

# CentOS/RHEL
sudo yum install -y rabbitmq-server
sudo systemctl start rabbitmq-server

# 启用管理插件
sudo rabbitmq-plugins enable rabbitmq_management
```

### 7. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt install -y nginx
sudo systemctl start nginx

# CentOS/RHEL
sudo yum install -y nginx
sudo systemctl start nginx
```

## 部署后端

### 1. 克隆代码

```bash
cd /opt
sudo git clone https://github.com/songbo236589/py-small-admin.git
cd py-small-admin/server
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
vim .env
```

详细的配置说明请参考：[环境变量配置详解](./env-config.md)

主要配置项：

```bash
# 生产环境配置
APP_DEBUG=False
APP_HOST=127.0.0.1
APP_PORT=8000

# 数据库配置
DB_DEFAULT=mysql://py_admin:your_password@localhost:3306/py_small_admin

# Redis 配置
REDIS_DEFAULT=redis://localhost:6379/0

# JWT 密钥（务必使用强随机字符串）
JWT_SECRET_KEY=your-strong-random-secret-key-change-this

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 邮件配置
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password

# 云存储配置（根据需要填写）
# 阿里云 OSS
ALIYUN_OSS_ACCESS_KEY_ID=your-access-key-id
ALIYUN_OSS_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_OSS_BUCKET_NAME=your-bucket-name
ALIYUN_OSS_ENDPOINT=your-endpoint
```

### 5. 数据库迁移

```bash
alembic upgrade head
```

### 6. 填充初始数据（可选）

```bash
python commands/seed.py
```

### 7. 安装 Gunicorn（生产环境）

```bash
pip install gunicorn
```

### 8. 配置 Systemd 服务

创建 `/etc/systemd/system/py-small-admin.service`：

```ini
[Unit]
Description=Py Small Admin
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/py-small-admin/server
Environment="PATH=/opt/py-small-admin/server/venv/bin"
ExecStart=/opt/py-small-admin/server/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 Modules.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start py-small-admin
sudo systemctl enable py-small-admin
```

## 部署前端

### 1. 进入前端目录

```bash
cd /opt/py-small-admin/admin-web
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置环境变量

创建 `.env.production`：

```bash
UMI_APP_API_BASE_URL=https://your-domain.com/api
UMI_APP_API_KEY=your-admin-api-key
UMI_APP_ENV=production
```

### 4. 构建生产版本

```bash
npm run build
```

### 5. 配置 Nginx

创建 `/etc/nginx/sites-available/py-small-admin`：

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /opt/py-small-admin/admin-web/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传文件
    location /uploads {
        alias /opt/py-small-admin/server/uploads;
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/py-small-admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 部署 Celery

### 1. 配置 Systemd 服务

创建 `/etc/systemd/system/py-small-admin-celery.service`：

```ini
[Unit]
Description=Celery Worker for Py Small Admin
After=network.target

[Service]
Type=forking
User=www-data
WorkingDirectory=/opt/py-small-admin/server
Environment="PATH=/opt/py-small-admin/server/venv/bin"
ExecStart=/opt/py-small-admin/server/venv/bin/celery -A Modules.common.libs.celery.celery_service.celery multi start worker -c 4
ExecStop=/opt/py-small-admin/server/venv/bin/celery -A Modules.common.libs.celery.celery_service.celery multi stopwait worker
Restart=always

[Install]
WantedBy=multi-user.target
```

创建 `/etc/systemd/system/py-small-admin-celerybeat.service`：

```ini
[Unit]
Description=Celery Beat for Py Small Admin
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/py-small-admin/server
Environment="PATH=/opt/py-small-admin/server/venv/bin"
ExecStart=/opt/py-small-admin/server/venv/bin/celery -A Modules.common.libs.celery.celery_service.celery beat --loglevel=INFO
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start py-small-admin-celery
sudo systemctl start py-small-admin-celerybeat
sudo systemctl enable py-small-admin-celery
sudo systemctl enable py-small-admin-celerybeat
```

## 部署 Flower（可选）

### 配置 Systemd 服务

创建 `/etc/systemd/system/py-small-admin-flower.service`：

```ini
[Unit]
Description=Flower for Py Small Admin
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/py-small-admin/server
Environment="PATH=/opt/py-small-admin/server/venv/bin"
ExecStart=/opt/py-small-admin/server/venv/bin/celery -A Modules.common.libs.celery.celery_service.celery flower
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start py-small-admin-flower
sudo systemctl enable py-small-admin-flower
```

Flower 将在 http://your-domain.com:5555 启动。

## 配置 HTTPS（推荐）

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 配置自动续期

Certbot 会自动添加续期任务到 systemd timer，无需手动配置。

## 防火墙配置

### 使用 UFW

```bash
# 允许 HTTP
sudo ufw allow 80/tcp

# 允许 HTTPS
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 使用 iptables

```bash
# 允许 HTTP
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 允许 HTTPS
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
```

## 监控和日志

### 查看日志

```bash
# 后端日志
sudo journalctl -u py-small-admin -f

# Celery 日志
sudo journalctl -u py-small-admin-celery -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 监控工具

- **Flower**：Celery 任务监控
- **Sentry**：错误追踪
- **Prometheus + Grafana**：性能监控

## 备份策略

### 数据库备份

创建备份脚本 `/opt/scripts/backup_db.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u py_admin -p'your_password' py_small_admin > $BACKUP_DIR/py_small_admin_$DATE.sql

# 保留最近 7 天的备份
find $BACKUP_DIR -name "py_small_admin_*.sql" -mtime +7 -delete
```

添加到 crontab：

```bash
crontab -e
```

每天凌晨 2 点执行备份：

```
0 2 * * * /opt/scripts/backup_db.sh
```

### 文件备份

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/py-small-admin/server/uploads
```

## 性能优化

### 数据库优化

- 添加索引
- 配置查询缓存
- 优化 SQL 语句
- 定期清理过期数据

### Redis 优化

- 配置最大内存
- 配置淘汰策略
- 使用连接池

### Nginx 优化

- 启用 Gzip 压缩
- 配置缓存
- 开启 keep-alive
- 调整 worker 进程数

### 应用优化

- 启用缓存
- 优化数据库查询
- 使用异步任务
- 启用 CDN

## 安全建议

1. **修改默认密码**：立即修改初始管理员密码
2. **使用强密码**：所有密码使用强随机字符串
3. **启用 HTTPS**：使用 SSL/TLS 加密
4. **配置防火墙**：只开放必要的端口
5. **定期更新**：及时更新系统和依赖包
6. **备份数据**：定期备份数据库和文件
7. **监控日志**：定期检查系统日志
8. **限制访问**：使用 IP 白名单限制 API 访问

## 常见问题

### 1. 服务启动失败

检查日志：

```bash
sudo journalctl -u py-small-admin -n 50
```

### 2. 数据库连接失败

检查 MySQL 服务和配置：

```bash
sudo systemctl status mysql
sudo mysql -u py_admin -p
```

### 3. Nginx 502 错误

检查后端服务是否正常运行：

```bash
sudo systemctl status py-small-admin
curl http://127.0.0.1:8000
```

### 4. 端口被占用

检查端口占用：

```bash
sudo netstat -tulpn | grep :8000
```