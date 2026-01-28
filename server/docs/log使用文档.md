# Log 模块使用文档

## 概述

`libs/log` 模块是一个强大的日志记录库，基于 Loguru 实现，提供了时区感知的日志记录功能。该模块支持按天生成日志文件，可通过环境变量进行灵活配置，并与项目配置系统紧密集成。

该模块主要包含以下文件：

- `setup_logging.py`: 日志初始化和配置设置
- `config/log.py`: 日志配置类，支持环境变量配置

## 主要功能

- 时区感知的日志记录
- 按天自动轮转日志文件
- 灵活的日志级别控制
- 自定义日志格式（控制台和文件）
- 日志文件自动压缩和清理
- 支持环境变量配置
- 与项目配置系统集成

## 安装与导入

```python
from Modules.common.libs.log import setup_logging
from loguru import logger

# 初始化日志系统
setup_logging()

# 使用logger记录日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误信息")
```

## 日志配置

### 基本配置

日志配置通过 `LogConfig` 类管理，支持环境变量配置：

```python
from config.log import LogConfig

# 获取日志配置
config = LogConfig()
print(config.level)        # 日志级别，默认为 "INFO"
print(config.console)      # 是否在控制台输出，默认为 True
print(config.file_path)    # 日志文件路径，默认为 "logs/{time:YYYY-MM-DD}.log"
```

### 环境变量配置

可以通过环境变量配置日志：

```bash
# 日志级别
LOG_LEVEL=DEBUG

# 是否在控制台输出日志
LOG_CONSOLE=true

# 日志文件路径
LOG_FILE_PATH=logs/app_{time:YYYY-MM-DD}.log

# 日志文件轮转策略
LOG_ROTATION=00:00

# 日志文件保留时间
LOG_RETENTION=30 days

# 轮转后的日志文件压缩格式
LOG_COMPRESSION=zip

# 控制台日志格式
LOG_CONSOLE_FORMAT="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# 文件日志格式
LOG_FILE_FORMAT="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
```

## 日志初始化

### 基本初始化

```python
from Modules.common.libs.log import setup_logging

# 初始化日志系统
setup_logging()
```

这会从应用配置中读取日志设置，并配置 Loguru 的输出处理器。

### 初始化过程详解

`setup_logging()` 函数执行以下操作：

1. 移除 Loguru 的默认处理器
2. 从配置中读取日志参数
3. 获取时区配置
4. 创建时区感知的格式化器
5. 配置控制台输出（如果启用）
6. 配置文件输出（如果指定了文件路径）

## 日志级别

### 级别说明

Loguru 支持以下日志级别（按严重程度递增）：

1. **TRACE**: 最详细的调试信息
2. **DEBUG**: 调试信息，开发环境常用
3. **INFO**: 一般信息，生产环境推荐
4. **WARNING**: 警告信息
5. **ERROR**: 错误信息
6. **CRITICAL**: 严重错误信息

### 级别配置

```python
# 通过环境变量设置
LOG_LEVEL=INFO

# 通过代码设置
from loguru import logger
logger.remove()
logger.add(sys.stderr, level="INFO")
```

### 使用不同级别

```python
from loguru import logger

# 不同级别的日志示例
logger.trace("最详细的调试信息")
logger.debug("调试信息：变量值 = {}", variable)
logger.info("用户登录成功：用户ID = {}", user_id)
logger.warning("磁盘空间不足：剩余空间 = {}GB", free_space)
logger.error("数据库连接失败：{}", error_message)
logger.critical("系统内存不足，即将崩溃")
```

## 日志格式

### 控制台格式

控制台日志支持颜色和样式，默认格式为：

```
<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>
```

示例输出：

```
2023-12-25 10:30:00 | INFO     | main:login:45 - 用户登录成功：用户ID = 123
2023-12-25 10:30:01 | WARNING  | main:check_disk:78 - 磁盘空间不足：剩余空间 = 5GB
2023-12-25 10:30:02 | ERROR    | main:db_connect:23 - 数据库连接失败：连接超时
```

### 文件格式

文件日志不包含颜色标记，默认格式为：

```
{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}
```

示例输出：

```
2023-12-25 10:30:00 | INFO | main:login:45 - 用户登录成功：用户ID = 123
2023-12-25 10:30:01 | WARNING | main:check_disk:78 - 磁盘空间不足：剩余空间 = 5GB
2023-12-25 10:30:02 | ERROR | main:db_connect:23 - 数据库连接失败：连接超时
```

