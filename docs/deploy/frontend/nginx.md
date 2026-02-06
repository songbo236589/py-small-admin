# Nginx 配置指南

本文档介绍如何配置 Nginx 作为 Py Small Admin 的反向代理和静态文件服务器。

## 基础配置

### 完整配置示例

创建 `/etc/nginx/sites-available/py-small-admin`：

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000;
    # 可以添加多个服务器实现负载均衡
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

# HTTP 服务器配置
server {
    listen 80;
    server_name your-domain.com;

    # 客户端最大请求体大小
    client_max_body_size 100M;

    # 前端静态文件
    location / {
        root /opt/py-small-admin/admin-web/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 上传文件访问
    location /uploads {
        alias /opt/py-small-admin/server/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";

        # 安全设置：禁止执行 PHP 等脚本
        location ~ \.php$ {
            deny all;
        }
    }

    # Celery Flower 监控（可选）
    location /flower {
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 基本认证（可选）
        # auth_basic "Flower";
        # auth_basic_user_file /etc/nginx/.htpasswd;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/rss+xml
        application/atom+xml
        image/svg+xml;

    # 自定义错误页面
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

## HTTPS 配置

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 证书自动续期
sudo certbot renew --dry-run
```

### 手动配置 SSL

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 其他配置同 HTTP
    # ...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 性能优化

### 1. 启用缓存

```nginx
# 静态资源缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# HTML 文件不缓存
location ~* \.html$ {
    expires -1;
    add_header Cache-Control "no-cache";
}
```

### 2. 启用 Buffer

```nginx
# 在 http 块中添加
sendfile on;
tcp_nopush on;
tcp_nodelay on;
```

### 3. 调整 Worker 进程

```nginx
# 在 /etc/nginx/nginx.conf 中
worker_processes auto;
worker_connections 1024;
```

### 4. 限制请求速率

```nginx
# 在 http 块中定义限流区域
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# 在 location 中应用限流
location /api {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://fastapi_backend;
}
```

## 安全配置

### 1. 隐藏版本信息

```nginx
# 在 http 块中
server_tokens off;
more_clear_headers Server 'X-Powered-By';
more_clear_headers 'X-Frame-Options';
```

### 2. 安全头部

```nginx
# 在 server 块中添加
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

### 3. IP 白名单

```nginx
# 限制 API 访问
location /api/admin {
    # 只允许特定 IP 访问
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;

    proxy_pass http://fastapi_backend;
}
```

### 4. 基本认证

```nginx
# 创建密码文件
sudo htpasswd /etc/nginx/.htpasswd admin

# 在 location 中应用
location /flower {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:5555;
}
```

## 日志配置

### 访问日志

```nginx
# 自定义日志格式
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                '$status $body_bytes_sent "$http_referer" '
                '"$http_user_agent" "$http_x_forwarded_for"';

# 访问日志
access_log /var/log/nginx/py-small-admin-access.log main;
```

### 错误日志

```nginx
error_log /var/log/nginx/py-small-admin-error.log warn;
```

### 日志轮转

```bash
sudo vim /etc/logrotate.d/nginx
```

```
/var/log/nginx/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
```

## 多域名配置

```nginx
# 主域名
server {
    listen 80;
    server_name example.com;
    # ... 配置
}

# 子域名
server {
    listen 80;
    server_name api.example.com;
    location / {
        proxy_pass http://fastapi_backend;
    }
}

# 静态资源 CDN 域名
server {
    listen 80;
    server_name static.example.com;
    root /var/www/py-small-admin/static;
}
```

## 负载均衡

### 轮询策略

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

### 最少连接策略

```nginx
upstream fastapi_backend {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
}
```

### IP Hash 策略

```nginx
upstream fastapi_backend {
    ip_hash;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
}
```

### 健康检查

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;

    # 健康检查端点
    check interval=30s rise=3 fall=2 timeout=10s;
}
```

## 反向代理配置详解

### proxy_pass 指令

```nginx
# 传递请求到后端
proxy_pass http://fastapi_backend;

# 重写 URL
location /api/v1/ {
    proxy_pass http://fastapi_backend/api/;
}
```

### proxy_set_header 指令

```nginx
# 设置请求头
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;

# 设置自定义请求头
proxy_set_header X-Custom-Header "custom-value";
```

### 超时配置

```nginx
# 连接超时
proxy_connect_timeout 60s;

# 发送超时
proxy_send_timeout 60s;

# 读取超时
proxy_read_timeout 60s;
```

## 故障排查

### 1. 配置测试

```bash
# 测试配置文件语法
sudo nginx -t

# 重载配置
sudo nginx -s reload
```

### 2. 查看日志

```bash
# 错误日志
sudo tail -f /var/log/nginx/error.log

# 访问日志
sudo tail -f /var/log/nginx/access.log
```

### 3. 502 Bad Gateway

```bash
# 检查后端服务状态
sudo systemctl status py-small-admin

# 检查端口监听
sudo netstat -tulpn | grep :8000

# 检查 SELinux 状态（CentOS）
sudo getenforce
```

### 4. 404 Not Found

检查 `root` 指向的路径是否正确，文件是否存在。

### 5. 上传文件失败

检查 `client_max_body_size` 是否足够大，以及 `client_body_timeout` 设置。

### 6. WebSocket 连接失败

确保以下配置存在：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```
