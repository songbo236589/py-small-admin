# Password 模块使用文档

## 概述

`libs/password` 模块是一个安全的密码管理库，基于 Passlib 实现，提供了密码哈希、验证等核心功能。该模块支持多种哈希算法，特别是 bcrypt，并提供了灵活的配置选项和安全增强功能。

该模块主要包含以下文件：

- `password.py`: 密码服务核心类
- `__init__.py`: 模块导出和示例代码
- `config/password.py`: 密码配置类，支持环境变量配置

## 主要功能

- 安全的密码哈希生成
- 密码验证功能
- 支持多种哈希算法（主要是 bcrypt）
- 可配置的安全参数
- 防止定时攻击的安全增强
- 自动处理 bcrypt 的 72 字节限制

## 安装与导入

```python
from Modules.common.libs.password import PasswordService

# 初始化密码服务
pwd_service = PasswordService()
```

## 密码配置

### 基本配置

密码配置通过 `PasswordConfig` 类管理，支持环境变量配置：

```python
from config.password import PasswordConfig

# 获取密码配置
config = PasswordConfig()
print(config.password_schemes)         # 启用的密码哈希算法列表
print(config.password_default_scheme)  # 默认密码哈希算法
print(config.bcrypt_rounds)           # bcrypt 计算轮数
```

### 环境变量配置

可以通过环境变量配置密码服务：

```bash
# 启用的密码哈希算法
PWD_PASSWORD_SCHEMES=["bcrypt"]

# 默认密码哈希算法
PWD_PASSWORD_DEFAULT_SCHEME="bcrypt"

# 是否自动弃用旧算法
PWD_PASSWORD_DEPRECATED="auto"

# bcrypt 计算轮数（安全成本）
PWD_BCRYPT_ROUNDS=12

# bcrypt 版本标识
PWD_BCRYPT_IDENT="2b"

# bcrypt salt 长度
PWD_BCRYPT_SALT_SIZE=22

# 密码超过 bcrypt 长度限制时是否报错
PWD_BCRYPT_TRUNCATE_ERROR=true

# 最小密码校验耗时（防定时攻击）
PWD_MIN_VERIFY_TIME=0.1
```

## 密码服务类

### PasswordService 类

`PasswordService` 是核心的密码服务类，提供密码哈希和验证功能。

#### 初始化密码服务

```python
from Modules.common.libs.password import PasswordService

# 使用默认配置初始化
pwd_service = PasswordService()
```

初始化过程会：
1. 从配置中读取密码相关参数
2. 构建 CryptContext 对象
3. 配置 bcrypt 特定参数
4. 设置安全增强选项

#### 密码哈希生成

```python
# 生成密码哈希
password = "user_password_123"
hashed_password = pwd_service.hash_password(password)
print(hashed_password)
# 输出示例: $2b$12$EixZaYVK1fsbw1ZfbX3OmePDBZ0QJ2XJkPjQXJXJXJXJXJXJXJX

# 验证密码哈希格式
print(hashed_password.startswith("$2b$"))  # True (bcrypt 哈希)
```

#### 密码验证

```python
# 验证密码
password = "user_password_123"
hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OmePDBZ0QJ2XJkPjQXJXJXJXJXJXJXJX"

# 正确密码验证
is_valid = pwd_service.verify_password(password, hashed_password)
print(is_valid)  # True

# 错误密码验证
is_valid = pwd_service.verify_password("wrong_password", hashed_password)
print(is_valid)  # False
```

## 实际应用场景

### 1. 用户注册和登录

