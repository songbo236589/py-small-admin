# 数据库填充

数据库填充工具用于在数据库中插入初始数据或测试数据，支持模块化的种子数据管理。

## 简介

数据库填充（Seed）是一种在开发、测试环境中快速填充数据库的方法。本项目提供了模块化的种子数据管理系统，支持：

- 按模块独立管理种子数据
- 环境区分（开发/测试/生产）
- 数据幂等性保证
- 数据验证和清理

## 基本用法

### 填充所有模块数据

```bash
python -m commands.seed run-all
```

### 填充指定模块数据

```bash
python -m commands.seed run --module admin
python -m commands.seed run --module quant
```

### 查看所有模块状态

```bash
python -m commands.seed list
```

输出示例：

```
模块填充状态:
--------------------------------------------------------------------------------
  模块名称      状态        模型数量    种子文件
--------------------------------------------------------------------------------
  admin         有填充      3 模型     1 种子文件
  quant         有填充      14 模型    2 种子文件
  system        有填充      2 模型     1 种子文件
--------------------------------------------------------------------------------
```

## 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `run-all` | 运行所有模块的种子数据 | `python -m commands.seed run-all` |
| `run --module <name>` | 运行指定模块的种子数据 | `python -m commands.seed run --module admin` |
| `list` | 列出所有模块状态 | `python -m commands.seed list` |
| `validate --module <name>` | 验证模块的种子数据 | `python -m commands.seed validate --module admin` |
| `dry-run --module <name>` | 模拟运行（不实际执行） | `python -m commands.seed dry-run --module admin` |
| `clean --module <name>` | 清理模块的种子数据 | `python -m commands.seed clean --module admin` |

## 环境区分

可以为不同环境指定不同的种子数据：

```bash
# 开发环境（默认）
python -m commands.seed run --module admin --env development

# 生产环境
python -m commands.seed run --module admin --env production

# 测试环境
python -m commands.seed run --module admin --env test
```

## 种子数据目录结构

```
Modules/
├── admin/
│   └── seeds/
│       ├── __init__.py
│       └── seed_data.py       # Admin 模块种子数据
└── quant/
    └── seeds/
        ├── __init__.py
        └── seed_data.py       # Quant 模块种子数据
```

## 自定义种子数据

### 创建种子数据文件

在模块的 `seeds/` 目录下创建 `seed_data.py`：

```python
from Modules.admin.models.admin_admin import AdminAdmin
from Modules.admin.models.admin_group import AdminGroup

def get_seed_data():
    """返回种子数据列表"""
    return [
        {
            "model": AdminGroup,
            "data": [
                {
                    "name": "超级管理员组",
                    "content": "拥有所有权限",
                    "rules": "1,2,3,4,5",
                    "status": 1,
                },
            ]
        },
        {
            "model": AdminAdmin,
            "data": [
                {
                    "username": "admin",
                    "name": "超级管理员",
                    "password": "admin123",  # 会被加密存储
                    "group_id": 1,
                    "status": 1,
                },
            ]
        },
    ]
```

### 使用种子数据

种子数据会自动被加载和处理，无需手动注册。

## 初始数据

### 初始管理员账号

执行 `run-all` 或运行 admin 模块的种子数据后，会创建初始管理员账号：

```
用户名：admin
密码：admin123
```

**注意**：生产环境请立即修改初始密码！

### 初始角色组

系统会创建以下初始角色组：

| 组名 | 说明 | 权限 |
|------|------|------|
| 超级管理员组 | 拥有所有权限 | 全部权限 |
| 编辑组 | 内容编辑权限 | 部分权限 |

### 初始系统配置

系统会创建以下初始配置：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| site_name | Py Small Admin | 网站名称 |
| site_keywords | Py Small Admin | 网站关键词 |
| site_description | Py Small Admin | 网站描述 |

## 最佳实践

### 1. 数据幂等性

确保种子数据可以重复执行而不产生重复数据：

```python
def get_seed_data():
    """幂等的种子数据"""
    return [
        {
            "model": AdminGroup,
            "data": [...],
            "update": True,  # 如果数据存在则更新
        },
    ]
```

### 2. 环境区分

为不同环境提供不同的种子数据：

```python
def get_seed_data():
    """根据环境返回不同的种子数据"""
    import os

    env = os.getenv('APP_ENV', 'development')

    if env == 'production':
        # 生产环境数据
        return [...]
    else:
        # 开发/测试环境数据
        return [...]
```

### 3. 数据验证

在种子数据中添加验证：

```python
def validate_seed_data(data):
    """验证种子数据"""
    for group in data.get('groups', []):
        if not group.get('name'):
            raise ValueError('角色组名称不能为空')
    return data
```

### 4. 数据清理

在填充前清理旧数据：

```bash
# 清理模块数据
python -m commands.seed clean --module admin

# 然后重新填充
python -m commands.seed run --module admin
```

## 常见问题

### 数据重复创建

**问题**：重复运行种子数据导致数据重复

**解决方案**：本工具已实现幂等性，会检查数据是否已存在。如果仍有问题，请检查种子数据文件。

### 模块未发现

**问题**：提示"模块 xxx 未发现"

**解决方案**：确保模块目录结构正确，包含 `seeds/` 目录和 `__init__.py` 文件。

### 密码加密

**问题**：种子数据中的密码是否会被加密？

**解决方案**：会自动加密。在种子数据中可以使用明文密码，系统会自动使用加密算法处理。

### 外键约束

**问题**：种子数据中存在外键依赖关系

**解决方案**：按照依赖顺序定义种子数据，被依赖的模型放在前面。

## 高级用法

### 数据导入导出

```bash
# 导出当前数据库为种子数据
python -m commands.seed export --module admin --output admin_seed.json

# 从 JSON 文件导入种子数据
python -m commands.seed import --module admin --input admin_seed.json
```

### 批量操作

```bash
# 清理所有模块数据
python -m commands.seed clean-all

# 填充所有模块数据
python -m commands.seed run-all

# 验证所有模块数据
python -m commands.seed validate-all
```

### 数据覆盖模式

```bash
# 覆盖模式（如果数据存在则更新）
python -m commands.seed run --module admin --force

# 追加模式（保留现有数据，只添加新数据）
python -m commands.seed run --module admin --append
```

## 相关文档

- [数据库迁移](./migrate.md)
- [数据库概览](../backend/database/index.md)
