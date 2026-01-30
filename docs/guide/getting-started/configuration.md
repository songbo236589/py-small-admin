# 配置说明

本文档详细介绍了 Py Small Admin 的所有配置项。

## 配置文件

Py Small Admin 使用 `.env` 文件进行配置管理。项目根目录的 `server/.env.example` 文件包含了所有可配置项的示例。

### 创建配置文件

```bash
cd server
cp .env.example .env
```

然后根据实际情况修改 `.env` 文件中的配置项。

## 应用配置

### 基础配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 应用名称 | `APP_NAME` | "Py Small Admin" | 应用显示名称 |
| 运行环境 | `APP_ENV` | "development" | local/development/testing/production |
| 调试模式 | `APP_DEBUG` | `True` | 开发环境开启，生产环境关闭 |
| 版本号 | `APP_VERSION` | "1.0.0" | API 版本号 |
| 描述 | `APP_DESCRIPTION` | "Py Small Admin 服务" | 应用描述 |
| 主机 | `APP_HOST` | "0.0.0.0" | 服务监听地址 |
| 端口 | `APP_PORT` | `8009` | 服务监听端口 |
| 自动重载 | `APP_RELOAD` | `True` | 代码变更自动重启 |
| API 前缀 | `APP_API_PREFIX` | "/api" | API 路径前缀 |

### API 文档配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 启用文档 | `APP_DOCS_ENABLED` | `True` | 是否启用 OpenAPI 文档 |
| 文档路径 | `APP_DOCS_URL` | "/docs" | Swagger UI 文档路径 |
| OpenAPI URL | `APP_OPENAPI_URL` | "/openapi.json" | OpenAPI JSON 规范路径 |

**注意**：生产环境建议关闭文档或使用复杂路径。

### 跨域配置（CORS）

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 允许所有来源 | `APP_CORS_ALLOW_ALL` | `True` | 是否允许所有来源 |
| 允许的来源 | `APP_CORS_ORIGINS` | `["*"]` | 允许的域名列表 |
| 允许的方法 | `APP_CORS_METHODS` | `["*"]` | 允许的 HTTP 方法 |
| 允许的头部 | `APP_CORS_HEADERS` | `["*"]` | 允许的请求头 |

### 其他配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 时区 | `APP_TIMEZONE` | "Asia/Shanghai" | 应用时区 |
| API 密钥 | `APP_ADMIN_X_API_KEY` | "" | 管理员接口 API 密钥 |

## 数据库配置

### MySQL 配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 默认连接 | `DB_DEFAULT` | "mysql" | 默认数据库连接名称 |
| 主机 | `DB_CONNECTIONS__MYSQL__HOST` | "127.0.0.1" | MySQL 服务器地址 |
| 端口 | `DB_CONNECTIONS__MYSQL__PORT` | 3306 | MySQL 服务器端口 |
| 数据库 | `DB_CONNECTIONS__MYSQL__DATABASE` | "fastapi_db" | 数据库名称 |
| 用户名 | `DB_CONNECTIONS__MYSQL__USERNAME` | "root" | 数据库用户名 |
| 密码 | `DB_CONNECTIONS__MYSQL__PASSWORD` | "" | 数据库密码 |
| 字符集 | `DB_CONNECTIONS__MYSQL__CHARSET` | "utf8mb4" | 字符集 |
| 排序规则 | `DB_CONNECTIONS__MYSQL__COLLATION` | "utf8mb4_unicode_ci" | 排序规则 |
| 表前缀 | `DB_CONNECTIONS__MYSQL__PREFIX` | "fa_" | 数据库表前缀 |

### Redis 配置

#### 默认 Redis 连接

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 主机 | `DB_REDIS__DEFAULT__HOST` | "127.0.0.1" | Redis 服务器地址 |
| 端口 | `DB_REDIS__DEFAULT__PORT` | 6379 | Redis 服务器端口 |
| 数据库 | `DB_REDIS__DEFAULT__DATABASE` | 0 | Redis 数据库编号 |
| 用户名 | `DB_REDIS__DEFAULT__USERNAME` | "default" | Redis 用户名 |
| 密码 | `DB_REDIS__DEFAULT__PASSWORD` | "" | Redis 密码 |
| 键前缀 | `DB_REDIS__DEFAULT__PREFIX` | "redis_default_" | 键名前缀 |
| 最大连接数 | `DB_REDIS__DEFAULT__MAX_CONNECTIONS` | 50 | 连接池最大连接数 |

#### 缓存 Redis 连接

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 数据库 | `DB_REDIS__CACHE__DATABASE` | 1 | Redis 数据库编号 |
| 键前缀 | `DB_REDIS__CACHE__PREFIX` | "cache_" | 键名前缀 |

## 缓存配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 连接名称 | `CACHE_CONNECTION` | "cache" | 使用的 Redis 连接名称 |
| 默认 TTL | `CACHE_DEFAULT_TTL` | 31536000 | 默认缓存过期时间（秒） |
| 键前缀 | `CACHE_KEY_PREFIX` | "cache" | 缓存键前缀 |

## 日志配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 日志级别 | `LOG_LEVEL` | "INFO" | 日志级别 |
| 控制台输出 | `LOG_CONSOLE` | `True` | 是否在控制台输出日志 |
| 日志文件路径 | `LOG_FILE_PATH` | "logs/{time:YYYY-MM-DD}.log" | 日志文件路径 |
| 日志轮转时间 | `LOG_ROTATION` | "00:00" | 日志轮转时间 |
| 日志保留时间 | `LOG_RETENTION` | "30 days" | 日志文件保留时间 |
| 压缩格式 | `LOG_COMPRESSION` | "zip" | 日志文件压缩格式 |