```python
from Modules.common.libs.password import PasswordService

class UserService:
    def __init__(self):
        self.pwd_service = PasswordService()
    
    async def register_user(self, username, password):
        """用户注册"""
        # 检查用户名是否已存在
        if await self.user_exists(username):
            raise ValueError("用户名已存在")
        
        # 生成密码哈希
        hashed_password = self.pwd_service.hash_password(password)
        
        # 保存用户信息到数据库
        user_id = await self.save_user_to_db(username, hashed_password)
        
        return {"user_id": user_id, "username": username}
    
    async def login_user(self, username, password):
        """用户登录"""
        # 从数据库获取用户信息
        user = await self.get_user_by_username(username)
        if not user:
            raise ValueError("用户名或密码错误")
        
        # 验证密码
        is_valid = self.pwd_service.verify_password(password, user["hashed_password"])
        if not is_valid:
            raise ValueError("用户名或密码错误")
        
        # 生成会话令牌
        session_token = await self.generate_session_token(user["user_id"])
        
        return {"user_id": user["user_id"], "session_token": session_token}
    
    async def change_password(self, user_id, old_password, new_password):
        """修改密码"""
        # 获取用户信息
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 验证旧密码
        is_valid = self.pwd_service.verify_password(old_password, user["hashed_password"])
        if not is_valid:
            raise ValueError("原密码错误")
        
        # 生成新密码哈希
        new_hashed_password = self.pwd_service.hash_password(new_password)
        
        # 更新数据库中的密码
        await self.update_user_password(user_id, new_hashed_password)
        
        return {"message": "密码修改成功"}

# 使用示例
user_service = UserService()

# 注册用户
try:
    result = await user_service.register_user("zhangsan", "secure_password_123")
    print(f"用户注册成功: {result}")
except ValueError as e:
    print(f"注册失败: {e}")

# 登录用户
try:
    result = await user_service.login_user("zhangsan", "secure_password_123")
    print(f"登录成功: {result}")
except ValueError as e:
    print(f"登录失败: {e}")
```

### 2. API 密码保护

```python
from fastapi import FastAPI, HTTPException, Depends
from Modules.common.libs.password import PasswordService

app = FastAPI()
pwd_service = PasswordService()

async def verify_api_key(api_key: str):
    """验证API密钥"""
    # 从数据库获取存储的API密钥哈希
    stored_hash = await get_stored_api_key_hash()
    
    # 验证API密钥
    if not pwd_service.verify_password(api_key, stored_hash):
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    return True

@app.get("/api/protected-data")
async def get_protected_data(authenticated: bool = Depends(verify_api_key)):
    """需要API密钥保护的接口"""
    return {"data": "这是受保护的数据", "access": "已授权"}

@app.post("/api/change-api-key")
async def change_api_key(
    new_api_key: str, 
    current_api_key: str,
    authenticated: bool = Depends(verify_api_key)
):
    """更改API密钥"""
    # 验证当前API密钥
    stored_hash = await get_stored_api_key_hash()
    if not pwd_service.verify_password(current_api_key, stored_hash):
        raise HTTPException(status_code=401, detail="当前API密钥无效")
    
    # 生成新API密钥的哈希
    new_hash = pwd_service.hash_password(new_api_key)
    
    # 更新数据库中的API密钥哈希
    await update_api_key_hash(new_hash)
    
    return {"message": "API密钥更新成功"}
```

### 3. 密码重置功能

