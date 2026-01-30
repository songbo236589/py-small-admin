# 环境要求

本文档列出了 Py Small Admin 开发所需的环境要求。

## 开发环境

### 必需环境

| 软件    | 最低版本 | 推荐版本 | 说明           |
| ------- | -------- | -------- | -------------- |
| Python  | 3.12+    | 3.12     | 后端开发语言   |
| Node.js | 22.12+   | 22.12    | 前端开发环境   |
| MySQL   | 5.7+     | 8.0+     | 关系型数据库   |
| Redis   | 5.0+     | 7.0+     | 缓存和消息队列 |

### 可选环境

| 软件     | 最低版本 | 推荐版本 | 说明                      |
| -------- | -------- | -------- | ------------------------- |
| RabbitMQ | 3.8+     | 3.12+    | 消息队列（Celery Broker） |
| Docker   | 20.10+   | 24.0+    | 容器化部署                |
| Git      | 2.30+    | 2.43+    | 版本控制                  |

## 系统要求

### 操作系统

- **Windows**: Windows 10/11
- **macOS**: macOS 11+ (Big Sur)
- **Linux**: Ubuntu 20.04+, CentOS 7+

### 硬件要求

| 资源 | 最低配置 | 推荐配置 |
| ---- | -------- | -------- |
| CPU  | 2 核     | 4 核+    |
| 内存 | 4 GB     | 8 GB+    |
| 硬盘 | 20 GB    | 50 GB+   |

### 网络要求

- 稳定的网络连接（用于下载依赖包）
- 如果使用云存储，需要配置相应的网络访问

## 开发工具推荐

### 后端开发工具

- **IDE**: PyCharm Professional / VS Code
- **数据库工具**: Navicat / DBeaver / MySQL Workbench
- **Redis 客户端**: RedisInsight / Another Redis Desktop Manager
- **API 测试**: Postman / Insomnia / Apifox

### 前端开发工具

- **IDE**: VS Code / WebStorm
- **浏览器**: Chrome / Edge（推荐使用 Chrome DevTools）
- **Node.js 管理**: nvm (Node Version Manager)

### 通用工具

- **Git 客户端**: Git Bash / SourceTree / GitHub Desktop
- **终端工具**: Windows Terminal / iTerm2 / Warp
- **Markdown 编辑器**: Typora / VS Code Markdown 插件

## Python 环境安装

### 环境管理方式选择

本项目支持两种 Python 环境管理方式：

| 方式 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| **Conda** | 需要安装 Python 或管理多版本 Python | 包管理完善，跨平台支持好 | 安装包较大 |
| **venv** | 项目已安装 Python，创建独立虚拟环境 | Python 内置，轻量级 | 需要先安装 Python |

#### 使用 Conda 安装 Python

如果没有安装 Python，推荐使用 **Miniconda**（Conda 的最小化安装版本）：

