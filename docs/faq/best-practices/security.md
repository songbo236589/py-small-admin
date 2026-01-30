# 安全最佳实践

本文档介绍了 Py Small Admin 的安全最佳实践，帮助您构建安全的后台管理系统。

## 目录

- [认证安全](#认证安全)
- [数据安全](#数据安全)
- [网络安全](#网络安全)
- [配置安全](#配置安全)
- [代码安全](#代码安全)
- [部署安全](#部署安全)

## 认证安全

### JWT 令牌安全

#### 1. 使用强密钥

JWT 密钥必须足够强，建议使用至少 32 字符的随机字符串：

```bash
# 生成强密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

```env
# .env
JWT_SECRET_KEY=your-generated-strong-key-here-at-least-32-characters
```

**安全等级**：
- ⚠️ 弱：少于 16 字符
- ⚠️ 中等：16-31 字符
- ✅ 强：32 字符及以上

#### 2. 设置合理的过期时间

| 令牌类型 | 推荐过期时间 | 说明 |
|---------|-------------|------|
| 访问令牌 (Access Token) | 15-30 分钟 | 短期有效，减少泄露风险 |
| 刷新令牌 (Refresh Token) | 7-14 天 | 较长期有效，便于用户使用 |

```env
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### 3. 启用令牌黑名单

在用户登出时将令牌加入黑名单：

```env
JWT_ENABLE_BLACKLIST=true
JWT_BLACKLIST_PREFIX=jwt:blacklist:admin:
```

#### 4. 验证令牌声明

服务端必须验证以下 JWT 声明：

- **iss (Issuer)**：令牌签发者
- **aud (Audience)**：令牌受众
- **exp (Expiration)**：过期时间
- **nbf (Not Before)**：生效时间
- **iat (Issued At)**：签发时间

### 密码安全

#### 1. 密码哈希

使用 bcrypt 算法哈希密码，工作因子至少为 12：

```python
# server/config/app.py
import bcrypt

def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
```

#### 2. 密码复杂度要求

要求用户密码满足以下条件：

- 最小长度：8 个字符
- 包含大小写字母
- 包含数字
- 包含特殊字符

```python
import re

def validate_password(password: str) -> bool:
    """验证密码复杂度"""
    if len(password) < 8:
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

#### 3. 防止弱密码

禁止常见弱密码：

```python
WEAK_PASSWORDS = [
    'password', '123456', '12345678', 'abc123',
    'qwerty', 'admin', 'welcome', 'monkey'
]
```

#### 4. 定期更换密码

建议用户每 90 天更换一次密码。

#### 5. 重置密码安全

- 新密码通过邮件发送
- 邮件链接有效期：24 小时
- 使用后立即失效
- 强制用户首次登录修改密码

### 多因素认证 (MFA)

建议启用多因素认证：

1. **基于时间的一次性密码 (TOTP)**
   - 使用 Google Authenticator
   - 使用 Authy
   - 使用 Microsoft Authenticator

2. **短信验证码**
   - 发送到注册手机号
   - 有效期：5 分钟
   - 每天限制发送次数

3. **邮箱验证码**
   - 发送到注册邮箱
   - 有效期：15 分钟
   - 每天限制发送次数

## 数据安全

### 数据库安全

#### 1. 使用最小权限原则

为数据库用户分配最小必要权限：

```sql
-- 创建专用数据库用户
CREATE USER 'py_admin'@'localhost' IDENTIFIED BY 'strong_password';

-- 只授予必要权限
GRANT SELECT, INSERT, UPDATE, DELETE ON py_small_admin.* TO 'py_admin'@'localhost';
FLUSH PRIVILEGES;
```

**禁止**：
- ❌ 不要使用 root 用户连接数据库
- ❌ 不要授予 DROP、ALTER、CREATE 权限给应用用户
- ❌ 不要授予 FILE 权限（防止读取文件）

#### 2. SQL 注入防护

使用参数化查询，永远不要拼接 SQL：

```python
# ✅ 正确：使用参数化查询
from sqlalchemy import text

session.execute(
    text("SELECT * FROM admins WHERE username = :username"),
    {"username": username}
)

# ❌ 错误：SQL 注入风险
session.execute(f"SELECT * FROM admins WHERE username = '{username}'")
```

#### 3. 敏感数据加密

对敏感数据进行加密存储：

```python
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """加密敏感数据"""
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted: str, key: bytes) -> str:
    """解密敏感数据"""
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()
```

**需要加密的数据**：
- 手机号
- 身份证号
- 银行卡号
- 地址信息

#### 4. 数据备份安全

- 定期备份数据库
- 备份文件加密存储
- 备份文件异地存储
- 定期测试备份恢复

```bash
#!/bin/bash
# 备份脚本示例
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
ENCRYPTION_KEY="your-encryption-key"

# 备份数据库
mysqldump -u py_admin -p'password' py_small_admin | \
  openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:$ENCRYPTION_KEY \
  > $BACKUP_DIR/backup_$DATE.sql.enc

# 保留最近 7 天的备份
find $BACKUP_DIR -name "backup_*.sql.enc" -mtime +7 -delete
```

#### 5. 数据脱敏

在日志和错误信息中脱敏敏感数据：

```python
def mask_phone(phone: str) -> str:
    """手机号脱敏"""
    return phone[:3] + '****' + phone[-4:]

def mask_email(email: str) -> str:
    """邮箱脱敏"""
    username, domain = email.split('@')
    return username[:2] + '***@' + domain

def mask_id_card(id_card: str) -> str:
    """身份证脱敏"""
    return id_card[:6] + '********' + id_card[-4:]
```

### 文件上传安全

#### 1. 文件类型验证

只允许上传安全的文件类型：

```python
ALLOWED_EXTENSIONS = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.webp'},
    'document': {'.pdf', '.doc', '.docx', '.xls', '.xlsx'},
    'video': {'.mp4', '.avi', '.mov'}
}

def is_allowed_file(filename: str, category: str) -> bool:
    """检查文件扩展名"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(category, set())
```

#### 2. 文件大小限制

限制上传文件大小：

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_file_size(file_size: int) -> bool:
    """验证文件大小"""
    return file_size <= MAX_FILE_SIZE
```

#### 3. 文件内容验证

验证文件真实类型，防止伪造扩展名：

```python
import magic

def get_real_file_type(file_path: str) -> str:
    """获取真实文件类型"""
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)
```

#### 4. 文件名安全处理

重命名上传文件，防止路径遍历攻击：

```python
import uuid
from datetime import datetime

def generate_safe_filename(original_filename: str) -> str:
    """生成安全的文件名"""
    ext = os.path.splitext(original_filename)[1]
    date_path = datetime.now().strftime('%Y/%m/%d')
    random_name = str(uuid.uuid4())
    return f"{date_path}/{random_name}{ext}"
```

#### 5. 病毒扫描

对上传文件进行病毒扫描：

```python
import pyclamd

def scan_file(file_path: str) -> bool:
    """扫描文件病毒"""
    cd = pyclamd.ClamdUnixSocket()
    if cd.ping():
        result = cd.scan_file(file_path)
        return result is None or result[file_path][0] == 'OK'
    return False
```

## 网络安全

### HTTPS 配置

#### 1. 强制使用 HTTPS

生产环境必须使用 HTTPS：

```nginx
# nginx 配置
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
}
```

#### 2. 使用强加密套件

配置安全的 SSL/TLS 加密套件：

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers on;
```

#### 3. 启用 HSTS

启用 HTTP 严格传输安全：

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### CORS 配置

正确配置跨域资源共享：

```python
# server/config/cors.py
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://your-domain.com",
    "https://www.your-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Type"],
)
```

**安全建议**：
- ❌ 不要使用 `allow_origins=["*"]`
- ✅ 明确指定允许的源
- ✅ 生产环境启用 allow_credentials
- ✅ 限制允许的 HTTP 方法

### 请求限流

防止 DDoS 攻击和暴力破解：

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/admin/common/login")
@limiter.limit("5/minute")  # 每分钟最多 5 次
async def login():
    pass
```

### 请求验证

#### 1. 验证请求来源

验证 Referer 和 Origin 头：

```python
from fastapi import Request, HTTPException

ALLOWED_ORIGINS = ["https://your-domain.com"]

async def check_request_origin(request: Request):
    """检查请求来源"""
    origin = request.headers.get("Origin")
    referer = request.headers.get("Referer")

    if origin and origin not in ALLOWED_ORIGINS:
        raise HTTPException(status_code=403, detail="Invalid origin")
```

#### 2. CSRF 保护

启用 CSRF 保护：

```python
from fastapi_csrf_protect import CsrfProtect

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfConfig(secret_key="your-secret-key")
```

## 配置安全

### 环境变量管理

#### 1. 使用 .env 文件

敏感配置存储在 `.env` 文件中：

```env
# .env (不要提交到版本控制)
DB_PASSWORD=your-db-password
JWT_SECRET_KEY=your-jwt-secret
API_KEY=your-api-key
```

#### 2. .gitignore 配置

确保敏感文件不被提交：

```gitignore
# .gitignore
.env
.env.local
.env.production
*.key
*.pem
credentials.json
```

#### 3. 提供 .env.example

提供环境变量示例：

```env
# .env.example
DB_PASSWORD=your-db-password-here
JWT_SECRET_KEY=your-jwt-secret-here
API_KEY=your-api-key-here
```

### 调试配置

生产环境必须关闭调试模式：

```env
# 生产环境
APP_DEBUG=False
APP_ENV=production
```

**调试模式的风险**：
- 暴露详细错误信息
- 暴露配置信息
- 暴露SQL查询语句
- 可能执行任意代码

### 日志安全

#### 1. 日志脱敏

日志中不要记录敏感信息：

```python
import logging

class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器"""

    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?[^"\',\s}]+', 'password=***'),
        (r'token["\']?\s*[:=]\s*["\']?[^"\',\s}]+', 'token=***'),
        (r'"\d{11}"', '"***"'),  # 手机号
    ]

    def filter(self, record):
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            record.msg = re.sub(pattern, replacement, str(record.msg))
        return True

logging.getLogger().addFilter(SensitiveDataFilter())
```

#### 2. 日志访问控制

确保日志文件只有授权用户可访问：

```bash
chmod 600 /var/log/py-small-admin/*.log
chown app-user:app-group /var/log/py-small-admin/*.log
```

#### 3. 日志轮转

配置日志轮转，防止日志文件过大：

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=10
)
```

## 代码安全

### 输入验证

#### 1. 验证所有输入

使用 Pydantic 验证所有输入数据：

```python
from pydantic import BaseModel, Field, validator

class AdminCreateRequest(BaseModel):
    """管理员创建请求"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v
```

#### 2. 防止 XSS 攻击

对用户输入进行转义：

```python
import html

def escape_user_input(text: str) -> str:
    """转义用户输入"""
    return html.escape(text, quote=True)
```

#### 3. 防止命令注入

永远不要使用用户输入构建命令：

```python
# ❌ 错误：命令注入风险
os.system(f"ping {user_input}")

# ✅ 正确：使用 subprocess
import subprocess
subprocess.run(['ping', user_input], check=True)
```

### 权限控制

#### 1. 基于角色的访问控制 (RBAC)

实现 RBAC 权限系统：

```python
from functools import wraps

def require_permission(permission: str):
    """权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request, **kwargs):
            user = await get_current_user(request)
            if not user.has_permission(permission):
                raise HTTPException(status_code=403, detail="权限不足")
            return await func(*args, request=request, **kwargs)
        return wrapper
    return decorator
```

#### 2. 最小权限原则

用户只拥有完成工作所需的最小权限。

#### 3. 定期审计权限

定期检查用户权限，移除不必要的权限。

### 安全审计

#### 1. 记录安全事件

记录重要安全事件：

```python
async def log_security_event(
    event_type: str,
    user_id: int,
    details: dict,
    ip: str
):
    """记录安全事件"""
    await SecurityLog.create(
        event_type=event_type,
        user_id=user_id,
        details=details,
        ip=ip,
        created_at=datetime.now()
    )
```

**需要记录的事件**：
- 登录成功/失败
- 登出
- 密码修改
- 权限变更
- 敏感操作

#### 2. 异常检测

检测异常行为：

- 多次登录失败
- 异常时间登录
- 异常地点登录
- 大量数据导出

## 部署安全

### 服务器安全

#### 1. 系统更新

定期更新系统和软件包：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 2. 关闭不必要的服务

关闭不必要的服务和端口：

```bash
# 查看开放端口
sudo netstat -tulpn

# 关闭不必要的服务
sudo systemctl stop unnecessary-service
sudo systemctl disable unnecessary-service
```

#### 3. 配置防火墙

使用 UFW 配置防火墙：

```bash
# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
```

#### 4. 禁用 root 登录

禁用 SSH root 登录：

```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
```

### 应用部署

#### 1. 使用非特权用户

使用非特权用户运行应用：

```ini
# /etc/systemd/system/py-small-admin.service
[Service]
User=app-user
Group=app-group
```

#### 2. 文件权限

设置正确的文件权限：

```bash
# 应用目录
sudo chown -R app-user:app-group /opt/py-small-admin
sudo chmod -R 750 /opt/py-small-admin

# 配置文件
sudo chmod 600 /opt/py-small-admin/server/.env
```

#### 3. 依赖更新

定期更新依赖包：

```bash
# 检查过期依赖
pip list --outdated

# 更新依赖
pip install --upgrade package-name
```

#### 4. 安全扫描

使用安全工具扫描漏洞：

```bash
# Python 依赖扫描
pip install safety
safety check

# 依赖漏洞扫描
pip install pip-audit
pip-audit
```

### 监控和告警

#### 1. 安全监控

监控以下指标：

- 异常登录
- 高失败率
- 异常流量
- CPU/内存使用率

#### 2. 告警配置

配置安全告警：

- 登录失败超过 5 次
- API 错误率超过 10%
- 服务器负载过高
- 磁盘空间不足

## 安全检查清单

### 上线前检查

- [ ] 修改所有默认密码
- [ ] 生成强 JWT 密钥
- [ ] 配置 HTTPS
- [ ] 关闭调试模式
- [ ] 配置 CORS
- [ ] 设置文件上传限制
- [ ] 配置请求限流
- [ ] 启用日志记录
- [ ] 配置备份策略
- [ ] 测试恢复流程

### 定期检查

- [ ] 更新系统和依赖包
- [ ] 检查安全公告
- [ ] 审查访问日志
- [ ] 测试备份恢复
- [ ] 审查用户权限
- [ ] 安全漏洞扫描

## 安全资源

### 学习资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Security Best Practices](https://safety.google/security/)

### 安全工具

- **依赖扫描**：Safety, Pip-audit
- **代码分析**：Bandit, Semgrep
- **渗透测试**：OWASP ZAP, Burp Suite
- **日志分析**：ELK Stack, Splunk
- **监控告警**：Prometheus, Grafana
