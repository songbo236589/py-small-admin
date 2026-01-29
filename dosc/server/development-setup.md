# 开发环境搭建

本文档详细介绍如何搭建 Py Small Admin 的开发环境。

## 概述

开发环境搭建包括：Python 环境配置、数据库安装、Redis 配置、IDE 设置等。

## 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.9 或更高版本
- **内存**: 至少 4GB RAM（推荐 8GB+）
- **磁盘空间**: 至少 10GB 可用空间

## Python 环境配置

### 1. 安装 Python

#### Windows

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.9 或更高版本的安装包
3. 运行安装程序，**勾选 "Add Python to PATH"**
4. 验证安装：

```bash
python --version
pip --version
```

#### macOS

使用 Homebrew 安装：

```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python@3.11
```

#### Linux (Ubuntu)

```bash
# 更新包列表
sudo apt update

# 安装 Python 和 pip
sudo apt install python3.11 python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
```

### 2. 创建虚拟环境

```bash
# 进入项目目录
cd server

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

:::tip 提示
虚拟环境可以隔离项目依赖，避免不同项目之间的冲突。
:::

### 3. 升级 pip

```bash
pip install --upgrade pip
```

### 4. 配置 pip 镜像源（可选）

为了加快下载速度，可以配置国内镜像源：

```bash
# 临时使用
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 数据库安装

### MySQL 安装

#### Windows

