# 监控指南

本指南将详细介绍如何监控 Py Small Admin 项目的运行状态，包括系统监控、应用监控、性能监控和告警配置。

## 监控概述

### 监控架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   应用服务   │────▶│  监控代理    │────▶│  监控服务器  │
│  (FastAPI)  │     │ (Agent)     │     │ (Prometheus)│
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   数据库    │────▶│  监控代理    │────▶│  可视化     │
│  (MySQL)    │     │ (Agent)     │     │ (Grafana)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   告警系统   │
                                        │ (Alertmanager)│
                                        └─────────────┘
```

### 监控层次

| 层次     | 监控内容                 | 工具                         |
| -------- | ------------------------ | ---------------------------- |
| 基础设施 | CPU、内存、磁盘、网络    | Prometheus + Node Exporter   |
| 应用层   | API 响应、错误率、吞吐量 | Prometheus + Custom Exporter |
| 数据库   | 连接数、查询性能、慢查询 | MySQL Exporter               |
| 缓存     | 命中率、内存使用、连接数 | Redis Exporter               |
| 业务层   | 用户活跃、订单量、转化率 | Custom Metrics               |

## 基础设施监控

### Node Exporter 安装

```bash
# 下载 Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz

# 解压
tar xvfz node_exporter-1.6.0.linux-amd64.tar.gz

# 移动到系统目录
sudo mv node_exporter-1.6.0.linux-amd64/node_exporter /usr/local/bin/

# 创建用户
sudo useradd --no-create-home --shell /bin/false node_exporter

# 创建 systemd 服务
sudo nano /etc/systemd/system/node_exporter.service
```

### Node Exporter 配置

```ini
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
    --collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($|/)

[Install]
WantedBy=multi-user.target
```

### 启动 Node Exporter

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start node_exporter

# 设置开机自启
sudo systemctl enable node_exporter

# 验证
curl http://localhost:9100/metrics
```

## 应用监控

### Prometheus 安装

```bash
# 下载 Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

# 解压
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz

# 移动到系统目录
sudo mv prometheus-2.45.0.linux-amd64 /opt/prometheus

# 创建用户
sudo useradd --no-create-home --shell /bin/false prometheus

# 创建目录
sudo mkdir -p /etc/prometheus /var/lib/prometheus

# 设置权限
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus
```

### Prometheus 配置

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: "py-small-admin"
    environment: "production"

# 告警规则文件
rule_files:
  - "/etc/prometheus/alerts/*.yml"

# 抓取配置
scrape_configs:
  # Prometheus 自身监控
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  # Node Exporter
  - job_name: "node"
    static_configs:
      - targets: ["localhost:9100"]

  # FastAPI 应用
  - job_name: "fastapi"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: "/metrics"

  # MySQL Exporter
  - job_name: "mysql"
    static_configs:
      - targets: ["localhost:9104"]

  # Redis Exporter
  - job_name: "redis"
    static_configs:
      - targets: ["localhost:9121"]

  # Celery Exporter
  - job_name: "celery"
    static_configs:
      - targets: ["localhost:9108"]
```

### 创建 systemd 服务

```ini
# /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
After=network.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/prometheus/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus \
    --web.console.templates=/opt/prometheus/consoles \
    --web.console.libraries=/opt/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090

[Install]
WantedBy=multi-user.target
```

### 启动 Prometheus

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start prometheus

# 设置开机自启
sudo systemctl enable prometheus

# 验证
curl http://localhost:9090
```

## 数据库监控

### MySQL Exporter 安装

```bash
# 下载 MySQL Exporter
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.15.0/mysqld_exporter-0.15.0.linux-amd64.tar.gz

# 解压
tar xvfz mysqld_exporter-0.15.0.linux-amd64.tar.gz

# 移动到系统目录
sudo mv mysqld_exporter-0.15.0.linux-amd64/mysqld_exporter /usr/local/bin/

# 创建用户
sudo useradd --no-create-home --shell /bin/false mysqld_exporter
```

### MySQL Exporter 配置