### 自定义格式

```python
# 通过环境变量自定义格式
LOG_CONSOLE_FORMAT="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
LOG_FILE_FORMAT="{time:YYYY-MM-DD HH:mm:ss.SSS} [{level}] {message}"

# 或者通过代码自定义
from loguru import logger
logger.add(
    "logs/custom.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {message}",
    level="INFO"
)
```

## 文件轮转与保留

### 轮转策略

支持多种轮转策略：

```bash
# 每天午夜轮转
LOG_ROTATION=00:00

# 每周轮转
LOG_ROTATION=1 week

# 按文件大小轮转
LOG_ROTATION=500 MB

# 每天特定时间轮转
LOG_ROTATION=10:00

# 每小时轮转
LOG_ROTATION=1 hour
```

### 保留策略

支持多种保留策略：

```bash
# 保留最近30天的日志
LOG_RETENTION=30 days

# 保留最近一周的日志
LOG_RETENTION=1 week

# 按总大小保留
LOG_RETENTION=10 GB

# 保留最近10个日志文件
LOG_RETENTION=10
```

### 压缩格式

支持多种压缩格式：

```bash
# ZIP压缩（默认）
LOG_COMPRESSION=zip

# GZIP压缩
LOG_COMPRESSION=gz

# TAR压缩
LOG_COMPRESSION=tar

# 不压缩
LOG_COMPRESSION=
```

## 时区支持

日志模块支持时区感知的时间戳，自动将日志时间转换为配置的时区：

```python
# 时区配置通过应用配置获取
# config/app.py
APP_CONFIG = {
    "timezone": "Asia/Shanghai",  # 默认时区
    # 其他配置...
}
```

日志时间会自动显示为配置的时区时间，便于本地化查看和分析。

## 实际应用场景

### 1. Web应用日志记录

```python
from fastapi import FastAPI, Request
from loguru import logger
from Modules.common.libs.log import setup_logging

# 初始化日志
setup_logging()

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应信息
    logger.info(
        f"请求完成: {request.method} {request.url} - "
        f"状态码: {response.status_code} - 处理时间: {process_time:.4f}s"
    )
    
    return response

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    logger.debug(f"获取用户信息: user_id={user_id}")
    
    try:
        user = await fetch_user_from_db(user_id)
        logger.info(f"成功获取用户信息: user_id={user_id}")
        return user
    except Exception as e:
        logger.error(f"获取用户信息失败: user_id={user_id}, error={str(e)}")
        raise
```

### 2. 数据库操作日志

```python
import asyncio
from loguru import logger

async def execute_query(query, params=None):
    """执行数据库查询并记录日志"""
    logger.debug(f"执行SQL查询: {query}, 参数: {params}")
    
    try:
        start_time = time.time()
        result = await db.execute(query, params)
        execution_time = time.time() - start_time
        
        logger.info(f"SQL查询成功: 耗时={execution_time:.4f}s, 影响行数={result.rowcount}")
        return result
    except Exception as e:
        logger.error(f"SQL查询失败: query={query}, error={str(e)}")
        raise

async def transaction_example():
    """事务操作日志示例"""
    logger.info("开始事务")
    
    try:
        async with db.transaction():
            logger.debug("执行事务操作1")
            await db.execute("INSERT INTO users (name) VALUES ($1)", "张三")
            
            logger.debug("执行事务操作2")
            await db.execute("UPDATE stats SET user_count = user_count + 1")
            
        logger.info("事务提交成功")
    except Exception as e:
        logger.error(f"事务回滚: error={str(e)}")
        raise
```

### 3. 错误处理和异常日志

```python
import traceback
from loguru import logger

class CustomException(Exception):
    """自定义异常"""
    pass

def risky_operation():
    """可能出错的操作"""
    try:
        # 模拟可能出错的操作
        if random.random() < 0.5:
            raise CustomException("随机错误")
        
        result = "操作成功"
        logger.info("操作执行成功")
        return result
    except CustomException as e:
        logger.warning(f"自定义异常: {str(e)}")
        raise
    except Exception as e:
        # 记录完整的异常堆栈
        logger.error(f"未预期的异常: {str(e)}\n{traceback.format_exc()}")
        raise

# 使用异常捕获装饰器
def log_exceptions(func):
    """异常日志装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"函数 {func.__name__} 执行异常")
            raise
    return wrapper

@log_exceptions
def api_call(endpoint):
    """API调用示例"""
    logger.debug(f"调用API: {endpoint}")
    # 模拟API调用
    response = requests.get(endpoint)
    response.raise_for_status()
    logger.info(f"API调用成功: {endpoint}")
    return response.json()
```

