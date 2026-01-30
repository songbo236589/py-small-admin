# 后端开发问题

本文档解答 Py Small Admin 后端开发的常见问题。

## 目录

- [开发环境](#开发环境)
- [数据库](#数据库)
- [API 开发](#api-开发)
- [常见问题](#常见问题)

## 开发环境

### Q: 如何搭建后端开发环境？

**A**:

详细的 Python 环境配置步骤请参考：[Python环境配置完整指南](../../../server/docs/Python环境配置完整指南.md)

快速搭建步骤：

1. **克隆项目**
   ```bash
   git clone https://github.com/songbo236589/py-small-admin.git
   cd py-small-admin/server
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置数据库等信息
   ```

5. **初始化数据库**
   ```bash
   alembic upgrade head
   python commands/seed.py  # 可选：填充初始数据
   ```

6. **启动服务**
   ```bash
   python run.py
   ```

### Q: 后端项目结构是怎样的？

**A**:

```
server/
├── Modules/              # 业务模块
│   ├── admin/           # Admin 模块
│   │   ├── controllers/ # 控制器
│   │   ├── services/    # 服务层
│   │   ├── models/      # 数据模型
│   │   ├── validators/  # 请求验证
│   │   └── routes/      # 路由定义
│   ├── common/          # 公共模块
│   │   ├── libs/        # 工具库
│   │   └── middleware/  # 中间件
│   └── quant/           # Quant 模块
├── config/              # 配置文件
├── commands/            # 命令脚本
├── logs/                # 日志文件
└── run.py               # 入口文件
```

### Q: 如何添加新的 API 接口？

**A**:

1. **定义模型** (`Modules/admin/models/xxx_model.py`):
   ```python
   from sqlmodel import SQLModel, Field

   class XxxModel(SQLModel, table=True):
       __tablename__ = "fa_xxx_xxxs"

       id: int = Field(primary_key=True)
       name: str
   ```

2. **创建验证器** (`Modules/admin/validators/xxx_validator.py`):
   ```python
   from pydantic import BaseModel

   class XxxCreateRequest(BaseModel):
       name: str

   class XxxUpdateRequest(BaseModel):
       name: str
   ```

3. **创建服务** (`Modules/admin/services/xxx_service.py`):
   ```python
   class XxxService:
       async def get_list(self, page: int, size: int):
           pass

       async def create(self, data: dict):
           pass
   ```

4. **创建控制器** (`Modules/admin/controllers/v1/xxx_controller.py`):
   ```python
   class XxxController:
       async def index(self, page: int = 1, size: int = 10):
           return await self.xxx_service.get_list(page, size)
   ```

5. **定义路由** (`Modules/admin/routes/xxx.py`):
   ```python
   from fastapi import APIRouter

   router = APIRouter(prefix="/xxx", tags=["XXX"])

   controller = XxxController()

   @router.get("/index")
   async def get_xxx_list(page: int = 1, size: int = 10):
       return await controller.index(page, size)
   ```

6. **注册路由** (`Modules/main.py`):
   ```python
   from Modules.admin.routes.xxx import router as xxx_router

   app.include_router(xxx_router, prefix="/api/admin", dependencies=[Depends(get_db)])
   ```

## 数据库

### Q: 如何执行数据库迁移？

**A**:

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

### Q: 如何在 SQLModel 中定义关系？

**A**:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class GroupModel(SQLModel, table=True):
    __tablename__ = "fa_admin_groups"

    id: int = Field(primary_key=True)
    name: str

    # 一对多关系
    admins: List["AdminModel"] = Relationship(back_populates="group")

class AdminModel(SQLModel, table=True):
    __tablename__ = "fa_admin_admins"

    id: int = Field(primary_key=True)
    name: str
    group_id: int = Field(foreign_key="fa_admin_groups.id")

    # 多对一关系
    group: Optional[GroupModel] = Relationship(back_populates="admins")
```

### Q: 如何使用原生 SQL 查询？

**A**:

```python
from sqlalchemy import text

async def custom_query(db: AsyncSession):
    result = await db.execute(
        text("SELECT * FROM fa_admin_admins WHERE status = :status"),
        {"status": 1}
    )
    return result.fetchall()
```

### Q: 如何处理数据库事务？

**A**:

```python
async def create_with_transaction(db: AsyncSession, data: dict):
    async with db.begin():
        # 创建记录
        admin = AdminModel(**data)
        db.add(admin)

        # 其他操作
        # ...

        # 自动提交或回滚
```

## API 开发

### Q: 如何实现文件上传？

**A**:

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")

    # 保存文件
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"url": f"/uploads/{file.filename}"}
```

### Q: 如何实现分页？

**A**:

```python
async def get_list(
    db: AsyncSession,
    page: int = 1,
    size: int = 10
):
    query = select(AdminModel).where(AdminModel.status == 1)

    # 获取总数
    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar()

    # 获取分页数据
    result = await db.execute(
        query.offset((page - 1) * size).limit(size)
    )
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }
```

### Q: 如何使用中间件？

**A**:

```python
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 请求前处理
    logger.info(f"Request: {request.method} {request.url}")

    # 执行请求
    response = await call_next(request)

    # 响应后处理
    response.headers["X-Custom-Header"] = "value"
    return response
```

### Q: 如何实现权限验证？

**A**:

```python
from functools import wraps

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            # 获取当前用户
            user = await get_current_user(request)

            # 验证权限
            if permission not in user.permissions:
                raise HTTPException(status_code=403, detail="权限不足")

            return await func(*args, request=request, **kwargs)
        return wrapper
    return decorator

# 使用
@router.get("/admin")
@require_permission("admin:view")
async def get_admin_list():
    pass
```

### Q: 如何使用 Celery 异步任务？

**A**:

```python
# 定义任务
from Modules.common.libs.celery.celery_service import celery

@celery.task
def send_email_task(to: str, subject: str, content: str):
    # 发送邮件逻辑
    pass

# 调用任务
async def send_email(to: str, subject: str, content: str):
    send_email_task.delay(to, subject, content)
```

## 常见问题

### Q: 如何处理 CORS 跨域问题？

**A**:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # 生产环境指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q: 如何调试 API？

**A**:

1. **使用日志**：
   ```python
   from loguru import logger
   logger.info("Debug info", extra={"data": some_data})
   ```

2. **使用 Swagger UI**：访问 `/docs` 查看 API 文档和测试接口

3. **使用断点调试**：
   ```python
   import pdb; pdb.set_trace()  # 设置断点
   ```

### Q: 如何优化数据库查询性能？

**A**:

1. **添加索引**
2. **使用 select 指定字段**
3. **避免 N+1 查询**
4. **使用 join 预加载关联数据**
5. **使用缓存**

```python
# ✅ 正确：只查询需要的字段
result = await db.execute(
    select(AdminModel.id, AdminModel.name)
)

# ✅ 正确：使用 join 预加载
result = await db.execute(
    select(AdminModel)
    .join(GroupModel)
    .options(selectinload(AdminModel.group))
)
```

### Q: 如何实现 JWT 认证？

**A**:

```python
import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的令牌")
```

### Q: 如何处理异常？

**A**:

```python
from fastapi import HTTPException, status

# 业务异常
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="用户名已存在"
)

# 自定义异常处理
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"code": 400, "message": str(exc)}
    )
```

## 更多资源

- [API 文档](../../api/)
- [后端开发指南](../../guide/backend/)
- [代码规范](../best-practices/code-style.md)
