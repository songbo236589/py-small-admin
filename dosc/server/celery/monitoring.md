# 监控指南

本指南将详细介绍如何监控 Celery 任务队列系统，包括任务监控、性能监控、告警配置等。

## 监控概述

### 监控目标

- **任务执行**: 监控任务执行状态、成功率、失败率
- **队列状态**: 监控队列长度、任务积压情况
- **Worker 健康**: 监控 worker 状态、资源使用情况
- **性能指标**: 监控任务执行时间、吞吐量
- **告警通知**: 及时发现和通知异常情况

### 监控指标

| 指标类别    | 具体指标               | 说明             |
| ----------- | ---------------------- | ---------------- |
| 任务指标    | 成功数、失败数、重试数 | 任务执行结果统计 |
| 队列指标    | 队列长度、任务积压     | 队列负载情况     |
| Worker 指标 | 活跃数、空闲数、并发数 | Worker 工作状态  |
| 性能指标    | 执行时间、吞吐量       | 系统性能表现     |
| 资源指标    | CPU、内存、网络        | 资源使用情况     |

## Flower 监控

### 安装和启动

```bash
# 安装 flower
pip install flower

# 启动 flower
celery -A config.celery_config flower --port=5555

# 指定 broker
celery -A config.celery_config flower --broker=redis://localhost:6379/0

# 指定认证
celery -A config.celery_config flower --basic_auth=user:password

# 后台运行
celery -A config.celery_config flower --port=5555 --detach
```

### Flower 功能

#### 1. Worker 监控

- Worker 状态：在线/离线
- Worker 并发数
- Worker 任务处理统计
- Worker 资源使用

#### 2. 任务监控

- 任务执行状态
- 任务执行时间
- 任务参数和结果
- 任务重试记录

#### 3. 队列监控

- 队列长度
- 队列任务分布
- 队列吞吐量

#### 4. 任务管理

- 查看任务详情
- 撤销任务
- 清空队列
- 重启 worker

### Flower API

```python
import requests

# 获取 worker 状态
def get_workers():
    """获取所有 worker 状态"""
    response = requests.get('http://localhost:5555/api/workers')
    return response.json()

# 获取任务信息
def get_task(task_id):
    """获取任务详情"""
    response = requests.get(f'http://localhost:5555/api/task/info/{task_id}')
    return response.json()

# 获取队列信息
def get_queues():
    """获取队列信息"""
    response = requests.get('http://localhost:5555/api/queues')
    return response.json()

# 获取统计信息
def get_stats():
    """获取统计信息"""
    response = requests.get('http://localhost:5555/api/stats')
    return response.json()
```

## Prometheus 监控

### 安装 Prometheus Exporter

```bash
# 安装 celery-prometheus-exporter
pip install celery-prometheus-exporter

# 启动 exporter
celery-prometheus-exporter \
    --broker-url=redis://localhost:6379/0 \
    --port=9108
```

### 配置 Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "celery"
    static_configs:
      - targets: ["localhost:9108"]
