# 故障排查指南

本指南将详细介绍 Py Small Admin 项目的常见问题及解决方案，帮助您快速定位和解决问题。

## 故障排查流程

### 排查步骤

```
1. 问题确认
   ↓
2. 信息收集
   ↓
3. 问题定位
   ↓
4. 解决方案
   ↓
5. 验证修复
   ↓
6. 预防措施
```

### 信息收集清单

| 类别     | 收集内容                       |
| -------- | ------------------------------ |
| 系统信息 | 操作系统版本、CPU、内存、磁盘  |
| 应用信息 | 应用版本、配置文件、日志       |
| 错误信息 | 错误消息、堆栈跟踪、错误码     |
| 环境信息 | 网络状态、依赖服务、数据库连接 |

## 应用层问题

### 1. 应用无法启动

#### 问题现象

```bash
# 启动应用时出现错误
python run.py
# Traceback (most recent call last):
#   File "run.py", line 5, in <module>
#     from Modules.main import app
# ImportError: No module named 'Modules'
```

#### 可能原因

- Python 路径配置错误
- 虚拟环境未激活
- 依赖包未安装
- 模块路径问题

#### 解决方案

```bash
# 1. 检查虚拟环境
which python
# 应该显示虚拟环境的 python 路径

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 检查依赖
pip list | grep fastapi

# 4. 重新安装依赖
pip install -r requirements.txt

# 5. 检查 Python 路径
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

### 2. 端口被占用

#### 问题现象

```bash
# 启动应用时提示端口被占用
# OSError: [Errno 98] Address already in use
```

#### 可能原因

- 其他进程占用了相同端口
- 应用未正常关闭
- 端口配置错误

#### 解决方案

```bash
# 1. 查找占用端口的进程
sudo lsof -i :8000

# 或使用 netstat
sudo netstat -tulpn | grep :8000

# 2. 杀死进程
sudo kill -9 <PID>

# 3. 修改应用端口
# 在 .env 文件中修改
APP_PORT=8001

# 4. 检查防火墙
sudo ufw status
```

### 3. 数据库连接失败

#### 问题现象

```bash
# 应用启动时数据库连接失败
# OperationalError: (2003, "Can't connect to MySQL server on 'localhost'")
```

#### 可能原因

- MySQL 服务未启动
- 连接配置错误
- 网络连接问题
- 防火墙阻止

#### 解决方案

```bash
# 1. 检查 MySQL 服务状态
sudo systemctl status mysql

# 2. 启动 MySQL
sudo systemctl start mysql

# 3. 检查连接配置
cat .env | grep DB_

# 4. 测试数据库连接
mysql -u py_admin -p -h localhost py_small_admin

# 5. 检查防火墙
sudo ufw allow 3306/tcp

# 6. 检查 MySQL 监听地址
sudo netstat -tulpn | grep mysql
```

### 4. Redis 连接失败

#### 问题现象

```bash
# Redis 连接失败
# redis.exceptions.ConnectionError: Error connecting to Redis
```

#### 可能原因

- Redis 服务未启动
- 连接配置错误
- Redis 密码错误

#### 解决方案

```bash
# 1. 检查 Redis 服务状态
sudo systemctl status redis

# 2. 启动 Redis
sudo systemctl start redis

# 3. 测试 Redis 连接
redis-cli ping
# 应该返回 PONG

# 4. 检查 Redis 配置
redis-cli CONFIG GET requirepass

# 5. 检查连接配置
cat .env | grep REDIS
```

### 5. API 响应慢

#### 问题现象

```bash
# API 响应时间过长
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/users
# time_namelookup: 0.003s
# time_connect: 0.005s
# time_appconnect: 0.000s
# time_pretransfer: 0.005s
# time_starttransfer: 2.500s
# time_total: 2.505s
```

#### 可能原因

- 数据库查询慢
- 网络延迟
- 资源不足
- 代码性能问题

#### 解决方案

```python
# 1. 启用慢查询日志
# MySQL 配置
slow_query_log = 1
long_query_time = 1

# 2. 分析慢查询
# 查看慢查询日志
sudo tail -f /var/log/mysql/mysql-slow.log

