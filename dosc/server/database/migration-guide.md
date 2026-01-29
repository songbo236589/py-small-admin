# 数据库迁移指南

本文档详细介绍如何使用 Alembic 进行数据库迁移。

## 概述

Alembic 是一个轻量级的数据库迁移工具，用于管理数据库版本和迁移脚本。

## 迁移命令

### 生成迁移文件

```bash
# 生成迁移文件
alembic revision --autogenerate -m "添加文章表"

# 指定迁移版本
alembic revision --autogenerate -m "添加文章表" --rev-id 001
```

### 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade 001

# 升级一步
alembic upgrade +1
```

### 回滚迁移

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade base

# 回滚到初始状态
alembic downgrade base
```

### 查看迁移历史

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 查看迁移状态
alembic heads
```

## 迁移文件结构

### 基本结构

```python
"""添加文章表

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None


def upgrade():
    # 升级操作
    pass


def downgrade():
    # 回滚操作
    pass
```

### 创建表

```python
def upgrade():
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('articles')
```

### 添加字段

```python
def upgrade():
    op.add_column('articles', sa.Column('author', sa.String(length=100), nullable=True))

def downgrade():
    op.drop_column('articles', 'author')
```

### 修改字段

```python
def upgrade():
    op.alter_column('articles', 'title', existing_type=sa.String(length=200), type_=sa.String(length=300))

def downgrade():
    op.alter_column('articles', 'title', existing_type=sa.String(length=300), type_=sa.String(length=200))
```

### 添加索引

```python
def upgrade():
    op.create_index('idx_articles_title', 'articles', ['title'])

def downgrade():
    op.drop_index('idx_articles_title', 'articles')
```

## 使用命令工具

### 运行迁移

```bash
# 使用命令工具运行迁移
python -m commands.migrate
```

### 命令工具功能

- 自动检测变更
- 生成迁移文件
- 执行迁移
- 回滚迁移

## 最佳实践

### 1. 提交前检查

在提交迁移前检查：

```bash
# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 2. 编写清晰的描述

使用清晰的迁移描述：

```python
"""添加文章表和索引

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
```

### 3. 测试迁移

在执行迁移前测试：

```python
# 在测试环境测试迁移
def upgrade():
    # 迁移逻辑
    pass

def downgrade():
    # 回滚逻辑
    pass
```

### 4. 备份数据

在执行重要迁移前备份数据：

```bash
# 备份数据库
mysqldump -u root -p py_small_admin > backup.sql
```

## 常见问题

### 1. 迁移冲突

如果多个开发者同时创建迁移，可能会产生冲突。

**解决方案**：

- 使用唯一的 revision ID
- 合并迁移文件
- 重新生成迁移

### 2. 迁移失败

如果迁移执行失败：

**解决方案**：

- 查看错误日志
- 检查数据库连接
- 回滚到上一个版本
- 修复问题后重新执行

### 3. 回滚失败

如果回滚失败：

**解决方案**：

- 检查回滚逻辑
- 手动执行 SQL
- 从备份恢复数据

## 相关链接

- [数据库使用指南](./database-guide.md)
- [关系映射指南](./relationship-guide.md)
- [数据库迁移使用文档](../../server/docs/数据库迁移使用文档.md)

---

通过遵循数据库迁移指南，您可以安全地管理数据库版本。
