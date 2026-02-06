# 后端配置指南

本文档介绍了后端项目的配置体系。

## 配置架构

项目采用分层配置架构：

```
配置加载流程:
1. 读取 .env 环境变量
2. 加载 config/default.py 默认配置
3. 根据环境加载 config/{env}.py 环境配置
4. 提供运行时动态配置
```

## 配置目录结构

```
server/
├── config/
│   ├── __init__.py        # 配置入口
│   ├── default.py         # 默认配置
│   ├── development.py     # 开发环境
│   ├── production.py      # 生产环境
│   └── test.py           # 测试环境
├── .env.development       # 开发环境变量
├── .env.production        # 生产环境变量
└── .env.test             # 测试环境变量
```

## 配置类结构

### 基础配置类

```python
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    """应用配置"""
    name: str = "py-small-admin"
    env: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"
    api_prefix: str = "/api"

    class Config:
        env_prefix = "APP_"

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    name: str = "py_small_admin"
    charset: str = "utf8mb4"

    class Config:
        env_prefix = "DB_"

    @property
    def url(self) -> str:
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
```

### 配置注册

```python
from Modules.common.libs.config.registry import ConfigRegistry

# 创建配置注册表
registry = ConfigRegistry()

# 注册配置
registry.register("app", AppConfig())
registry.register("database", DatabaseConfig())
registry.register("redis", RedisConfig())
registry.register("jwt", JwtConfig())
```

## 使用配置

### 获取配置

```python
from Modules.common.libs.config import Config

# 获取配置值
app_name = Config.get("app.name")
db_url = Config.get("database.url")

# 带默认值
timeout = Config.get("app.timeout", default=30)

# 获取整个配置对象
app_config = Config.get("app")
print(app_config.name, app_config.port)
```

### 类型安全访问

```python
from Modules.common.libs.config import Config

# 支持类型提示
from typing import Any
app_name: str = Config.get("app.name")
port: int = Config.get("app.port")
debug: bool = Config.get("app.debug")
```

## 环境切换

### 通过环境变量

```bash
# 设置运行环境
export APP_ENV=production

# Windows
set APP_ENV=production
```

### 通过命令行参数

```bash
python main.py --env production
```

### 通过配置文件

创建 `.env` 文件：

```env
APP_ENV=production
```

## 配置最佳实践

### 1. 配置分离

将不同环境的配置分离到不同文件：

```python
# config/development.py
DEBUG = True
DATABASE_HOST = "localhost"

# config/production.py
DEBUG = False
DATABASE_HOST = "prod-db.example.com"
```

### 2. 敏感信息保护

使用环境变量存储敏感信息：

```python
class DatabaseConfig(BaseSettings):
    password: str  # 从环境变量 DB_PASSWORD 读取
```

### 3. 配置验证

使用 Pydantic 进行配置验证：

```python
from pydantic import Field, validator

class AppConfig(BaseSettings):
    port: int = Field(..., ge=1024, le=65535)
    debug: bool = True

    @validator("port")
    def validate_port(cls, v):
        if v < 1024 or v > 65535:
            raise ValueError("端口必须在 1024-65535 之间")
        return v
```

### 4. 配置优先级

配置读取优先级（从高到低）：

1. 环境变量
2. .env 文件
3. 环境配置文件 (config/production.py)
4. 默认配置文件 (config/default.py)
5. 代码默认值

## 动态配置

### 运行时修改配置

```python
from Modules.common.libs.config import Config

# 修改配置
Config.set("app.debug", False)

# 批量修改
Config.update({
    "app.debug": False,
    "log.level": "WARNING"
})
```

### 配置监听

```python
from Modules.common.libs.config import Config

def on_config_change(key: str, value: Any):
    print(f"配置变更: {key} = {value}")

# 注册监听器
Config.add_listener("app.debug", on_config_change)
```

## 配置调试

### 查看当前配置

```python
from Modules.common.libs.config import Config

# 打印所有配置
Config.print_all()

# 获取所有配置键
keys = Config.keys()
```

### 配置检查

```python
from Modules.common.libs.config import Config

# 检查配置是否存在
if Config.has("app.port"):
    port = Config.get("app.port")

# 检查必需配置
required_configs = ["app.name", "database.url"]
missing = [c for c in required_configs if not Config.has(c)]
if missing:
    raise ValueError(f"缺少必需配置: {missing}")
```

## 相关文档

- [环境变量配置](./env-variables.md)
- [数据库配置](../features/cache.md)
- [Celery 配置](../async/celery-guide.md)
