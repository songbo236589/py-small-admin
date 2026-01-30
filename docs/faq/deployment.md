# 部署问题

本文档解答 Py Small Admin 部署相关的常见问题。

## 目录

- [环境准备](#环境准备)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [常见问题](#常见问题)

## 环境准备

### Q: 服务器最低配置要求是什么？

**A**:

| 资源 | 开发环境 | 生产环境 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 硬盘 | 20 GB | 50 GB+ |
| 操作系统 | Ubuntu 20.04+ / CentOS 7+ | Ubuntu 20.04+ / CentOS 7+ |

### Q: 需要安装哪些软件？

**A**:

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 22.12+ | 前端构建环境 |
| MySQL | 5.7+ | 数据库 |
| Redis | 5.0+ | 缓存和消息队列 |
| Nginx | 1.18+ | Web 服务器 |
| Git | 最新版 | 版本控制 |

### Q: 如何安装 Python 3.11？

**A**:

Python 环境配置请参考：[Python环境配置完整指南](../../../server/docs/Python环境配置完整指南.md)

该指南包含：
- Python 3.12.7 安装（或更高版本）
- 虚拟环境创建和激活
- pip 配置和依赖安装
- VSCode 配置
- 常见问题解决方案

### Q: 如何安装 Node.js 22.12？

**A**:

**使用 nvm**:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
```

**Ubuntu/Debian**:
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 后端部署

### Q: 如何部署后端服务？

**A**:

1. **克隆代码**
   ```bash
   cd /opt
   sudo git clone https://github.com/songbo236589/py-small-admin.git
   cd py-small-admin/server
   ```

2. **创建虚拟环境**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   vim .env
   # 修改数据库、Redis 等配置
   ```

5. **执行数据库迁移**
   ```bash
   alembic upgrade head
   ```

6. **配置 Systemd 服务**
   ```bash
   sudo vim /etc/systemd/system/py-small-admin.service
   ```

   ```ini
   [Unit]
   Description=Py Small Admin
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/py-small-admin/server
   Environment="PATH=/opt/py-small-admin/server/venv/bin"
   ExecStart=/opt/py-small-admin/server/venv/bin/python run.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

7. **启动服务**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start py-small-admin
   sudo systemctl enable py-small-admin
   ```

### Q: 如何配置 Gunicorn？

**A**:

```bash
pip install gunicorn
```

修改 Systemd 服务配置：

```ini
[Service]
Type=notify
ExecStart=/opt/py-small-admin/server/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8000 \
    Modules.main:app
```

### Q: 如何部署 Celery？

**A**:

**Celery Worker 服务**:
```bash
sudo vim /etc/systemd/system/py-small-admin-celery.service
```

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

**Celery Beat 服务**:
```bash
sudo vim /etc/systemd/system/py-small-admin-celerybeat.service
```

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

## 前端部署

### Q: 如何构建前端？

**A**:

```bash
cd admin-web

# 安装依赖
npm install

# 构建生产版本
npm run build
```

构建产物在 `dist/` 目录。

### Q: 如何配置 Nginx？

**A**:

```bash
sudo vim /etc/nginx/sites-available/py-small-admin
```

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

### Q: 如何配置 HTTPS？

**A**:

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 常见问题

### Q: 服务启动失败怎么办？

**A**:

1. **查看日志**
   ```bash
   sudo journalctl -u py-small-admin -n 50
   ```

2. **检查配置**
   ```bash
   # 检查端口是否被占用
   sudo netstat -tulpn | grep :8000

   # 检查数据库连接
   python -c "from config.database import engine; print('OK')"
   ```

3. **检查权限**
   ```bash
   # 确保用户有权限访问目录
   sudo chown -R www-data:www-data /opt/py-small-admin
   ```

### Q: 数据库连接失败？

**A**:

1. **检查 MySQL 服务**
   ```bash
   sudo systemctl status mysql
   ```

2. **检查数据库配置**
   ```bash
   # 测试连接
   mysql -u py_admin -p py_small_admin
   ```

3. **检查防火墙**
   ```bash
   sudo ufw status
   ```

### Q: 502 Bad Gateway 错误？

**A**:

1. **检查后端服务是否运行**
   ```bash
   sudo systemctl status py-small-admin
   curl http://127.0.0.1:8000
   ```

2. **检查 Nginx 配置**
   ```bash
   sudo nginx -t
   ```

3. **查看 Nginx 日志**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Q: 静态文件 404？

**A**:

1. **检查文件路径**
   ```bash
   ls -la /opt/py-small-admin/admin-web/dist
   ```

2. **检查 Nginx 配置**
   ```nginx
   location / {
       root /opt/py-small-admin/admin-web/dist;
       index index.html;
       try_files $uri $uri/ /index.html;
   }
   ```

3. **检查文件权限**
   ```bash
   sudo chown -R www-data:www-data /opt/py-small-admin/admin-web/dist
   ```

### Q: 如何备份数据？

**A**:

创建备份脚本 `/opt/scripts/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
mysqldump -u py_admin -p'password' py_small_admin > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/py-small-admin/server/uploads

# 保留最近 7 天的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

添加到 crontab：
```bash
crontab -e
# 每天凌晨 2 点执行备份
0 2 * * * /opt/scripts/backup.sh
```

### Q: 如何更新代码？

**A**:

```bash
cd /opt/py-small-admin

# 拉取最新代码
git pull origin main

# 后端更新
cd server
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart py-small-admin

# 前端更新
cd ../admin-web
npm install
npm run build
sudo systemctl reload nginx
```

### Q: 如何监控服务状态？

**A**:

1. **查看服务状态**
   ```bash
   sudo systemctl status py-small-admin
   sudo systemctl status py-small-admin-celery
   sudo systemctl status nginx
   ```

2. **使用 Flower 监控 Celery**
   ```bash
   pip install flower
   celery -A Modules.common.libs.celery.celery_service.celery flower
   ```

3. **配置监控告警**（推荐使用 Prometheus + Grafana）

### Q: 如何优化性能？

**A**:

1. **数据库优化**
   - 添加索引
   - 配置查询缓存
   - 定期清理过期数据

2. **Redis 优化**
   - 配置最大内存
   - 配置淘汰策略

3. **Nginx 优化**
   - 启用 Gzip 压缩
   - 配置缓存
   - 调整 worker 进程数

4. **应用优化**
   - 启用缓存
   - 使用 CDN
   - 优化图片

### Q: 如何配置防火墙？

**A**:

**使用 UFW**:
```bash
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

### Q: 如何设置自动启动？

**A**:

```bash
# 启用服务
sudo systemctl enable py-small-admin
sudo systemctl enable py-small-admin-celery
sudo systemctl enable py-small-admin-celerybeat
sudo systemctl enable nginx

# 检查启动状态
sudo systemctl is-enabled py-small-admin
```

## 更多资源

- [部署文档](../../deploy/)
- [安全最佳实践](../best-practices/security.md)
- [性能优化](../best-practices/performance.md)
