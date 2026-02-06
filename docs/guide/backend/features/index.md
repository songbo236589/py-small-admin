# 后端功能模块

本文档介绍了后端项目的各种功能模块。

## 功能模块列表

### 核心功能

| 模块 | 说明 | 文档 |
|------|------|------|
| 缓存功能 | Redis 缓存的使用和管理 | [cache.md](./cache.md) |
| 异常处理 | 统一的异常处理机制 | [exception.md](./exception.md) |
| 日志管理 | 日志配置和使用 | [log.md](./log.md) |
| 文件上传 | 文件上传和处理 | [upload.md](./upload.md) |
| 数据验证 | 数据验证和校验 | [validation.md](./validation.md) |

## 缓存功能 (Cache)

项目使用 Redis 作为缓存后端，提供了简单易用的缓存 API。

### 主要功能

- 基础缓存操作（get、set、delete）
- 缓存装饰器
- 缓存策略（Cache-Aside、Write-Through、Write-Behind）
- 缓存预热和更新
- 缓存统计

### 使用场景

- 热点数据缓存
- 查询结果缓存
- API 响应缓存
- 分布式锁

## 异常处理 (Exception)

项目使用 FastAPI 的异常处理机制，提供了统一的异常处理和错误响应。

### 主要功能

- 基础异常类型
- 自定义业务异常
- 全局异常处理器
- 异常日志记录

### 异常类型

| 异常类 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| `NotFoundException` | 资源不存在 | 404 |
| `ValidationException` | 数据验证失败 | 422 |
| `UnauthorizedException` | 未授权 | 401 |
| `BusinessException` | 业务异常 | 400 |

## 日志管理 (Log)

项目使用 `loguru` 作为日志库，提供了强大的日志功能和灵活的配置。

### 主要功能

- 多级别日志（DEBUG、INFO、WARNING、ERROR）
- 日志轮转和压缩
- 结构化日志
- 请求日志和性能日志
- 日志监控和告警

### 日志配置

- 控制台输出（彩色）
- 文件输出（按大小/时间轮转）
- 日志保留策略
- 日志格式化

## 文件上传 (Upload)

项目支持多种文件上传方式，包括本地存储和云存储。

### 存储方式

| 存储类型 | 说明 | 配置 |
|----------|------|------|
| 本地存储 | 文件保存到本地服务器 | `UPLOAD_DRIVER=local` |
| 七牛云 | 对象存储服务 | `UPLOAD_DRIVER=qiniu` |
| 阿里云 OSS | 对象存储服务 | `UPLOAD_DRIVER=aliyun` |
| 腾讯云 COS | 对象存储服务 | `UPLOAD_DRIVER=tencent` |

### 主要功能

- 文件类型验证
- 文件大小限制
- 图片处理（缩略图、水印、压缩）
- 分片上传
- 上传进度

## 数据验证 (Validation)

项目使用 Pydantic 进行数据验证，提供了强大的类型检查和验证功能。

### 主要功能

- 基础数据验证
- 自定义验证器
- 嵌套验证
- 列表验证
- 验证错误处理

### 验证装饰器

| 装饰器 | 说明 |
|--------|------|
| `@validate_request_data` | 请求数据验证 |
| `@validate_body_data` | 请求体验证 |
| `@field_validator` | 字段验证 |
| `@model_validator` | 模型验证 |

## 功能依赖关系

```
┌─────────────┐
│   请求入口   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  数据验证   │ ◄────────┐
└──────┬──────┘          │
       │                 │
       ▼                 │
┌─────────────┐          │
│  业务逻辑   │          │
└──────┬──────┘          │
       │                 │
       ▼                 │
┌─────────────┐          │
│   缓存层    │          │
└──────┬──────┘          │
       │                 │
       ▼                 │
┌─────────────┐          │
│  数据库层   │          │
└─────────────┘          │
                          │
       ▲                  │
       │                  │
┌──────┴──────────────────┘
│
│ ┌─────────┐  ┌──────────┐
│ │异常处理  │  │ 日志记录  │
│ └─────────┘  └──────────┘
└────────────────────────┘
```

## 最佳实践

### 1. 使用缓存减少数据库压力

```python
@cache(key_prefix="user", ttl=3600)
def get_user(user_id: int):
    """获取用户信息，缓存 1 小时"""
    return db.query_user(user_id)
```

### 2. 统一异常处理

```python
try:
    result = process_data()
except ValidationException as e:
    return error_response(e.message)
except Exception as e:
    logger.error("处理失败", exc_info=True)
    return error_response("系统错误")
```

### 3. 记录关键操作日志

```python
logger.info("用户登录", extra={
    "user_id": user.id,
    "ip": request.client.host,
    "action": "login"
})
```

### 4. 文件上传安全验证

```python
# 验证文件类型
validator = FileValidator()
if not validator.validate_type(file, allowed_types):
    raise ValidationException("不支持的文件类型")

# 验证文件大小
if not validator.validate_size(file, max_size=10*1024*1024):
    raise ValidationException("文件大小超过限制")
```

## 相关文档

- [配置指南](../config/index.md)
- [API 文档](../../api/)
- [模块开发规范](../module-guide.md)