### 4. 性能监控日志

```python
import time
from functools import wraps
from loguru import logger

def log_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"函数 {func.__name__} 执行成功，耗时: {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.4f}s, 错误: {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"函数 {func.__name__} 执行成功，耗时: {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.4f}s, 错误: {str(e)}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

# 使用示例
@log_performance
async def process_data(data):
    """数据处理函数"""
    logger.debug(f"开始处理数据，数据量: {len(data)}")
    
    # 模拟数据处理
    await asyncio.sleep(0.5)
    
    logger.debug("数据处理完成")
    return {"processed": len(data)}
```

## 高级用法

### 1. 条件日志记录

```python
from loguru import logger

# 使用条件判断记录不同级别的日志
def log_based_on_user_role(user_role, message):
    if user_role == "admin":
        logger.info(f"[管理员] {message}")
    elif user_role == "moderator":
        logger.info(f"[版主] {message}")
    else:
        logger.debug(f"[用户] {message}")

# 使用日志级别判断
def log_with_level(level, message):
    if level == "debug":
        logger.debug(message)
    elif level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.info(message)  # 默认级别
```

### 2. 结构化日志

```python
from loguru import logger
import json

# 记录结构化数据
def log_structured_data():
    user_data = {
        "user_id": 123,
        "username": "张三",
        "email": "zhangsan@example.com",
        "roles": ["user", "moderator"],
        "last_login": "2023-12-25T10:30:00Z"
    }
    
    # 记录为JSON字符串
    logger.info(f"用户数据: {json.dumps(user_data, ensure_ascii=False)}")
    
    # 或者使用logger.bind添加额外字段
    logger.bind(user_id=user_data["user_id"], username=user_data["username"]).info(
        "用户登录成功"
    )

# 使用logger.bind添加上下文信息
def log_with_context():
    # 创建带有上下文的logger
    context_logger = logger.bind(request_id="req-123", user_id=456)
    
    context_logger.info("开始处理请求")
    context_logger.debug("执行业务逻辑")
    context_logger.info("请求处理完成")
```

### 3. 日志过滤

```python
from loguru import logger

# 创建过滤器
def critical_only(record):
    """只允许CRITICAL级别的日志通过"""
    return record["level"].name == "CRITICAL"

def not_debug(record):
    """过滤掉DEBUG级别的日志"""
    return record["level"].name != "DEBUG"

# 添加带过滤器的处理器
logger.add(
    "logs/critical.log",
    filter=critical_only,
    level="DEBUG"  # 设置为DEBUG级别，但过滤器会进一步筛选
)

logger.add(
    "logs/no_debug.log",
    filter=not_debug,
    level="DEBUG"
)

# 使用lambda表达式过滤
logger.add(
    "logs/specific_module.log",
    filter=lambda record: "specific_module" in record["name"],
    level="DEBUG"
)
```

### 4. 异步日志记录

```python
import asyncio
from loguru import logger

# 启用异步模式（默认已启用）
logger.add("logs/async.log", enqueue=True)

async def async_logging_example():
    """异步日志记录示例"""
    tasks = []
    
    # 创建多个异步日志任务
    for i in range(10):
        task = asyncio.create_task(
            asyncio.to_thread(logger.info, f"异步日志消息 {i}")
        )
        tasks.append(task)
    
    # 等待所有日志任务完成
    await asyncio.gather(*tasks)
    logger.info("所有异步日志记录完成")
```

## 最佳实践

### 1. 日志级别使用建议

```python
# 开发环境
LOG_LEVEL=DEBUG

# 生产环境
LOG_LEVEL=INFO

# 测试环境
LOG_LEVEL=WARNING
```

### 2. 敏感信息保护

```python
import re
from loguru import logger

def sanitize_sensitive_data(message):
    """清理敏感信息"""
    # 隐藏密码
    message = re.sub(r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'password "***"', message, flags=re.IGNORECASE)
    
    # 隐藏手机号
    message = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', message)
    
    # 隐藏邮箱
    message = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'***@\2', message)
    
    return message

# 使用自定义过滤器
def sensitive_filter(record):
    """敏感信息过滤器"""
    record["message"] = sanitize_sensitive_data(record["message"])
    return record

logger.add("logs/sanitized.log", filter=sensitive_filter)
```

