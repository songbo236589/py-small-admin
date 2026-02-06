# 数据库迁移

数据库迁移工具用于管理数据库表结构的变更，支持多模块独立的迁移管理。

## 简介

数据库迁移（Migration）是一种版本控制数据库结构变更的方法。本项目使用 Alembic 作为迁移工具，支持：

- 多模块独立迁移
- 自动生成迁移脚本
- 迁移版本管理
- 迁移回滚

## 基本用法

### 升级所有模块

```bash
python -m commands.migrate up
```

### 升级指定模块

```bash
python -m commands.migrate up --module admin
python -m commands.migrate up --module quant
```

### 降级模块

```bash
# 降级一个版本
python -m commands.migrate down --module admin

# 降级到初始版本
python -m commands.migrate reset --module admin
```

### 查看所有模块状态

```bash
python -m commands.migrate list
```

输出示例：

```
发现的模块:
------------------------------------------------------------
模块名称              迁移状态         当前版本        版本表
------------------------------------------------------------
admin                 已初始化         abc12345        fa_admin_alembic_versions
quant                 已初始化         def67890        fa_quant_alembic_versions
------------------------------------------------------------
```

## 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `init --module <name>` | 初始化模块迁移系统 | `python -m commands.migrate init --module user` |
| `create --module <name> --message <msg>` | 创建新迁移 | `python -m commands.migrate create --module user --message "添加邮箱字段"` |
| `up [--module <name>]` | 升级到最新版本 | `python -m commands.migrate up` |
| `down [--module <name>]` | 降级一个版本 | `python -m commands.migrate down --module admin` |
| `reset --module <name>` | 重置到初始版本 | `python -m commands.migrate reset --module admin` |
| `current --module <name>` | 查看当前版本 | `python -m commands.migrate current --module admin` |
| `history --module <name>` | 查看迁移历史 | `python -m commands.migrate history --module admin` |
| `list` | 列出所有模块状态 | `python -m commands.migrate list` |

## 开发流程

### 为新模块创建迁移

```bash
# 1. 初始化迁移系统
python -m commands.migrate init --module user

# 2. 创建迁移文件
python -m commands.migrate create --module user --message "创建用户表"

# 3. 编辑迁移文件
# 编辑 Modules/user/migrations/versions/xxxxx_create_user_table.py

# 4. 执行迁移
python -m commands.migrate up --module user
```

### 修改现有模块表结构

```bash
# 1. 修改模型文件
# 编辑 Modules/user/models/user_model.py

# 2. 创建新的迁移
python -m commands.migrate create --module user --message "添加邮箱字段"

# 3. 编辑迁移文件（如果需要）

# 4. 执行迁移
python -m commands.migrate up --module user
```

### 迁移文件示例

```python
"""create user table

Revision ID: abc123
Revises:
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel

# revision identifiers, used by Alembic.
revision = 'abc123'
down_revision = None


def upgrade():
    # 创建表
    op.create_table(
        'fa_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # 创建索引
    op.create_index('idx_users_username', 'fa_users', ['username'])


def downgrade():
    # 删除索引
    op.drop_index('idx_users_username', 'fa_users')
    # 删除表
    op.drop_table('fa_users')
```

## 迁移目录结构

```
Modules/
├── admin/
│   └── migrations/
│       └── versions/
│           ├── 001_initial.py
│           ├── 002_add_email_column.py
│           └── ...
├── quant/
│   └── migrations/
│       └── versions/
│           ├── 001_initial.py
│           ├── 002_add_industry_table.py
│           └── ...
```

## 迁移最佳实践

### 1. 迁移命名规范

使用清晰的迁移名称：

```bash
# 好的命名
python -m commands.migrate create --module admin --message "add_email_column_to_users"

# 不好的命名
python -m commands.migrate create --module admin --message "update"
```

### 2. 小步迁移

每个迁移只做一件事：

```python
# 不推荐：一次做多个修改
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(100)))
    op.add_column('users', sa.Column('phone', sa.String(20)))
    op.create_table('profiles', ...)

# 推荐：每个迁移只做一件事
# 迁移1: add_email_column
# 迁移2: add_phone_column
# 迁移3: create_profiles_table
```

### 3. 可逆迁移

确保迁移可以回滚：

```python
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(100)))

def downgrade():
    op.drop_column('users', 'email')
```

### 4. 数据迁移

对于涉及数据迁移的情况，使用批量处理：

```python
from sqlalchemy.orm import sessionmaker
from sqlalchemy import orm

def upgrade():
    # 添加新列
    op.add_column('users', sa.Column('full_name', sa.String(100)))

    # 迁移数据
    session = sessionmaker(bind=op.get_bind())()
    session.execute(
        "UPDATE fa_users SET full_name = CONCAT(first_name, ' ', last_name)"
    )
    session.commit()

    # 删除旧列
    op.drop_column('users', sa.Column('first_name'))
    op.drop_column('users', sa.Column('last_name'))
```

## 常见问题

### 迁移失败

**问题**：执行迁移时报错

**解决方案**：
1. 检查数据库连接是否正常
2. 检查数据库是否已创建
3. 查看详细错误日志定位问题
4. 如果是部分失败，可以使用 `down` 回滚后修复

### 模块未初始化

**问题**：提示"模块 xxx 的迁移系统未初始化"

**解决方案**：
```bash
python -m commands.migrate init --module <模块名>
```

### 迁移冲突

**问题**：多人同时修改模型导致迁移冲突

**解决方案**：
1. 协调迁移顺序
2. 合并迁移文件
3. 使用 `merge` 命令：

```bash
alembic merge -m "合并迁移"
```

### 数据丢失风险

**问题**：迁移可能导致数据丢失

**解决方案**：
1. 迁移前备份数据库
2. 使用事务确保原子性
3. 先在测试环境验证

## 生产环境迁移

### 迁移前检查清单

- [ ] 备份当前数据库
- [ ] 在测试环境验证迁移
- [ ] 通知相关人员维护窗口
- [ ] 准备回滚方案

### 迁移步骤

```bash
# 1. 备份数据库
mysqldump -u root -p py_small_admin > backup_$(date +%Y%m%d).sql

# 2. 查看当前版本
python -m commands.migrate current --module admin

# 3. 查看待执行的迁移
python -m commands.migrate history --module admin

# 4. 执行迁移
python -m commands.migrate up --module admin

# 5. 验证迁移结果
python -m commands.migrate current --module admin
```

### 回滚方案

如果迁移出现问题，立即回滚：

```bash
# 回滚到上一个版本
python -m commands.migrate down --module admin

# 或恢复备份
mysql -u root -p py_small_admin < backup_20240101.sql
```

## 相关文档

- [数据库填充](./seed.md)
- [数据库概览](../backend/database/index.md)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