# 3. 使用 EXPLAIN 分析查询
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

# 4. 添加索引
CREATE INDEX idx_user_email ON users(email);

# 5. 优化代码
# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()
```

## Celery 问题

### 1. Worker 无法启动

#### 问题现象

```bash
# 启动 Celery Worker 时出错
celery -A config.celery_config worker -l info
# Error: Unable to load celery application module
```

#### 可能原因

- 配置文件路径错误
- 依赖包未安装
- Broker 连接失败

#### 解决方案

```bash
# 1. 检查配置文件
ls -la config/celery_config.py

# 2. 检查 Python 路径
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# 3. 测试配置文件
python -c "from config.celery_config import celery_app; print(celery_app)"

# 4. 检查依赖
pip list | grep celery

# 5. 测试 Broker 连接
redis-cli ping
```

### 2. 任务不执行

#### 问题现象

```python
# 任务已提交但不执行
task = send_email_task.delay('test@example.com', '测试', '内容')
print(task.status)  # PENDING
```

#### 可能原因

- Worker 未运行
- 队列配置错误
- 任务路由错误

#### 解决方案

```bash
# 1. 检查 Worker 状态
celery -A config.celery_config inspect active

# 2. 检查队列长度
redis-cli LLEN celery

# 3. 查看任务状态
celery -A config.celery_config inspect registered

# 4. 检查任务路由
celery -A config.celery_config inspect active_queues

# 5. 查看 Worker 日志
tail -f /var/log/py-small-admin/celery.log
```

### 3. 任务失败重试

#### 问题现象

```python
# 任务反复失败重试
# Task raised exception: ConnectionError('Connection refused')
```

#### 可能原因

- 依赖服务不可用
- 任务逻辑错误
- 资源不足

#### 解决方案

```python
# 1. 查看任务错误信息
from celery.result import AsyncResult
result = AsyncResult(task_id)
print(result.traceback)

# 2. 检查依赖服务
# 检查数据库连接
mysql -u py_admin -p -h localhost py_small_admin

# 检查 Redis 连接
redis-cli ping

# 3. 调整重试策略
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError,)
)
def my_task(self, data):
    try:
        return process(data)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

# 4. 查看失败任务
celery -A config.celery_config inspect failed
```

### 4. 队列积压

#### 问题现象

```bash
# 队列任务积压严重
redis-cli LLEN celery
# 10000
```

#### 可能原因

- Worker 数量不足
- 任务执行时间长
- 任务产生速度快

#### 解决方案

```bash
# 1. 增加 Worker 数量
celery -A config.celery_config worker -l info -c 8

# 2. 启动临时 Worker
celery -A config.celery_config worker -l info -n temp_worker@%h -c 4

# 3. 优化任务性能
# 使用批量处理
@shared_task
def batch_process(items):
    for item in items:
        process(item)

# 4. 使用优先级队列
celery -A config.celery_config worker -l info -Q high_priority

# 5. 清空队列（谨慎使用）
celery -A config.celery_config purge
```

## 性能问题

### 1. 内存泄漏

#### 问题现象

```bash
# 应用内存持续增长
top -p $(pgrep -f "python run.py")
# PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
# 12345 deploy    20   0  1024M   800M   100M R  50.0  20.0   0:10.00 python
```

#### 可能原因

- 循环引用
- 缓存未清理
- 全局变量累积

#### 解决方案

```python
# 1. 使用内存分析工具
pip install memory_profiler
python -m memory_profiler run.py

# 2. 检查循环引用
import gc
gc.collect()
print(len(gc.get_objects()))

# 3. 优化缓存
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=3600)

# 4. 使用上下文管理器
class DatabaseConnection:
    def __enter__(self):
        self.conn = create_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

# 5. 定期清理
@shared_task
def cleanup_task():
    """定期清理任务"""
    cache.clear()
    gc.collect()
```

### 2. CPU 使用率过高

#### 问题现象

```bash
# CPU 使用率持续高位
top -p $(pgrep -f "python run.py")
# %CPU  95.0
```

#### 可能原因

- 死循环
- 密集计算
- 无限重试

#### 解决方案

```python
# 1. 使用性能分析工具
pip install py-spy
sudo py-spy top --pid $(pgrep -f "python run.py")

