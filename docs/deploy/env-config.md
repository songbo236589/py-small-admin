# 环境变量配置详解

本文档详细说明了 `.env` 配置文件中的所有环境变量及其作用。

## 快速开始

### 1. 复制配置文件模板

```bash
# 进入服务端目录
cd server

# 复制模板文件
cp .env.example .env
```

### 2. 修改配置

根据你的部署环境，修改 `.env` 文件中的配置项。重点需要修改的配置已用 **[必须修改]** 标注。

### 3. 配置文件规则

- 配置格式：`KEY=value`
- 注释符号：`#`
- 字符串建议用引号包裹：`KEY="value"`
- 布尔值：`true` 或 `false`
- JSON 格式：`KEY='["item1", "item2"]'`

---

## 配置项详解

### 应用基础配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `APP_NAME` | 应用名称 | Py Small Admin | 用于日志、文档等显示 |
| `APP_ENV` | 运行环境 | development | 可选: development/production/testing |
| `APP_DEBUG` | 调试模式 | true | **生产环境必须设为 false** |
| `APP_VERSION` | 应用版本号 | 1.0.0 | 用于 API 版本控制 |
| `APP_DESCRIPTION` | 应用描述 | Py Small Admin 服务 | 用于 API 文档生成 |
| `APP_HOST` | 服务监听地址 | 0.0.0.0 | 0.0.0.0=监听所有网卡 |
| `APP_PORT` | 服务监听端口 | 8009 | 1-65535 |
| `APP_RELOAD` | 代码自动重载 | true | 开发环境 true，生产环境 false |
| `APP_API_PREFIX` | API 路径前缀 | /api | 所有 API 路由的前缀 |
| `APP_TIMEZONE` | 时区设置 | Asia/Shanghai | 影响日志、定时任务等 |

### API 文档配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `APP_DOCS_ENABLED` | 是否启用 API 文档 | true | 生产环境可选择性关闭 |
| `APP_DOCS_URL` | Swagger UI 路径 | /docs | 访问地址: http://host:port/docs |
| `APP_OPENAPI_URL` | OpenAPI JSON 路径 | /openapi.json | 用于生成客户端 SDK |

### 跨域配置 (CORS)

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `APP_CORS_ALLOW_ALL` | 是否允许所有来源 | true | **生产环境建议 false** |
| `APP_CORS_ORIGINS` | 允许的来源列表 | ["*"] | JSON 格式 |
| `APP_CORS_METHODS` | 允许的 HTTP 方法 | ["*"] | JSON 格式 |
| `APP_CORS_HEADERS` | 允许的请求头 | ["*"] | JSON 格式 |

**生产环境推荐配置**：
```env
APP_CORS_ALLOW_ALL=false
APP_CORS_ORIGINS=["https://yourdomain.com"]
APP_CORS_METHODS=["GET","POST","PUT","DELETE","PATCH"]
APP_CORS_HEADERS=["Content-Type","Authorization"]
```

### 管理员账号配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `APP_ADMIN_X_API_KEY` | 管理 API 密钥 | QPp38siu... | **[必须修改]** |
| `APP_DEFAULT_ADMIN_USERNAME` | 默认管理员账号 | admin | 首次启动时创建 |
| `APP_DEFAULT_ADMIN_PASSWORD` | 默认管理员密码 | 123456 | **[必须修改] 首次启动后请立即修改** |

### 日志配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `LOG_LEVEL` | 日志级别 | INFO | DEBUG/INFO/WARNING/ERROR/CRITICAL |
| `LOG_CONSOLE` | 是否输出到控制台 | true | |
| `LOG_FILE_PATH` | 日志文件路径 | logs/{time:YYYY-MM-DD}.log | 支持按日期分割 |
| `LOG_ROTATION` | 日志轮转时间 | 00:00 | 每天何时创建新日志文件 |
| `LOG_RETENTION` | 日志保留时间 | 30 days | 超过此时长的日志将被删除 |
| `LOG_COMPRESSION` | 压缩格式 | zip | zip/gz/tar/空字符串 |

