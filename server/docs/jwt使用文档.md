# JWT 模块使用文档

## 概述

`libs/jwt` 模块是一个完整的 JWT (JSON Web Token) 认证解决方案，提供了令牌生成、验证、解码和管理功能。该模块支持多种签名算法、令牌黑名单、过期时间管理，并与配置系统和缓存服务深度集成。

该模块主要包含以下文件：

- `jwt_service.py`: JWT 服务核心类
- `utils.py`: JWT 便捷工具函数
- `config/jwt.py`: JWT 配置类

## 主要功能

- 访问令牌和刷新令牌的生成
- 令牌验证和解码
- 令牌黑名单管理（基于 Redis）
- 支持多种签名算法（HS256/384/512, RS256/384/512, ES256/384/512）
- 灵活的令牌过期时间配置
- 单例模式的 JWT 服务实例
- 完整的错误处理和日志记录

## 安装与导入

```python
from Modules.common.libs.jwt import (
    # JWT 服务类
    JWTService,
    get_jwt_service,
    
    # 便捷函数
    jwt_create_access_token,
    jwt_create_refresh_token,
    jwt_verify_token,
    jwt_decode_token,
    jwt_is_token_blacklisted,
    jwt_blacklist_token,
    jwt_get_token_payload_without_verification,
    
    # 工具函数
    create_user_token_payload,
    extract_user_info_from_token_payload,
    is_access_token,
    is_refresh_token,
    get_token_remaining_time,
    format_token_info,
)
```

## JWT 配置

### 基本配置

JWT 配置通过 `JWTConfig` 类管理，支持环境变量配置：

```python
from config.jwt import JWTConfig, JWTAlgorithm, TokenType

# 获取 JWT 配置
config = JWTConfig()
print(config.secret_key)  # JWT 密钥
print(config.algorithm)   # 签名算法
print(config.access_token_expire_minutes)  # 访问令牌过期时间
print(config.refresh_token_expire_days)    # 刷新令牌过期时间
```

### 环境变量配置

可以通过环境变量配置 JWT：

```bash
# 基础配置
JWT_SECRET_KEY="your-super-secure-jwt-secret-key"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 校验相关
JWT_ISSUER="your-app-name"
JWT_AUDIENCE="your-app-users"
JWT_VERIFY_EXPIRATION=true
JWT_VERIFY_ISSUER=true
JWT_VERIFY_AUDIENCE=true


# Claim 配置

JWT_ACCESS_TOKEN_TYPE="access"
JWT_REFRESH_TOKEN_TYPE="refresh"

# 黑名单配置
JWT_ENABLE_BLACKLIST=true
JWT_BLACKLIST_PREFIX="jwt:blacklist:"
```

### 支持的签名算法

```python
from config.jwt import JWTAlgorithm

# 对称算法（HS系列）
HS256 = "HS256"  # HMAC + SHA-256
HS384 = "HS384"  # HMAC + SHA-384
HS512 = "HS512"  # HMAC + SHA-512

# 非对称算法（RS系列）
RS256 = "RS256"  # RSA + SHA-256
RS384 = "RS384"  # RSA + SHA-384
RS512 = "RS512"  # RSA + SHA-512

# 非对称算法（ES系列）
ES256 = "ES256"  # ECDSA P-256 + SHA-256
ES384 = "ES384"  # ECDSA P-384 + SHA-384
ES512 = "ES512"  # ECDSA P-521 + SHA-512
```

## JWT 服务类

### JWTService 类

`JWTService` 是核心的 JWT 服务类，提供所有令牌操作方法。

#### 初始化 JWT 服务

```python
from Modules.common.libs.jwt import JWTService

# 创建 JWT 服务实例
jwt_service = JWTService()

# 或者使用单例模式
from Modules.common.libs.jwt import get_jwt_service
jwt_service = get_jwt_service()
```

#### 创建访问令牌

```python
# 基本用法
payload = {"sub": "123", "username": "张三"}
access_token = jwt_service.create_access_token(payload)

# 自定义过期时间
from datetime import timedelta
custom_token = jwt_service.create_access_token(
    payload, 
    expires_delta=timedelta(hours=2)
)
```

#### 创建刷新令牌

```python
# 基本用法
payload = {"sub": "123", "username": "张三"}
refresh_token = jwt_service.create_refresh_token(payload)

# 自定义过期时间
from datetime import timedelta
custom_refresh_token = jwt_service.create_refresh_token(
    payload, 
    expires_delta=timedelta(days=30)
)
```

#### 验证令牌

