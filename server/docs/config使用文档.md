# Config 配置系统使用文档

## 概述

本项目采用基于 Pydantic Settings 的配置管理系统，提供了类型安全、环境变量支持、多级路径访问等特性。配置系统由两部分组成：

1. **配置类**：位于 `config/` 目录下，定义各类配置的结构和默认值
2. **配置访问接口**：位于 `Modules/common/libs/config/` 目录下，提供统一的配置访问门面

## 主要特性

- ✅ **类型安全**：基于 Pydantic 的类型校验和转换
- ✅ **环境变量支持**：自动从环境变量和 `.env` 文件读取配置
- ✅ **多级路径访问**：支持通过点号分隔访问嵌套配置
- ✅ **线程安全**：配置注册中心采用线程安全设计
- ✅ **延迟加载**：只在首次访问时初始化配置
- ✅ **配置验证**：自动验证配置值的有效性

## 配置类结构

### 1. BaseConfig - 基础配置类

位置：[`config/base.py`](config/base.py:1)

所有配置类的基类，定义了通用的配置行为，包括：

- `.env` 文件读取配置
- 环境变量前缀设置
- 类型校验和转换规则
- 嵌套字段分隔符设置

### 2. AppConfig - 应用基础配置

位置：[`config/app.py`](config/app.py:1)

管理应用的基础设置，如名称、版本、环境等。

**环境变量前缀**：`APP_`

**主要配置项**：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | str | "Fast API" | 应用名称 |
| `env` | AppEnv | AppEnv.production | 运行环境 |
| `debug` | bool | False | 调试模式 |
| `version` | str | "1.0.0" | API版本 |
| `host` | str | "0.0.0.0" | 服务主机地址 |
| `port` | int | 8000 | 服务端口 |
| `api_prefix` | str | "/api" | API前缀 |
| `docs_enabled` | bool | True | 是否启用OpenAPI文档 |
| `timezone` | str | "Asia/Shanghai" | 时区设置 |

### 3. DatabaseConfig - 数据库配置

位置：[`config/database.py`](config/database.py:1)

管理数据库（SQL + Redis）连接配置。

**环境变量前缀**：`DB_`

**主要配置项**：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `default` | str | "mysql" | 默认数据库连接名称 |
| `connections` | dict | - | 数据库连接配置字典 |
| `redis` | dict | - | Redis连接配置字典 |

### 4. CacheConfig - 缓存配置

位置：[`config/cache.py`](config/cache.py:1)

管理缓存设置，支持 Redis 和内存缓存。

**环境变量前缀**：`CACHE_`

**主要配置项**：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `default` | str | "redis" | 默认缓存驱动 |
| `stores` | dict | - | 缓存存储配置字典 |

### 5. JWTConfig - JWT认证配置

位置：[`config/jwt.py`](config/jwt.py:1)

管理JWT认证相关设置。

**环境变量前缀**：`JWT_`

**主要配置项**：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `secret_key` | str | "my-super-secure-jwt-secret-key-12345" | JWT密钥 |
| `algorithm` | JWTAlgorithm | HS256 | 签名算法 |
| `access_token_expire_minutes` | int | 30 | 访问令牌过期时间(分钟) |
| `refresh_token_expire_days` | int | 7 | 刷新令牌过期时间(天) |
| `enable_blacklist` | bool | False | 是否启用JWT黑名单 |

### 6. LogConfig - 日志配置

位置：[`config/log.py`](config/log.py:1)

管理日志输出设置。

**环境变量前缀**：`LOG_`

**主要配置项**：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `level` | str | "INFO" | 日志级别 |
| `console` | bool | True | 是否在控制台输出日志 |
| `file_path` | str | "logs/{time:YYYY-MM-DD}.log" | 日志文件路径 |
| `rotation` | str | "00:00" | 日志文件轮转策略 |
| `retention` | str | "30 days" | 日志文件保留时间 |
| `compression` | str | "zip" | 轮转后的日志文件压缩格式 |

### 7. PasswordConfig - 密码配置

位置：[`config/password.py`](config/password.py:1)

管理密码哈希和验证相关设置。

**环境变量前缀**：`PWD_`

