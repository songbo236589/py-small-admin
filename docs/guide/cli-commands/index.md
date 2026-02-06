# 命令行工具

本项目提供了一系列命令行工具，帮助开发者快速完成数据库迁移、数据填充、模块创建等常见操作。

## 工具列表

| 工具 | 功能描述 | 详细文档 |
|------|---------|---------|
| [数据库迁移](./migrate.md) | 管理数据库表结构迁移 | [详细文档](../../../server/docs/数据库迁移使用文档.md) |
| [数据库填充](./seed.md) | 填充初始数据和测试数据 | [详细文档](../../../server/docs/数据库填充使用文档.md) |
| [Celery 管理](./celery-manager.md) | 管理 Celery Worker、Beat、Flower | [详细文档](../../../server/docs/Celery管理脚本使用文档.md) |
| [模块创建](./create-module.md) | 快速创建标准化的新模块 | [详细文档](../../../server/docs/模块创建工具使用文档.md) |
| [密钥生成](./generate-keys.md) | 生成安全的 API 密钥和 JWT 密钥 | [详细文档](../../../server/docs/密钥生成工具使用文档.md) |

## 快速开始

### 安装后首次使用

```bash
# 1. 数据库迁移
python -m commands.migrate up

# 2. 填充初始数据
python -m commands.seed run-all

# 3. 生成安全密钥（可选）
python -m commands.generate_keys --all
```

### 日常开发

```bash
# 查看所有模块状态
python -m commands.migrate list
python -m commands.seed list

# 创建新模块
python -m commands.create_module create --module user

# 管理 Celery 组件
python -m commands.celery_manager status
```

## 命令格式规范

所有命令行工具遵循统一的调用格式：

```bash
python -m commands.<工具名> <子命令> [参数]
```

### 示例

```bash
# 数据库迁移
python -m commands.migrate up --module admin

# 数据库填充
python -m commands.seed run --module admin --env production

# Celery 管理
python -m commands.celery_manager worker start

# 模块创建
python -m commands.create_module create --module user

# 密钥生成
python -m commands.generate_keys --all --dry-run
```

## 获取帮助

每个工具都提供了内置的帮助信息：

```bash
# 查看工具帮助
python -m commands.migrate --help

# 查看子命令帮助
python -m commands.migrate up --help
```

## 常见问题

### Q: 如何查看所有可用的命令？

A: 使用 `--help` 参数查看：

```bash
python -m commands.<工具名> --help
```

### Q: 命令执行失败怎么办？

A: 请检查以下几点：
1. 是否在项目根目录 (`server/`) 下执行命令
2. 虚拟环境是否已激活
3. 依赖包是否已安装 (`pip install -r requirements.txt`)
4. 配置文件 (`.env`) 是否正确配置

### Q: 生产环境使用需要注意什么？

A: 生产环境建议：
1. 备份数据库后再执行迁移操作
2. 使用 `--env production` 参数指定生产环境
3. 先在测试环境验证迁移和填充操作
4. 查看详细文档了解最佳实践

## 相关文档

- [安装指南](../getting-started/install.md)
- [环境配置说明](../../../server/docs/环境配置说明.md)
