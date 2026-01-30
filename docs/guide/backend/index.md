# 后端开发环境搭建

本文档将帮助你搭建后端开发环境。

## 环境要求

确保你已经满足以下环境要求：

- Python 3.11+
- MySQL 5.7+
- Redis 5.0+
- Git

详细的安装说明请参考 [环境要求](../getting-started/index.md)。

## 克隆项目

```bash
git clone https://github.com/songbo236589/py-small-admin.git
cd py-small-admin
```

## 创建虚拟环境

```bash
cd server
python -m venv venv
```

## 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

## 安装依赖

```bash
pip install -r requirements.txt
```

如果下载速度较慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 配置环境变量

### 1. 创建配置文件

```bash
cp .env.example .env
```

如果没有 `.env.example` 文件，请手动创建 `.env` 文件。

### 2. 编辑配置文件

使用你喜欢的编辑器打开 `.env` 文件：

```bash
code .env
```

### 3. 配置数据库

```bash
DB_DEFAULT=mysql://root:password@localhost:3306/py_small_admin
```

将 `root:password` 替换为你的 MySQL 用户名和密码。

### 4. 配置 Redis

```bash
REDIS_DEFAULT=redis://localhost:6379/0
```

如果 Redis 设置了密码，需要包含密码：

```bash
REDIS_DEFAULT=redis://:password@localhost:6379/0
```

### 5. 配置 JWT

```bash
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

**重要**：生产环境请使用强随机字符串作为 `JWT_SECRET_KEY`。

### 6. 其他配置

根据需要配置其他选项，如 Celery、邮件、云存储等。

详细的配置说明请参考 [配置说明](../getting-started/configuration.md)。

## 创建数据库

### 1. 登录 MySQL

```bash
mysql -u root -p
```

### 2. 创建数据库

```sql
CREATE DATABASE py_small_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

## 数据库迁移

### 1. 执行迁移

```bash
alembic upgrade head
```

### 2. 验证迁移

检查数据表是否创建成功：

```bash
mysql -u root -p py_small_admin
```

```sql
SHOW TABLES;
```

你应该能看到类似以下的表：

```
fa_admin_admins
fa_admin_groups
fa_admin_rules
fa_admin_sys_configs
fa_admin_uploads
fa_quant_stocks
fa_quant_industrys
fa_quant_concepts
fa_quant_stock_concepts
fa_quant_stock_kline1ds
fa_quant_stock_kline1ws
fa_quant_stock_kline1ms
...
```

## 填充初始数据（可选）

如果你需要初始管理员数据和菜单数据：

```bash
python commands/seed.py
```

初始管理员账号：
- 用户名：`admin`
- 密码：`admin123`

**注意**：生产环境请立即修改初始密码！

## 启动开发服务器

```bash
python run.py
```

服务将在 http://localhost:8000 启动。

## 验证安装

### 1. 访问系统信息

打开浏览器访问 http://localhost:8000，你应该能看到系统信息。

### 2. 访问 API 文档

访问 http://localhost:8000/docs 查看 OpenAPI 文档。

### 3. 测试登录接口

使用 curl 或 Postman 测试登录接口：

```bash
curl -X POST http://localhost:8000/api/admin/common/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

如果返回访问令牌，说明安装成功。

## 开发工具配置

### PyCharm 配置

1. **设置 Python 解释器**
   - 打开 Settings → Project → Python Interpreter
   - 选择虚拟环境的 Python 解释器（`venv/bin/python` 或 `venv\Scripts\python.exe`）

2. **配置运行配置**
   - Run → Edit Configurations
   - 添加新的 Python 配置
   - Script path: `server/run.py`
   - Working directory: `server`

3. **代码风格**
   - Settings → Tools → External Tools
   - 添加 Ruff 工具用于代码检查和格式化

### VS Code 配置

1. **选择 Python 解释器**
   - Ctrl/Cmd + Shift + P
   - 输入 "Python: Select Interpreter"
   - 选择虚拟环境的 Python 解释器

2. **安装扩展**
   - Python
   - Pylance
   - Ruff
   - GitLens

3. **配置 settings.json**

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### 数据库工具推荐

- **DBeaver**: 免费、开源、功能强大的数据库工具
- **Navicat**: 功能丰富，但收费
- **MySQL Workbench**: MySQL 官方工具

### Redis 工具推荐

- **RedisInsight**: Redis 官方工具，功能强大
- **Another Redis Desktop Manager**: 简单易用的桌面客户端

## 常见问题

### 1. 依赖安装失败

**问题**：`pip install` 时报错

**解决方案**：

```bash
# 升级 pip
pip install --upgrade pip setuptools wheel

# 清除缓存
pip cache purge

# 重新安装
pip install -r requirements.txt
```

### 2. 数据库连接失败

**问题**：`Can't connect to MySQL server`

**解决方案**：

1. 检查 MySQL 服务是否启动
2. 检查 `.env` 文件中的数据库配置是否正确
3. 检查用户名和密码是否正确
4. 检查防火墙设置

### 3. 迁移失败

**问题**：`alembic upgrade head` 报错

**解决方案**：

```bash
# 重置迁移
alembic downgrade base
alembic upgrade head

# 或者重新创建迁移
rm -rf Modules/admin/migrations/versions/*
rm -rf Modules/quant/migrations/versions/*
alembic revision --autogenerate
alembic upgrade head
```

### 4. 端口被占用

**问题**：`Address already in use`

**解决方案**：

```bash
# 修改 .env 文件中的端口号
APP_PORT=8001
```

或终止占用端口的进程。