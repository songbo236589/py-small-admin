# 数据库迁移

本文档介绍了如何使用 Alembic 进行数据库迁移。

## Alembic 简介

Alembic 是 SQLAlchemy 的轻量级数据库迁移工具，用于：

- 管理数据库架构变更
- 自动生成迁移脚本
- 版本控制数据库结构
- 支持升级和回滚

## 初始化 Alembic

### 1. 安装 Alembic

```bash
pip install alembic
```

### 2. 初始化 Alembic

```bash
cd server
alembic init alembic
```

这将创建 `alembic/` 目录和 `alembic.ini` 配置文件。

### 3. 配置 Alembic

编辑 `alembic.ini`：

```ini
# 数据库连接字符串
sqlalchemy.url = mysql://root:password@localhost:3306/py_small_admin

# 迁移脚本存放目录
script_location = alembic

# 迁移脚本文件名格式
file_template = %%(rev)s_%%(slug)s

# 时区设置
timezone = Asia/Shanghai
```

编辑 `alembic/env.py`：

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Modules.common.libs.config import Config

# 导入所有模型
from Modules.admin.models.admin_admin import AdminAdmin
from Modules.admin.models.admin_group import AdminGroup
from Modules.admin.models.admin_rule import AdminRule
from Modules.admin.models.admin_sys_config import AdminSysConfig
from Modules.admin.models.admin_upload import AdminUpload
from Modules.quant.models.quant_stock import QuantStock
from Modules.quant.models.quant_industry import QuantIndustry
from Modules.quant.models.quant_concept import QuantConcept
# ... 导入其他模型

config = context.config

# 从配置获取数据库 URL
config.set_main_option("sqlalchemy.url", Config.get("database.connections.mysql.url"))

target_metadata = Base.metadata

def run_migrations_offline() -> " ... "
def run_migrations_online() -> " ... "
```

## 创建迁移

### 自动生成迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "Initial migration"
```

这将自动检测模型变化并生成迁移脚本。

### 手动创建迁移

```bash
# 创建空的迁移脚本
alembic revision -m "Custom migration"
```

然后在生成的迁移文件中手动编写 SQL。

## 执行迁移

### 升级到最新版本

```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision_id>

# 升级 N 个版本
alembic upgrade +1
```

### 回滚迁移

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到初始版本
alembic downgrade base

# 回滚到指定版本
alembic downgrade <revision_id>
```

### 查看当前版本

```bash
# 查看当前数据库版本
alembic current

# 查看迁移历史
alembic history

