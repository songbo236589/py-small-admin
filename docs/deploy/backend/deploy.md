# 后端部署指南

本文档详细介绍 Py Small Admin 后端的传统部署方式（不使用 Docker）。

## 部署流程概览

```mermaid
graph LR
    A[环境准备] --> B[安装依赖]
    B --> C[配置环境变量]
    C --> D[数据库迁移]
    D --> E[安装 Gunicorn]
    E --> F[配置 Systemd]
    F --> G[启动服务]
```

## 详细部署步骤

### 1. 环境准备

确保服务器已安装：
- Python 3.11+
- MySQL 5.7+ 或 8.0+
- Redis 5.0+
- Git

### 2. 部署应用

#### 2.1 创建部署目录

```bash
sudo mkdir -p /opt/py-small-admin
sudo chown $USER:$USER /opt/py-small-admin
cd /opt/py-small-admin
```

#### 2.2 克隆代码

```bash
git clone https://github.com/songbo236589/py-small-admin.git
cd py-small-admin/server
```

#### 2.3 创建虚拟环境

```bash
python3.11 -m venv venv
source venv/bin/activate
```

#### 2.4 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 3. 配置环境变量

```bash
cp .env.example .env
vim .env
```

**关键配置项**：

```bash
# 应用配置
APP_DEBUG=false
APP_HOST=127.0.0.1
APP_PORT=8000
APP_ADMIN_X_API_KEY=your-strong-api-key

# 数据库配置
DB_DEFAULT=mysql://py_admin:your_password@localhost:3306/py_small_admin

# Redis 配置
REDIS_DEFAULT=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-very-strong-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 邮件配置（可选）
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_USE_TLS=true

# 文件上传配置
UPLOAD_MAX_SIZE=10485760
UPLOAD_ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx

# 日志配置
LOG_LEVEL=INFO
```

### 4. 数据库迁移

```bash
# 执行迁移
alembic upgrade head

# 填充初始数据（可选）
python commands/seed.py
```

### 5. 创建必要的目录

```bash
mkdir -p uploads logs
chmod 755 uploads logs
```

### 6. 配置 Gunicorn

Gunicorn 是一个高性能的 Python WSGI HTTP 服务器，适合生产环境。

#### 6.1 测试 Gunicorn

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 Modules.main:app
```

参数说明：
- `-w 4`: 4 个 worker 进程
- `-k uvicorn.workers.UvicornWorker`: 使用 Uvicorn worker（支持异步）
- `-b 127.0.0.1:8000`: 绑定地址和端口

#### 6.2 配置 Systemd 服务

创建服务文件 `/etc/systemd/system/py-small-admin.service`：

```ini
[Unit]
Description=Py Small Admin FastAPI Application
After=network.target mysql.service redis.service
Wants=mysql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/py-small-admin/server
Environment="PATH=/opt/py-small-admin/server/venv/bin"
ExecStart=/opt/py-small-admin/server/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /opt/py-small-admin/server/logs/access.log \
    --error-logfile /opt/py-small-admin/server/logs/error.log \
    --log-level info \
    Modules.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 创建日志目录
sudo mkdir -p /opt/py-small-admin/server/logs
sudo chown www-data:www-data /opt/py-small-admin/server/logs

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start py-small-admin

# 开机自启
sudo systemctl enable py-small-admin

# 查看状态
sudo systemctl status py-small-admin

# 查看日志
sudo journalctl -u py-small-admin -f
```

### 7. 配置 Nginx 反向代理

创建配置文件 `/etc/nginx/sites-available/py-small-admin`：

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # 最大上传大小
    client_max_body_size 100M;

    # 前端静态文件
    location / {
        root /opt/py-small-admin/admin-web/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 上传文件目录
    location /uploads {
        alias /opt/py-small-admin/server/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/py-small-admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 性能调优

### 1. Worker 进程数量

根据 CPU 核心数调整 worker 数量：

```ini
# 公式：worker 数量 = (2 x CPU 核心数) + 1
ExecStart=/opt/py-small-admin/server/venv/bin/gunicorn -w 9 ...
```

### 2. Worker 类型

对于异步应用，使用 Uvicorn Worker：

```bash
-k uvicorn.workers.UvicornWorker
```

### 3. 超时配置

根据应用需求调整超时时间：

```ini
TimeoutStartSec=300
```

## 监控和日志

### 查看应用日志

```bash
# 实时日志
sudo journalctl -u py-small-admin -f

# 最近 100 行
sudo journalctl -u py-small-admin -n 100

# 自定义时间范围
sudo journalctl -u py-small-admin --since "2024-01-01" --until "2024-01-02"
```

### 配置日志轮转

创建 `/etc/logrotate.d/py-small-admin`：

```
/opt/py-small-admin/server/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload py-small-admin > /dev/null 2>&1 || true
    endscript
}
```

## 故障排查

### 服务无法启动

1. 检查配置文件语法
2. 查看详细日志
3. 检查端口占用
4. 验证数据库连接

### 数据库连接失败

```bash
# 测试 MySQL 连接
mysql -u py_admin -p -h localhost py_small_admin

# 测试 Redis 连接
redis-cli ping
```

### 端口冲突

```bash
# 查看端口占用
sudo netstat -tulpn | grep :8000
sudo ss -tulpn | grep :8000
```

## 升级部署

### 滚动更新

```bash
# 1. 拉取最新代码
cd /opt/py-small-admin/server
git pull

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 更新依赖
pip install -r requirements.txt

# 4. 执行数据库迁移
alembic upgrade head

# 5. 重启服务
sudo systemctl restart py-small-admin
```

### 蓝绿部署

```bash
# 1. 部署新版本到新目录
/opt/py-small-admin-v2

# 2. 测试新版本
curl http://localhost:8001/health

# 3. 切换 Nginx 配置
sudo nginx -s reload
```

## 生产环境建议

1. **使用专门的部署用户**：创建专门的系统用户运行应用
2. **限制文件权限**：上传目录和应用文件设置适当的权限
3. **启用防火墙**：只开放必要的端口
4. **配置 HTTPS**：使用 SSL/TLS 加密
5. **定期备份**：每天自动备份数据库
6. **监控告警**：配置监控和告警系统
7. **日志管理**：定期清理和归档日志
