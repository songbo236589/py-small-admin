# API 开发规范

本文档介绍了 API 开发的规范和最佳实践。

## RESTful 设计

### 资源命名

使用名词复数表示资源：

```http
GET    /api/admin/admins           # 获取管理员列表
POST   /api/admin/admins           # 添加管理员
GET    /api/admin/admins/1         # 获取单个管理员
PUT    /api/admin/admins/1         # 更新管理员
DELETE /api/admin/admins/1         # 删除管理员
```

### HTTP 方法

| 方法 | 用途 | 幂等性 |
|------|------|--------|
| GET | 获取资源 | 是 |
| POST | 创建资源 | 否 |
| PUT | 完整更新资源 | 是 |
| PATCH | 部分更新资源 | 否 |
| DELETE | 删除资源 | 是 |

### 状态码

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | GET、PUT、DELETE |
| 201 | 已创建 | POST |
| 204 | 无内容 | DELETE |
| 400 | 请求错误 | 参数验证失败 |
| 401 | 未认证 | Token 无效或过期 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 未找到 | 资源不存在 |
| 500 | 服务器错误 | 服务器异常 |

## 请求格式

### 请求头

```http
Content-Type: application/json
Authorization: Bearer <access_token>
X-API-Key: <api_key>
```

### 请求体

```json
{
  "name": "管理员姓名",
  "username": "admin",
  "password": "123456"
}
```

### 分页参数

```http
GET /api/admin/admins?page=1&size=10&keyword=admin&status=1
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页数量，默认 10 |
| keyword | str | 否 | 搜索关键词 |
| status | int | 否 | 状态 |

### 排序参数

```http
GET /api/admin/admins?sort_field=created_at&sort_order=desc
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sort_field | str | 否 | 排序字段 |
| sort_order | str | 否 | 排序方向，asc/desc，默认 desc |

## 响应格式

### 成功响应

#### 单个资源

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "管理员",
    "username": "admin"
  }
}
```

#### 资源列表

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "管理员1",
        "username": "admin1"
      },
      {
        "id": 2,
        "name": "管理员2",
        "username": "admin2"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

#### 分页响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 资源列表 |
| total | number | 总数 |
| page | number | 当前页码 |
| size | number | 每页数量 |
| pages | number | 总页数（可选） |

### 错误响应

```json
{
  "code": 400,
  "message": "参数验证失败",
  "data": {
    "errors": [
      {
        "field": "username",
        "message": "用户名不能为空"
      },
      {
        "field": "password",
        "message": "密码长度至少 6 位"
      }
    ]
  }
}
```

### 4xx 错误响应

| 字段 | 类型 | 说明 |
|------|------|------|
| code | number | 错误码 |
| message | string | 错误信息 |
| data | object/null | 错误详情 |

## 路由设计

### 路由层级

```python
from fastapi import APIRouter

# 主路由
router = APIRouter(prefix="/admin", tags=["Admin"])

# 子路由
admin_router = APIRouter(prefix="/admin", tags=["管理员"])
group_router = APIRouter(prefix="/group", tags=["角色组"])
rule_router = APIRouter(prefix="/rule", tags=["菜单规则"])

# 挂载路由
router.include_router(admin_router)
router.include_router(group_router)
router.include_router(rule_router)
```

### 路由命名

使用清晰、描述性的路由名称：

```python
# 好的命名
@router.get("/admin/index")
async def get_admin_list():
    """获取管理员列表"""
    pass

@router.post("/admin/add")
async def create_admin():
    """添加管理员"""
    pass

# 不好的命名
@router.get("/list")
async def list():
    """列表"""
    pass

@router.get("/add")
async def add():
    """添加"""
    pass
```

## 数据验证

### 使用 Pydantic 验证

```python
from pydantic import BaseModel, Field, validator

class AdminCreateValidator(BaseModel):
    """管理员创建验证器"""
    
    name: str = Field(..., min_length=1, max_length=50, description="管理员姓名")
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    group_id: Optional[int] = Field(None, description="角色组 ID")
    
    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        """用户名必须是字母和数字"""
        if not v.isalnum():
            raise ValueError('用户名只能是字母和数字')
        return v
    
    @validator('password')
    def password_must_be_strong(cls, v):
        """密码必须足够复杂"""
        if len(v) < 6:
            raise ValueError('密码长度至少 6 位')
        return v
```

### 使用 FastAPI 依赖注入

```python
from fastapi import Depends, Query

async def get_admin_by_id(id: int):
    """根据 ID 获取管理员"""
    admin = await AdminService.get_by_id(id)
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")
    return admin

@router.get("/admin/edit/{id}")
async def edit_admin(id: int, admin: dict = Depends(get_admin_by_id)):
    """获取管理员编辑数据"""
    return {"code": 200, "data": admin}