## JWT 认证配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 密钥 | `JWT_SECRET_KEY` | "" | JWT 签名密钥（必须修改） |
| 算法 | `JWT_ALGORITHM` | "HS256" | JWT 签名算法 |
| 访问令牌过期时间 | `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | 访问令牌过期时间（分钟） |
| 刷新令牌过期时间 | `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 7 | 刷新令牌过期时间（天） |
| 签发者 | `JWT_ISSUER` | "fast-api-admin" | JWT 签发者 |
| 受众 | `JWT_AUDIENCE` | "fast-client-admin" | JWT 受众 |
| 启用黑名单 | `JWT_ENABLE_BLACKLIST` | `True` | 是否启用令牌黑名单 |

**重要**：生产环境必须使用强随机字符串作为 `JWT_SECRET_KEY`！

生成强密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Celery 配置

### Broker 配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| Broker URL | `CELERY_BROKER_URL` | "" | 消息代理 URL |
| 连接重试 | `CELERY_BROKER_CONNECTION_RETRY` | `True` | 连接失败是否重试 |

### Worker 配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 执行池类型 | `CELERY_WORKER_POOL` | "threads" | Worker 执行池类型 |
| 并发数 | `CELERY_WORKER_CONCURRENCY` | 4 | Worker 并发数 |
| 预取倍数 | `CELERY_WORKER_PREFETCH_MULTIPLIER` | 4 | 预取倍数 |
| 最大任务数 | `CELERY_WORKER_MAX_TASKS_PER_CHILD` | 1000 | 每个 Worker 处理的最大任务数 |

### 任务配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 默认队列 | `CELERY_TASK_DEFAULT_QUEUE` | "default" | 默认队列名称 |
| 硬超时时间 | `CELERY_TASK_DEFAULT_TIME_LIMIT` | 3600 | 任务硬超时时间（秒） |
| 软超时时间 | `CELERY_TASK_DEFAULT_SOFT_TIME_LIMIT` | 3000 | 任务软超时时间（秒） |
| 最大重试次数 | `CELERY_TASK_DEFAULT_MAX_RETRIES` | 3 | 任务最大重试次数 |
| 重试延迟 | `CELERY_TASK_DEFAULT_RETRY_DELAY` | 60 | 任务重试延迟（秒） |

## 默认管理员账号

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 用户名 | `APP_DEFAULT_ADMIN_USERNAME` | "admin" | 默认管理员用户名 |
| 密码 | `APP_DEFAULT_ADMIN_PASSWORD` | "123456" | 默认管理员密码 |

**注意**：生产环境请务必修改默认密码！

## 配置示例

### 开发环境配置

```bash
# 应用配置
APP_NAME="Py Small Admin"
APP_ENV=development
APP_DEBUG=true
APP_PORT=8009

# 数据库配置
DB_CONNECTIONS__MYSQL__HOST=127.0.0.1
DB_CONNECTIONS__MYSQL__DATABASE=fastapi_db
DB_CONNECTIONS__MYSQL__USERNAME=root
DB_CONNECTIONS__MYSQL__PASSWORD=root

# Redis 配置
DB_REDIS__DEFAULT__HOST=127.0.0.1
DB_REDIS__DEFAULT__DATABASE=0

# JWT 配置
JWT_SECRET_KEY="dev-secret-key-change-in-production"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery 配置
CELERY_BROKER_URL="redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/2"
```

### 生产环境配置

```bash
# 应用配置
APP_NAME="Py Small Admin"
APP_ENV=production
APP_DEBUG=false
APP_PORT=8000

# 数据库配置
DB_CONNECTIONS__MYSQL__HOST=your-mysql-host
DB_CONNECTIONS__MYSQL__DATABASE=py_small_admin
DB_CONNECTIONS__MYSQL__USERNAME=py_admin
DB_CONNECTIONS__MYSQL__PASSWORD=strong-password-here

# Redis 配置
DB_REDIS__DEFAULT__HOST=your-redis-host
DB_REDIS__DEFAULT__PASSWORD=strong-redis-password

# JWT 配置
JWT_SECRET_KEY="your-very-strong-secret-key-at-least-32-characters-long"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery 配置
CELERY_BROKER_URL="amqp://celery:strong-rabbitmq-password@your-rabbitmq-host:5672//"
CELERY_RESULT_BACKEND="redis://:strong-redis-password@your-redis-host:6379/2"
```

## 安全建议

### 必须修改的配置

生产环境必须修改以下配置：

1. **JWT_SECRET_KEY**：使用强随机字符串
2. **APP_ADMIN_X_API_KEY**：使用强随机字符串
3. **APP_DEFAULT_ADMIN_PASSWORD**：修改默认管理员密码
4. **数据库密码**：使用强密码
5. **Redis 密码**：如果 Redis 设置了密码
6. **RabbitMQ 密码**：使用强密码

### 推荐的安全配置

```bash
# 关闭调试模式
APP_DEBUG=false

# 关闭 API 文档（或使用复杂路径）
APP_DOCS_ENABLED=false

# 限制 CORS 来源
APP_CORS_ALLOW_ALL=false
APP_CORS_ORIGINS=["https://yourdomain.com"]

# 配置 API Key
APP_ADMIN_X_API_KEY="your-strong-api-key-here"

# 使用强密钥
JWT_SECRET_KEY="your-very-strong-secret-key-at-least-32-characters-long"
```

## 获取帮助

如果配置遇到问题：

1. 查看错误日志
2. 检查配置文件语法
3. 参考 [环境要求](./index.md)
4. 查看 [常见问题](../../faq/)