# 2. 优化算法
# 使用更高效的算法
# 避免嵌套循环

# 3. 使用异步
import asyncio

async def process_data():
    tasks = [async_task(item) for item in items]
    await asyncio.gather(*tasks)

# 4. 添加超时
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 秒超时
```

### 3. 磁盘空间不足

#### 问题现象

```bash
# 磁盘空间不足
df -h
# /dev/sda1      100G   95G     5G  95% /
```

#### 可能原因

- 日志文件过大
- 上传文件未清理
- 缓存文件过多

#### 解决方案

```bash
# 1. 清理日志文件
sudo logrotate -f /etc/logrotate.d/py-small-admin

# 2. 清理旧日志
find /var/log/py-small-admin -name "*.log.*" -mtime +30 -delete

# 3. 清理上传文件
find /path/to/uploads -mtime +30 -delete

# 4. 清理缓存
find /tmp -name "*.cache" -delete

# 5. 清理 Docker 镜像
docker system prune -a

# 6. 查找大文件
find / -type f -size +100M 2>/dev/null
```

## 网络问题

### 1. 无法访问 API

#### 问题现象

```bash
# 无法访问 API
curl http://localhost:8000/api/users
# curl: (7) Failed to connect to localhost port 8000: Connection refused
```

#### 可能原因

- 应用未启动
- 端口未开放
- 防火墙阻止

#### 解决方案

```bash
# 1. 检查应用状态
sudo systemctl status py-small-admin

# 2. 检查端口监听
sudo netstat -tulpn | grep :8000

# 3. 检查防火墙
sudo ufw status
sudo ufw allow 8000/tcp

# 4. 检查 Nginx 配置
sudo nginx -t
sudo systemctl restart nginx

# 5. 检查网络连接
ping localhost
telnet localhost 8000
```

### 2. SSL 证书问题

#### 问题现象

```bash
# SSL 证书错误
curl https://example.com/api/users
# curl: (60) SSL certificate problem: unable to get local issuer certificate
```

#### 可能原因

- 证书过期
- 证书配置错误
- 证书链不完整

#### 解决方案

```bash
# 1. 检查证书有效期
openssl x509 -in /path/to/cert.pem -noout -dates

# 2. 续期证书
sudo certbot renew

# 3. 检查证书配置
sudo nginx -t

# 4. 重启 Nginx
sudo systemctl restart nginx

# 5. 验证证书
openssl s_client -connect example.com:443 -servername example.com
```

## 数据库问题

### 1. 慢查询

#### 问题现象

```bash
# 查询执行时间长
# 查询耗时超过 10 秒
```

#### 可能原因

- 缺少索引
- 查询语句不优化
- 数据量过大

#### 解决方案

```sql
-- 1. 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- 2. 分析慢查询
-- 查看慢查询日志
SELECT * FROM mysql.slow_log
WHERE start_time > NOW() - INTERVAL 1 DAY;

-- 3. 使用 EXPLAIN 分析
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 4. 添加索引
CREATE INDEX idx_user_email ON users(email);

-- 5. 优化查询
-- 避免使用 SELECT *
-- 使用 LIMIT 限制返回行数
-- 使用 JOIN 代替子查询
```

### 2. 连接池耗尽

#### 问题现象

```python
# 数据库连接错误
# sqlalchemy.exc.PoolError: Connection pool exhausted
```

#### 可能原因

- 连接未关闭
- 连接池配置过小
- 并发请求过多

#### 解决方案

```python
# 1. 检查连接池配置
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)

# 2. 使用上下文管理器
with engine.connect() as conn:
    result = conn.execute(query)

# 3. 检查连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';

# 4. 调整 MySQL 配置
max_connections = 200
wait_timeout = 600
```

### 3. 数据库锁

#### 问题现象

```python
# 查询超时
# sqlalchemy.exc.OperationalError: (1205, 'Lock wait timeout exceeded')
```

#### 可能原因

- 长事务未提交
- 死锁
- 锁等待超时

#### 解决方案

```sql
-- 1. 查看当前锁
SHOW ENGINE INNODB STATUS;