```python
import secrets
from datetime import datetime, timedelta
from Modules.common.libs.password import PasswordService

class PasswordResetService:
    def __init__(self):
        self.pwd_service = PasswordService()
    
    async def request_password_reset(self, email):
        """请求密码重置"""
        # 检查邮箱是否存在
        user = await self.get_user_by_email(email)
        if not user:
            # 为了安全，即使用户不存在也返回成功
            return {"message": "如果邮箱存在，重置链接已发送"}
        
        # 生成重置令牌
        reset_token = secrets.token_urlsafe(32)
        
        # 存储重置令牌（带过期时间）
        expiry_time = datetime.now() + timedelta(hours=1)
        await self.store_reset_token(user["user_id"], reset_token, expiry_time)
        
        # 发送重置邮件（这里只是示例）
        reset_link = f"https://example.com/reset-password?token={reset_token}"
        await self.send_reset_email(email, reset_link)
        
        return {"message": "重置链接已发送到邮箱"}
    
    async def reset_password(self, token, new_password):
        """重置密码"""
        # 验证重置令牌
        token_data = await self.get_reset_token(token)
        if not token_data or token_data["expiry_time"] < datetime.now():
            raise ValueError("重置令牌无效或已过期")
        
        # 获取用户信息
        user = await self.get_user_by_id(token_data["user_id"])
        if not user:
            raise ValueError("用户不存在")
        
        # 生成新密码哈希
        new_hashed_password = self.pwd_service.hash_password(new_password)
        
        # 更新用户密码
        await self.update_user_password(user["user_id"], new_hashed_password)
        
        # 删除重置令牌
        await self.delete_reset_token(token)
        
        return {"message": "密码重置成功"}
    
    async def validate_reset_token(self, token):
        """验证重置令牌是否有效"""
        token_data = await self.get_reset_token(token)
        if not token_data or token_data["expiry_time"] < datetime.now():
            return False
        return True

# 使用示例
reset_service = PasswordResetService()

# 请求密码重置
result = await reset_service.request_password_reset("user@example.com")
print(result)

# 重置密码
try:
    result = await reset_service.reset_password(
        "reset_token_here", 
        "new_secure_password_456"
    )
    print(result)
except ValueError as e:
    print(f"重置失败: {e}")
```

## 安全最佳实践

### 1. 配置建议

```python
# 生产环境推荐配置
PWD_PASSWORD_SCHEMES=["bcrypt"]
PWD_PASSWORD_DEFAULT_SCHEME="bcrypt"
PWD_BCRYPT_ROUNDS=14  # 更高的安全成本
PWD_BCRYPT_IDENT="2b"
PWD_BCRYPT_TRUNCATE_ERROR=true
PWD_MIN_VERIFY_TIME=0.1  # 防止定时攻击

# 开发环境配置（更快但安全性较低）
PWD_BCRYPT_ROUNDS=10
```

### 2. 密码策略

```python
import re

class PasswordPolicy:
    """密码策略检查"""
    
    @staticmethod
    def validate_password_strength(password):
        """验证密码强度"""
        errors = []
        
        # 长度检查
        if len(password) < 8:
            errors.append("密码长度至少8位")
        
        # 复杂度检查
        if not re.search(r'[a-z]', password):
            errors.append("密码必须包含小写字母")
        
        if not re.search(r'[A-Z]', password):
            errors.append("密码必须包含大写字母")
        
        if not re.search(r'\d', password):
            errors.append("密码必须包含数字")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("密码必须包含特殊字符")
        
        return len(errors) == 0, errors

# 使用示例
policy = PasswordPolicy()
is_valid, errors = policy.validate_password_strength("MySecurePass123!")
if not is_valid:
    print("密码不符合要求:", errors)
```

### 3. 密码哈希升级

```python
class PasswordUpgradeService:
    """密码哈希升级服务"""
    
    def __init__(self):
        self.pwd_service = PasswordService()
    
    async def verify_and_upgrade_if_needed(self, user_id, password, current_hash):
        """验证密码并在需要时升级哈希"""
        # 验证密码
        if not self.pwd_service.verify_password(password, current_hash):
            return False
        
        # 检查是否需要升级哈希
        if self.needs_upgrade(current_hash):
            # 生成新的哈希
            new_hash = self.pwd_service.hash_password(password)
            
            # 更新数据库中的哈希
            await self.update_user_password_hash(user_id, new_hash)
            
            print(f"用户 {user_id} 的密码哈希已升级")
        
        return True
    
    def needs_upgrade(self, hashed_password):
        """检查是否需要升级密码哈希"""
        # 检查哈希算法
        if not hashed_password.startswith("$2b$"):
            return True
        
        # 检查成本因子
        current_rounds = int(hashed_password.split("$")[2])
        target_rounds = Config.get("password.bcrypt_rounds")
        
        return current_rounds < target_rounds

# 使用示例
upgrade_service = PasswordUpgradeService()

# 用户登录时检查并升级密码哈希
success = await upgrade_service.verify_and_upgrade_if_needed(
    user_id=123,
    password="user_password",
    current_hash="$2b$10$oldhashhere"
)
```

