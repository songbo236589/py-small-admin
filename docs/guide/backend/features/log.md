# 日志管理

本文档介绍了项目的日志管理功能。

## 简介

项目使用 `loguru` 作为日志库，提供了强大的日志功能和灵活的配置。

## 基础使用

### 导入 logger

```python
from loguru import logger

logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
logger.debug("这是一条调试日志")
```

### 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| TRACE | 最详细的跟踪信息 | 调试复杂问题 |
| DEBUG | 调试信息 | 开发调试 |
| INFO | 一般信息 | 记录正常流程 |
| WARNING | 警告信息 | 潜在问题 |
| ERROR | 错误信息 | 错误但程序可继续 |
| CRITICAL | 严重错误 | 程序无法继续 |

## 日志配置

### 基础配置

```python
from loguru import logger
import sys

# 移除默认处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# 添加文件输出
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    compression="zip",
)
```

### 配置说明

| 参数 | 说明 | 示例 |
|------|------|------|
| level | 日志级别 | "INFO", "DEBUG" |
| format | 日志格式 | "{time} {level} {message}" |
| rotation | 日志轮转 | "500 MB", "00:00", "1 day" |
| retention | 日志保留 | "10 days", "1 month" |
| compression | 压缩格式 | "zip", "gz" |
| encoding | 编码 | "utf-8" |
| colorize | 颜色输出 | True, False |

## 日志格式

### 格式化变量

```python
logger.add(
    "logs/app.log",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
)
```

### 可用变量

| 变量 | 说明 |
|------|------|
| {time} | 时间 |
| {level} | 日志级别 |
| {name} | 模块名 |
| {function} | 函数名 |
| {line} | 行号 |
| {file} | 文件名 |
| {message} | 日志内容 |
| {exception} | 异常信息 |

## 结构化日志

### 使用 extra

```python
# 添加额外信息
logger.bind(user_id=123, action="login").info("用户登录")

# 使用 extra
logger.info("请求处理", extra={
    "user_id": 123,
    "action": "get_data",
    "duration": 0.5
})
```

### 使用 context

```python
from loguru import logger

# 添加 context
logger.contextualize(user_id=123, request_id="abc123")
logger.info("处理请求")

# 使用 patch
with logger.contextualize(user_id=456):
    logger.info("这个日志包含 user_id=456")
```

## 异常日志

### 记录异常

```python
try:
    result = 1 / 0
except Exception as e:
    # 记录异常（包含堆栈跟踪）
    logger.exception("发生错误")

    # 或使用 exc_info
    logger.error("发生错误", exc_info=True)
```

### 捕获异常栈

```python
@logger.catch
def risky_function():
    """自动捕获异常并记录"""
    result = 1 / 0

# 使用
risky_function()  # 异常会被 logger 捕获并记录
```

## 日志轮转

### 按大小轮转

```python
logger.add(
    "logs/app.log",
    rotation="500 MB",  # 文件达到 500MB 时创建新文件
)
```

### 按时间轮转

```python
logger.add(
    "logs/app.log",
    rotation="00:00",      # 每天午夜轮转
    # rotation="1 day",   # 或每天轮转
    # rotation="1 week",  # 或每周轮转
)
```

## 日志保留

### 按时间保留

```python
logger.add(
    "logs/app.log",
    retention="7 days",   # 保留 7 天
    # retention="1 month",  # 或保留 1 个月
    # retention="10 MB",    # 或保留最近 10MB
)
```

### 日志清理

```python
logger.add(
    "logs/app.log",
    retention=lambda files: [  # 自定义清理逻辑
        f for f in files
        if "important" in f.name or f.stat().st_size > 1024
    ]
)
```

## 请求日志

### 记录请求信息

```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求"""
    start_time = time.time()

    # 记录请求
    logger.info(f"请求开始: {request.method} {request.url.path}")

    response = await call_next(request)

    # 记录响应
    duration = time.time() - start_time
    logger.info(
        f"请求完成: {request.method} {request.url.path}",
        extra={
            "status_code": response.status_code,
            "duration": duration,
        }
    )

    return response
```

## 性能日志

### 记录执行时间

```python
from loguru import logger
import time

def time_it(func):
    """函数执行时间装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} 执行耗时: {duration:.2f}秒")
        return result
    return wrapper

# 使用
@time_it
def process_data():
    # 处理数据...
    pass
```

## 日志最佳实践

### 1. 合适的日志级别

```python
# DEBUG: 详细信息，用于开发调试
logger.debug(f"变量值: {variable}")

# INFO: 关键流程信息
logger.info("用户登录成功", extra={"user_id": 123})

# WARNING: 潜在问题
logger.warning("缓存命中率较低", extra={"hit_rate": 0.3})

# ERROR: 错误信息
logger.error("数据库连接失败", exc_info=True)
```

### 2. 添加上下文信息

```python
# 好
logger.info("用户登录", extra={"user_id": 123, "ip": "192.168.1.1"})

# 不好
logger.info("用户登录成功")
```

### 3. 敏感信息脱敏

```python
def mask_password(password):
    """密码脱敏"""
    return "*" * len(password)

logger.info("用户登录", extra={
    "username": "admin",
    "password": mask_password("password123")  # *********
})
```

### 4. 避免过度日志

```python
# 不好 - 循环中每条都记录
for item in items:
    logger.info(f"处理项目: {item.id}")

# 好 - 记录汇总
logger.info(f"处理 {len(items)} 个项目")
```

## 日志监控

### 日志告警

```python
from loguru import logger

class AlertHandler:
    """日志告警处理器"""

    def __init__(self):
        self.error_count = 0
        self.threshold = 10

    def write(self, message):
        if "ERROR" in message:
            self.error_count += 1
            if self.error_count >= self.threshold:
                # 发送告警
                send_alert(f"错误数量超过阈值: {self.error_count}")

# 添加处理器
logger.add(AlertHandler())
```

## 相关文档

- [异常处理](./exception.md)
- [配置指南](../config/index.md)