### 数据库配置

#### MySQL 连接配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `DB_DEFAULT` | 默认数据库类型 | mysql | |
| `DB_CONNECTIONS__MYSQL__HOST` | MySQL 主机地址 | mysql | Docker 内部用容器名 |
| `DB_CONNECTIONS__MYSQL__PORT` | MySQL 端口 | 3306 | |
| `DB_CONNECTIONS__MYSQL__DATABASE` | 数据库名称 | fastapi_db | 需提前创建 |
| `DB_CONNECTIONS__MYSQL__USERNAME` | 用户名 | root | **[必须修改]** |
| `DB_CONNECTIONS__MYSQL__PASSWORD` | 密码 | root123456 | **[必须修改]** |
| `DB_CONNECTIONS__MYSQL__CHARSET` | 字符集 | utf8mb4 | |
| `DB_CONNECTIONS__MYSQL__COLLATION` | 排序规则 | utf8mb4_unicode_ci | |
| `DB_CONNECTIONS__MYSQL__PREFIX` | 表前缀 | fa_ | 用于多应用共享数据库 |

#### Redis 默认连接配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `DB_REDIS__DEFAULT__HOST` | Redis 主机 | redis | Docker 内部用容器名 |
| `DB_REDIS__DEFAULT__PORT` | Redis 端口 | 6379 | |
| `DB_REDIS__DEFAULT__USERNAME` | 用户名 | default | Redis 6.0+ 支持 |
| `DB_REDIS__DEFAULT__PASSWORD` | 密码 | redis123456 | **[必须修改]** |
| `DB_REDIS__DEFAULT__DATABASE` | 数据库编号 | 0 | 0-15 |
| `DB_REDIS__DEFAULT__PREFIX` | 键前缀 | redis_default_ | |
| `DB_REDIS__DEFAULT__MAX_CONNECTIONS` | 连接池最大连接数 | 50 | 推荐核心数*2+1 |
| `DB_REDIS__DEFAULT__SOCKET_TIMEOUT` | 读写超时(秒) | 5 | |
| `DB_REDIS__DEFAULT__HEALTH_CHECK_INTERVAL` | 健康检查间隔(秒) | 30 | |

#### Redis 缓存连接配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `DB_REDIS__CACHE__HOST` | Redis 主机 | redis | |
| `DB_REDIS__CACHE__PORT` | Redis 端口 | 6379 | |
| `DB_REDIS__CACHE__DATABASE` | 数据库编号 | 1 | 使用不同 DB 与业务分离 |
| `DB_REDIS__CACHE__PASSWORD` | 密码 | redis123456 | **[必须修改]** |
| `DB_REDIS__CACHE__PREFIX` | 键前缀 | cache_ | |

### 缓存配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CACHE_CONNECTION` | 使用的缓存连接名 | cache | 对应 DB_REDIS__CACHE__ |
| `CACHE_DEFAULT_TTL` | 默认过期时间(秒) | 31536000 | 0 表示永不过期 |
| `CACHE_KEY_PREFIX` | 缓存键前缀 | cache | |

### 密码配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `PWD_PASSWORD_SCHEMES` | 支持的加密算法 | ["bcrypt"] | 可选: bcrypt/argon2/pbkdf2_sha256 |
| `PWD_PASSWORD_DEFAULT_SCHEME` | 默认加密算法 | bcrypt | |
| `PWD_BCRYPT_ROUNDS` | bcrypt 加密轮数 | 12 | 范围 4-31，值越大越安全但越慢 |
| `PWD_BCRYPT_IDENT` | bcrypt 算法标识符 | 2b | 当前标准版本 |

### JWT 认证配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `JWT_SECRET_KEY` | JWT 密钥 | 9fXZLvB7... | **[必须修改] 至少32字符** |
| `JWT_ALGORITHM` | 签名算法 | HS256 | HS256/RS256/ES256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 访问令牌有效期(分钟) | 30 | |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 刷新令牌有效期(天) | 7 | |
| `JWT_ISSUER` | 签发者标识 | fast-api-admin | |
| `JWT_AUDIENCE` | 目标受众 | fast-client-admin | |
| `JWT_ENABLE_BLACKLIST` | 是否启用令牌黑名单 | true | 启用后登出/刷新的令牌会被加入黑名单 |

