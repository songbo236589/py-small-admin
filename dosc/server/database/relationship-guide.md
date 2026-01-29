# 关系映射指南

本文档详细介绍如何在 SQLModel 中定义和使用关系映射。

## 概述

SQLModel 提供了强大的关系映射功能，支持一对一、一对多、多对多等关系。

## 关系类型

### 一对多关系

一个管理员可以有多个上传文件：

```python
from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .admin_upload import AdminUpload

class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    # 外键
    uploads: list["AdminUpload"] = Relationship(back_populates="admin")


class AdminUpload(BaseTableModel, table=True):
    """上传文件模型"""

    # 外键
    admin_id: int = Field(default=0, foreign_key="admin_admins.id")
    admin: Mapped[Optional["AdminAdmin"]] = Relationship(back_populates="uploads")
```

### 多对一关系

多个管理员可以属于一个角色：

```python
class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    # 外键
    group_id: int | None = Field(default=None, foreign_key="admin_groups.id")
    group: Mapped[Optional["AdminGroup"]] = Relationship(back_populates="admins")


class AdminGroup(BaseTableModel, table=True):
    """角色模型"""

    # 关系
    admins: list["AdminAdmin"] = Relationship(back_populates="group")
```

### 一对一关系

一个用户对应一个用户信息：

```python
class User(BaseTableModel, table=True):
    """用户模型"""

    # 外键
    profile_id: int | None = Field(default=None, foreign_key="user_profiles.id")
    profile: Mapped[Optional["UserProfile"]] = Relationship(back_populates="user")


class UserProfile(BaseTableModel, table=True):
    """用户信息模型"""

    # 关系
    user: Mapped[Optional["User"]] = Relationship(back_populates="profile")
```

### 多对多关系

文章和标签是多对多关系：

```python
class Article(BaseTableModel, table=True):
    """文章模型"""

    # 关系
    tags: list["Tag"] = Relationship(
        back_populates="articles",
        link_model=ArticleTag  # 中间表
    )


class Tag(BaseTableModel, table=True):
    """标签模型"""

    # 关系
    articles: list["Article"] = Relationship(
        back_populates="tags",
        link_model=ArticleTag
    )


class ArticleTag(BaseTableModel, table=True):
    """文章标签中间表"""

    article_id: int = Field(default=0, foreign_key="articles.id")
    tag_id: int = Field(default=0, foreign_key="tags.id")
```

## 关系加载

### 预加载关系

```python
from sqlalchemy.orm import selectinload

async def get_admin_with_group(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin)
            .options(selectinload(AdminAdmin.group))
            .where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

### 延迟加载

```python
async def get_admin(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).where(AdminAdmin.id == id)
        )
        admin = result.scalar_one_or_none()

        # 访问关系时自动加载
        if admin and admin.group:
            return admin.group.name
        return None
```

### 选择性加载

```python
from sqlalchemy.orm import load_only

async def get_admin_with_group(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin)
            .options(
                selectinload(AdminAdmin.group).load_only(
                    AdminGroup.id,
                    AdminGroup.name
                )
            )
            .where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

## 最佳实践

### 1. 使用预加载避免 N+1 问题

```python
# ✅ 正确 - 使用预加载
query = select(AdminAdmin).options(selectinload(AdminAdmin.group))

# ❌ 错误 - N+1 问题
query = select(AdminAdmin)
```

### 2. 使用正确的级联操作

```python
# ✅ 正确
admin_id: int = Field(
    default=None,
    foreign_key="admin_admins.id",
    ondelete="SET NULL"  # 级联删除
)

# ❌ 错误 - 没有级联操作
admin_id: int = Field(default=None, foreign_key="admin_admins.id")
```

### 3. 使用类型提示

```python
# ✅ 正确
group: Mapped[Optional["AdminGroup"]] = Relationship(back_populates="admins")

# ❌ 错误
group = Relationship(back_populates="admins")
```

## 常见问题

### 1. 如何定义自引用关系？

```python
class Category(BaseTableModel, table=True):
    """分类模型"""

    parent_id: int | None = Field(default=None, foreign_key="categories.id")
    parent: Mapped[Optional["Category"]] = Relationship(
        back_populates="children",
        remote_side=[id]
    )
    children: list["Category"] = Relationship(
        back_populates="parent",
        remote_side=[parent_id]
    )
```

### 2. 如何定义多列外键？

```python
class Order(BaseTableModel, table=True):
    """订单模型"""

    user_id: int = Field(default=0, foreign_key="users.id")
    product_id: int = Field(default=0, foreign_key="products.id")

    user: Mapped["User"] = Relationship(foreign_keys="[user_id]")
    product: Mapped["Product"] = Relationship(foreign_keys="[product_id]")
```

## 相关链接

- [数据库使用指南](./database-guide.md)
- [模型开发指南](../api-development/model-guide.md)
- [查询优化指南](./query-optimization.md)

---

通过遵循关系映射指南，您可以定义清晰、高效的数据模型关系。
