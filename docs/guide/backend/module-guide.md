# 模块开发规范

本文档介绍了如何开发新的业务模块。

## 模块结构

### 标准模块目录结构

```
Modules/
└── your_module/          # 你的模块名称
    ├── __init__.py       # 模块初始化
    ├── controllers/      # 控制器（请求处理）
    │   └── your_controller.py
    ├── models/           # 数据模型（SQLModel）
    │   └── your_model.py
    ├── routes/           # 路由定义
    │   └── main_router.py
    ├── services/         # 业务逻辑
    │   └── your_service.py
    ├── validators/       # 数据验证
    │   └── your_validator.py
    ├── migrations/       # 数据库迁移文件
    │   └── versions/
    ├── seeds/            # 初始数据填充
    │   └── seed_data.py
    ├── tasks/            # 异步任务定义
    │   └── your_task.py
    └── queues/           # Celery 任务队列
        └── your_queue.py
```

### 各层职责

#### 1. Models - 数据模型层

**职责**：定义数据表结构和字段

```python
from sqlmodel import SQLModel, Field
from Modules.common.models.base_model import BaseTableModel
from typing import Optional
from sqlalchemy import Column, String, DateTime

class YourModel(BaseTableModel, table=True):
    """你的模型说明"""
    
    __tablename__ = "fa_your_models"
    __table_comment__ = "你的表说明"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="名称")
    description: Optional[str] = Field(default=None, description="描述")
    status: int = Field(default=1, description="状态")
```

#### 2. Validators - 验证器层

**职责**：定义请求和响应的数据验证

```python
from pydantic import BaseModel, Field
from typing import Optional

class YourCreateValidator(BaseModel):
    """创建验证器"""
    name: str = Field(..., min_length=1, max_length=100, description="名称")
    description: Optional[str] = Field(None, description="描述")
    status: int = Field(1, description="状态")

class YourUpdateValidator(BaseModel):
    """更新验证器"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="名称")
    description: Optional[str] = Field(None, description="描述")
    status: Optional[int] = Field(None, description="状态")

class YourSearchValidator(BaseModel):
    """搜索验证器"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    status: Optional[int] = Field(None, description="状态")
```

#### 3. Services - 服务层

**职责**：业务逻辑处理、数据库操作

```python
from sqlmodel import Session, select
from Modules.common.libs.database.sql import get_session
from Modules.your_module.models.your_model import YourModel

class YourService:
    """你的服务类"""
    
    @staticmethod
    async def create(data: YourCreateValidator):
        """创建记录"""
        with Session(get_session()) as session:
            model = YourModel(**data.dict())
            session.add(model)
            session.commit()
            session.refresh(model)
            return model
    
    @staticmethod
    async def update(id: int, data: YourUpdateValidator):
        """更新记录"""
        with Session(get_session()) as session:
            model = session.get(YourModel, id)
            if not model:
                return None
            for key, value in data.dict(exclude_unset=True).items():
                setattr(model, key, value)
            session.commit()
            session.refresh(model)
            return model
    
    @staticmethod
    async def delete(id: int):
        """删除记录"""
        with Session(get_session()) as session:
            model = session.get(YourModel, id)
            if not model:
                return False
            session.delete(model)
            session.commit()
            return True
    
    @staticmethod
    async def get_list(page: int = 1, size: int = 10, keyword: str = None, status: int = None):
        """获取列表"""
        with Session(get_session()) as session:
            statement = select(YourModel)
            
            # 搜索条件
            if keyword:
                statement = statement.where(YourModel.name.like(f"%{keyword}%"))
            
            if status is not None:
                statement = statement.where(YourModel.status == status)
            
            # 软删除过滤
            statement = statement.where(YourModel.deleted_at.is_(None))
            
            # 排序
            statement = statement.order_by(YourModel.created_at.desc())
            
            # 分页
            total = len(session.exec(statement).all())
            offset = (page - 1) * size
            statement = statement.offset(offset).limit(size)
            items = session.exec(statement).all()
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "size": size
            }
    
    @staticmethod
    async def get_by_id(id: int):
        """根据 ID 获取"""
        with Session(get_session()) as session:
            return session.get(YourModel, id)
```