```python
# 验证访问令牌
try:
    payload = jwt_service.verify_token(access_token, token_type="access")
    print(f"用户ID: {payload['sub']}")
    print(f"用户名: {payload['username']}")
except jwt.InvalidTokenError as e:
    print(f"令牌无效: {e}")

# 验证刷新令牌
try:
    payload = jwt_service.verify_token(refresh_token, token_type="refresh")
    print(f"刷新令牌有效，用户ID: {payload['sub']}")
except jwt.InvalidTokenError as e:
    print(f"刷新令牌无效: {e}")
```

#### 解码令牌（不验证）

```python
# 仅解码，不验证签名和过期时间
payload = jwt_service.decode_token(token)
print(payload)
```

#### 令牌黑名单管理

```python
from datetime import datetime, UTC

# 检查令牌是否在黑名单中
token_jti = payload.get("jti")
is_blacklisted = await jwt_service.is_token_blacklisted(token_jti)

# 将令牌加入黑名单
expires_at = datetime.fromtimestamp(payload["exp"], UTC)
success = await jwt_service.blacklist_token(token_jti, expires_at)
```

#### 获取令牌载荷（不验证）

```python
# 用于调试和日志记录
payload = jwt_service.get_token_payload_without_verification(token)
print(payload)
```

## 便捷函数

模块提供了一系列便捷函数，简化 JWT 操作：

```python
from Modules.common.libs.jwt import (
    jwt_create_access_token, jwt_create_refresh_token,
    jwt_verify_token, jwt_decode_token,
    jwt_blacklist_token, jwt_is_token_blacklisted,
    jwt_get_token_payload_without_verification
)
from datetime import timedelta

# 创建访问令牌
payload = {"sub": "123", "username": "张三"}
access_token = await jwt_create_access_token(payload)

# 创建刷新令牌
refresh_token = await jwt_create_refresh_token(
    payload, 
    expires_delta=timedelta(days=30)
)

# 验证令牌
try:
    payload = await jwt_verify_token(access_token, token_type="access")
    print(f"验证成功: {payload}")
except jwt.InvalidTokenError as e:
    print(f"验证失败: {e}")

# 解码令牌
payload = jwt_decode_token(access_token)

# 黑名单操作
token_jti = payload.get("jti")
is_blacklisted = await jwt_is_token_blacklisted(token_jti)
await jwt_blacklist_token(token_jti, datetime.now(UTC))
```

## 工具函数

### 用户令牌载荷创建

```python
from Modules.common.libs.jwt import create_user_token_payload

# 创建标准用户令牌载荷
payload = create_user_token_payload(
    user_id="123",
    username="张三",
    role="admin",
    permissions=["read", "write", "delete"]
)

print(payload)
# 输出:
# {
#     "sub": "123",
#     "username": "张三",
#     "role": "admin",
#     "permissions": ["read", "write", "delete"]
# }
```

### 提取用户信息

```python
from Modules.common.libs.jwt import extract_user_info_from_token_payload

# 从令牌载荷中提取用户信息
user_info = extract_user_info_from_token_payload(payload)

print(user_info)
# 输出:
# {
#     "user_id": "123",
#     "username": "张三",
#     "token_type": "access",
#     "issued_at": 1703505600,
#     "expires_at": 1703507400,
#     "jwt_id": "550e8400-e29b-41d4-a716-446655440000"
# }
```

### 令牌类型检查

```python
from Modules.common.libs.jwt import is_access_token, is_refresh_token

# 检查令牌类型
if is_access_token(payload):
    print("这是一个访问令牌")

if is_refresh_token(payload):
    print("这是一个刷新令牌")
```

### 获取令牌剩余时间

```python
from Modules.common.libs.jwt import get_token_remaining_time

# 获取令牌剩余有效时间（秒）
remaining_seconds = get_token_remaining_time(payload)
print(f"令牌剩余时间: {remaining_seconds} 秒")

if remaining_seconds == 0:
    print("令牌已过期")
```

### 格式化令牌信息

```python
from Modules.common.libs.jwt import format_token_info

# 格式化令牌信息为可读格式
token_info = format_token_info(payload)

print(token_info)
# 输出:
# {
#     "user_id": "123",
#     "username": "张三",
#     "token_type": "access",
#     "issued_at": 1703505600,
#     "expires_at": 1703507400,
#     "jwt_id": "550e8400-e29b-41d4-a716-446655440000",
#     "is_expired": False,
#     "remaining_seconds": 1800,
#     "formatted_expires_at": "2023-12-25T10:30:00+00:00",
#     "formatted_issued_at": "2023-12-25T10:00:00+00:00"
# }
```

