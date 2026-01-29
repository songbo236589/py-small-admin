# 模型开发指南

本文档详细介绍如何开发模型层。

## 概述

模型层负责定义数据模型和数据库表结构，使用 SQLModel 实现。

## 模型结构

### 基本结构

```python
from sqlmodel import Field
from Modules.common.models.base_model import BaseTableModel

class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""
    __table_comment__ = "管理员表"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(default="", index=True)
    password: str = Field(default="")
    status: int = Field(default=1)
```

### 继承 BaseTableModel

继承 BaseTableModel 获得基础功能：

```python
from Modules.common.models.base_model import BaseTableModel

class Article(BaseTableModel, table=True):
    """文章模型"""
    # 自动获得：
    # - id 主键
    # - created_at 创建时间
    # - updated_at 更新时间
    # - 自动表名生成
    # - 表前缀支持
    pass
```

## 字段定义

### 基本字段

```python
from sqlmodel import Field
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.mysql import INTEGER

class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    # 整数字段
    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 字符串字段
    username: str | None = Field(
        sa_column=Column(
            String(50),
            nullable=False,
            server_default="",
            comment="用户名",
        ),
        default="",
    )

    # 日期时间字段
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(),
            nullable=False,
            comment="创建时间",
            index=True,
        ),
        default=None,
    )
```

### 字段选项

#### primary_key

主键字段：

```python
id: int | None = Field(default=None, primary_key=True)
```

#### index

索引字段：

```python
username: str = Field(default="", index=True)
```

#### unique

唯一字段：

```python
username: str = Field(default="", unique=True)
```

#### default

默认值：

```python
status: int = Field(default=1)
```

#### nullable

可为空：

```python
phone: str | None = Field(default=None, nullable=True)
```

#### comment

字段注释：

```python
username: str = Field(
    sa_column=Column(String(50), comment="用户名")
)
```

## 关系定义

### 一对多关系

```python
from sqlmodel import Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .admin_upload import AdminUpload

class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    # 一对多：管理员 → 上传文件
    uploads: list["AdminUpload"] = Relationship(back_populates="admin")
```

### 多对一关系

```python
from sqlmodel import Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .admin_group import AdminGroup

class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    # 多对一：管理员 → 角色
    group_id: int | None = Field(default=None, foreign_key="admin_groups.id")
    group: Mapped[Optional["AdminGroup"]] = Relationship(back_populates="admins")
```

### 多对多关系

```python
class Article(BaseTableModel, table=True):
    """文章模型"""

    # 多对多：文章 → 标签
    tags: list["Tag"] = Relationship(
        back_populates="articles",
        link_model=ArticleTag  # 中间表
    )
```

## 表配置

### 表注释

```python
class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""
    __table_comment__ = "管理员表"
```

### 表参数

```python
from sqlalchemy import Index

class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_status", "status"),
    )
```

## 最佳实践

### 1. 使用类型提示

使用类型提示提高代码可读性：

```python
# ✅ 正确
username: str | None = Field(default=None)
created_at: datetime | None = Field(default=None)

# ❌ 错误
username = Field(default=None)
created_at = Field(default=None)
```

### 2. 添加字段注释

为所有字段添加注释：

```python
# ✅ 正确
username: str = Field(
    sa_column=Column(String(50), comment="用户名")
)

# ❌ 错误
username: str = Field(sa_column=Column(String(50)))
```

### 3. 使用索引

为常用查询字段添加索引：

```python
# ✅ 正确
username: str = Field(default="", index=True)
status: int = Field(default=1, index=True)
created_at: datetime = Field(default=None, index=True)

# ❌ 错误
username: str = Field(default="")
status: int = Field(default=1)
created_at: datetime = Field(default=None)
```

## 常见问题

### 1. 如何定义外键？

```python
group_id: int | None = Field(
    default=None,
    foreign_key="admin_groups.id"
)
```

### 2. 如何定义复合索引？

```python
from sqlalchemy import Index

__table_args__ = (
    Index("idx_username_status", "username", "status"),
)
```

### 3. 如何定义唯一约束？

```python
username: str = Field(default="", unique=True)
```

## 相关链接

- [服务层开发指南](./service-guide.md)
- [BaseTableModel 源码](../../server/Modules/common/models/base_model.py)
- [第一个接口开发](../first-api.md)

---

通过遵循模型开发指南，您可以定义清晰、规范的数据库表结构。
