# 环境变量配置

本文档介绍了项目的环境变量配置。

## 配置文件位置

- 开发环境: `.env.development`
- 生产环境: `.env.production`
- 测试环境: `.env.test`

## 基础配置

### 应用配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `APP_NAME` | 应用名称 | py-small-admin | - |
| `APP_ENV` | 运行环境 | development | development/production |
| `APP_DEBUG` | 调试模式 | true | true/false |
| `APP_PORT` | 应用端口 | 8000 | 8000 |
| `APP_HOST` | 应用主机 | 0.0.0.0 | 0.0.0.0 |
| `API_PREFIX` | API 前缀 | /api | /api |

### 数据库配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `DB_HOST` | 数据库主机 | localhost | 127.0.0.1 |
| `DB_PORT` | 数据库端口 | 3306 | 3306 |
| `DB_USER` | 数据库用户名 | root | admin |
| `DB_PASSWORD` | 数据库密码 | - | password123 |
| `DB_NAME` | 数据库名称 | py_small_admin | py_small_admin |
| `DB_CHARSET` | 字符集 | utf8mb4 | utf8mb4 |

### Redis 配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `REDIS_HOST` | Redis 主机 | localhost | 127.0.0.1 |
| `REDIS_PORT` | Redis 端口 | 6379 | 6379 |
| `REDIS_PASSWORD` | Redis 密码 | - | - |
| `REDIS_DB` | Redis 数据库 | 0 | 0 |
| `REDIS_CACHE_DB` | 缓存数据库 | 1 | 1 |
| `REDIS_CELERY_DB` | Celery 数据库 | 2 | 2 |

### JWT 配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `JWT_SECRET_KEY` | JWT 密钥 | - | your-secret-key |
| `JWT_ALGORITHM` | JWT 算法 | HS256 | HS256/RS256 |
| `JWT_ACCESS_TOKEN_EXPIRES` | 访问令牌过期时间 | 7200 | 7200 (秒) |
| `JWT_REFRESH_TOKEN_EXPIRES` | 刷新令牌过期时间 | 604800 | 604800 (秒) |

### Celery 配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `CELERY_BROKER_URL` | Broker URL | redis://localhost:6379/3 | redis://localhost:6379/3 |
| `CELERY_RESULT_BACKEND` | 结果存储 | redis://localhost:6379/4 | redis://localhost:6379/4 |
| `CELERY_TIMEZONE` | 时区 | Asia/Shanghai | Asia/Shanghai |
| `CELERY_WORKER_CONCURRENCY` | Worker 并发数 | 4 | 4 |

### 文件上传配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `UPLOAD_DRIVER` | 上传驱动 | local | local/qiniu/aliyun/tencent |
| `UPLOAD_PATH` | 本地上传路径 | uploads | ./uploads |
| `UPLOAD_URL_PREFIX` | 访问 URL 前缀 | /uploads | /uploads |
| `UPLOAD_MAX_SIZE` | 最大文件大小 | 10485760 | 10485760 (10MB) |

#### 七牛云配置

| 变量名 | 说明 |
|--------|------|
| `QINIU_ACCESS_KEY` | 访问密钥 |
| `QINIU_SECRET_KEY` | 秘密密钥 |
| `QINIU_BUCKET` | 存储桶名称 |
| `QINIU_DOMAIN` | 访问域名 |

#### 阿里云 OSS 配置

| 变量名 | 说明 |
|--------|------|
| `ALIYUN_OSS_ACCESS_KEY_ID` | 访问密钥 ID |
| `ALIYUN_OSS_ACCESS_KEY_SECRET` | 访问密钥 Secret |
| `ALIYUN_OSS_BUCKET` | 存储桶名称 |
| `ALIYUN_OSS_ENDPOINT` | 节点地址 |
| `ALIYUN_OSS_DOMAIN` | 访问域名 |

#### 腾讯云 COS 配置

| 变量名 | 说明 |
|--------|------|
| `TENCENT_COS_SECRET_ID` | 秘密 ID |
| `TENCENT_COS_SECRET_KEY` | 秘密密钥 |
| `TENCENT_COS_BUCKET` | 存储桶名称 |
| `TENCENT_COS_REGION` | 地域 |
| `TENCENT_COS_DOMAIN` | 访问域名 |

