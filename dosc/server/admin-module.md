# Admin 模块详解

本文档详细介绍 Admin 管理员模块的功能和实现。

## 概述

Admin 模块负责系统管理员的管理，包括用户管理、角色管理、权限管理、系统配置等功能。

## 模块结构

```
Modules/admin/
├── controllers/              # 控制器层
│   └── v1/
│       ├── admin_controller.py
│       ├── common_controller.py
│       ├── email_controller.py
│       ├── group_controller.py
│       ├── rule_controller.py
│       ├── sys_config_controller.py
│       └── upload_controller.py
├── services/                 # 服务层
│   ├── admin_service.py
│   ├── auth_service.py
│   ├── captcha_service.py
│   ├── email_service.py
│   ├── group_service.py
│   ├── rule_service.py
│   ├── sys_config_service.py
│   └── upload_service.py
├── models/                   # 模型层
│   ├── admin_admin.py
│   ├── admin_group.py
│   ├── admin_rule.py
│   ├── admin_sys_config.py
│   └── admin_upload.py
├── routes/                   # 路由层
│   ├── admin.py
│   ├── common.py
│   ├── email.py
│   ├── group.py
│   ├── rule.py
│   ├── sys_config.py
│   └── upload.py
├── validators/               # 验证器层
│   ├── admin_validator.py
│   ├── common_validator.py
│   ├── email_validator.py
│   ├── group_validator.py
│   ├── rule_validator.py
│   └── sys_config_validator.py
├── middleware/               # 中间件
│   └── permission_middleware.py
├── migrations/               # 数据库迁移
├── seeds/                   # 数据填充
│   └── admin_seed.py
├── queues/                  # 队列
│   └── email_queues.py
└── tasks/                   # 异步任务
    └── default_tasks.py
```

## 核心功能

### 1. 管理员管理

#### 功能列表

- 管理员列表（分页、搜索、排序）
- 添加管理员
- 编辑管理员
- 删除管理员
- 批量删除管理员
- 重置密码
- 设置状态

#### 数据模型

```python
class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""
    __table_comment__ = "管理员表"

    username: str = Field(default="", index=True)
    password: str = Field(default="")
    name: str = Field(default="")
    phone: str = Field(default="")
    status: int = Field(default=1, index=True)
    group_id: int | None = Field(default=None)

    # 关系
    group: Mapped["AdminGroup"] = Relationship(back_populates="admins")
    uploads: list["AdminUpload"] = Relationship(back_populates="admin")
```

#### API 接口

| 方法   | 路径                       | 说明           |
| ------ | -------------------------- | -------------- |
| GET    | /api/admin/index           | 获取管理员列表 |
| POST   | /api/admin/add             | 添加管理员     |
| GET    | /api/admin/edit/{id}       | 获取管理员信息 |
| PUT    | /api/admin/update/{id}     | 更新管理员     |
| DELETE | /api/admin/destroy/{id}    | 删除管理员     |
| DELETE | /api/admin/destroy_all     | 批量删除管理员 |
| PUT    | /api/admin/set_status/{id} | 设置管理员状态 |
| PUT    | /api/admin/reset_pwd/{id}  | 重置密码       |

### 2. 角色管理

#### 功能列表

- 角色列表
- 添加角色
- 编辑角色
- 删除角色
- 分配权限

#### 数据模型

```python
class AdminGroup(BaseTableModel, table=True):
    """角色模型"""
    __table_comment__ = "角色表"

    name: str = Field(default="", index=True)
    code: str = Field(default="", unique=True)
    status: int = Field(default=1)
    sort: int = Field(default=0)

    # 关系
    admins: list["AdminAdmin"] = Relationship(back_populates="group")
    rules: list["AdminRule"] = Relationship(back_populates="groups")
```

#### API 接口

| 方法   | 路径                       | 说明         |
| ------ | -------------------------- | ------------ |
| GET    | /api/group/index           | 获取角色列表 |
| POST   | /api/group/add             | 添加角色     |
| GET    | /api/group/edit/{id}       | 获取角色信息 |
| PUT    | /api/group/update/{id}     | 更新角色     |
| DELETE | /api/group/destroy/{id}    | 删除角色     |
| PUT    | /api/group/set_status/{id} | 设置角色状态 |

### 3. 权限管理

#### 功能列表

- 权限列表
- 添加权限
- 编辑权限
- 删除权限
- 权限树

#### 数据模型

```python
class AdminRule(BaseTableModel, table=True):
    """权限模型"""
    __table_comment__ = "权限表"

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

#### API 接口

| 方法   | 路径                      | 说明         |
| ------ | ------------------------- | ------------ |
| GET    | /api/rule/index           | 获取权限列表 |
| POST   | /api/rule/add             | 添加权限     |
| GET    | /api/rule/edit/{id}       | 获取权限信息 |
| PUT    | /api/rule/update/{id}     | 更新权限     |
| DELETE | /api/rule/destroy/{id}    | 删除权限     |
| PUT    | /api/rule/set_status/{id} | 设置权限状态 |

### 4. 系统配置

#### 功能列表

- 配置列表
- 添加配置
- 编辑配置
- 删除配置
- 配置分组

#### 数据模型

```python
class AdminSysConfig(BaseTableModel, table=True):
    """系统配置模型"""
    __table_comment__ = "系统配置表"

    group: str = Field(default="")
    name: str = Field(default="", unique=True)
    title: str = Field(default="")
    value: str = Field(default="")
    type: str = Field(default="text")
    options: str = Field(default="")
    sort: int = Field(default=0)
    status: int = Field(default=1)
