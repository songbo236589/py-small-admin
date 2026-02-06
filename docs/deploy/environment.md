# 环境准备

本文档详细介绍 Py Small Admin 部署前需要准备的环境和依赖。

## 服务器要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 硬盘 | 20 GB | 50 GB+ SSD |
| 网络 | 10 Mbps | 100 Mbps+ |

### 操作系统支持

| 系统 | 版本 | 说明 |
|------|------|------|
| Ubuntu | 20.04 LTS / 22.04 LTS | 推荐 |
| Debian | 10+ / 11+ | 推荐 |
| CentOS | 7+ | 企业用户 |
| Windows Server | 2019+ | 不推荐 |

## 软件依赖

### 核心依赖

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 22.12+ | 前端构建环境 |
| MySQL | 5.7+ / 8.0+ | 数据库 |
| Redis | 5.0+ | 缓存/消息队列 |
| Nginx | 1.18+ | Web 服务器 |

### 可选依赖

| 软件 | 版本 | 用途 |
|------|------|------|
| RabbitMQ | 3.8+ | 消息队列（Celery broker） |
| Docker | 20.10+ | 容器化部署 |
| Docker Compose | 1.29+ | 多容器编排 |

## 详细安装指南

### Ubuntu/Debian 安装

#### 1. 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. 安装 Python 3.11

```bash
# 添加 deadsnakes PPA
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# 设置为默认 Python（可选）
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

#### 3. 安装 Node.js 22

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载配置
source ~/.bashrc

# 安装 Node.js
nvm install 22
nvm use 22
nvm alias default 22
```

#### 4. 安装 MySQL

```bash
# 安装 MySQL 8.0
sudo apt install -y mysql-server mysql-client

# 启动 MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation

# 登录 MySQL
sudo mysql
```

创建数据库和用户：

```sql
CREATE DATABASE py_small_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'py_admin'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON py_small_admin.* TO 'py_admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 5. 安装 Redis

```bash
# 安装 Redis
sudo apt install -y redis-server

# 配置 Redis
sudo vim /etc/redis/redis.conf
# 设置：bind 127.0.0.1
# 设置：requirepass your_redis_password

# 启动 Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### 6. 安装 Nginx

```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### CentOS/RHEL 安装

#### 1. 更新系统

```bash
sudo yum update -y
```

#### 2. 安装 Python 3.11

```bash
# 安装 EPEL
sudo yum install -y epel-release

# 安装 Python 3.11
sudo yum install -y python3.11 python3.11-pip python3.11-devel
```

#### 3. 安装 Node.js 22

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载配置
source ~/.bashrc

# 安装 Node.js
nvm install 22
nvm use 22
nvm alias default 22
```

#### 4. 安装 MySQL

```bash
# 安装 MySQL
sudo yum install -y mysql-server mysql

# 启动 MySQL
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 获取临时密码
sudo grep 'temporary password' /var/log/mysqld.log

# 安全配置
sudo mysql_secure_installation
```

#### 5. 安装 Redis

```bash
sudo yum install -y redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### 6. 安装 Nginx

```bash
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Docker 环境（可选）

### 安装 Docker

```bash
# 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 添加 Docker 仓库
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

### 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

## 环境验证

### 验证 Python

```bash
python3 --version
# 应输出：Python 3.11.x

pip3 --version
# 应输出：pip 23.x+
```

### 验证 Node.js

```bash
node --version
# 应输出：v22.x.x

npm --version
# 应输出：10.x+
```

### 验证 MySQL

```bash
mysql --version
# 应输出：mysql Ver 8.0.x

# 测试连接
mysql -u py_admin -p
```

### 验证 Redis

```bash
redis-cli --version
# 应输出：redis-cli 6.x

# 测试连接
redis-cli ping
# 应输出：PONG
```

### 验证 Nginx

```bash
nginx -v
# 应输出：nginx version: nginx/1.18.x

# 测试服务
curl http://localhost
```

## 防火墙配置

### Ubuntu (UFW)

```bash
# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP
sudo ufw allow 80/tcp

# 允许 HTTPS
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### CentOS (firewalld)

```bash
# 允许 HTTP
sudo firewall-cmd --permanent --add-service=http

# 允许 HTTPS
sudo firewall-cmd --permanent --add-service=https

# 重载防火墙
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```

## SELinux 配置（CentOS）

如果使用 CentOS，可能需要配置 SELinux：

```bash
# 查看当前状态
sudo getenforce

# 临时关闭（用于测试）
sudo setenforce 0

# 永久关闭（不推荐）
sudo vim /etc/selinux/config
# 设置：SELINUX=permissive
```

## 下一步

环境准备完成后，请参考：
- [传统部署](../getting-started/deploy.md) - 传统方式部署
- [Docker 部署](backend/docker.md) - 使用 Docker 部署
- [配置说明](../getting-started/configuration.md) - 详细配置说明