**Miniconda 下载**：
- **Windows**: [Miniconda3 Windows 安装器](https://docs.conda.io/en/latest/miniconda.html#windows-installers)
- **macOS**: [Miniconda3 macOS 安装器](https://docs.conda.io/en/latest/miniconda.html#macosx-installers)
- **Linux**: [Miniconda3 Linux 安装器](https://docs.conda.io/en/latest/miniconda.html#linux-installers)

**配置 Conda 清华镜像源**（加速下载）：

```bash
# 重置 conda 源并配置清华镜像
conda config --remove-key channels
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2/
conda config --set channel_priority strict
conda config --set show_channel_urls yes

# 检查频道配置（确认是清华镜像）
conda config --show channels
```

**使用 Conda 创建环境**：

```bash
# 创建 Python 3.12 环境
conda create -n py-small-admin python=3.12

# 激活环境
# Windows (cmd/Anaconda Prompt):
conda activate py-small-admin

# Linux/macOS:
conda activate py-small-admin
```

#### 使用 venv 创建虚拟环境

如果已安装 Python，可以使用内置的 venv 创建虚拟环境：

**创建虚拟环境**：

```cmd
# Windows (CMD)
python -m venv venv

# Linux/macOS
python3 -m venv venv
```

**激活虚拟环境**：

- **Windows (CMD)** - 推荐：
  ```cmd
  venv\Scripts\activate
  ```

- **Windows (PowerShell)**：
  ```powershell
  # 如果遇到执行策略问题
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

  # 激活（推荐使用批处理文件）
  venv\Scripts\activate.bat

  # 或使用 PowerShell 脚本
  .\venv\Scripts\Activate.ps1
  ```

- **Linux/macOS**：
  ```bash
  source venv/bin/activate
  ```

**验证激活成功**：命令行前面会显示 `(venv)` 前缀

### 升级 pip 和配置镜像源

激活环境后，首先升级 pip：

```cmd
python -m pip install --upgrade pip
```

**配置 pip 清华镜像源**（永久）：

```cmd
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**临时使用镜像源安装**：

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 安装项目依赖

```cmd
pip install -r requirements.txt
```

### 验证安装

```cmd
# 查看 Python 版本
python --version

# 查看已安装的包
pip list
```

## Node.js 环境安装

推荐使用 **nvm** (Node Version Manager) 管理 Node.js 版本，可以轻松安装和切换不同版本的 Node.js。

### 安装 nvm

**Windows (推荐使用 nvm-windows)**:

1. 下载 [nvm-windows](https://github.com/coreybutler/nvm-windows/releases)
2. 运行安装程序 `nvm-setup.exe`
3. 重启终端

**Linux/macOS**:

```bash
# 使用 curl 安装
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 或使用 wget 安装
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重启终端或执行
source ~/.bashrc
```

### 安装 Node.js

安装 nvm 后，使用以下命令安装 Node.js 22.12.0：

```bash
# 列出可用的 Node.js 版本
nvm list available

# 安装 Node.js 22.12.0
nvm install 22.12.0

# 使用指定版本
nvm use 22.12.0

# 设置默认版本
nvm alias default 22.12.0
```

### 配置 npm 镜像源

为加速包下载，建议配置国内镜像源：

```bash
# 永久配置（推荐 npmmirror）
npm config set registry https://registry.npmmirror.com

# 或使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 查看当前镜像源
npm config get registry
```

### 安装 Yarn（可选）

Yarn 是一个快速、可靠、安全的替代 npm 的包管理器。

```bash
# 全局安装 Yarn
npm install -g yarn

# 或安装 tyarn（更快的替代品，支持 pnpm 和 npm）
npm install -g tyarn

# 验证安装
yarn --version
# 或
tyarn --version

# 查看安装位置
which yarn  # Linux/macOS
where yarn  # Windows
```

### 配置 Yarn 镜像源

```bash
# 设置淘宝镜像源
yarn config set registry https://registry.npmmirror.com

# 查看当前镜像源
yarn config get registry
```

### 配置缓存目录（可选）

为防止 C 盘占用过大，可修改 npm 和 Yarn 的缓存目录：

**Windows**:

```cmd
# 设置 npm 缓存目录
npm config set cache "D:\nodejs\npm_cache"

# 设置 Yarn 缓存目录
yarn config set cache-folder "D:\nodejs\yarn_cache"
yarn config set global-folder "D:\nodejs\yarn_global"
```

**Linux/macOS**:

```bash
# 设置 npm 缓存目录
npm config set cache "~/.npm-cache"

# 设置 Yarn 缓存目录
yarn config set cache-folder "~/.yarn-cache"
yarn config set global-folder "~/.yarn-global"
```

### 清理缓存

```bash
# 清理 npm 缓存
npm cache clean --force

# 清理 Yarn 缓存
yarn cache clean
```

### 验证安装

```bash
# 查看 Node.js 版本
node --version

# 查看 npm 版本
npm --version

# 查看已安装的版本
nvm list
```

### nvm 常用命令

```bash
# 查看已安装的 Node.js 版本
nvm list

# 查看可安装的版本
nvm list available

# 安装指定版本
nvm install 22.12.0

# 使用指定版本
nvm use 22.12.0

# 设置默认版本
nvm alias default 22.12.0

# 卸载指定版本
nvm uninstall 22.12.0
```

### Yarn 常用命令

```bash
# 初始化项目
yarn init

# 安装依赖
yarn install
yarn add <package>

# 安装开发依赖
yarn add <package> --dev

# 全局安装
yarn global add <package>

# 升级依赖
yarn upgrade
yarn upgrade <package>

# 移除依赖
yarn remove <package>

# 运行脚本
yarn run <script>

# 查看依赖
yarn list
yarn global list
```

## MySQL 环境安装

本项目使用 MySQL 作为关系型数据库，推荐安装 MySQL 8.0+ 版本。

### Windows 安装

**方式一：使用 MySQL Installer（推荐）**

1. 下载 [MySQL Installer](https://dev.mysql.com/downloads/installer/)
2. 运行安装程序，选择 **Custom** 安装类型
3. 选择 **MySQL Server 8.0.x** 和 **Tools**（包含 MySQL Workbench）
4. 配置 root 密码（请记住密码）
5. 完成安装

**方式二：使用 ZIP 包**

1. 下载 [MySQL ZIP Archive](https://dev.mysql.com/downloads/mysql/)
2. 解压到目标目录（如 `C:\mysql`）
3. 创建配置文件 `my.ini`：
   ```ini
   [mysqld]
   basedir=C:\\mysql
   datadir=C:\\mysql\\data
   port=3306
   character-set-server=utf8mb4
   ```
4. 初始化数据库：
   ```cmd
   cd C:\mysql\bin
   mysqld --initialize --console
   ```
5. 安装服务：
   ```cmd
   mysqld --install
   net start mysql
   ```

### Linux/macOS 安装

**Ubuntu/Debian**：

```bash
# 更新包列表
sudo apt update

# 安装 MySQL Server
sudo apt install mysql-server -y

# 安装 MySQL 客户端
sudo apt install mysql-client -y

# 启动 MySQL 服务
sudo systemctl start mysql

# 设置开机自启
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation
```

**macOS**：

```bash
# 使用 Homebrew 安装
brew install mysql@8.0

# 启动 MySQL 服务
brew services start mysql@8.0

# 设置开机自启
brew services list
```

### 验证安装

```bash
# 查看 MySQL 版本
mysql --version

# 登录 MySQL
mysql -u root -p

# 查看 MySQL 状态
# Linux
sudo systemctl status mysql

# macOS
brew services list
```

### MySQL 配置建议

**配置文件位置**：
- **Windows**: `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
- **Linux**: `/etc/mysql/my.cnf`
- **macOS**: `/usr/local/etc/my.cnf`

**推荐配置**：

```ini
[mysqld]
# 字符集
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 连接数
max_connections=200

# 缓存
innodb_buffer_pool_size=256M
query_cache_size=32M

# 日志
slow_query_log=1
long_query_time=2

# 时区
default-time-zone='+08:00'
```

### 常用管理命令

```bash
# 启动 MySQL
# Windows
net start mysql
# Linux
sudo systemctl start mysql
# macOS
brew services start mysql@8.0

# 停止 MySQL
# Windows
net stop mysql
# Linux
sudo systemctl stop mysql
# macOS
brew services stop mysql@8.0

# 重启 MySQL
# Windows
net restart mysql
# Linux
sudo systemctl restart mysql
# macOS
brew services restart mysql@8.0
```

### 使用 Docker 运行 MySQL

如果已安装 Docker，可以使用 Docker 运行 MySQL。

#### MySQL Docker 环境变量说明

| 环境变量 | 作用 | 是否必需 | 说明 |
|---------|------|---------|------|
| `MYSQL_ROOT_PASSWORD` | 设置 **root** 用户密码 | **必需** | root 用户名固定，无需指定 |
| `MYSQL_ROOT_HOST` | 设置 root 允许连接的主机 | 可选 | 默认 `localhost`，设 `%` 允许所有主机 |
| `MYSQL_DATABASE` | 自动创建数据库 | 可选 | 创建后自动授权给新用户 |
| `MYSQL_USER` | 创建普通用户 | 可选 | 不能是 "root"，需配合 `MYSQL_PASSWORD` |
| `MYSQL_PASSWORD` | 普通用户密码 | 可选 | 需配合 `MYSQL_USER` 使用 |

#### 方式一：仅使用 root 用户（简单）

```bash
# 运行 MySQL（仅 root 用户）
docker run -d --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_ROOT_HOST=% \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# 连接测试
docker exec -it mysql mysql -uroot -p
```

#### 方式二：创建普通用户（推荐，更安全）

```bash
# 运行 MySQL（root + 普通用户）
docker run -d --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_ROOT_HOST=% \
  -e MYSQL_DATABASE=fastapi_db \
  -e MYSQL_USER=fastapi_user \
  -e MYSQL_PASSWORD=user_password \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# 使用 root 连接（管理用）
docker exec -it mysql mysql -uroot -p

# 使用普通用户连接（应用用）
docker exec -it mysql mysql -ufastapi_user -p fastapi_db
```

#### 使用 Docker Compose

**仅 root 用户**：

```yaml
# docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_ROOT_HOST: "%"
    volumes:
      - mysql-data:/var/lib/mysql
volumes:
  mysql-data:
```

**root + 普通用户（推荐）**：

```yaml
# docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      # root 用户（管理用）
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_ROOT_HOST: "%"
      # 普通用户（应用连接用）
      MYSQL_DATABASE: fastapi_db
      MYSQL_USER: fastapi_user
      MYSQL_PASSWORD: user_password
      TZ: Asia/Shanghai
    volumes:
      - mysql-data:/var/lib/mysql
volumes:
  mysql-data:
```

启动：`docker compose up -d`

#### 安全性建议

| 场景 | 推荐配置 | 说明 |
|------|---------|------|
| **生产环境** | 创建普通用户，应用使用普通用户连接 | root 仅用于数据库管理 |
| **开发环境** | 可仅使用 root | 方便开发调试 |
| **容器内应用** | 使用普通用户 | 避免权限过大 |

#### 常用管理命令

```bash
# 启动容器
docker start mysql

# 停止容器
docker stop mysql

# 重启容器
docker restart mysql

# 查看日志
docker logs -f mysql

# 进入容器
docker exec -it mysql bash

# 连接 MySQL
docker exec -it mysql mysql -uroot -p

# 删除容器
docker rm -f mysql

# 删除数据卷（慎用！会删除数据）
docker volume rm mysql-data
```

## Redis 环境安装

### Windows 安装

1. 下载 [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
2. 解压到目标目录（如 `C:\redis`）
3. 运行 `redis-server.exe` 启动服务

### Linux 安装

```bash
# Ubuntu/Debian
sudo apt install redis-server -y

# 启动 Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### macOS 安装

```bash
brew install redis
brew services start redis
```

### 验证安装

```bash
# 启动 Redis 客户端
redis-cli

# 测试连接
ping
# 应返回 PONG
```

### 常用管理命令

```bash
# 启动 Redis
# Windows
redis-server

# Linux
sudo systemctl start redis

# macOS
brew services start redis

# 停止 Redis
# Linux
sudo systemctl stop redis

# macOS
brew services stop redis
```

### 使用 Docker 运行 Redis

如果已安装 Docker，可以使用 Docker 运行 Redis：

```bash
# 运行 Redis
docker run -d --name redis \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7.0 \
  redis-server --appendonly yes

# 启动容器
docker start redis

# 停止容器
docker stop redis

# 查看日志
docker logs -f redis

# 使用 redis-cli 连接
docker exec -it redis redis-cli
```

**使用 Docker Compose**：

```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7.0
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
volumes:
  redis-data:
```

启动：`docker compose up -d`

## Docker 环境安装

Docker 是一个开源的容器化平台，用于开发、交付和运行应用程序。

### Windows 安装

**要求**：Windows 10/11 专业版或企业版（64位）

**架构选择**：

下载时需要选择处理器架构：

| 架构   | 适用场景                                 | 选择建议         |
| ------ | ---------------------------------------- | ---------------- |
| AMD64  | Intel 或 AMD 处理器（大多数 Windows 电脑） | **99% 用户选择** |
| ARM64  | ARM 架构处理器（如 Snapdragon）           | 少数 Windows 笔电 |

**如何判断您的架构**：

```powershell
# 在 PowerShell 中运行
wmic cpu get Name
```

或：

```powershell
# 查看处理器架构
$env:PROCESSOR_ARCHITECTURE
```

- 输出 `AMD64` → 选择 **AMD64** 版本
- 输出 `ARM64` → 选择 **ARM64** 版本

**使用 Docker Desktop（推荐）**：

1. 下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)（根据上述架构选择对应版本）
2. 运行安装程序
3. 安装时确保启用以下选项：
   - **Use WSL 2 based engine**（推荐）
   - **Add shortcut to desktop**
4. 完成安装后重启计算机
5. 启动 Docker Desktop

**启用 WSL 2 后端**（如果未启用）：

```powershell
# 以管理员身份运行 PowerShell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启计算机后，设置 WSL 2 为默认版本
wsl --set-default-version 2
```

### Linux 安装

**Ubuntu/Debian**：

```bash
# 更新包索引
sudo apt update

# 安装依赖
sudo apt install -y ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组（免 sudo）
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

**CentOS/RHEL**：

```bash
# 安装依赖
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
```

### macOS 安装

**使用 Homebrew（推荐）**：

```bash
# 安装 Docker Desktop
brew install --cask docker

# 启动 Docker Desktop（从应用程序启动）
```

**或使用安装包**：

1. 下载 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
2. 打开 `.dmg` 文件
3. 将 Docker 拖到应用程序文件夹
4. 从应用程序启动 Docker

### 验证安装

```bash
# 查看 Docker 版本
docker --version

# 查看 Docker Compose 版本
docker compose version

# 运行测试容器
docker run hello-world

# 查看 Docker 信息
docker info
```

### Docker 镜像加速（可选）

为加速镜像下载，建议配置国内镜像源：

**Docker Desktop（Windows/macOS）**：

1. 打开 Docker Desktop
2. 进入 **Settings** → **Docker Engine**
3. 添加以下配置：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

4. 点击 **Apply & Restart**

**Linux**：

```bash
# 创建或编辑配置文件
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF

# 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Docker Compose 常用命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 进入容器
docker compose exec <service> bash
```

### 常用管理命令

```bash
# 启动 Docker
# Linux
sudo systemctl start docker

# macOS/Windows: 启动 Docker Desktop

# 停止 Docker
# Linux
sudo systemctl stop docker

# macOS/Windows: 关闭 Docker Desktop

# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看镜像列表
docker images

# 清理未使用的资源
docker system prune -a
```

## RabbitMQ 环境安装

RabbitMQ 是一个开源的消息代理软件，用作 Celery 的消息队列（Broker）。

### Windows 安装

**使用 Chocolatey（推荐）**：

```powershell
# 安装 Chocolatey（如果未安装）
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 安装 RabbitMQ
choco install rabbitmq -y
```

**使用安装包**：

1. 下载 [RabbitMQ Installer](https://www.rabbitmq.com/download.html)
2. 运行安装程序
3. 安装完成后，RabbitMQ 服务会自动启动

**启用管理插件**：

```powershell
# 以管理员身份运行
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12\sbin"
rabbitmq-plugins.bat enable rabbitmq_management
```

### Linux 安装

**Ubuntu/Debian**：

```bash
# 添加 Erlang 仓库（RabbitMQ 依赖）
sudo apt-get install -y erlang

# 添加 RabbitMQ 仓库
curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.deb.sh | sudo bash

# 安装 RabbitMQ
sudo apt-get install -y rabbitmq-server

# 启动 RabbitMQ
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# 启用管理插件
sudo rabbitmq-plugins enable rabbitmq_management

# 添加管理员用户
sudo rabbitmqctl add_user admin password123
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

# 删除默认 guest 用户（可选）
sudo rabbitmqctl delete_user guest
```

**CentOS/RHEL**：

```bash
# 安装 Erlang
sudo yum install -y epel-release
sudo yum install -y erlang

# 添加 RabbitMQ 仓库
curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.rpm.sh | sudo bash

# 安装 RabbitMQ
sudo yum install -y rabbitmq-server

# 启动 RabbitMQ
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# 启用管理插件
sudo rabbitmq-plugins enable rabbitmq_management

# 添加管理员用户
sudo rabbitmqctl add_user admin password123
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

### macOS 安装

```bash
# 使用 Homebrew 安装
brew install rabbitmq

# 启动 RabbitMQ
brew services start rabbitmq

# 启用管理插件
rabbitmq-plugins enable rabbitmq_management

# 添加管理员用户
rabbitmqctl add_user admin password123
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

### 验证安装

```bash
# 查看 RabbitMQ 状态
# Linux/macOS
sudo systemctl status rabbitmq-server  # Linux
brew services list                     # macOS

# Windows
# 检查服务列表中的 RabbitMQ 服务
```

**访问管理界面**：

打开浏览器访问：`http://localhost:15672`

- 默认用户：`admin`（或 `guest`）
- 默认密码：`password123`（或 `guest`）

### 常用管理命令

```bash
# 启动 RabbitMQ
# Windows
net start RabbitMQ

# Linux
sudo systemctl start rabbitmq-server

# macOS
brew services start rabbitmq

# 停止 RabbitMQ
# Windows
net stop RabbitMQ

# Linux
sudo systemctl stop rabbitmq-server

# macOS
brew services stop rabbitmq

# 重启 RabbitMQ
# Windows
net restart RabbitMQ

# Linux
sudo systemctl restart rabbitmq-server

# macOS
brew services restart rabbitmq

# 查看队列状态
rabbitmqctl list_queues

# 查看连接状态
rabbitmqctl list_connections

# 查看用户列表
rabbitmqctl list_users

# 添加新用户
rabbitmqctl add_user username password

# 设置用户权限
rabbitmqctl set_permissions -p / username ".*" ".*" ".*"

# 删除用户
rabbitmqctl delete_user username
```

### 使用 Docker 运行 RabbitMQ

如果已安装 Docker，可以使用 Docker 运行 RabbitMQ：

```bash
# 运行 RabbitMQ
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=password123 \
  rabbitmq:3.12-management

# 启动容器
docker start rabbitmq

# 停止容器
docker stop rabbitmq

# 查看日志
docker logs -f rabbitmq
```

访问管理界面：`http://localhost:15672`，用户名 `admin`，密码 `password123`。

## Docker 一键部署

如果你想快速启动整个项目（包括后端服务、数据库、缓存、消息队列等），可以使用项目提供的 Docker Compose 配置进行一键部署。

### 前置条件

- 已安装 Docker 和 Docker Compose
- 已克隆项目到本地

### 快速启动

```bash
# 1. 进入 Docker 配置目录
cd server/docker

# 2. 准备 Docker 服务配置
cp .env.example .env
# 修改密码（可选）

# 3. 准备应用配置
cd ..
cp .env.example .env
# 修改应用配置，特别是 Docker 环境的主机名：
# - DB_CONNECTIONS__MYSQL__HOST=mysql
# - DB_REDIS__DEFAULT__HOST=redis
# - CELERY_BROKER_URL 中的主机改为 rabbitmq

# 4. 启动所有服务
cd docker
docker-compose up -d

# 5. 查看服务状态
docker-compose ps

# 6. 查看服务日志
docker-compose logs -f
```

### 服务访问

| 服务 | 地址 | 用户名 | 密码 | 说明 |
|------|------|--------|------|------|
| **FastAPI** | http://localhost:8009 | - | - | 后端 API 服务 |
| **API 文档** | http://localhost:8009/docs | - | - | Swagger UI |
| **MySQL** | localhost:3306 | root | root123456 | 数据库 |
| **MySQL** | localhost:3306 | fastapi_user | fastapi_password | 应用用户 |
| **Redis** | localhost:6379 | - | redis123456 | 缓存 |
| **RabbitMQ** | http://localhost:15672 | admin | admin123 | 管理界面 |
| **Flower** | http://localhost:5555 | admin | 123456 | Celery 监控 |

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启指定服务
docker-compose restart mysql

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec fastapi bash

# 删除所有容器和数据卷（完全重置）
docker-compose down -v
```

### 镜像重建

当代码或配置修改后，需要重新构建镜像：

```bash
# 停止所有服务
docker-compose down

# 重新构建镜像（不使用缓存）
docker-compose build --no-cache

# 启动所有服务
docker-compose up -d

# 查看日志确认启动成功
docker-compose logs -f
```

**常见需要重建的场景**：
- 修改了 `Dockerfile`
- 修改了 `requirements.txt`（新增/删除依赖）
- 修改了应用代码
- 修改了 `server/.env` 配置文件

### 配置说明

Docker 环境使用**两个独立的配置文件**：

| 配置文件 | 路径 | 用途 |
|----------|------|------|
| **Docker 服务配置** | `server/docker/.env` | MySQL/Redis/RabbitMQ 启动参数 |
| **应用配置** | `server/.env` | 应用连接数据库、缓存、消息队列的参数 |

**重要配置项**：

```bash
# docker/.env - Docker 服务配置
PROJECT_NAME=py-small-admin        # 容器名前缀
MYSQL_ROOT_PASSWORD=root123456     # MySQL root 密码
REDIS_PASSWORD=redis123456          # Redis 密码
RABBITMQ_DEFAULT_USER=admin         # RabbitMQ 用户
RABBITMQ_DEFAULT_PASS=admin123      # RabbitMQ 密码

# 端口配置（可避免多实例端口冲突）
HOST_PORT_MYSQL=3306
HOST_PORT_REDIS=6379
HOST_PORT_RABBITMQ_AMQP=5672
HOST_PORT_RABBITMQ_MGMT=15672
HOST_PORT_FASTAPI=8009
HOST_PORT_FLOWER=5555
```

### 多实例部署

如需在同一台宿主机运行多个实例：

```bash
# 实例 1：开发环境（默认）
cp .env.example .env.dev
docker-compose -p dev -f docker-compose.yml --env-file .env.dev up -d

# 实例 2：测试环境
cp .env.example .env.test
# 修改 .env.test：
#   PROJECT_NAME=py-small-admin-test
#   HOST_PORT_MYSQL=3307
#   HOST_PORT_FASTAPI=8010
docker-compose -p test -f docker-compose.yml --env-file .env.test up -d
```

## Git 环境安装

Git 是一个分布式版本控制系统，用于代码版本管理和协作。

### Windows 安装

**使用安装包（推荐）**：

1. 下载 [Git for Windows](https://git-scm.com/download/win)
2. 运行安装程序
3. 安装时推荐配置：
   - **默认编辑器**：选择 VS Code（如果已安装）
   - **PATH 环境**：选择 **Git from the command line and also from 3rd-party software**
   - **HTTPS 传输后端**：选择 **Use the native Windows Secure Channel library**
   - **行结束符转换**：选择 **Checkout Windows-style, commit Unix-style line endings**
   - **终端模拟器**：选择 **Use MinTTY**（默认）
4. 完成安装

**验证安装**：

```cmd
git --version
```

**使用 Chocolatey**：

```powershell
choco install git -y
```

### Linux 安装

**Ubuntu/Debian**：

```bash
sudo apt update
sudo apt install git -y
```

**CentOS/RHEL**：

```bash
sudo yum install git -y
```

**Fedora**：

```bash
sudo dnf install git -y
```

### macOS 安装

**使用 Homebrew（推荐）**：

```bash
brew install git
```

**或使用安装包**：

1. 下载 [Git for macOS](https://git-scm.com/download/mac)
2. 运行安装程序

**注意**：macOS 可能已预装 Git，可通过 `git --version` 检查版本。

### 验证安装

```bash
# 查看 Git 版本
git --version

# 查看 Git 配置
git config --list
```

### Git 初始配置

安装完成后，建议进行基本配置：

```bash
# 设置用户名
git config --global user.name "Your Name"

# 设置邮箱
git config --global user.email "your.email@example.com"

# 设置默认分支名称
git config --global init.defaultBranch main

# 设置凭证存储（避免每次输入密码）
git config --global credential.helper store

# 或使用缓存（临时记住密码 1 小时）
git config --global credential.helper 'cache --timeout=3600'

# 查看配置
git config --list
```

### 常用 Git 命令

```bash
# 克隆仓库
git clone https://github.com/songbo236589/py-small-admin.git

# 查看状态
git status

# 查看分支
git branch

# 切换分支
git checkout main

# 创建并切换到新分支
git checkout -b feature-branch

# 添加文件到暂存区
git add .
git add filename

# 提交更改
git commit -m "提交信息"

# 推送到远程
git push origin main

# 拉取最新代码
git pull origin main

# 查看提交历史
git log

# 查看文件差异
git diff

# 合并分支
git merge feature-branch

# 删除分支
git branch -d feature-branch
```

### 配置 SSH 密钥（可选）

如需使用 SSH 方式访问 Git 仓库：

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 复制公钥到 Git 平台（GitHub/GitLab/Gitee）
```

**Windows (PowerShell)**：

```powershell
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 查看公钥
cat $env:USERPROFILE\.ssh\id_ed25519.pub
```

### 常见问题

**Q: git 命令找不到？**

A: 确保 Git 已正确安装并添加到系统 PATH。

- **Windows**: 重启终端或计算机
- **Linux/macOS**: 执行 `source ~/.bashrc` 或重启终端

**Q: 如何设置代理？**

A:

```bash
# 设置 HTTP 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy https://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

**Q: 如何取消凭证存储？**

A:

```bash
# 取消凭证存储
git config --global --unset credential.helper

# Windows 清除凭证管理器
# 控制面板 → 凭证管理器 → Windows 凭证 → 删除 git:https://github.com 相关凭证
```

## 常用管理命令

### Conda 环境管理

```bash
# 查看所有环境
conda env list

# 停用环境
conda deactivate

# 删除环境
conda remove -n py-small-admin --all

# 导出环境配置
conda env export > environment.yml

# 从配置文件创建环境
conda env create -f environment.yml
```

### venv 环境管理

```cmd
# 退出虚拟环境
deactivate

# 删除虚拟环境（Windows）
rd /s /q venv

# 删除虚拟环境（Linux/macOS）
rm -rf venv

# 更新 requirements.txt
pip freeze > requirements.txt
```

## 故障排除

### 关闭所有 Python 进程

如果遇到端口占用或文件锁定问题：

```cmd
taskkill /f /im python.exe
```

### Conda 相关问题

**清理缓存**：

```bash
# 清理缓存（损坏的包、临时文件）
conda clean -y --all
```

**解除锁文件（Windows）**：

```cmd
REM 复制到终端执行，将"你的用户名"替换为实际用户名
rd /s /q "C:\Users\你的用户名\.conda\locks"
md "C:\Users\你的用户名\.conda\locks"
```

### venv 相关问题

**问题：PowerShell 无法激活虚拟环境**

症状：执行 `venv\Scripts\activate` 后没有 `(venv)` 前缀

解决方案：

1. **推荐：使用 CMD 而不是 PowerShell**
2. **PowerShell 中使用批处理文件**：`venv\Scripts\activate.bat`
3. **检查激活状态**：`where python` 应指向 venv 目录

**问题：pip 安装速度慢或失败**

解决方案：

1. 使用清华镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
2. 配置永久镜像源：`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`
3. 升级 pip 后重试：`python -m pip install --upgrade pip`

**问题：VSCode 无法识别虚拟环境**

解决方案：

1. 重新加载窗口：`Ctrl+Shift+P` → `Developer: Reload Window`
2. 手动选择解释器：`Ctrl+Shift+P` → `Python: Select Interpreter` → 选择 `./venv/Scripts/python.exe`

### 常见问题

**Q: conda 命令找不到？**

A: 确保 Conda 已正确安装并添加到系统 PATH。

- **Windows**: 推荐使用 **Anaconda Prompt**（开始菜单搜索），或使用 **cmd**（命令提示符）
- **PowerShell**: 需要先执行 `conda init powershell` 并重启终端
- **macOS/Linux**: 确保终端已初始化，执行 `conda init bash`

**Q: 下载速度慢？**

A: 确保已配置清华镜像源。
- Conda: 使用 `conda config --show channels` 检查配置
- pip: 使用 `pip config list` 检查配置

**Q: 虚拟环境激活失败？**

A:
- **Windows**: 使用 **Anaconda Prompt** 或 **cmd**，不要使用 PowerShell（除非已初始化）
- **macOS/Linux**: 确保已执行 `conda init bash` 或 `source ~/.bashrc`