**主要配置项**：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `password_schemes` | list[str] | ["bcrypt"] | 启用的密码哈希算法列表 |
| `password_default_scheme` | str | "bcrypt" | 默认密码哈希算法 |
| `bcrypt_rounds` | int | 12 | bcrypt计算轮数 |
| `bcrypt_ident` | str | "2b" | bcrypt版本标识 |

## 配置访问接口

### Config 类

位置：[`Modules/common/libs/config/config.py`](Modules/common/libs/config/config.py:1)

提供统一的配置访问接口，支持通过点号分隔的键名来访问和设置配置值。

#### 主要方法

##### 1. 获取配置值

```python
from Modules.common.libs.config import Config

# 获取整个配置对象
app_config = Config.get("app")

# 获取配置对象的特定属性
app_name = Config.get("app.name")
debug_mode = Config.get("app.debug", False)  # 带默认值

# 多级路径访问
db_host = Config.get("database.connections.mysql.host", "localhost")
```

##### 2. 设置配置值

```python
# 动态设置配置值（仅影响当前进程）
Config.set("app.debug", True)

# 注意：只支持设置一层属性
# Config.set("app.database.host", "localhost")  # 会抛出 ValueError
```

##### 3. 检查配置是否存在

```python
# 检查配置对象是否存在
has_app = Config.has("app")  # True

# 检查配置对象的属性是否存在
has_name = Config.has("app.name")  # True
has_nonexistent = Config.has("app.nonexistent")  # False
```

##### 4. 获取所有配置快照

```python
# 获取所有配置的只读副本（调试用）
all_configs = Config.all()
```

### ConfigRegistry 类

位置：[`Modules/common/libs/config/registry.py`](Modules/common/libs/config/registry.py:1)

配置注册中心，负责管理所有配置实例的生命周期。采用单例模式确保全局只实例化一次配置。

#### 主要方法

```python
from Modules.common.libs.config import ConfigRegistry

# 初始化并注册所有配置（线程安全）
ConfigRegistry.load()

# 获取指定名称的配置实例
app_config = ConfigRegistry.get("app")

# 获取所有配置实例的只读副本
all_configs = ConfigRegistry.all()
```

## 环境变量配置

### .env 文件格式

项目使用 `.env` 文件来管理环境变量，参考 [`.env.example`](.env.example:1) 文件。

### 环境变量命名规则

1. **简单配置**：`{PREFIX}_{FIELD_NAME}`
   - 例如：`APP_NAME`, `LOG_LEVEL`, `JWT_SECRET_KEY`

2. **嵌套配置**：`{PREFIX}__{NESTED_KEY}__{FIELD_NAME}`
   - 使用双下划线 `__` 作为嵌套分隔符
   - 例如：`CACHE_STORES__REDIS__PORT`, `DB_CONNECTIONS__MYSQL__HOST`

### 配置示例

```bash
# 应用基础配置
APP_NAME="Quantify API"
APP_VERSION="1.0.0"
DEBUG=true

# 数据库配置
DB_DEFAULT=mysql
DB_CONNECTIONS__MYSQL__HOST=127.0.0.1
DB_CONNECTIONS__MYSQL__PORT=3306
DB_CONNECTIONS__MYSQL__DATABASE=quantify_db

# Redis配置
DB_REDIS__DEFAULT__HOST=127.0.0.1
DB_REDIS__DEFAULT__PORT=6379
DB_REDIS__DEFAULT__DATABASE=0

# 缓存配置
CACHE_DEFAULT=redis
CACHE_STORES__REDIS__ENDPOINT=127.0.0.1
CACHE_STORES__REDIS__PORT=6379
CACHE_STORES__REDIS__DB=1

# JWT配置
JWT_SECRET_KEY="your-super-secret-jwt-key-change-in-production"
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 日志配置
LOG_LEVEL=INFO
LOG_CONSOLE=true
LOG_FILE_PATH="logs/{time:YYYY-MM-DD}.log"
```

## 使用示例

### 1. 基本使用