```ini
# /etc/.mysqld_exporter.cnf
[client]
user=exporter
password=exporter_password
host=localhost
port=3306
```

### 创建监控用户

```sql
-- 在 MySQL 中创建监控用户
CREATE USER 'exporter'@'localhost' IDENTIFIED BY 'exporter_password';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'localhost';
FLUSH PRIVILEGES;
```

### 创建 systemd 服务

```ini
# /etc/systemd/system/mysqld_exporter.service
[Unit]
Description=MySQL Exporter
After=network.target mysql.service

[Service]
User=mysqld_exporter
Group=mysqld_exporter
Type=simple
ExecStart=/usr/local/bin/mysqld_exporter \
    --config.my-cnf=/etc/.mysqld_exporter.cnf \
    --collect.global_status \
    --collect.info_schema.innodb_metrics \
    --collect.auto_increment.columns \
    --web.listen-address=0.0.0.0:9104

[Install]
WantedBy=multi-user.target
```

### 启动 MySQL Exporter

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start mysqld_exporter

# 设置开机自启
sudo systemctl enable mysqld_exporter

# 验证
curl http://localhost:9104/metrics
```

## Redis 监控

### Redis Exporter 安装

```bash
# 下载 Redis Exporter
wget https://github.com/oliver006/redis_exporter/releases/download/v1.52.0/redis_exporter-v1.52.0.linux-amd64.tar.gz

# 解压
tar xvfz redis_exporter-v1.52.0.linux-amd64.tar.gz

# 移动到系统目录
sudo mv redis_exporter-v1.52.0.linux-amd64/redis_exporter /usr/local/bin/

# 创建用户
sudo useradd --no-create-home --shell /bin/false redis_exporter
```

### 创建 systemd 服务

```ini
# /etc/systemd/system/redis_exporter.service
[Unit]
Description=Redis Exporter
After=network.target redis.service

[Service]
User=redis_exporter
Group=redis_exporter
Type=simple
ExecStart=/usr/local/bin/redis_exporter \
    --redis.addr=redis://localhost:6379 \
    --web.listen-address=0.0.0.0:9121

[Install]
WantedBy=multi-user.target
```

### 启动 Redis Exporter

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start redis_exporter

# 设置开机自启
sudo systemctl enable redis_exporter

# 验证
curl http://localhost:9121/metrics
```

## 应用指标

### 集成 Prometheus

```python
# config/prometheus_config.py
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

def setup_prometheus(app: FastAPI):
    """配置 Prometheus 监控"""
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
```

### 自定义指标

```python
# metrics/custom_metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
import time

# 请求计数器
request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# 请求延迟直方图
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# 活跃用户数
active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

# 数据库连接数
db_connections = Gauge(
    'db_connections_active',
    'Active database connections'
)

# 任务队列长度
queue_length = Gauge(
    'celery_queue_length',
    'Celery queue length',
    ['queue']
)

# 应用信息
app_info = Info('application', 'Application information')

# 使用示例
def track_request(method: str, endpoint: str, status: int):
    """记录请求"""
    request_counter.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()

def track_request_duration(method: str, endpoint: str, duration: float):
    """记录请求时间"""
    request_duration.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)

def update_active_users(count: int):
    """更新活跃用户数"""
    active_users.set(count)

def update_db_connections(count: int):
    """更新数据库连接数"""
    db_connections.set(count)

def update_queue_length(queue_name: str, length: int):
    """更新队列长度"""
    queue_length.labels(queue=queue_name).set(length)

def set_app_info(version: str, environment: str):
    """设置应用信息"""
    app_info.info({
        'version': version,
        'environment': environment
    })
```

### 中间件集成

```python
# middleware/prometheus_middleware.py
import time
from fastapi import Request
from metrics.custom_metrics import (
    track_request,
    track_request_duration
)

async def prometheus_middleware(request: Request, call_next):
    """Prometheus 监控中间件"""
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    duration = time.time() - start_time

    # 记录指标
    track_request(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    )
    track_request_duration(
        method=request.method,
        endpoint=request.url.path,
        duration=duration
    )

    return response
```