## 常见问题

### Q: 如何处理超长密码？

A: bcrypt 有 72 字节的限制，模块提供了两种处理方式：

```python
# 方式1：启用截断错误（推荐）
PWD_BCRYPT_TRUNCATE_ERROR=true
# 超过72字节的密码会抛出异常

# 方式2：自动截断（默认行为）
PWD_BCRYPT_TRUNCATE_ERROR=false
# 超过72字节的密码会被自动截断
```

### Q: 如何防止定时攻击？

A: 可以设置最小验证时间来防止定时攻击：

```python
# 设置最小验证时间为0.1秒
PWD_MIN_VERIFY_TIME=0.1
```

这会确保密码验证至少花费指定时间，防止攻击者通过响应时间推断密码信息。

### Q: 如何迁移现有的密码哈希？

A: 可以使用以下策略进行迁移：

```python
class PasswordMigrationService:
    """密码迁移服务"""
    
    def __init__(self):
        self.new_pwd_service = PasswordService()
    
    async def migrate_legacy_passwords(self):
        """迁移旧密码哈希"""
        # 获取所有使用旧哈希算法的用户
        users = await self.get_users_with_legacy_hashes()
        
        for user in users:
            try:
                # 验证旧密码哈希格式
                if self.is_legacy_hash(user["password_hash"]):
                    # 在用户下次登录时升级哈希
                    # 或者强制用户重置密码
                    await self.force_password_reset(user["user_id"])
            except Exception as e:
                print(f"迁移用户 {user['user_id']} 失败: {e}")
    
    def is_legacy_hash(self, password_hash):
        """检查是否为旧版哈希"""
        # 检查哈希前缀或其他特征
        return not password_hash.startswith("$2b$")
```

### Q: 如何选择合适的 bcrypt 轮数？

A: bcrypt 轮数的选择需要在安全性和性能之间平衡：

- **开发环境**: 10-12 轮（较快，便于测试）
- **生产环境**: 12-14 轮（推荐的安全级别）
- **高安全要求**: 14-16 轮（更安全但性能开销大）

建议根据服务器性能和用户体验进行调整，确保验证时间在 100-500ms 范围内。

## API 参考

### PasswordService 类方法

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `hash_password(password)` | 生成密码哈希 | `password` (str): 明文密码 | `str`: 密码哈希值 |
| `verify_password(password, hashed_password)` | 验证密码 | `password` (str): 明文密码<br>`hashed_password` (str): 密码哈希值 | `bool`: 验证结果 |

### PasswordConfig 类属性

| 属性 | 描述 | 默认值 |
|------|------|--------|
| `password_schemes` | 启用的密码哈希算法列表 | `["bcrypt"]` |
| `password_default_scheme` | 默认密码哈希算法 | `"bcrypt"` |
| `password_deprecated` | 是否自动弃用旧算法 | `"auto"` |
| `bcrypt_rounds` | bcrypt 计算轮数 | `12` |
| `bcrypt_ident` | bcrypt 版本标识 | `"2b"` |
| `bcrypt_salt_size` | bcrypt salt 长度 | `22` |
| `bcrypt_truncate_error` | 超长密码是否报错 | `True` |
| `min_verify_time` | 最小验证耗时（秒） | `None` |

## 版本历史

- v1.0.0: 初始版本，提供基本的密码哈希和验证功能
- v1.1.0: 添加 bcrypt 特定参数配置
- v1.2.0: 增加安全增强功能（防定时攻击）
- v1.3.0: 优化错误处理和配置管理