```python
from Modules.common.libs.config import Config

# 获取应用名称
app_name = Config.get("app.name")

# 获取数据库配置
db_config = Config.get("database")
mysql_host = Config.get("database.connections.mysql.host")

# 获取JWT配置
jwt_secret = Config.get("jwt.secret_key")
jwt_expire = Config.get("jwt.access_token_expire_minutes")
```

### 2. 带默认值的获取

```python
# 获取调试模式，默认为 False
debug_mode = Config.get("app.debug", False)

# 获取数据库端口，默认为 3306
db_port = Config.get("database.connections.mysql.port", 3306)
```

### 3. 检查配置存在性

```python
# 检查配置是否存在
if Config.has("app.api_prefix"):
    prefix = Config.get("app.api_prefix")
else:
    prefix = "/api"
```

### 4. 动态设置配置

```python
# 设置调试模式（仅影响当前进程）
Config.set("app.debug", True)

# 设置日志级别
Config.set("log.level", "DEBUG")
```

### 5. 在应用初始化中使用

```python
from fastapi import FastAPI
from Modules.common.libs.config import Config

app = FastAPI(
    title=Config.get("app.name"),
    description=Config.get("app.description"),
    version=Config.get("app.version"),
    debug=Config.get("app.debug"),
    openapi_url=Config.get("app.openapi_url"),
)

# 获取数据库配置
db_url = Config.get("database.connections.mysql.url")
```

## 最佳实践

1. **环境变量优先**：优先使用环境变量配置，便于不同环境的部署
2. **敏感信息**：密钥、密码等敏感信息不要提交到版本控制
3. **默认值**：为重要配置提供合理的默认值
4. **类型安全**：利用 Pydantic 的类型校验确保配置值正确
5. **文档更新**：添加新配置时及时更新文档

## 注意事项

1. **动态设置限制**：`Config.set()` 只支持设置一层属性，不支持多级路径
2. **进程隔离**：动态设置的配置仅影响当前进程，不会持久化
3. **线程安全**：配置初始化是线程安全的，但动态设置不是
4. **性能考虑**：配置系统采用延迟加载，只在首次访问时初始化

## 扩展配置

### 添加新的配置类

1. 在 `config/` 目录下创建新的配置类，继承 `BaseConfig`
2. 在 `Modules/common/libs/config/registry.py` 的 `load()` 方法中注册新配置
3. 更新 `.env.example` 文件，添加相关环境变量示例

### 示例：添加邮件配置

```python
# config/email.py
from pydantic import Field
from config.base import BaseConfig

class EmailConfig(BaseConfig):
    model_config = BaseConfig.model_config | {"env_prefix": "EMAIL_"}
    
    smtp_host: str = Field(default="smtp.example.com", description="SMTP服务器地址")
    smtp_port: int = Field(default=587, description="SMTP服务器端口")
    username: str = Field(default="", description="邮箱用户名")
    password: str = Field(default="", description="邮箱密码")
    from_email: str = Field(default="", description="发件人邮箱")

# Modules/common/libs/config/registry.py
@classmethod
def load(cls) -> None:
    # ... 其他代码 ...
    cls._configs = {
        "app": AppConfig(),
        "log": LogConfig(),
        "database": DatabaseConfig(),
        "cache": CacheConfig(),
        "password": PasswordConfig(),
        "jwt": JWTConfig(),
        "email": EmailConfig(),  # 新增配置
    }
    # ... 其他代码 ...
```

## 常见问题

### Q: 如何在不同环境中使用不同的配置？

A: 使用环境变量和 `.env` 文件。为每个环境创建不同的 `.env` 文件（如 `.env.development`, `.env.production`），在部署时加载对应的环境配置。

### Q: 配置修改后是否需要重启应用？

A: 环境变量的修改需要重启应用才能生效。使用 `Config.set()` 动态设置的配置只影响当前进程，不需要重启。

### Q: 如何处理敏感配置信息？

A: 敏感信息（如密钥、密码）应该通过环境变量或安全的密钥管理系统提供，不要硬编码在代码中或提交到版本控制。

### Q: 如何验证配置是否正确加载？

A: 使用 `Config.all()` 获取所有配置快照进行检查，或在应用启动时打印关键配置信息（注意不要输出敏感信息）。