#### 4. Controllers - 控制器层

**职责**：处理 HTTP 请求、调用服务层

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from Modules.your_module.services.your_service import YourService
from Modules.your_module.validators.your_validator import (
    YourCreateValidator,
    YourUpdateValidator,
    YourSearchValidator
)

router = APIRouter(prefix="/your-module", tags=["你的模块"])

@router.get("/index")
async def index(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词"),
    status: int = Query(None, description="状态")
):
    """获取列表"""
    result = await YourService.get_list(page, size, keyword, status)
    return {"code": 200, "message": "success", "data": result}

@router.post("/add")
async def add(data: YourCreateValidator):
    """添加"""
    result = await YourService.create(data)
    return {"code": 200, "message": "添加成功", "data": result}

@router.get("/edit/{id}")
async def edit(id: int):
    """获取编辑数据"""
    result = await YourService.get_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"code": 200, "message": "success", "data": result}

@router.put("/update/{id}")
async def update(id: int, data: YourUpdateValidator):
    """更新"""
    result = await YourService.update(id, data)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"code": 200, "message": "更新成功", "data": result}

@router.delete("/destroy/{id}")
async def destroy(id: int):
    """删除"""
    result = await YourService.delete(id)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"code": 200, "message": "删除成功"}

@router.delete("/destroy_all")
async def destroy_all(ids: list[int]):
    """批量删除"""
    for id in ids:
        await YourService.delete(id)
    return {"code": 200, "message": "批量删除成功"}
```

#### 5. Routes - 路由层

**职责**：组织路由、挂载到主应用

```python
from fastapi import APIRouter
from Modules.your_module.controllers.your_controller import router as your_router

main_router = APIRouter(prefix="/your-module", tags=["你的模块"])
main_router.include_router(your_router)
```

#### 6. Tasks - 异步任务层

**职责**：定义 Celery 异步任务

```python
from Modules.common.libs.celery.celery_service import celery

@celery.task(name="Modules.your_module.tasks.your_task.your_task")
def your_task(param1: str, param2: int):
    """你的异步任务"""
    # 任务逻辑
    print(f"Task executed with params: {param1}, {param2}")
    return {"status": "success", "result": "done"}
```

#### 7. Queues - 任务队列层

**职责**：定义 Celery 任务队列

```python
from Modules.common.libs.celery.celery_service import celery
from celery import Celery

@celery.task(name="Modules.your_module.queues.your_queue.your_queue_task")
def your_queue_task(param: str):
    """你的队列任务"""
    # 任务逻辑
    return {"status": "success"}
```

## 快速创建模块

### 使用命令行工具

项目提供了快速创建模块的命令行工具：

```bash
python commands/create_module.py your_module
```

这将自动创建完整的模块目录结构和基础文件。

### 手动创建

如果需要手动创建，按照以下步骤：

#### 1. 创建目录结构

```bash
mkdir -p Modules/your_module/{controllers,models,routes,services,validators,migrations,seeds,tasks,queues}
```

#### 2. 创建初始化文件

```python
# Modules/your_module/__init__.py
"""你的模块"""
```

#### 3. 创建模型

参考上面的 Models 示例。

#### 4. 创建验证器

参考上面的 Validators 示例。

#### 5. 创建服务

参考上面的 Services 示例。

#### 6. 创建控制器

参考上面的 Controllers 示例。

#### 7. 创建路由

参考上面的 Routes 示例。

#### 8. 注册路由

在 `Modules/main.py` 中注册路由：

```python
from Modules.your_module.routes.main_router import main_router as your_router

app.include_router(your_router, prefix=Config.get("app.api_prefix", ""))
```

#### 9. 创建迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "Add your_module"

# 执行迁移
alembic upgrade head
```