-- 2. 查看锁等待
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- 3. 杀死锁定的进程
KILL <process_id>;

-- 4. 优化事务
-- 缩短事务时间
-- 避免在事务中执行耗时操作

-- 5. 设置锁超时
SET innodb_lock_wait_timeout = 50;
```

## 日志问题

### 1. 日志文件过大

#### 问题现象

```bash
# 日志文件占用大量磁盘空间
du -sh /var/log/py-small-admin/
# 5.0G
```

#### 解决方案

```bash
# 1. 配置日志轮转
sudo nano /etc/logrotate.d/py-small-admin

# 2. 手动轮转日志
sudo logrotate -f /etc/logrotate.d/py-small-admin

# 3. 压缩旧日志
gzip /var/log/py-small-admin/app.log.1

# 4. 删除旧日志
find /var/log/py-small-admin -name "*.log.*" -mtime +30 -delete
```

### 2. 日志丢失

#### 问题现象

```bash
# 部分日志没有记录
```

#### 解决方案

```python
# 1. 检查日志配置
import logging
logger = logging.getLogger('py_small_admin')
print(logger.handlers)
print(logger.level)

# 2. 检查文件权限
ls -la /var/log/py-small-admin/

# 3. 检查磁盘空间
df -h /var/log/

# 4. 检查日志级别
logger.setLevel(logging.DEBUG)
```

## 监控告警

### 1. 告警过于频繁

#### 问题现象

```bash
# 收到大量重复告警
```

#### 解决方案

```yaml
# 1. 配置告警抑制
# 在 Prometheus 配置中添加
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']

# 2. 增加告警持续时间
- alert: HighCPUUsage
  expr: cpu_usage > 80
  for: 10m  # 增加到 10 分钟

# 3. 配置告警聚合
# 在 Alertmanager 中配置
group_wait: 30s
group_interval: 5m
repeat_interval: 12h
```

### 2. 告警未触发

#### 问题现象

```bash
# 问题发生但未收到告警
```

#### 解决方案

```yaml
# 1. 检查告警规则
# 验证查询语句
expr: up{job="fastapi"} == 0

# 2. 检查告警状态
# 访问 Prometheus UI
http://localhost:9090/alerts

# 3. 检查 Alertmanager
# 访问 Alertmanager UI
http://localhost:9093

# 4. 检查通知配置
# 测试邮件发送
echo "Test" | mail -s "Test" admin@example.com
```

## 常用排查命令

### 系统检查

```bash
# 查看系统负载
uptime

# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看进程
ps aux | grep python

# 查看端口监听
sudo netstat -tulpn

# 查看系统日志
sudo journalctl -xe
```

### 应用检查

```bash
# 查看应用日志
tail -f /var/log/py-small-admin/app.log

# 查看 Gunicorn 状态
sudo supervisorctl status py-small-admin

# 查看 Celery 状态
celery -A config.celery_config inspect active

# 查看数据库连接
mysql -u py_admin -p -e "SHOW PROCESSLIST;"
```

### 网络检查

```bash
# 测试网络连接
ping google.com

# 测试端口
telnet localhost 8000

# 查看 DNS
nslookup example.com

# 查看路由
traceroute example.com
```

## 最佳实践

### 1. 预防措施

```python
# 1. 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk': check_disk()
    }

    if all(checks.values()):
        return {'status': 'healthy'}
    else:
        return {'status': 'unhealthy', 'checks': checks}
```

### 2. 监控告警

```yaml
# 配置关键指标告警
- alert: ApplicationDown
  expr: up{job="fastapi"} == 0
  for: 1m
  annotations:
    summary: "应用服务宕机"
```

### 3. 备份恢复

```bash
# 定期备份数据库
mysqldump -u py_admin -p py_small_admin > backup.sql

# 定期备份配置文件
tar -czf config-backup.tar.gz /path/to/config
```

## 相关文档

- [部署指南](./deployment-guide.md)
- [监控指南](./monitoring.md)
- [日志指南](./logging.md)
- [Celery 指南](../celery/celery-guide.md)