```

### Prometheus 指标

```python
# 主要指标
celery_tasks_total{status="success|failure|retry"}  # 任务总数
celery_tasks_duration_seconds                       # 任务执行时间
celery_queue_length{queue="name"}                    # 队列长度
celery_workers_active{worker="name"}                 # 活跃 worker 数
celery_workers_idle{worker="name"}                   # 空闲 worker 数
```

### Grafana 仪表盘

```json
{
  "dashboard": {
    "title": "Celery 监控",
    "panels": [
      {
        "title": "任务执行趋势",
        "targets": [
          {
            "expr": "rate(celery_tasks_total[5m])",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "title": "队列长度",
        "targets": [
          {
            "expr": "celery_queue_length",
            "legendFormat": "{{queue}}"
          }
        ]
      },
      {
        "title": "任务执行时间",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(celery_tasks_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          }
        ]
      }
    ]
  }
}
```

## 自定义监控

### 监控脚本

```python
# scripts/monitor_celery.py
import redis
import time
from celery import Celery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CeleryMonitor:
    """Celery 监控类"""

    def __init__(self, broker_url='redis://localhost:6379/0'):
        self.broker_url = broker_url
        self.redis_client = redis.from_url(broker_url)
        self.celery_app = Celery('monitor', broker=broker_url)

    def get_queue_length(self, queue_name):
        """获取队列长度"""
        queue_key = f'celery:{queue_name}'
        return self.redis_client.llen(queue_key)

    def get_worker_stats(self):
        """获取 worker 统计"""
        inspect = self.celery_app.control.inspect()
        stats = inspect.stats()
        return stats

    def get_active_tasks(self):
        """获取活跃任务"""
        inspect = self.celery_app.control.inspect()
        active = inspect.active()
        return active

    def get_scheduled_tasks(self):
        """获取预定任务"""
        inspect = self.celery_app.control.inspect()
        scheduled = inspect.scheduled()
        return scheduled

    def monitor(self, interval=60):
        """持续监控"""
        while True:
            logger.info("=" * 50)
            logger.info(f"监控时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # 监控队列
            queues = ['default', 'admin', 'quant']
            for queue in queues:
                length = self.get_queue_length(queue)
                logger.info(f"队列 {queue}: {length} 个任务")

            # 监控 worker
            stats = self.get_worker_stats()
            if stats:
                for worker, data in stats.items():
                    logger.info(f"Worker {worker}: {data}")

            # 监控活跃任务
            active = self.get_active_tasks()
            if active:
                total_active = sum(len(tasks) for tasks in active.values())
                logger.info(f"活跃任务: {total_active}")

            time.sleep(interval)

if __name__ == '__main__':
    monitor = CeleryMonitor()
    monitor.monitor(interval=60)
```

### 监控 API

```python
# api/monitoring.py
from fastapi import APIRouter
from scripts.monitor_celery import CeleryMonitor

router = APIRouter()
monitor = CeleryMonitor()

@router.get("/queues")
async def get_queue_status():
    """获取队列状态"""
    queues = ['default', 'admin', 'quant']
    status = {}

    for queue in queues:
        length = monitor.get_queue_length(queue)
        status[queue] = {
            'length': length,
            'status': 'normal' if length < 100 else 'busy'
        }

    return {
        'code': 200,
        'data': status
    }

@router.get("/workers")
async def get_worker_status():
    """获取 worker 状态"""
    stats = monitor.get_worker_stats()

    return {
        'code': 200,
        'data': stats
    }

@router.get("/tasks/active")
async def get_active_tasks():
    """获取活跃任务"""
    active = monitor.get_active_tasks()

    return {
        'code': 200,
        'data': active
    }
```

## 告警配置

### 告警规则

```python
# scripts/alerts.py
import smtplib
from email.mime.text import MIMEText
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertManager:
    """告警管理器"""

    def __init__(self, email_config=None):
        self.email_config = email_config

    def send_email(self, subject, content):
        """发送邮件告警"""
        if not self.email_config:
            logger.warning("邮件配置未设置，跳过发送")
            return

        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']

        with smtplib.SMTP(
            self.email_config['host'],
            self.email_config['port']
        ) as server:
            server.starttls()
            server.login(
                self.email_config['user'],
                self.email_config['password']
            )
            server.send_message(msg)

        logger.info(f"告警邮件已发送: {subject}")

    def check_queue_alert(self, queue_name, threshold=1000):
        """检查队列告警"""
        from scripts.monitor_celery import CeleryMonitor
        monitor = CeleryMonitor()
        length = monitor.get_queue_length(queue_name)

        if length > threshold:
            subject = f"队列告警: {queue_name}"
            content = f"""
            队列 {queue_name} 积压严重

            当前长度: {length}
            告警阈值: {threshold}

            请及时处理！
            """
            self.send_email(subject, content)
            return True

        return False

    def check_worker_alert(self):
        """检查 worker 告警"""
        from scripts.monitor_celery import CeleryMonitor
        monitor = CeleryMonitor()
        stats = monitor.get_worker_stats()

        if not stats or len(stats) == 0:
            subject = "Worker 告警: 无活跃 worker"
            content = """
            系统检测到没有活跃的 worker

            请检查 worker 服务是否正常运行！
            """
            self.send_email(subject, content)
            return True

        return False
```

### 告警任务

```python
# tasks/alert_task.py
from celery import shared_task
from scripts.alerts import AlertManager

@shared_task
def queue_monitor_task():
    """队列监控任务"""
    alert_manager = AlertManager()

    queues = ['default', 'admin', 'quant']
    for queue in queues:
        alert_manager.check_queue_alert(queue, threshold=1000)

@shared_task
def worker_monitor_task():
    """Worker 监控任务"""
    alert_manager = AlertManager()
    alert_manager.check_worker_alert()
```

### 定时告警

```python
# config/celery_config.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # 每 5 分钟检查队列
    'queue-monitor': {
        'task': 'tasks.alert_task.queue_monitor_task',
        'schedule': 300.0,
    },

    # 每 10 分钟检查 worker
    'worker-monitor': {
        'task': 'tasks.alert_task.worker_monitor_task',
        'schedule': 600.0,
    },
}
```

## 性能监控

### 任务执行时间

```python
# scripts/performance_monitor.py
import time
from functools import wraps
from celery import shared_task

def monitor_task_performance(func):
    """任务性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # 记录执行时间
            log_task_performance(
                func.__name__,
                execution_time,
                status='success'
            )

            return result

        except Exception as e:
            execution_time = time.time() - start_time

            # 记录失败
            log_task_performance(
                func.__name__,
                execution_time,
                status='failed',
                error=str(e)
            )

            raise

    return wrapper

def log_task_performance(task_name, execution_time, status, error=None):
    """记录任务性能"""
    import logging

    logger = logging.getLogger('task_performance')

    logger.info({
        'task': task_name,
        'execution_time': execution_time,
        'status': status,
        'error': error,
        'timestamp': time.time()
    })

# 使用示例
@shared_task
@monitor_task_performance
def monitored_task(data):
    """带性能监控的任务"""
    return process(data)
```

### 吞吐量监控

```python
# scripts/throughput_monitor.py
from collections import defaultdict
import time

class ThroughputMonitor:
    """吞吐量监控"""

    def __init__(self):
        self.task_counts = defaultdict(int)
        self.start_time = time.time()

    def record_task(self, task_name):
        """记录任务"""
        self.task_counts[task_name] += 1

    def get_throughput(self, interval=60):
        """获取吞吐量（任务/秒）"""
        elapsed_time = time.time() - self.start_time

        if elapsed_time < interval:
            return {}

        throughput = {}
        for task_name, count in self.task_counts.items():
            throughput[task_name] = count / elapsed_time

        # 重置计数
        self.task_counts.clear()
        self.start_time = time.time()

        return throughput

# 全局监控实例
throughput_monitor = ThroughputMonitor()

# 在任务中记录
@shared_task
def task_with_throughput(data):
    """记录吞吐量的任务"""
    throughput_monitor.record_task('task_with_throughput')
    return process(data)
```

## 日志监控

### 结构化日志

```python
# config/logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    """配置结构化日志"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # JSON 格式化器
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    file_handler = logging.FileHandler('logs/celery.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
```

### 日志分析

```python
# scripts/log_analyzer.py
import json
import re
from collections import Counter

def analyze_logs(log_file='logs/celery.log'):
    """分析日志"""
    task_stats = Counter()
    error_stats = Counter()

    with open(log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)

                # 统计任务
                if 'task' in log_entry:
                    task_stats[log_entry['task']] += 1

                # 统计错误
                if log_entry.get('levelname') == 'ERROR':
                    error = log_entry.get('message', 'unknown')
                    error_stats[error] += 1

            except json.JSONDecodeError:
                continue

    return {
        'task_stats': dict(task_stats),
        'error_stats': dict(error_stats)
    }
```

## 最佳实践

### 1. 分层监控

```python
# 分层监控策略
monitoring_layers = {
    '基础设施': ['CPU', '内存', '磁盘', '网络'],
    '应用层': ['任务执行', '队列状态', 'Worker 健康'],
    '业务层': ['业务指标', '用户体验', 'SLA']
}
```

### 2. 告警分级

```python
# 告警级别
alert_levels = {
    'CRITICAL': '系统不可用，立即处理',
    'WARNING': '性能下降，尽快处理',
    'INFO': '正常状态，仅供参考'
}
```

### 3. 监控频率

```python
# 监控频率配置
monitoring_intervals = {
    '实时监控': 10,      # 10 秒
    '性能监控': 60,      # 1 分钟
    '健康检查': 300,     # 5 分钟
    '统计报告': 3600     # 1 小时
}
```

## 常见问题

### 1. 监控数据不准确

**问题**：监控数据与实际情况不符

**解决方案**：

- 检查监控脚本配置
- 验证数据采集频率
- 确认数据源正确性

### 2. 告警过于频繁

**问题**：收到大量告警通知

**解决方案**：

- 调整告警阈值
- 实现告警聚合
- 增加告警冷却时间

### 3. 性能影响

**问题**：监控系统影响业务性能

**解决方案**：

- 降低监控频率
- 优化监控逻辑
- 使用异步监控

## 相关文档

- [Celery 基础指南](./celery-guide.md)
- [任务开发指南](./task-development.md)
- [队列管理](./queue-management.md)
- [部署指南](../deployment/deployment-guide.md)
- [日志指南](../deployment/logging.md)