#### 10. 测试接口

访问 http://localhost:8000/docs 测试新接口。

## 开发规范

### 命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 模块名 | snake_case | `your_module` |
| 模型名 | PascalCase | `YourModel` |
| 验证器名 | PascalCase + Validator | `YourCreateValidator` |
| 服务类名 | PascalCase + Service | `YourService` |
| 控制器函数名 | snake_case | `get_list` |
| 任务名 | snake_case + _task | `your_task` |

### 代码规范

#### 1. 导入顺序

```python
# 标准库
from datetime import datetime
from typing import Optional

# 第三方库
from fastapi import APIRouter, Depends
from pydantic import Field
from sqlmodel import Session, select

# 本地模块
from Modules.common.libs.database.sql import get_session
from Modules.your_module.models.your_model import YourModel
```

#### 2. 类型注解

所有函数都应该添加类型注解：

```python
async def get_list(page: int = 1, size: int = 10) -> dict:
    """获取列表"""
    pass
```

#### 3. 文档字符串

所有类和函数都应该添加文档字符串：

```python
class YourService:
    """你的服务类"""
    
    @staticmethod
    async def create(data: YourCreateValidator):
        """创建记录
        
        Args:
            data: 创建数据
            
        Returns:
            创建的模型实例
        """
        pass
```

#### 4. 异常处理

使用 HTTPException 返回错误：

```python
from fastapi import HTTPException

if not model:
    raise HTTPException(status_code=404, detail="记录不存在")
```

#### 5. 数据验证

使用 Pydantic 进行数据验证：

```python
from pydantic import BaseModel, Field, validator

class YourCreateValidator(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="名称")
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('名称不能为空')
        return v
```

## 最佳实践

### 1. 使用依赖注入

```python
from fastapi import Depends
from Modules.common.libs.database.sql import get_session

@router.get("/index")
async def index(session: Session = Depends(get_session)):
    """使用依赖注入获取数据库会话"""
    pass
```

### 2. 使用缓存

```python
from Modules.common.libs.cache.cache import cache

@cache(key_prefix="your_model", ttl=3600)
async def get_by_id(id: int):
    """使用缓存"""
    pass
```

### 3. 使用事务

```python
with Session(get_session()) as session:
    try:
        # 数据库操作
        session.commit()
    except Exception as e:
        session.rollback()
        raise
```

### 4. 使用异步任务

```python
from Modules.your_module.tasks.your_task import your_task

@router.post("/async-task")
async def async_task():
    """触发异步任务"""
    result = your_task.delay("param1", 123)
    return {"code": 200, "message": "任务已提交", "task_id": result.id}
```

## 测试

### 单元测试

```python
import pytest
from Modules.your_module.services.your_service import YourService
from Modules.your_module.validators.your_validator import YourCreateValidator

@pytest.mark.asyncio
async def test_create():
    """测试创建"""
    data = YourCreateValidator(name="测试", description="测试描述")
    result = await YourService.create(data)
    assert result.name == "测试"
```

### 集成测试

```python
from fastapi.testclient import TestClient
from Modules.main import app

client = TestClient(app)

def test_index():
    """测试列表接口"""
    response = client.get("/api/your-module/index")
    assert response.status_code == 200
    assert response.json()["code"] == 200
```

## 常见问题

### 1. 如何添加软删除？

在模型中添加 `deleted_at` 字段：

```python
deleted_at: Optional[datetime] = Field(default=None, description="软删除时间")
```

查询时过滤已删除的记录：

```python
statement = statement.where(YourModel.deleted_at.is_(None))
```

### 2. 如何添加分页？

使用 offset 和 limit：

```python
offset = (page - 1) * size
statement = statement.offset(offset).limit(size)
```

### 3. 如何添加搜索？

使用 like 查询：

```python
if keyword:
    statement = statement.where(YourModel.name.like(f"%{keyword}%"))
```