## Grafana 可视化

### 安装 Grafana

```bash
# 添加 Grafana 仓库
sudo wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

# 更新包列表
sudo apt-get update

# 安装 Grafana
sudo apt-get install grafana

# 启动 Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# 访问 Grafana
# http://localhost:3000
# 默认用户名/密码: admin/admin
```

### 配置数据源

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "isDefault": true
}
```

### 创建仪表盘

```json
{
  "dashboard": {
    "title": "Py Small Admin 监控",
    "panels": [
      {
        "title": "请求速率",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "请求延迟",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P50"
          }
        ]
      },
      {
        "title": "CPU 使用率",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "内存使用率",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "活跃用户数",
        "type": "stat",
        "targets": [
          {
            "expr": "active_users_total"
          }
        ]
      },
      {
        "title": "Celery 队列长度",
        "type": "graph",
        "targets": [
          {
            "expr": "celery_queue_length",
            "legendFormat": "{{queue}}"
          }
        ]
      }
    ]
  }
}
```

## 告警配置

### Alertmanager 安装

```bash
# 下载 Alertmanager
wget https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz

# 解压
tar xvfz alertmanager-0.26.0.linux-amd64.tar.gz

# 移动到系统目录
sudo mv alertmanager-0.26.0.linux-amd64 /opt/alertmanager

# 创建用户
sudo useradd --no-create-home --shell /bin/false alertmanager

# 创建目录
sudo mkdir -p /etc/alertmanager

# 设置权限
sudo chown -R alertmanager:alertmanager /opt/alertmanager /etc/alertmanager
```

### Alertmanager 配置

```yaml
# /etc/alertmanager/alertmanager.yml
global:
  resolve_timeout: 5m

# 路由配置
route:
  group_by: ["alertname", "cluster", "service"]
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: "default"

  # 子路由
  routes:
    - match:
        severity: critical
      receiver: "critical"
      continue: true

    - match:
        severity: warning
      receiver: "warning"

# 接收器配置
receivers:
  - name: "default"
    email_configs:
      - to: "admin@example.com"
        from: "alertmanager@example.com"
        smarthost: "smtp.example.com:587"
        auth_username: "alertmanager@example.com"
        auth_password: "password"

  - name: "critical"
    email_configs:
      - to: "oncall@example.com"
        from: "alertmanager@example.com"
        smarthost: "smtp.example.com:587"
        auth_username: "alertmanager@example.com"
        auth_password: "password"

  - name: "warning"
    email_configs:
      - to: "team@example.com"
        from: "alertmanager@example.com"
        smarthost: "smtp.example.com:587"
        auth_username: "alertmanager@example.com"
        auth_password: "password"