### 验证码配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CAPTCHA_LENGTH` | 验证码字符长度 | 4 | 4-8 个字符 |
| `CAPTCHA_WIDTH` | 图片宽度(像素) | 120 | 80-300 |
| `CAPTCHA_HEIGHT` | 图片高度(像素) | 50 | 30-150 |
| `CAPTCHA_FONT_SIZE` | 字体大小(像素) | 36 | 20-60 |
| `CAPTCHA_CHAR_TYPE` | 字符类型 | alphanumeric | numeric/alpha/alphanumeric/mixed |
| `CAPTCHA_EXPIRE_SECONDS` | 过期时间(秒) | 300 | |
| `CAPTCHA_DEFAULT_TYPE` | 默认验证码类型 | image | image/math |

### 文件上传配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `UPLOAD_DIR` | 本地存储目录 | ./uploads | |
| `UPLOAD_URL_PREFIX` | 访问 URL 前缀 | /uploads | |
| `UPLOAD_FILENAME_RULE` | 文件命名规则 | uuid | uuid/timestamp/original/md5 |
| `UPLOAD_PATH_RULE` | 路径规则 | Y-m-d | 按日期分层 |

#### 阿里云 OSS 配置

| 变量名 | 说明 | 备注 |
|--------|------|------|
| `UPLOAD_OSS_ACCESS_KEY_ID` | AccessKey ID | 在阿里云控制台获取 |
| `UPLOAD_OSS_ACCESS_KEY_SECRET` | AccessKey Secret | **[必须修改]** |
| `UPLOAD_OSS_BUCKET` | 存储桶名称 | Bucket 名称，全局唯一 |
| `UPLOAD_OSS_REGION` | 区域 | oss-cn-hangzhou 等 |
| `UPLOAD_OSS_CDN_DOMAIN` | CDN 加速域名 | 可选 |

#### 腾讯云 COS 配置

| 变量名 | 说明 | 备注 |
|--------|------|------|
| `UPLOAD_COS_SECRET_ID` | SecretId | 在腾讯云控制台获取 |
| `UPLOAD_COS_SECRET_KEY` | SecretKey | **[必须修改]** |
| `UPLOAD_COS_BUCKET` | 存储桶名称 | 格式: BucketName-APPID |
| `UPLOAD_COS_REGION` | 区域 | ap-guangzhou 等 |

#### 七牛云 Kodo 配置

| 变量名 | 说明 | 备注 |
|--------|------|------|
| `UPLOAD_KODO_ACCESS_KEY` | AccessKey | 在七牛云控制台获取 |
| `UPLOAD_KODO_SECRET_KEY` | SecretKey | **[必须修改]** |
| `UPLOAD_KODO_BUCKET` | 存储空间名称 | |
| `UPLOAD_KODO_REGION` | 存储区域 | z0(华东)/z1(华北) 等 |
| `UPLOAD_KODO_DOMAIN` | CDN 域名 | |

### Celery + RabbitMQ 配置

#### Broker 配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CELERY_BROKER_URL` | Broker URL | amqp://admin:admin123@... | **[必须修改]** |
| `CELERY_BROKER_CONNECTION_RETRY` | 连接失败自动重试 | true | |
| `CELERY_BROKER_CONNECTION_MAX_RETRIES` | 最大重试次数 | 5 | |
| `CELERY_BROKER_USE_SSL` | 是否使用 SSL | false | 生产环境建议开启 |

#### Result Backend 配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CELERY_RESULT_BACKEND` | 结果存储 URL | redis://default:redis... | **[必须修改]** |
| `CELERY_RESULT_EXPIRES` | 结果过期时间(秒) | 3600 | |