## 实际应用场景

### 1. 用户登录认证

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Modules.common.libs.jwt import (
    jwt_create_access_token, jwt_create_refresh_token,
    jwt_verify_token, create_user_token_payload
)
from datetime import timedelta

app = FastAPI()
security = HTTPBearer()

@app.post("/auth/login")
async def login(username: str, password: str):
    # 验证用户凭据（示例）
    if not verify_user_credentials(username, password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 获取用户信息
    user = get_user_by_username(username)
    
    # 创建令牌载荷
    payload = create_user_token_payload(
        user_id=str(user.id),
        username=user.username,
        role=user.role
    )
    
    # 生成令牌
    access_token = await jwt_create_access_token(
        payload, 
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = await jwt_create_refresh_token(
        payload, 
        expires_delta=timedelta(days=7)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户依赖"""
    try:
        payload = await jwt_verify_token(credentials.credentials, token_type="access")
        return extract_user_info_from_token_payload(payload)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的访问令牌")

@app.get("/users/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
```

### 2. 令牌刷新机制

```python
from fastapi import HTTPException
from Modules.common.libs.jwt import (
    jwt_verify_token, jwt_create_access_token,
    jwt_blacklist_token, create_user_token_payload
)
from datetime import datetime, UTC

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        payload = await jwt_verify_token(refresh_token, token_type="refresh")
        
        # 将旧的刷新令牌加入黑名单
        token_jti = payload.get("jti")
        expires_at = datetime.fromtimestamp(payload["exp"], UTC)
        await jwt_blacklist_token(token_jti, expires_at)
        
        # 创建新的用户载荷
        user_payload = create_user_token_payload(
            user_id=payload["sub"],
            username=payload["username"],
            role=payload.get("role")
        )
        
        # 生成新的访问令牌
        new_access_token = await jwt_create_access_token(user_payload)
        
        # 生成新的刷新令牌
        new_refresh_token = await jwt_create_refresh_token(user_payload)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """用户登出"""
    try:
        # 验证访问令牌
        payload = await jwt_verify_token(credentials.credentials, token_type="access")
        
        # 将访问令牌加入黑名单
        token_jti = payload.get("jti")
        expires_at = datetime.fromtimestamp(payload["exp"], UTC)
        await jwt_blacklist_token(token_jti, expires_at)
        
        return {"message": "成功登出"}
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的访问令牌")
```

### 3. 权限验证装饰器

```python
from functools import wraps
from fastapi import HTTPException
from Modules.common.libs.jwt import jwt_verify_token, is_access_token

def require_permission(required_permission: str):
    """权限验证装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从请求中获取令牌
            token = get_token_from_request()
            
            try:
                # 验证令牌
                payload = await jwt_verify_token(token, token_type="access")
                
                # 检查权限
                user_permissions = payload.get("permissions", [])
                if required_permission not in user_permissions:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"需要 {required_permission} 权限"
                    )
                
                # 将用户信息添加到 kwargs
                kwargs["current_user"] = payload
                return await func(*args, **kwargs)
                
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="无效的访问令牌")
        
        return wrapper
    return decorator

# 使用示例
@app.delete("/users/{user_id}")
@require_permission("delete_user")
async def delete_user(user_id: str, current_user: dict = None):
    """删除用户（需要 delete_user 权限）"""
    # 执行删除操作
    return {"message": f"用户 {user_id} 已删除"}
```

### 4. API 限流

```python
from Modules.common.libs.jwt import jwt_verify_token, get_token_remaining_time
from Modules.common.libs.cache import cache_increment, cache_expire

async def rate_limit_by_user(token: str, limit: int, window: int):
    """基于用户的 API 限流"""
    try:
        # 验证令牌并获取用户信息
        payload = await jwt_verify_token(token, token_type="access")
        user_id = payload["sub"]
        
        # 限流计数器键
        rate_limit_key = f"rate_limit:user:{user_id}"
        
        # 递增计数器
        count = await cache_increment(rate_limit_key, 1)
        
        # 首次调用时设置过期时间
        if count == 1:
            await cache_expire(rate_limit_key, window)
        
        # 检查是否超过限制
        if count > limit:
            remaining_time = get_token_remaining_time(payload)
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，请在 {window} 秒后重试"
            )
        
        return True
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的访问令牌")