```

### Prometheus 告警规则

```yaml
# /etc/prometheus/alerts/rules.yml
groups:
  - name: application_alerts
    interval: 30s
    rules:
      # 应用宕机
      - alert: ApplicationDown
        expr: up{job="fastapi"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "应用服务宕机"
          description: "应用服务 {{ $labels.instance }} 已宕机超过 1 分钟"

      # 高错误率
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "高错误率"
          description: "错误率超过 5%: {{ $value }}"

      # 高延迟
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "高延迟"
          description: "P95 延迟超过 1 秒: {{ $value }}"

  - name: infrastructure_alerts
    interval: 30s
    rules:
      # CPU 使用率过高
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率过高"
          description: "CPU 使用率超过 80%: {{ $value }}%"

      # 内存使用率过高
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "内存使用率超过 80%: {{ $value }}%"

      # 磁盘空间不足
      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"}) * 100 < 20
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "磁盘空间不足"
          description: "磁盘 {{ $labels.mountpoint }} 剩余空间低于 20%: {{ $value }}%"

  - name: database_alerts
    interval: 30s
    rules:
      # MySQL 宕机
      - alert: MySQLDown
        expr: mysql_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MySQL 数据库宕机"
          description: "MySQL 数据库 {{ $labels.instance }} 已宕机"

      # 慢查询
      - alert: SlowQueries
        expr: rate(mysql_global_status_slow_queries[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "慢查询过多"
          description: "慢查询速率超过 10/秒: {{ $value }}"

  - name: celery_alerts
    interval: 30s
    rules:
      # Worker 宕机
      - alert: CeleryWorkerDown
        expr: celery_worker_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Celery Worker 宕机"
          description: "Celery Worker {{ $labels.instance }} 已宕机"

      # 队列积压
      - alert: QueueBacklog
        expr: celery_queue_length > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "队列积压"
          description: "队列 {{ $labels.queue }} 积压超过 1000 个任务: {{ $value }}"
```

### 启动 Alertmanager

```bash
# 创建 systemd 服务
sudo nano /etc/systemd/system/alertmanager.service
```

```ini
[Unit]
Description=Alertmanager
After=network.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple
ExecStart=/opt/alertmanager/alertmanager \
    --config.file=/etc/alertmanager/alertmanager.yml \
    --storage.path=/var/lib/alertmanager \
    --web.listen-address=0.0.0.0:9093

[Install]
WantedBy=multi-user.target
```

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start alertmanager

# 设置开机自启
sudo systemctl enable alertmanager

# 验证
curl http://localhost:9093
```

### 配置 Prometheus 告警

```yaml
# 在 prometheus.yml 中添加
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - "localhost:9093"
```

## 日志监控

### ELK Stack 安装

```bash
# 安装 Elasticsearch
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
sudo apt-get update
sudo apt-get install elasticsearch

# 安装 Logstash
sudo apt-get install logstash

# 安装 Kibana
sudo apt-get install kibana

# 启动服务
sudo systemctl start elasticsearch
sudo systemctl start logstash
sudo systemctl start kibana

# 设置开机自启
sudo systemctl enable elasticsearch
sudo systemctl enable logstash
sudo systemctl enable kibana
```

### Logstash 配置

```conf
# /etc/logstash/conf.d/py-small-admin.conf
input {
  file {
    path => "/var/log/py-small-admin/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
  }
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "py-small-admin-%{+YYYY.MM.dd}"
  }
}
```

## 最佳实践

### 1. 监控指标选择

```python
# 关键指标
key_metrics = {
    '可用性': '应用是否正常运行',
    '延迟': '请求响应时间',
    '错误率': '请求失败比例',
    '吞吐量': '每秒处理请求数',
    '资源使用': 'CPU、内存、磁盘'
}
```

### 2. 告警阈值设置

```python
# 告警阈值建议
alert_thresholds = {
    'CPU 使用率': {
        'warning': 70,
        'critical': 90
    },
    '内存使用率': {
        'warning': 75,
        'critical': 90
    },
    '错误率': {
        'warning': 0.01,  # 1%
        'critical': 0.05   # 5%
    },
    '延迟': {
        'warning': 0.5,   # 500ms
        'critical': 1.0   # 1s
    }
}
```

### 3. 监控频率

```python
# 监控频率建议
monitoring_intervals = {
    '基础设施': 15,  # 15 秒
    '应用指标': 15,
    '业务指标': 60,  # 1 分钟
    '告警评估': 30
}
```

## 常见问题

### 1. 指标采集失败

**问题**：Prometheus 无法采集指标

**解决方案**：

- 检查 exporter 是否正常运行
- 验证网络连接
- 查看防火墙规则

### 2. 告警过于频繁

**问题**：收到大量告警通知

**解决方案**：

- 调整告警阈值
- 增加告警持续时间
- 配置告警抑制

### 3. Grafana 数据不更新

**问题**：Grafana 仪表盘数据不更新

**解决方案**：

- 检查 Prometheus 数据源
- 验证查询语句
- 查看浏览器控制台错误

## 相关文档

- [部署指南](./deployment-guide.md)
- [日志指南](./logging.md)
- [故障排查](./troubleshooting.md)
- [Celery 监控](../celery/monitoring.md)