```

## 错误处理

### 使用 HTTPException

```python
from fastapi import HTTPException

@router.post("/admin/add")
async def create_admin(data: AdminCreateValidator):
    # 验证用户名是否已存在
    existing_admin = await AdminService.get_by_username(data.username)
    if existing_admin:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建管理员
    admin = await AdminService.create(data)
    return {"code": 200, "data": admin}
```

### 自定义异常

```python
class BusinessException(Exception):
    """业务异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)

# 使用
@router.post("/admin/add")
async def create_admin(data: AdminCreateValidator):
    if not data.username:
        raise BusinessException("用户名不能为空")
    pass
```

## 认证授权

### JWT 认证

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前登录的管理员"""
    token = credentials.credentials
    payload = decode_jwt(token)
    admin_id = payload.get("sub")
    
    admin = await AdminService.get_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")
    
    if admin.status == 0:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    return admin

@router.get("/admin/index")
async def get_admin_list(admin: dict = Depends(get_current_admin)):
    """获取管理员列表（需要认证）"""
    pass
```

### API Key 认证

```python
from fastapi import Depends, Header

async def verify_api_key(x_api_key: str = Header(...)):
    """验证 API Key"""
    if x_api_key != Config.get("app.admin_x_api_key"):
        raise HTTPException(status_code=403, detail="API Key 无效")
    return x_api_key

@router.get("/admin/index")
async def get_admin_list(api_key: str = Depends(verify_api_key)):
    """获取管理员列表（需要 API Key）"""
    pass
```

## 日志记录

### 使用 Loguru

```python
from loguru import logger

@router.post("/admin/add")
async def create_admin(data: AdminCreateValidator):
    """添加管理员"""
    logger.info(f"开始添加管理员: {data.username}")
    
    try:
        admin = await AdminService.create(data)
        logger.success(f"管理员添加成功: {admin.id}")
        return {"code": 200, "data": admin}
    except Exception as e:
        logger.error(f"添加管理员失败: {e}")
        raise
```

## 性能优化

### 使用缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_config(key: str) -> str:
    """获取配置（缓存）"""
    return db.query(Config).filter_by(key=key).first()
```

### 使用异步

```python
@router.get("/admin/index")
async def get_admin_list(page: int = 1, size: int = 10):
    """获取管理员列表（异步）"""
    result = await AdminService.get_list(page, size)
    return {"code": 200, "data": result}
```

### 数据库查询优化

```python
# 使用 select_related 减少查询次数
statement = select(Admin).options(select_related(Admin.group))

# 使用 only 只查询需要的字段
statement = select(Admin).only(Admin.id, Admin.name, Admin.username)

# 使用 limit 限制查询数量
statement = select(Admin).limit(100)
```

## 测试

### 编写测试

```python
import pytest
from fastapi.testclient import TestClient
from Modules.main import app

client = TestClient(app)

def test_get_admin_list():
    """测试获取管理员列表"""
    response = client.get("/api/admin/admin/index")
    assert response.status_code == 200
    assert response.json()["code"] == 200
    assert "items" in response.json()["data"]

def test_create_admin():
    """测试创建管理员"""
    data = {
        "name": "测试管理员",
        "username": "test_admin",
        "password": "123456"
    }
    response = client.post("/api/admin/admin/add", json=data)
    assert response.status_code == 200
    assert response.json()["code"] == 200
    assert response.json()["data"]["username"] == "test_admin"
```

## 文档

### 使用 Docstring

```python
@router.get("/admin/index")
async def get_admin_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词"),
    status: int = Query(None, description="状态")
):
    """
    获取管理员列表
    
    Args:
        page: 页码
        size: 每页数量
        keyword: 搜索关键词
        status: 状态
    
    Returns:
        管理员列表
    """
    result = await AdminService.get_list(page, size, keyword, status)
    return {"code": 200, "data": result}
```

## 最佳实践

### 1. 统一响应格式

使用统一的响应格式：

```python
def success(data: Any = None, message: str = "success", code: int = 200):
    """成功响应"""
    return {"code": code, "message": message, "data": data}

def error(message: str, code: int = 400, data: Any = None):
    """错误响应"""
    return {"code": code, "message": message, "data": data}
```

### 2. 使用枚举

使用枚举定义常量：

```python
from enum import IntEnum

class AdminStatus(IntEnum):
    """管理员状态"""
    DISABLED = 0
    ENABLED = 1
```

### 3. 使用类型注解

所有函数都应该添加类型注解：

```python
async def get_admin_list(page: int = 1, size: int = 10) -> dict:
    """获取管理员列表"""
    pass
```

### 4. 使用依赖注入

使用依赖注入提高代码复用性：

```python
@router.get("/admin/index")
async def get_admin_list(db: Session = Depends(get_session)):
    """获取管理员列表"""
    pass
```