# 使用示例
@app.get("/api/data")
async def get_api_data(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取数据（带限流）"""
    # 每用户每分钟最多 100 次请求
    await rate_limit_by_user(credentials.credentials, limit=100, window=60)
    
    # 处理请求
    return {"data": "some data"}
```

## 最佳实践

### 1. 安全的密钥管理

```python
# 生产环境应该使用足够复杂和长的密钥
# 对称算法（HS系列）至少 32 字符
SECRET_KEY = "your-super-secure-jwt-secret-key-at-least-32-chars-long"

# 非对称算法（RS/ES系列）使用 PEM 格式的密钥
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
...your private key here...
-----END RSA PRIVATE KEY-----"""

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
...your public key here...
-----END PUBLIC KEY-----"""
```

### 2. 合理的过期时间设置

```python
# 访问令牌：短期有效（15-30分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 刷新令牌：长期有效（7-30天）
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 敏感操作令牌：极短期有效（5-15分钟）
SENSITIVE_TOKEN_EXPIRE_MINUTES = 15
```

### 3. 令牌载荷设计

```python
# 推荐：最小化载荷，只包含必要信息
payload = {
    "sub": "123",           # 用户ID（标准Claim）
    "username": "张三",     # 用户名
    "role": "admin",        # 用户角色
    "permissions": ["read", "write"],  # 权限列表
}

# 避免：在载荷中包含敏感信息
# 不推荐的做法：
# payload = {
#     "sub": "123",
#     "password": "hashed_password",  # 不要包含密码
#     "credit_card": "1234-5678-9012-3456",  # 不要包含敏感信息
# }
```

### 4. 错误处理

```python
from fastapi import HTTPException
from loguru import logger
import jwt

async def safe_verify_token(token: str, token_type: str = None):
    """安全的令牌验证"""
    try:
        return await jwt_verify_token(token, token_type)
    except jwt.ExpiredSignatureError:
        logger.warning("令牌已过期")
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError as e:
        logger.warning(f"令牌无效: {e}")
        raise HTTPException(status_code=401, detail="无效的令牌")
    except Exception as e:
        logger.error(f"令牌验证出错: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
```

### 5. 令牌黑名单策略

```python
# 启用黑名单功能
JWT_ENABLE_BLACKLIST = True

# 在以下情况将令牌加入黑名单：
# 1. 用户主动登出
# 2. 令牌刷新（旧的刷新令牌）
# 3. 密码修改后使所有现有令牌失效
# 4. 管理员强制用户下线

async def invalidate_all_user_tokens(user_id: str):
    """使用户所有令牌失效"""
    # 在数据库中记录令牌失效时间戳
    await update_user_token_version(user_id)
    
    # 可选：将已知令牌加入黑名单
    # 这需要维护一个活跃令牌列表
```

## 常见问题

### Q: 如何处理令牌泄露？

A: 如果怀疑令牌泄露，可以采取以下措施：

1. 立即将泄露的令牌加入黑名单
2. 修改用户密码，使所有现有令牌失效
3. 重新签发新的令牌
4. 记录安全事件，监控异常活动

```python
async def handle_token_leak(token: str):
    """处理令牌泄露"""
    try:
        # 验证令牌获取用户信息
        payload = await jwt_verify_token(token)
        user_id = payload["sub"]
        
        # 将泄露的令牌加入黑名单
        token_jti = payload.get("jti")
        expires_at = datetime.fromtimestamp(payload["exp"], UTC)
        await jwt_blacklist_token(token_jti, expires_at)
        
        # 修改用户密码
        await change_user_password(user_id, new_random_password())
        
        # 记录安全事件
        await log_security_event("token_leak", user_id)
        
        return {"message": "安全事件已处理，请重新登录"}
        
    except jwt.InvalidTokenError:
        return {"message": "无效令牌"}
```

### Q: 如何实现令牌续期？

A: 可以通过滑动窗口或定期刷新实现令牌续期：

```python
async def sliding_window_refresh(current_token: str):
    """滑动窗口续期"""
    try:
        payload = await jwt_verify_token(current_token)
        
        # 检查剩余时间
        remaining_time = get_token_remaining_time(payload)
        
        # 如果剩余时间少于阈值，则续期
        if remaining_time < 300:  # 5分钟
            # 创建新令牌
            user_payload = create_user_token_payload(
                user_id=payload["sub"],
                username=payload["username"]
            )
            new_token = await jwt_create_access_token(user_payload)
            
            # 将旧令牌加入黑名单
            old_jti = payload.get("jti")
            old_expires = datetime.fromtimestamp(payload["exp"], UTC)
            await jwt_blacklist_token(old_jti, old_expires)
            
            return new_token
        
        return current_token
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效令牌")
```

### Q: 如何支持多设备登录？

A: 可以为每个设备生成独立的令牌，并维护设备列表：

```python
async def create_device_token(user_id: str, device_info: dict):
    """为特定设备创建令牌"""
    # 创建包含设备信息的载荷
    payload = create_user_token_payload(
        user_id=user_id,
        username=get_username(user_id),
        device_id=device_info["device_id"],
        device_name=device_info["device_name"],
        device_type=device_info["device_type"]
    )
    
    # 生成令牌
    token = await jwt_create_access_token(payload)
    
    # 记录设备信息
    await save_user_device(user_id, device_info)
    
    return token

async def revoke_device_token(user_id: str, device_id: str):
    """撤销特定设备的令牌"""
    # 获取设备活跃令牌
    active_tokens = await get_user_device_tokens(user_id, device_id)
    
    # 将所有相关令牌加入黑名单
    for token_info in active_tokens:
        await jwt_blacklist_token(
            token_info["jti"], 
            token_info["expires_at"]
        )
    
    # 移除设备记录
    await remove_user_device(user_id, device_id)
```

### Q: 如何优化 JWT 性能？

A: 可以通过以下方式优化 JWT 性能：

1. 使用高效的签名算法（如 HS256）
2. 减小令牌载荷大小
3. 使用缓存存储验证结果
4. 批量验证令牌

```python
from Modules.common.libs.cache import cache_get_or_set

async def cached_verify_token(token: str, token_type: str = None):
    """带缓存的令牌验证"""
    # 生成缓存键
    cache_key = f"token_verify:{hash(token)}:{token_type or 'any'}"
    
    async def verify_and_cache():
        return await jwt_verify_token(token, token_type)
    
    # 缓存验证结果 5 分钟
    return await cache_get_or_set(cache_key, verify_and_cache, ttl=300)
```

## API 参考

### JWTService 类方法

| 方法 | 描述 |
|------|------|
| `create_access_token(payload, expires_delta=None)` | 创建访问令牌 |
| `create_refresh_token(payload, expires_delta=None)` | 创建刷新令牌 |
| `verify_token(token, token_type=None)` | 验证令牌并返回载荷 |
| `decode_token(token)` | 解码令牌（不验证） |
| `is_token_blacklisted(token_jti)` | 检查令牌是否在黑名单中 |
| `blacklist_token(token_jti, expires_at)` | 将令牌加入黑名单 |
| `get_token_payload_without_verification(token)` | 获取令牌载荷（不验证） |

### 便捷函数

| 函数 | 描述 |
|------|------|
| `jwt_create_access_token(payload, expires_delta=None)` | 便捷函数：创建访问令牌 |
| `jwt_create_refresh_token(payload, expires_delta=None)` | 便捷函数：创建刷新令牌 |
| `jwt_verify_token(token, token_type=None)` | 便捷函数：验证令牌 |
| `jwt_decode_token(token)` | 便捷函数：解码令牌（不验证） |
| `jwt_is_token_blacklisted(token_jti)` | 便捷函数：检查令牌是否在黑名单中 |
| `jwt_blacklist_token(token_jti, expires_at)` | 便捷函数：将令牌加入黑名单 |
| `jwt_get_token_payload_without_verification(token)` | 便捷函数：获取令牌载荷（不验证） |

### 工具函数

| 函数 | 描述 |
|------|------|
| `create_user_token_payload(user_id, username, **extra_claims)` | 创建标准用户令牌载荷 |
| `extract_user_info_from_token_payload(payload)` | 从令牌载荷中提取用户信息 |
| `is_access_token(payload)` | 检查是否为访问令牌 |
| `is_refresh_token(payload)` | 检查是否为刷新令牌 |
| `get_token_remaining_time(payload)` | 获取令牌剩余有效时间（秒） |
| `format_token_info(payload)` | 格式化令牌信息为可读格式 |

### 配置类

| 类 | 描述 |
|------|------|
| `JWTConfig` | JWT 配置类，支持环境变量配置 |
| `JWTAlgorithm` | JWT 签名算法枚举 |
| `TokenType` | JWT 令牌类型枚举 |

## 版本历史

- v1.0.0: 初始版本，提供基本的 JWT 令牌生成和验证功能
- v1.1.0: 添加令牌黑名单支持和便捷函数
- v1.2.0: 增强错误处理和日志记录
- v1.3.0: 添加更多签名算法支持和工具函数
- v1.4.0: 优化性能和缓存集成