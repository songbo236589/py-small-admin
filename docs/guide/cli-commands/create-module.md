# 模块创建

模块创建工具用于快速创建标准化的新模块，自动生成符合项目规范的目录结构和代码文件。

## 基本用法

### 创建新模块

```bash
python -m commands.create_module create --module user
```

这将创建一个名为 `user` 的新模块，包含完整的目录结构。

### 查看所有模块

```bash
python -m commands.create_module list
```

### 查看详细信息

```bash
python -m commands.create_module list --detail
```

输出示例：

```
发现的模块:
------------------------------------------------------------
模块名称              文件数
------------------------------------------------------------
admin                 15
user                  8
system                12
------------------------------------------------------------
```

### 验证模块结构

```bash
python -m commands.create_module validate --module user
```

## 生成的目录结构

创建模块后会自动生成以下目录结构：

```
Modules/user/
├── __init__.py              # 模块初始化文件
├── controllers/             # 控制器目录
│   ├── __init__.py
│   └── v1/                  # V1 版本控制器
│       ├── __init__.py
│       └── test_controller.py
├── models/                  # 模型目录
│   └── __init__.py
├── queues/                  # 队列目录
│   └── __init__.py
├── routes/                  # 路由目录
│   ├── __init__.py
│   └── test.py
├── seeds/                   # 种子数据目录
│   └── __init__.py
├── services/                # 服务层目录
│   └── __init__.py
├── tasks/                   # 任务目录
│   └── __init__.py
└── validators/              # 验证器目录
    └── __init__.py
```

## 模块命名规范

模块名称必须符合以下规则：

- 以小写字母开头
- 只能包含小写字母、数字和下划线
- 不能是 Python 保留关键字

### 有效示例

```bash
python -m commands.create_module create --module user
python -m commands.create_module create --module order_manage
python -m commands.create_module create --module shop_api
```

### 无效示例

```bash
# ❌ 以下名称无效
python -m commands.create_module create --module User      # 大写字母开头
python -m commands.create_module create --module 123user   # 数字开头
python -m commands.create_module create --module user-name # 包含连字符
python -m commands.create_module create --module class     # Python 关键字
```

## 创建后的步骤

### 1. 初始化迁移系统

```bash
python -m commands.migrate init --module user
```

### 2. 创建数据模型

在 `Modules/user/models/` 目录下创建模型文件。

### 3. 创建迁移

```bash
python -m commands.migrate create --module user --message "创建用户表"
```

### 4. 执行迁移

```bash
python -m commands.migrate up --module user
```

### 5. 注册路由

在应用启动时注册新模块的路由。

## 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `create --module <name>` | 创建新模块 | `python -m commands.create_module create --module user` |
| `list [--detail]` | 列出所有模块 | `python -m commands.create_module list --detail` |
| `validate --module <name>` | 验证模块结构 | `python -m commands.create_module validate --module user` |

## 常见问题

### 模块已存在

**问题**：创建模块时提示"模块 xxx 已存在"

**解决方案**：工具会提示是否覆盖，如需覆盖请确认操作。建议先备份现有模块。

### 验证失败

**问题**：验证模块时提示缺少文件或目录

**解决方案**：检查模块目录结构是否完整，缺少的目录可以手动创建。

## 详细文档

更多详细用法请参考 [模块创建工具使用文档](../../../server/docs/模块创建工具使用文档.md)