# 查看待执行的迁移
alembic heads
```

## 迁移脚本结构

### 迁移脚本示例

```python
"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """升级操作"""
    # 创建管理员表
    op.create_table(
        'fa_admin_admins',
        sa.Column('id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False, server_default=''),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='管理员表'
    )
    
    # 创建索引
    op.create_index('idx_admin_admins_username', 'fa_admin_admins', ['username'], unique=True)

def downgrade():
    """回滚操作"""
    # 删除索引
    op.drop_index('idx_admin_admins_username', table_name='fa_admin_admins')
    
    # 删除表
    op.drop_table('fa_admin_admins')
```

## 常见操作

### 添加表

```python
def upgrade():
    op.create_table(
        'your_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('your_table')
```

### 添加列

```python
def upgrade():
    op.add_column('your_table', sa.Column('new_column', sa.String(100), nullable=True))

def downgrade():
    op.drop_column('your_table', 'new_column')
```

### 修改列

```python
def upgrade():
    op.alter_column('your_table', 'column_name', 
                   existing_type=sa.String(50),
                   type_=sa.String(100),
                   nullable=False)

def downgrade():
    op.alter_column('your_table', 'column_name',
                   existing_type=sa.String(100),
                   type_=sa.String(50),
                   nullable=True)
```

### 删除列

```python
def upgrade():
    op.drop_column('your_table', 'column_name')

def downgrade():
    op.add_column('your_table', sa.Column('column_name', sa.String(100)))
```

### 添加索引

```python
def upgrade():
    op.create_index('idx_table_column', 'your_table', ['column_name'])

def downgrade():
    op.drop_index('idx_table_column', table_name='your_table')
```

### 添加外键

```python
def upgrade():
    op.create_foreign_key(
        'fk_table_column',
        'child_table',
        'parent_table',
        ['parent_id'],
        ['id']
    )

def downgrade():
    op.drop_constraint('fk_table_column', 'child_table', type_='foreignkey')
```

## 数据迁移

### 迁移数据

```python
from sqlalchemy.sql import table, column

def upgrade():
    # 定义数据表对象
    users_table = table('users',
        column('id', sa.Integer),
        column('name', sa.String(100))
    )
    
    # 执行批量插入
    op.bulk_insert(users_table, [
        {'id': 1, 'name': 'User 1'},
        {'id': 2, 'name': 'User 2'},
        {'id': 3, 'name': 'User 3'},
    ])

def downgrade():
    # 删除数据
    op.execute("DELETE FROM users WHERE id IN (1, 2, 3)")
```

## 命令行工具

项目提供了便捷的命令行工具。

### 使用命令行工具

```bash
# 初始化数据库
python commands/migrate.py init

# 升级到最新版本
python commands/migrate.py upgrade head

# 回滚到上一个版本
python commands/migrate.py downgrade -1

# 回滚到初始版本
python commands/migrate.py downgrade base

# 生成迁移脚本
python commands/migrate.py revision --autogenerate -m "Add new table"

# 查看当前版本
python commands/migrate.py current

# 查看迁移历史
python commands/migrate.py history
```

## 最佳实践

### 1. 迁移命名

使用清晰、描述性的迁移名称：

```bash
# 好的命名
alembic revision -m "Add email field to users table"
alembic revision -m "Create orders table with foreign keys"

# 不好的命名
alembic revision -m "Update db"
alembic revision -m "Fix stuff"
```

### 2. 迁移分组

按功能分组迁移：

```bash
# Admin 模块迁移
alembic revision -m "admin: Add admin table"

# Quant 模块迁移
alembic revision -m "quant: Add stock table"
```

### 3. 保持可逆

始终实现 `downgrade()` 函数，确保可以回滚：

```python
def upgrade():
    # 可逆的操作
    pass

def downgrade():
    # 回滚操作
    pass
```

### 4. 测试迁移

在执行迁移前，先在开发环境测试：

```bash
# 在开发环境测试
alembic upgrade head
alembic downgrade -1

# 确认无误后，在生产环境执行
```

### 5. 备份数据

在生产环境执行迁移前，先备份数据：

```bash
# 备份数据库
mysqldump -u root -p py_small_admin > backup_before_migration_$(date +%Y%m%d).sql
```

## 常见问题

### 1. 自动生成失败

**问题**：`alembic revision --autogenerate` 报错

**解决方案**：

1. 确保所有模型都已导入
2. 检查 `alembic/env.py` 中的 `target_metadata`
3. 清除缓存：`rm -rf alembic/__pycache__/`

### 2. 迁移冲突

**问题**：多个开发者同时创建迁移导致冲突

**解决方案**：

1. 使用唯一的迁移 ID
2. 合并迁移时手动解决冲突
3. 使用 `--head` 参数重新生成迁移

### 3. 回滚失败

**问题**：`alembic downgrade` 失败

**解决方案**：

1. 检查 `downgrade()` 函数是否正确
2. 手动修复数据库
3. 标记迁移为已应用：`alembic stamp <revision_id>`

### 4. 数据库连接失败

**问题**：无法连接到数据库

**解决方案**：

1. 检查数据库服务是否运行
2. 检查 `alembic.ini` 中的连接字符串
3. 检查数据库用户名和密码

## 高级用法

### 1. 批量操作

```python
def upgrade():
    # 批量创建表
    for table_name in ['table1', 'table2', 'table3']:
        op.create_table(
            table_name,
            sa.Column('id', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
```

### 2. 条件迁移

```python
def upgrade():
    # 根据数据库版本执行不同操作
    if context.get_x_argument('version') == '1':
        op.add_column('users', sa.Column('email', sa.String(100)))
    else:
        op.add_column('users', sa.Column('email', sa.String(200)))
```

### 3. 数据库特定操作

```python
def upgrade():
    # MySQL 特定操作
    if context.bind.dialect.name == 'mysql':
        op.execute("ALTER TABLE users ENGINE=InnoDB")
```

## 生产环境建议

### 1. 代码审查

迁移脚本必须经过代码审查：

- 检查 SQL 语句是否正确
- 检查是否有性能问题
- 检查回滚操作是否完整

### 2. 灰度发布

逐步在生产环境部署迁移：

1. 先在一个实例上执行迁移
2. 观察运行情况
3. 逐步扩展到所有实例

### 3. 监控和日志

记录迁移执行情况：

```python
from loguru import logger

def upgrade():
    logger.info("Starting migration...")
    # 迁移逻辑
    logger.info("Migration completed successfully")
```