### 3. 日志轮转配置建议

```bash
# 开发环境：保留较少的日志，便于调试
LOG_ROTATION=100 MB
LOG_RETENTION=3 days
LOG_COMPRESSION=zip

# 生产环境：保留较长时间的日志，便于问题追踪
LOG_ROTATION=00:00
LOG_RETENTION=90 days
LOG_COMPRESSION=gz

# 高流量环境：按大小轮转，防止单个文件过大
LOG_ROTATION=1 GB
LOG_RETENTION=30 days
LOG_COMPRESSION=gz
```

### 4. 性能优化

```python
# 使用异步模式
logger.add("logs/performance.log", enqueue=True)

# 适当设置日志级别，避免记录过多调试信息
logger.remove()
logger.add(sys.stderr, level="INFO")  # 生产环境使用INFO级别

# 避免在循环中频繁记录日志
def process_items(items):
    logger.info(f"开始处理 {len(items)} 个项目")
    
    for i, item in enumerate(items):
        # 只记录关键信息，避免每项都记录
        if i % 100 == 0:
            logger.debug(f"已处理 {i}/{len(items)} 个项目")
        
        # 处理项目
        process_item(item)
    
    logger.info("所有项目处理完成")
```

## 常见问题

### Q: 如何在多进程环境中使用日志？

A: Loguru 在多进程环境中可能需要特殊配置：

```python
import multiprocessing
from loguru import logger

def worker_process():
    # 在子进程中重新配置日志
    logger.remove()
    logger.add(f"logs/worker_{multiprocessing.current_process().pid}.log")
    logger.info("子进程启动")

if __name__ == "__main__":
    # 主进程配置
    logger.add("logs/main.log")
    
    # 创建子进程
    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=worker_process)
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
```

### Q: 如何将日志发送到远程服务？

A: 可以通过自定义sink将日志发送到远程服务：

```python
import requests
from loguru import logger

def remote_sink(message):
    """远程日志sink"""
    try:
        requests.post(
            "https://api.logservice.com/logs",
            json={"message": message, "timestamp": time.time()},
            timeout=5
        )
    except Exception as e:
        # 避免日志记录失败导致应用崩溃
        print(f"发送远程日志失败: {e}")

# 添加远程日志处理器
logger.add(remote_sink, level="ERROR")
```

### Q: 如何动态调整日志级别？

A: 可以通过代码动态调整日志级别：

```python
from loguru import logger

def set_log_level(level):
    """动态设置日志级别"""
    logger.remove()
    logger.add(sys.stderr, level=level)
    logger.info(f"日志级别已设置为: {level}")

# 根据环境变量动态设置
import os
log_level = os.getenv("LOG_LEVEL", "INFO")
set_log_level(log_level)
```

## API 参考

### setup_logging 函数

| 函数 | 描述 |
|------|------|
| `setup_logging()` | 初始化日志系统，从配置中读取设置 |

### LogConfig 类属性

| 属性 | 描述 | 默认值 |
|------|------|--------|
| `level` | 日志级别 | "INFO" |
| `console` | 是否在控制台输出 | True |
| `file_path` | 日志文件路径 | "logs/{time:YYYY-MM-DD}.log" |
| `rotation` | 文件轮转策略 | "00:00" |
| `retention` | 文件保留时间 | "30 days" |
| `compression` | 压缩格式 | "zip" |
| `console_format` | 控制台日志格式 | 带颜色的格式字符串 |
| `file_format` | 文件日志格式 | 纯文本格式字符串 |

### 日志级别

| 级别 | 描述 |
|------|------|
| `TRACE` | 最详细的调试信息 |
| `DEBUG` | 调试信息 |
| `INFO` | 一般信息 |
| `WARNING` | 警告信息 |
| `ERROR` | 错误信息 |
| `CRITICAL` | 严重错误信息 |

## 版本历史

- v1.0.0: 初始版本，提供基本的日志记录功能
- v1.1.0: 添加时区感知的日志时间戳
- v1.2.0: 增强文件轮转和压缩功能
- v1.3.0: 优化性能，添加异步日志支持