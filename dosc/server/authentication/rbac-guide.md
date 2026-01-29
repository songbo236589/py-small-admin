# RBAC 权限模型指南

本文档详细介绍如何实现基于角色的访问控制（RBAC）。

## 概述

RBAC（Role-Based Access Control）是一种基于角色的访问控制模型，通过角色来管理用户权限。

## 权限模型

### 角色管理

```python
class AdminGroup(BaseTableModel, table=True):
    """角色模型"""
    __table_comment__ = "角色表"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(default="", index=True)
    code: str = Field(default="", unique=True)
    status: int = Field(default=1)
    sort: int = Field(default=0)

    # 关系
    admins: list["AdminAdmin"] = Relationship(back_populates="group")
    rules: list["AdminRule"] = Relationship(back_populates="groups")
```

### 权限管理

```python
class AdminRule(BaseTableModel, table=True):
    """权限模型"""
    __table_comment__ = "权限表"

    id: int = Field(default=None, primary_key=True)
    parent_id: int = Field(default=0)
    name: str = Field(default="")
    title: str = Field(default="")
    icon: str = Field(default="")
    path: str = Field(default="")
    type: str = Field(default="menu")
    status: int = Field(default=1)
    sort: int = Field(default=0)

    # 关系
    groups: list["AdminGroup"] = Relationship(back_populates="rules")
```

### 用户角色关联

```python
class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""
    __table_comment__ = "管理员表"

    id: int = Field(default=None, primary_key=True)
    username: str = Field(default="", index=True)
    password: str = Field(default="")
    status: int = Field(default=1)
    group_id: int | None = Field(default=None, foreign_key="admin_groups.id")

    # 关系
    group: Mapped[Optional["AdminGroup"]] = Relationship(back_populates="admins")
```

## 权限验证

### 权限中间件

```python
from fastapi import Request, HTTPException, status
from Modules.common.libs.jwt.jwt import get_current_user

async def permission_required(permission: str):
    """权限验证装饰器"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # 获取当前用户
            user_id = await get_current_user(request)

            # 获取用户权限
            user_permissions = await get_user_permissions(user_id)

            # 验证权限
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有权限: {permission}"
                )

            # 调用原始函数
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 获取用户权限

```python
async def get_user_permissions(user_id: int) -> list[str]:
    """获取用户权限列表"""
    async with get_async_session() as session:
        # 获取用户角色
        admin = await session.get(AdminAdmin, user_id)
        if not admin or not admin.group:
            return []

        # 获取角色权限
        group = admin.group
        if not group:
            return []

        permissions = []
        for rule in group.rules:
            if rule.status == 1:
                permissions.append(rule.code)

        return permissions
```

### 权限检查

```python
async def check_permission(user_id: int, permission: str) -> bool:
    """检查用户是否有权限"""
    permissions = await get_user_permissions(user_id)
    return permission in permissions
```

## 权限使用

### 保护路由

```python
from Modules.common.libs.middleware.permission import permission_required

@router.get("/admin/index")
@permission_required("admin:index")
async def admin_index():
    """管理员列表 - 需要权限"""
    pass
```

### 多权限要求

```python
@router.post("/admin/add")
@permission_required("admin:add")
@permission_required("admin:edit")
async def admin_add():
    """管理员添加 - 需要多个权限"""
    pass
```

## 权限分配

### 分配角色权限

```python
async def assign_permissions_to_group(group_id: int, permission_ids: list[int]):
    """为角色分配权限"""
    async with get_async_session() as session:
        group = await session.get(AdminGroup, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )

        # 清除现有权限
        group.rules = []

        # 分配新权限
        for permission_id in permission_ids:
            rule = await session.get(AdminRule, permission_id)
            if rule:
                group.rules.append(rule)

        await session.commit()
```

### 为用户分配角色

```python
async def assign_group_to_user(user_id: int, group_id: int):
    """为用户分配角色"""
    async with get_async_session() as session:
        admin = await session.get(AdminAdmin, user_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        admin.group_id = group_id
        await session.commit()
```

## 最佳实践

### 1. 最小权限原则

只分配必要的权限，避免权限过大。

### 2. 定期审查权限

定期审查用户权限，及时撤销不必要的权限。

### 3. 使用权限组

将相关权限分组，便于管理。

### 4. 记录权限变更

记录所有权限变更，便于审计。

## 常见问题

### 1. 如何处理权限继承？

使用角色继承或权限组。

### 2. 如何处理临时权限？

使用临时角色或临时权限。

### 3. 如何实现数据权限？

在业务逻辑中添加数据权限检查。

## 相关链接

- [JWT 使用指南](./jwt-guide.md)
- [中间件开发指南](../api-development/middleware-guide.md)

---

通过遵循 RBAC 权限模型指南，您可以实现灵活、安全的权限管理。