```

#### API 接口

| 方法   | 路径                            | 说明         |
| ------ | ------------------------------- | ------------ |
| GET    | /api/sys_config/index           | 获取配置列表 |
| POST   | /api/sys_config/add             | 添加配置     |
| GET    | /api/sys_config/edit/{id}       | 获取配置信息 |
| PUT    | /api/sys_config/update/{id}     | 更新配置     |
| DELETE | /api/sys_config/destroy/{id}    | 删除配置     |
| PUT    | /api/sys_config/set_status/{id} | 设置配置状态 |

### 5. 文件上传

#### 功能列表

- 图片上传
- 视频上传
- 音频上传
- 文档上传
- 媒体库管理

#### 数据模型

```python
class AdminUpload(BaseTableModel, table=True):
    """上传文件模型"""
    __table_comment__ = "上传文件表"

    admin_id: int = Field(default=0)
    name: str = Field(default="")
    path: str = Field(default="")
    url: str = Field(default="")
    mime_type: str = Field(default="")
    size: int = Field(default=0)
    category: str = Field(default="image")

    # 关系
    admin: Mapped["AdminAdmin"] = Relationship(back_populates="uploads")
```

#### API 接口

| 方法 | 路径                 | 说明       |
| ---- | -------------------- | ---------- |
| POST | /api/upload/image    | 上传图片   |
| POST | /api/upload/video    | 上传视频   |
| POST | /api/upload/audio    | 上传音频   |
| POST | /api/upload/document | 上传文档   |
| GET  | /api/upload/library  | 获取媒体库 |

### 6. 认证授权

#### 功能列表

- 管理员登录
- 获取验证码
- 刷新 Token
- 退出登录
- 权限验证

#### API 接口

| 方法 | 路径                | 说明       |
| ---- | ------------------- | ---------- |
| POST | /api/common/login   | 管理员登录 |
| GET  | /api/common/captcha | 获取验证码 |
| POST | /api/common/refresh | 刷新 Token |
| POST | /api/common/logout  | 退出登录   |

## 核心服务

### AdminService

管理员服务，提供管理员相关的业务逻辑。

```python
class AdminService(BaseService):
    """管理员服务"""

    async def index(self, data: dict) -> JSONResponse:
        """获取管理员列表"""

    async def add(self, data: dict) -> JSONResponse:
        """添加管理员"""

    async def update(self, id: int, data: dict) -> JSONResponse:
        """更新管理员"""

    async def destroy(self, id: int) -> JSONResponse:
        """删除管理员"""

    async def reset_pwd(self, id: int) -> JSONResponse:
        """重置密码"""
```

### AuthService

认证服务，提供登录、Token 管理等功能。

```python
class AuthService:
    """认证服务"""

    async def login(self, username: str, password: str) -> JSONResponse:
        """管理员登录"""

    async def refresh_token(self, refresh_token: str) -> JSONResponse:
        """刷新 Token"""

    async def logout(self, token: str) -> JSONResponse:
        """退出登录"""
```

### GroupService

角色服务，提供角色相关的业务逻辑。

```python
class GroupService(BaseService):
    """角色服务"""

    async def index(self, data: dict) -> JSONResponse:
        """获取角色列表"""

    async def add(self, data: dict) -> JSONResponse:
        """添加角色"""

    async def update(self, id: int, data: dict) -> JSONResponse:
        """更新角色"""

    async def destroy(self, id: int) -> JSONResponse:
        """删除角色"""
```

## 权限中间件

### PermissionMiddleware

权限验证中间件，用于验证用户权限。

```python
class PermissionMiddleware:
    """权限中间件"""

    async def __call__(self, request: Request, call_next):
        # 验证 Token
        # 验证权限
        response = await call_next(request)
        return response
```

### 使用方式

```python
# 在路由中使用权限中间件
@router.get("/admin/index")
@permission_required("admin:index")
async def index(...):
    pass
```

## 数据填充

### AdminSeed

管理员数据填充，用于初始化默认管理员和角色。

```python
class AdminSeed:
    """管理员数据填充"""

    async def run(self):
        """运行数据填充"""
        # 创建默认角色
        # 创建默认管理员
        # 创建默认权限
```

### 使用方式

```bash
# 运行数据填充
python -m commands.seed
```

## 邮件功能

### EmailService

邮件服务，提供邮件发送功能。

```python
class EmailService:
    """邮件服务"""

    async def send_email(self, to: str, subject: str, content: str):
        """发送邮件"""
```

### EmailTasks

邮件任务，使用 Celery 异步发送邮件。

```python
@shared_task
def send_email_task(to: str, subject: str, content: str):
    """异步发送邮件任务"""
```

## 最佳实践

### 1. 管理员密码安全

- 使用强加密算法
- 强制密码复杂度
- 定期提醒修改密码

### 2. 权限控制

- 最小权限原则
- 定期审查权限
- 记录权限变更

### 3. 操作日志

- 记录所有敏感操作
- 记录登录信息
- 记录权限变更

## 常见问题

### 1. 如何添加新的权限？

在 `admin_rules` 表中添加新权限记录，然后为角色分配权限。

### 2. 如何修改默认管理员密码？

修改 `.env` 文件中的 `APP_DEFAULT_ADMIN_PASSWORD`，然后运行数据填充。

### 3. 如何禁用某个管理员？

调用 `/api/admin/set_status/{id}` 接口，将状态设置为 0。

## 相关链接

- [项目结构说明](./project-structure.md)
- [模块开发指南](./module-development.md)
- [Quant 模块详解](./quant-module.md)
- [Common 模块详解](./common-module.md)

---

Admin 模块是系统的核心模块，负责管理员和权限管理。