### 邮件配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `MAIL_HOST` | 邮件服务器 | smtp.qq.com | smtp.gmail.com |
| `MAIL_PORT` | 邮件端口 | 587 | 587 |
| `MAIL_USERNAME` | 邮件用户名 | - | user@example.com |
| `MAIL_PASSWORD` | 邮件密码 | - | password |
| `MAIL_FROM` | 发件人 | - | noreply@example.com |
| `MAIL_ENCRYPTION` | 加密方式 | tls | tls/ssl |
| `MAIL_FROM_NAME` | 发件人名称 | - | 系统通知 |

### 日志配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `LOG_LEVEL` | 日志级别 | INFO | DEBUG/INFO/WARNING/ERROR |
| `LOG_PATH` | 日志路径 | logs | ./logs |
| `LOG_MAX_SIZE` | 单文件最大大小 | 10485760 | 10485760 (10MB) |
| `LOG_BACKUP_COUNT` | 备份文件数量 | 10 | 10 |

### CORS 配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `CORS_ORIGINS` | 允许的源 | * | http://localhost:5173 |
| `CORS_CREDENTIALS` | 允许携带凭证 | true | true/false |
| `CORS_METHODS` | 允许的方法 | * | GET,POST,PUT,DELETE |
| `CORS_HEADERS` | 允许的头部 | * | Content-Type,Authorization |

### Ollama AI 配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `CONTENT_OLLAMA_BASE_URL` | Ollama 服务地址 | http://localhost:11434 | http://localhost:11434 |
| `CONTENT_OLLAMA_MODEL` | 默认使用的模型 | qwen2.5:7b | llama3.2:8b |
| `CONTENT_OLLAMA_TIMEOUT` | AI 生成超时时间（秒） | 120 | 120 |
| `CONTENT_OLLAMA_ENABLED` | 是否启用 AI 功能 | true | true/false |

**Ollama 安装说明**：详见 [安装指南 - Ollama 安装](../../getting-started/install.md#42-安装-ollama可选)

## 配置示例

### 开发环境 (.env.development)

```env
# 应用配置
APP_NAME=py-small-admin
APP_ENV=development
APP_DEBUG=true
APP_PORT=8000
API_PREFIX=/api

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=py_small_admin

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT 配置
JWT_SECRET_KEY=dev-secret-key
JWT_ACCESS_TOKEN_EXPIRES=7200
JWT_REFRESH_TOKEN_EXPIRES=604800

# 上传配置
UPLOAD_DRIVER=local
UPLOAD_PATH=uploads

# 邮件配置
MAIL_HOST=smtp.qq.com
MAIL_PORT=587
MAIL_USERNAME=your@qq.com
MAIL_PASSWORD=your-password
MAIL_FROM=your@qq.com
```

### 生产环境 (.env.production)

```env
# 应用配置
APP_NAME=py-small-admin
APP_ENV=production
APP_DEBUG=false
APP_PORT=8000
API_PREFIX=/api

# 数据库配置
DB_HOST=your-db-host
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=strong-password
DB_NAME=py_small_admin

# Redis 配置
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=redis-password
REDIS_DB=0

# JWT 配置
JWT_SECRET_KEY=your-production-secret-key
JWT_ACCESS_TOKEN_EXPIRES=7200
JWT_REFRESH_TOKEN_EXPIRES=604800

# 上传配置 (使用七牛云)
UPLOAD_DRIVER=qiniu
QINIU_ACCESS_KEY=your-access-key
QINIU_SECRET_KEY=your-secret-key
QINIU_BUCKET=your-bucket
QINIU_DOMAIN=https://cdn.example.com

# 邮件配置
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=noreply@example.com
MAIL_PASSWORD=mail-password
MAIL_FROM=noreply@example.com
MAIL_FROM_NAME=系统通知
```

## 配置读取

在代码中使用配置：

```python
from Modules.common.libs.config import Config

# 获取配置
app_name = Config.get("app.name")
app_port = Config.get("app.port", default=8000)

# 获取嵌套配置
db_host = Config.get("database.host")
jwt_secret = Config.get("jwt.secret_key")
```

## 安全建议

1. **敏感信息**: 不要在代码中硬编码密钥、密码等敏感信息
2. **版本控制**: 将 `.env.*.example` 文件提交到版本控制，实际的 `.env.*` 文件加入 `.gitignore`
3. **权限控制**: 确保配置文件的读取权限正确设置
4. **密钥轮换**: 定期更换 JWT 密钥等敏感配置
5. **环境隔离**: 开发、测试、生产环境使用不同的配置
