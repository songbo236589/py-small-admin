# Docker 安装 Redis 使用文档

本文档详细介绍如何使用 Docker 安装和配置 Redis，适用于开发和生产环境。

## 目录

- [前言](#前言)
- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [数据持久化](#数据持久化)
- [生产环境配置](#生产环境配置)
- [常用操作](#常用操作)
- [连接测试](#连接测试)
- [故障排查](#故障排查)
- [常见问题](#常见问题)

---

## 前言

### 为什么使用 Docker 安装 Redis

- **环境一致性**：确保开发、测试、生产环境 Redis 版本一致
- **快速部署**：一条命令即可启动 Redis
- **版本管理**：轻松切换不同 Redis 版本
- **隔离性**：不影响系统环境
- **易于维护**：容器化便于备份和迁移

### Redis 版本选择建议

| Redis 版本 | 发布时间 | 特点 | 适用场景 |
|------------|---------|------|---------|
| Redis 3.0 | 2015年 | 基础功能，不支持 ACL | 旧项目兼容 |
| Redis 5.0 | 2018年 | 支持 Stream、模块系统 | 通用场景 |
| Redis 6.0 | 2020年 | 支持 ACL、多线程 IO | 现代应用 |
| Redis 7.0+ | 2022年+ | 性能优化、新特性 | 新项目推荐 |

**本项目推荐**：Redis 7.0 或更高版本

---

## 前置要求

### 1. 安装 Docker

#### Windows

1. 下载 Docker Desktop for Windows
   - 官网：https://www.docker.com/products/docker-desktop/
   - 下载并安装

2. 验证安装
   ```bash
   docker --version
   docker-compose --version
   ```

#### macOS

1. 下载 Docker Desktop for Mac
   - 官网：https://www.docker.com/products/docker-desktop/
   - 下载并安装

2. 验证安装
   ```bash
   docker --version
   docker-compose --version
   ```

#### Linux (Ubuntu/Debian)

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install ca-certificates curl gnupg

# 添加 Docker 官方 GPG 密钥
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 验证安装
docker --version
```

### 2. 检查 Docker 状态

```bash
# 查看 Docker 服务状态
sudo systemctl status docker  # Linux
# 或在 Docker Desktop 中查看状态（Windows/macOS）

# 测试 Docker
docker run hello-world
```

---

## 快速开始

### 方式一：使用 docker run 命令

#### 基础安装（无密码）

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7.0
```

#### 带密码安装

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7.0 \
  --requirepass "123456"
```

### 方式二：使用 docker-compose（推荐）

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  redis:
    image: redis:7.0
    container_name: redis
    ports:
      - "6379:6379"
    command: redis-server --requirepass "123456"
    restart: always
```

启动 Redis：

```bash
docker-compose up -d
```

---

## 详细配置

### 1. 完整配置示例

```bash
docker run -d \
  --name redis \
  --restart always \
  -p 6379:6379 \
  -v /data/redis/data:/data \
  -v /data/redis/conf/redis.conf:/usr/local/etc/redis/redis.conf \
  redis:7.0 \
  redis-server /usr/local/etc/redis/redis.conf \
  --requirepass "123456"
```

### 2. 参数说明

| 参数 | 说明 | 示例 |
|-----|------|------|
| `-d` | 后台运行 | - |
| `--name` | 容器名称 | `--name redis` |
| `--restart` | 重启策略 | `always` / `on-failure` / `no` |
| `-p` | 端口映射 | `-p 6379:6379` |
| `-v` | 数据卷挂载 | `-v /host/path:/container/path` |
| `--requirepass` | 设置密码 | `--requirepass "123456"` |

### 3. 端口映射说明

```bash
# 格式：-p 主机端口:容器端口
-p 6379:6379        # 将主机 6379 端口映射到容器 6379 端口
-p 16379:6379       # 将主机 16379 端口映射到容器 6379 端口（避免端口冲突）
```

### 4. 重启策略说明

| 策略 | 说明 |
|-----|------|
| `no` | 不自动重启（默认） |
| `on-failure[:max-retries]` | 容器异常退出时重启，可指定最大重试次数 |
| `always` | 总是重启，包括手动停止 |
| `unless-stopped` | 总是重启，除非手动停止 |

---

## 数据持久化

### 1. 为什么需要数据持久化

- **防止数据丢失**：容器重启后数据仍然存在
- **数据备份**：可以备份持久化数据
- **迁移方便**：数据卷可以轻松迁移到其他服务器

### 2. RDB 持久化（快照）

#### 启用 RDB 持久化

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v /data/redis/data:/data \
  redis:7.0 \
  --requirepass "123456" \
  --save 900 1 \
  --save 300 10 \
  --save 60 10000
```

#### RDB 配置参数说明

| 参数 | 说明 |
|-----|------|
| `--save 900 1` | 900 秒内至少有 1 个 key 变化时保存 |
| `--save 300 10` | 300 秒内至少有 10 个 key 变化时保存 |
| `--save 60 10000` | 60 秒内至少有 10000 个 key 变化时保存 |

### 3. AOF 持久化（追加日志）

#### 启用 AOF 持久化

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v /data/redis/data:/data \
  redis:7.0 \
  --requirepass "123456" \
  --appendonly yes \
  --appendfsync everysec
```

#### AOF 配置参数说明

| 参数 | 说明 |
|-----|------|
| `--appendonly yes` | 启用 AOF 持久化 |
| `--appendfsync always` | 每次写入都同步（最安全，性能最差） |
| `--appendfsync everysec` | 每秒同步一次（推荐） |
| `--appendfsync no` | 由操作系统决定同步（最快，最不安全） |

### 4. 混合持久化（RDB + AOF）

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v /data/redis/data:/data \
  redis:7.0 \
  --requirepass "123456" \
  --save 900 1 \
  --save 300 10 \
  --save 60 10000 \
  --appendonly yes \
  --appendfsync everysec
```

---

## 生产环境配置

### 1. 使用配置文件

#### 创建 Redis 配置文件

```bash
# 创建配置目录
mkdir -p /data/redis/conf

# 创建配置文件
cat > /data/redis/conf/redis.conf << 'EOF'
# 网络配置
bind 0.0.0.0
port 6379
protected-mode no

# 认证配置
requirepass 123456

# 持久化配置
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# 内存配置
maxmemory 256mb
maxmemory-policy allkeys-lru

# 日志配置
loglevel notice
logfile ""

# 性能配置
tcp-backlog 511
timeout 0
tcp-keepalive 300
EOF
```

#### 使用配置文件启动

```bash
docker run -d \
  --name redis \
  --restart always \
  -p 6379:6379 \
  -v /data/redis/data:/data \
  -v /data/redis/conf/redis.conf:/usr/local/etc/redis/redis.conf \
  redis:7.0 \
  redis-server /usr/local/etc/redis/redis.conf
```

### 2. docker-compose 生产环境配置

```yaml
version: '3.8'

services:
  redis:
    image: redis:7.0
    container_name: redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - ./redis/data:/data
      - ./redis/conf/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "123456", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

networks:
  app-network:
    driver: bridge
```

### 3. 安全配置建议

#### 1. 使用强密码

```bash
# 生成强密码
openssl rand -base64 32

# 在配置文件中使用
requirepass "your-strong-password-here"
```

#### 2. 限制访问

```bash
# 只允许特定 IP 访问（通过防火墙）
# 或使用 Docker 网络隔离
```

#### 3. 禁用危险命令

在 `redis.conf` 中添加：

```bash
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

---

## 常用操作

### 1. 容器管理

#### 启动容器

```bash
docker start redis
```

#### 停止容器

```bash
docker stop redis
```

#### 重启容器

```bash
docker restart redis
```

#### 删除容器

```bash
# 删除容器（保留数据卷）
docker rm redis

# 删除容器和数据卷
docker rm -v redis
```

### 2. 查看容器状态

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 查看容器日志
docker logs redis

# 实时查看日志
docker logs -f redis

# 查看容器详细信息
docker inspect redis
```

### 3. 进入容器

```bash
# 进入容器 shell
docker exec -it redis bash

# 进入容器并连接 Redis
docker exec -it redis redis-cli -a "123456"
```

### 4. 数据备份

#### 备份 RDB 文件

```bash
# 复制数据卷中的文件
docker cp redis:/data/dump.rdb /backup/dump.rdb
```

#### 备份 AOF 文件

```bash
docker cp redis:/data/appendonly.aof /backup/appendonly.aof
```

#### 恢复数据

```bash
# 停止容器
docker stop redis

# 恢复文件
docker cp /backup/dump.rdb redis:/data/dump.rdb

# 启动容器
docker start redis
```

---

## 连接测试

### 1. 使用 redis-cli 连接

#### 连接到本地 Redis

```bash
# 无密码
redis-cli -h 127.0.0.1 -p 6379

# 有密码
redis-cli -h 127.0.0.1 -p 6379 -a "123456"
```

#### 连接到容器内的 Redis

```bash
docker exec -it redis redis-cli -a "123456"
```

### 2. 测试基本操作

```bash
# 连接 Redis
redis-cli -h 127.0.0.1 -p 6379 -a "123456"

# 测试连接
127.0.0.1:6379> PING
PONG

# 设置键值
127.0.0.1:6379> SET test "Hello Redis"
OK

# 获取键值
127.0.0.1:6379> GET test
"Hello Redis"

# 删除键
127.0.0.1:6379> DEL test
(integer) 1

# 查看所有键
127.0.0.1:6379> KEYS *
(empty array)

# 退出
127.0.0.1:6379> EXIT
```

### 3. 使用 Python 连接测试

```python
import redis

# 连接 Redis
r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    password='123456',
    db=0
)

# 测试连接
try:
    result = r.ping()
    print(f"连接成功: {result}")
except Exception as e:
    print(f"连接失败: {e}")

# 测试基本操作
r.set('test', 'Hello Redis')
value = r.get('test')
print(f"获取值: {value.decode('utf-8')}")
```

### 4. 使用 Celery 连接测试

```python
from celery import Celery

# 创建 Celery 应用
app = Celery('test', broker='redis://:123456@127.0.0.1:6379/0')

# 测试连接
try:
    # 尝试发送测试任务
    from celery import current_app
    result = current_app.control.ping()
    print(f"Celery 连接成功: {result}")
except Exception as e:
    print(f"Celery 连接失败: {e}")
```

---

## 故障排查

### 1. 容器无法启动

#### 检查端口占用

```bash
# Windows
netstat -ano | findstr :6379

# Linux/macOS
lsof -i :6379
```

#### 检查容器日志

```bash
docker logs redis
```

#### 检查配置文件

```bash
# 进入容器
docker exec -it redis bash

# 检查配置文件
cat /usr/local/etc/redis/redis.conf
```

### 2. 无法连接 Redis

#### 检查容器状态

```bash
docker ps | grep redis
```

#### 检查端口映射

```bash
docker port redis
```

#### 测试网络连接

```bash
# 测试端口是否开放
telnet 127.0.0.1 6379

# 或使用 nc
nc -zv 127.0.0.1 6379
```

#### 检查防火墙

```bash
# Windows
# 在 Windows Defender 防火墙中添加入站规则

# Linux
sudo ufw allow 6379/tcp

# macOS
# 在系统偏好设置 -> 安全性与隐私 -> 防火墙中添加例外
```

### 3. 认证失败

#### 检查密码配置

```bash
# 查看容器启动命令
docker inspect redis | grep -A 10 "Cmd"
```

#### 测试密码

```bash
# 尝试无密码连接
redis-cli -h 127.0.0.1 -p 6379

# 尝试有密码连接
redis-cli -h 127.0.0.1 -p 6379 -a "123456"
```

### 4. 数据丢失

#### 检查持久化配置

```bash
# 进入容器
docker exec -it redis bash

# 检查 RDB 文件
ls -lh /data/dump.rdb

# 检查 AOF 文件
ls -lh /data/appendonly.aof
```

#### 检查数据卷挂载

```bash
docker inspect redis | grep -A 10 "Mounts"
```

---

## 常见问题

### Q1: Docker 容器重启后数据丢失？

**原因**：没有配置数据持久化，数据只存在于容器内存中。

**解决**：
```bash
# 添加数据卷挂载
-v /data/redis/data:/data

# 启用持久化
--appendonly yes
```

### Q2: 如何升级 Redis 版本？

**步骤**：
1. 备份数据
2. 停止并删除旧容器
3. 使用新版本镜像启动新容器
4. 恢复数据

```bash
# 1. 备份数据
docker cp redis:/data/dump.rdb /backup/

# 2. 停止并删除容器
docker stop redis
docker rm redis

# 3. 使用新版本启动
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v /data/redis/data:/data \
  redis:7.2 \
  --requirepass "123456"

# 4. 恢复数据（如果需要）
docker cp /backup/dump.rdb redis:/data/dump.rdb
```

### Q3: 如何设置 Redis 最大内存？

**方法 1：命令行参数**
```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7.0 \
  --maxmemory 256mb \
  --maxmemory-policy allkeys-lru
```

**方法 2：配置文件**
```bash
# 在 redis.conf 中添加
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Q4: 如何监控 Redis 性能？

**方法 1：使用 redis-cli**
```bash
# 查看 Redis 信息
redis-cli -a "123456" INFO

# 查看内存使用
redis-cli -a "123456" INFO memory

# 查看统计信息
redis-cli -a "123456" INFO stats
```

**方法 2：使用 Redis 命令**
```bash
# 查看连接数
redis-cli -a "123456" CLIENT LIST

# 查看慢查询
redis-cli -a "123456" SLOWLOG GET

# 查看键空间
redis-cli -a "123456" INFO keyspace
```

**方法 3：使用监控工具**
- RedisInsight（官方 GUI 工具）
- Redis Commander（Web 界面）
- Prometheus + Grafana

### Q5: 如何配置 Redis 主从复制？

**主节点配置**：
```bash
docker run -d \
  --name redis-master \
  -p 6379:6379 \
  redis:7.0 \
  --requirepass "123456"
```

**从节点配置**：
```bash
docker run -d \
  --name redis-slave \
  -p 6380:6379 \
  redis:7.0 \
  --slaveof 127.0.0.1 6379 \
  --masterauth "123456" \
  --requirepass "123456"
```

### Q6: 如何配置 Redis 集群？

使用 Redis Cluster 模式：

```bash
# 创建网络
docker network create redis-cluster

# 启动 6 个节点（3 主 3 从）
for port in 7000 7001 7002 7003 7004 7005; do
  docker run -d \
    --name redis-${port} \
    --net redis-cluster \
    -p ${port}:${port} \
    redis:7.0 \
    redis-server --port ${port} --cluster-enabled yes \
    --cluster-config-file nodes-${port}.conf \
    --cluster-node-timeout 5000 \
    --appendonly yes \
    --appendfilename appendonly-${port}.aof \
    --requirepass "123456" \
    --masterauth "123456"
done

# 创建集群
docker exec -it redis-7000 redis-cli -a "123456" --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1
```

---

## 总结

### 最佳实践

1. **使用数据卷持久化**：确保数据不会因容器重启而丢失
2. **设置强密码**：保护 Redis 安全
3. **选择合适的持久化策略**：根据业务需求选择 RDB、AOF 或混合模式
4. **监控 Redis 性能**：定期检查内存使用、连接数等指标
5. **定期备份数据**：防止意外数据丢失
6. **使用合适的 Redis 版本**：新项目推荐使用 Redis 7.0+
7. **配置重启策略**：确保容器异常退出后自动重启

### 推荐配置

**开发环境**：
```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7.0 \
  --requirepass "123456"
```

**生产环境**：
```bash
docker run -d \
  --name redis \
  --restart always \
  -p 6379:6379 \
  -v /data/redis/data:/data \
  -v /data/redis/conf/redis.conf:/usr/local/etc/redis/redis.conf \
  redis:7.0 \
  redis-server /usr/local/etc/redis/redis.conf
```

### 相关资源

- [Redis 官方文档](https://redis.io/documentation)
- [Docker Hub Redis](https://hub.docker.com/_/redis)
- [Redis 配置生成器](https://redis.io/topics/config)
- [Redis 性能优化](https://redis.io/topics/admin)

---

**文档版本**：1.0  
**最后更新**：2026-01-07  
**维护者**：项目团队