#### Worker 配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CELERY_WORKER_POOL` | 执行池类型 | threads | threads/gevent/solo |
| `CELERY_WORKER_CONCURRENCY` | 并发数 | 4 | 推荐核心数*2-4 |
| `CELERY_WORKER_PREFETCH_MULTIPLIER` | 预取倍数 | 4 | |
| `CELERY_WORKER_MAX_TASKS_PER_CHILD` | 每进程最大任务数 | 1000 | 防止内存泄漏 |

#### 任务配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CELERY_TASK_DEFAULT_QUEUE` | 默认队列名称 | default | |
| `CELERY_TASK_DEFAULT_RATE_LIMIT` | 默认速率限制 | 空 | 格式: "10/s" 或 "100/m" |
| `CELERY_TASK_DEFAULT_TIME_LIMIT` | 硬超时(秒) | 3600 | 超时强制终止 |
| `CELERY_TASK_DEFAULT_SOFT_TIME_LIMIT` | 软超时(秒) | 3000 | 可捕获处理 |
| `CELERY_TASK_DEFAULT_MAX_RETRIES` | 最大重试次数 | 3 | |
| `CELERY_TASK_ACKS_LATE` | 延迟确认 | true | 生产环境推荐开启 |

#### Beat 定时任务配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CELERY_BEAT_SCHEDULE_FILENAME` | 调度状态文件 | celerybeat-schedule | |
| `CELERY_BEAT_MAX_LOOP_INTERVAL` | 最大循环间隔(秒) | 5 | |
| `CELERY_BEAT_SCHEDULER` | 调度器类型 | PersistentScheduler | |

#### Flower 监控配置

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `CELERY_FLOWER_PORT` | 监控服务端口 | 5555 | |
| `CELERY_FLOWER_HOST` | 监听地址 | 0.0.0.0 | |
| `CELERY_FLOWER_BASIC_AUTH` | 基本认证 | admin:123456 | **[必须修改]** |

---

## 生产环境安全检查清单

部署到生产环境前，请务必确认以下配置已修改：

- [ ] `APP_DEBUG=false` - 关闭调试模式
- [ ] `APP_ADMIN_X_API_KEY` - 修改为强密钥
- [ ] `APP_DEFAULT_ADMIN_PASSWORD` - 修改为强密码
- [ ] `DB_CONNECTIONS__MYSQL__USERNAME` - 使用专用数据库账号
- [ ] `DB_CONNECTIONS__MYSQL__PASSWORD` - 使用强密码
- [ ] `DB_REDIS__DEFAULT__PASSWORD` - 设置 Redis 密码
- [ ] `DB_REDIS__CACHE__PASSWORD` - 设置缓存 Redis 密码
- [ ] `JWT_SECRET_KEY` - 修改为至少32字符的强密钥
- [ ] `CELERY_BROKER_URL` - 修改 RabbitMQ 密码
- [ ] `CELERY_RESULT_BACKEND` - 修改 Redis 密码
- [ ] `CELERY_FLOWER_BASIC_AUTH` - 修改 Flower 认证密码
- [ ] `APP_CORS_ALLOW_ALL=false` - 限制 CORS 来源
- [ ] `APP_CORS_ORIGINS` - 设置为实际的前端域名

---

## 常见问题

### 1. 配置不生效？

检查以下几点：
- 配置文件是否在 `server/.env`
- 配置格式是否正确（注意引号和逗号）
- JSON 格式的配置是否正确
- 是否已重启服务

### 2. 如何生成强密钥？

```bash
# Python 方式
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL 方式
openssl rand -base64 32
```

### 3. Docker 部署时的注意事项

- 容器间通信使用容器名作为主机地址（如 `mysql`、`redis`）
- 宿主机访问使用 `localhost` 或 `127.0.0.1`
- 端口映射后，外部访问使用映射后的端口

### 4. 环境变量优先级

代码中的配置优先级：环境变量 > .env 文件 > 默认值

---

## 下一步

配置完成后，请参考：
- [后端部署](./backend/deploy.md) - 后端服务部署
- [前端部署](./frontend/build.md) - 前端构建和部署
- [数据库迁移](./database/migration.md) - 数据库初始化