1. 下载 [MySQL Installer](https://dev.mysql.com/downloads/installer/)
2. 运行安装程序，选择 "Developer Default"
3. 设置 root 密码（请记住！）
4. 完成安装

#### macOS

```bash
# 使用 Homebrew 安装
brew install mysql

# 启动 MySQL 服务
brew services start mysql

# 设置 root 密码
mysql_secure_installation
```

#### Linux (Ubuntu)

```bash
# 安装 MySQL
sudo apt install mysql-server

# 启动 MySQL 服务
sudo systemctl start mysql

# 设置 root 密码
sudo mysql_secure_installation
```

### 创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE py_small_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户（可选）
CREATE USER 'py_admin'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON py_small_admin.* TO 'py_admin'@'localhost';
FLUSH PRIVILEGES;

# 退出
EXIT;
```

### 配置数据库连接

编辑 `.env` 文件：

```env
DB_CONNECTIONS__MYSQL__HOST=localhost
DB_CONNECTIONS__MYSQL__PORT=3306
DB_CONNECTIONS__MYSQL__USER=root
DB_CONNECTIONS__MYSQL__PASSWORD=your_mysql_password
DB_CONNECTIONS__MYSQL__DATABASE=py_small_admin
```

## Redis 安装（可选）

Redis 用于缓存和会话存储，强烈建议安装。

### Windows

Redis 不支持 Windows，可以使用以下替代方案：

1. 使用 Docker 运行 Redis
2. 使用 Memurai（Redis 的 Windows 兼容版本）
3. 使用 WSL2 运行 Linux 版 Redis

#### 使用 Docker 运行 Redis

```bash
# 拉取 Redis 镜像
docker pull redis:7

# 运行 Redis 容器
docker run -d -p 6379:6379 --name redis redis:7

# 验证运行
docker ps
```

#### 使用 WSL2 运行 Redis

```bash
# 在 WSL2 中安装 Redis
sudo apt update
sudo apt install redis-server

# 启动 Redis
sudo service redis-server start

# 验证运行
redis-cli ping
# 应返回 PONG
```

### macOS

```bash
# 使用 Homebrew 安装
brew install redis

# 启动 Redis
brew services start redis

# 验证运行
redis-cli ping
```

### Linux (Ubuntu)

```bash
# 安装 Redis
sudo apt install redis-server

# 启动 Redis
sudo systemctl start redis

# 验证运行
redis-cli ping
```

### 配置 Redis 连接

编辑 `.env` 文件：

```env
DB_REDIS__DEFAULT__HOST=localhost
DB_REDIS__DEFAULT__PORT=6379
DB_REDIS__DEFAULT__DB=0
DB_REDIS__DEFAULT__PASSWORD=
DB_REDIS__DEFAULT__USERNAME=default

DB_REDIS__CACHE__HOST=localhost
DB_REDIS__CACHE__PORT=6379
DB_REDIS__CACHE__DB=1
DB_REDIS__CACHE__PASSWORD=
DB_REDIS__CACHE__USERNAME=default
```

## RabbitMQ 安装（可选）

RabbitMQ 用于 Celery 任务队列，如果需要使用异步任务功能则需要安装。

### 使用 Docker 运行 RabbitMQ（推荐）

```bash
# 拉取 RabbitMQ 镜像
docker pull rabbitmq:3.12-management

# 运行 RabbitMQ 容器
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=your_password \
  rabbitmq:3.12-management

# 验证运行
docker ps

# 访问管理界面
# http://localhost:15672
# 用户名: admin
# 密码: your_password
```

### 本地安装

#### macOS

```bash
brew install rabbitmq

# 启动 RabbitMQ
brew services start rabbitmq

# 启用管理插件
rabbitmq-plugins enable rabbitmq_management
```

#### Linux (Ubuntu)

```bash
# 添加 RabbitMQ 仓库
sudo apt install erlang-nox
sudo apt install rabbitmq-server

# 启动 RabbitMQ
sudo systemctl start rabbitmq-server

# 启用管理插件
sudo rabbitmq-plugins enable rabbitmq_management
```

### 配置 RabbitMQ 连接

编辑 `.env` 文件：

```env
CELERY_BROKER_URL=amqp://admin:your_password@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_FLOWER_BASIC_AUTH=admin:your_flower_password
```

## 安装项目依赖

```bash
# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 配置环境变量

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑 .env 文件
# 根据实际情况修改以下配置：
# - 数据库连接信息
# - Redis 连接信息
# - JWT 密钥
# - 管理员账号密码
```

:::warning 警告
生产环境请使用 `.env.production.example` 创建配置文件，并务必修改所有默认密码和密钥！
:::

### 生成安全密钥

```bash
# 生成 JWT 密钥
python -m commands.generate_keys
```

## 初始化数据库

```bash
# 运行数据库迁移
python -m commands.migrate

# 填充初始数据
python -m commands.seed
```

## IDE 配置

### VS Code

推荐使用 VS Code 作为开发 IDE。

#### 安装扩展

1. **Python**: Microsoft 官方 Python 扩展
2. **Pylance**: Python 语言服务器
3. **Python Test Explorer**: 测试管理
4. **GitLens**: Git 增强
5. **Material Icon Theme**: 图标主题

#### 配置 settings.json

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/server/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

#### 配置 launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "Modules.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "cwd": "${workspaceFolder}/server",
      "envFile": "${workspaceFolder}/server/.env"
    }
  ]
}
```

### PyCharm

#### 配置解释器

1. 打开 `File > Settings > Project > Python Interpreter`
2. 点击齿轮图标，选择 `Add`
3. 选择 `Existing environment`
4. 浏览到 `server/venv/Scripts/python.exe` (Windows) 或 `server/venv/bin/python` (Linux/Mac)

#### 配置运行配置

1. 打开 `Run > Edit Configurations`
2. 点击 `+`，选择 `Flask server` 或 `Python`
3. 配置如下：
   - Script path: `server/run.py`
   - Working directory: `server`
   - Environment variables: 从 `.env` 文件加载

## 启动项目

### 开发模式启动

```bash
# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 启动项目
python run.py
```

### 使用 uvicorn 启动

```bash
uvicorn Modules.main:app --reload --host 0.0.0.0 --port 8000
```

### 验证启动

1. 访问 http://localhost:8000/docs 查看 API 文档
2. 访问 http://localhost:8000/ 查看系统信息
3. 使用默认账号登录测试

## 开发工具

### Git 配置

```bash
# 配置用户名和邮箱
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置默认分支名
git config --global init.defaultBranch main
```

### 代码格式化

```bash
# 安装代码格式化工具
pip install black isort

# 格式化代码
black .
isort .
```

### 代码检查

```bash
# 安装代码检查工具
pip install pylint flake8

# 运行代码检查
pylint Modules/
flake8 Modules/
```

## 常见问题

### 1. Python 版本不兼容

**问题**：提示 Python 版本过低

**解决方案**：

- 升级到 Python 3.9 或更高版本
- 使用 pyenv 管理多个 Python 版本

### 2. 依赖安装失败

**问题**：`pip install` 时出现错误

**解决方案**：

- 升级 pip：`python -m pip install --upgrade pip`
- 使用国内镜像源
- 检查 Python 版本是否符合要求

### 3. 数据库连接失败

**问题**：启动时提示数据库连接失败

**解决方案**：

- 检查 MySQL 服务是否启动
- 确认 `.env` 文件中的数据库配置正确
- 检查数据库用户名和密码
- 确认数据库已创建

### 4. Redis 连接失败

**问题**：提示 Redis 连接失败

**解决方案**：

- 检查 Redis 服务是否启动
- 确认 `.env` 文件中的 Redis 配置正确
- 如果不需要 Redis，可以在配置中禁用

### 5. 端口被占用

**问题**：启动时提示端口 8000 被占用

**解决方案**：

- 修改 `.env` 文件中的 `APP_PORT` 配置
- 或停止占用端口的其他服务

## 下一步

- 📖 阅读 [快速开始](./getting-started.md) 了解基本使用
- 🏗️ 查看 [项目结构说明](./project-structure.md) 了解项目架构
- 💻 学习 [第一个接口开发](./first-api.md) 开始开发
- 🎨 参考 [架构概览](../guides/architecture-overview.md) 了解系统设计

## 相关链接

- [快速开始](./getting-started.md)
- [项目结构说明](./project-structure.md)
- [Python环境配置完整指南](../../server/docs/Python环境配置完整指南.md)
- [环境配置说明](../../server/docs/环境配置说明.md)

---

开发环境搭建完成后，您就可以开始开发了！🎉
