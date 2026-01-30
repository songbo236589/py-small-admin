# 安装指南

本指南将帮助你完成项目的安装和配置。

## 前置准备

在开始安装之前，请确保你已经完成 [环境要求](./index.md) 中的所有步骤：

- ✅ Python 3.11+ 已安装
- ✅ Node.js 22.12+ 已安装
- ✅ MySQL 5.7+ 已安装并运行
- ✅ Redis 5.0+ 已安装并运行
- ✅ Git 已安装

## 克隆项目

### 1. 克隆代码仓库

```bash
git clone https://github.com/songbo236589/py-small-admin.git
cd py-small-admin
```

## 后端安装

### 2. 创建虚拟环境

```bash
cd server
python -m venv venv
```

### 3. 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

如果下载速度较慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 配置环境变量

复制示例配置文件：

```bash
cp .env.example .env
```

如果没有 `.env.example` 文件，请手动创建 `.env` 文件并添加以下内容：

```bash
# 应用配置
APP_NAME=Py Small Admin
APP_DEBUG=True
APP_HOST=0.0.0.0
APP_PORT=8000
APP_RELOAD=True
APP_API_PREFIX=/api
APP_TIMEZONE=Asia/Shanghai
APP_ADMIN_X_API_KEY=your-admin-api-key

# 数据库配置
DB_DEFAULT=mysql://root:password@localhost:3306/py_small_admin

# Redis 配置
REDIS_DEFAULT=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 邮件配置
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True

# 上传配置
UPLOAD_DIR=uploads
UPLOAD_URL_PREFIX=/uploads
UPLOAD_MAX_SIZE=10485760
UPLOAD_ALLOWED_EXTENSIONS=image,document,video,audio

# 云存储配置（根据需要填写）
# 阿里云 OSS
ALIYUN_OSS_ACCESS_KEY_ID=
ALIYUN_OSS_ACCESS_KEY_SECRET=
ALIYUN_OSS_BUCKET_NAME=
ALIYUN_OSS_ENDPOINT=

# 腾讯云 COS
TENCENT_COS_SECRET_ID=
TENCENT_COS_SECRET_KEY=
TENCENT_COS_BUCKET=
TENCENT_COS_REGION=

# 七牛云
QINIU_ACCESS_KEY=
QINIU_SECRET_KEY=
QINIU_BUCKET=
QINIU_DOMAIN=
```

**重要提示**：在生产环境中，请务必修改以下敏感配置：
- `JWT_SECRET_KEY`：使用强随机字符串
- `APP_DEBUG`：设置为 `False`
- 数据库密码
- 邮件密码
- 云存储密钥

### 6. 创建数据库

登录 MySQL：

```bash
mysql -u root -p
```

执行以下 SQL 命令：

```sql
CREATE DATABASE py_small_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 7. 数据库迁移

执行数据库迁移，创建数据表：

```bash
alembic upgrade head
```

或者使用命令行工具：

```bash
python commands/migrate.py upgrade head
```

### 8. 填充初始数据（可选）

填充初始管理员数据和菜单数据：

```bash
python commands/seed.py
```

初始管理员账号：
- 用户名：`admin`
- 密码：`admin123`

**注意**：生产环境请立即修改初始密码！

## 前端安装

### 9. 进入前端目录

```bash
cd ../admin-web
```

### 10. 安装 Node.js 依赖

```bash
npm install
```

如果使用 yarn：

```bash
yarn install
```

如果下载速度较慢，可以使用淘宝镜像：

```bash
npm install --registry=https://registry.npmmirror.com
```

### 11. 配置环境变量

创建 `.env` 文件并添加以下内容：

```bash
UMI_APP_API_KEY=your-admin-api-key
UMI_APP_API_BASE_URL=http://localhost:8000/api
UMI_APP_ENV=dev
```

**注意**：`UMI_APP_API_KEY` 必须与后端配置文件中的 `APP_ADMIN_X_API_KEY` 一致。

## 验证安装

### 12. 启动后端服务

```bash
cd server
python run.py
```

看到以下输出表示启动成功：

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

访问 http://localhost:8000 查看系统信息。

访问 http://localhost:8000/docs 查看 API 文档。

### 13. 启动前端服务

打开新的终端窗口：

```bash
cd admin-web
npm start
```

浏览器会自动打开 http://localhost:8000。

### 14. 登录测试

使用初始账号登录：
- 用户名：`admin`
- 密码：`admin123`

## 可选配置

### 启动 Celery 任务队列

如果你需要使用异步任务功能（如邮件发送、数据同步等），需要启动 Celery：

**启动 Celery Worker：**

```bash
cd server
celery -A Modules.common.libs.celery.celery_service.celery worker -l info
```

**启动 Celery Beat（定时任务）：**

```bash
celery -A Modules.common.libs.celery.celery_service.celery beat -l info
```

**启动 Flower 监控（可选）：**

```bash
celery -A Modules.common.libs.celery.celery_service.celery flower
```

访问 http://localhost:5555 查看任务监控界面。

### 配置 RabbitMQ（可选）

如果使用 RabbitMQ 作为消息代理，需要修改 `.env` 文件中的 Celery 配置：

```bash
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## 常见问题

### 1. 依赖安装失败

**问题**：`pip install` 时报错 `Microsoft Visual C++ 14.0 is required`

**解决方案**（Windows）：
- 下载并安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
- 或使用预编译的 wheel 文件

**问题**：`npm install` 时报错

**解决方案**：
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 2. 数据库连接失败

**问题**：`Can't connect to MySQL server on 'localhost'`

**解决方案**：
- 检查 MySQL 服务是否启动
- 检查 `.env` 文件中的数据库配置是否正确
- 检查用户名和密码是否正确
- 检查防火墙设置

### 3. Redis 连接失败

**问题**：`Error connecting to Redis`

**解决方案**：
- 检查 Redis 服务是否启动
- 检查 `.env` 文件中的 Redis 配置是否正确
- 如果设置了密码，需要在 URL 中包含密码：`redis://:password@localhost:6379/0`

### 4. 端口被占用

**问题**：`Address already in use`

**解决方案**：
- 修改 `.env` 文件中的端口号
- 或终止占用端口的进程

**查找占用端口的进程（Windows）**：
```bash
netstat -ano | findstr :8000
```

**查找占用端口的进程（macOS/Linux）**：
```bash
lsof -i :8000
```

### 5. 迁移失败

**问题**：`alembic upgrade head` 报错

**解决方案**：
- 检查数据库连接是否正常
- 检查数据库是否已创建
- 检查表是否已存在，可以尝试重新初始化迁移：
  ```bash
  alembic upgrade base
  alembic upgrade head
  ```