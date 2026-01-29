# 日志指南

本指南将详细介绍 Py Small Admin 项目的日志管理，包括日志配置、日志收集、日志分析和日志归档。

## 日志概述

### 日志架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   应用服务   │────▶│  日志文件    │────▶│  日志收集    │
│  (FastAPI)  │     │  (File)     │     │ (Logstash)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Celery    │────▶│  日志文件    │────▶│  日志存储    │
│  (Worker)   │     │  (File)     │     │(Elasticsearch)│
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  日志可视化  │
                                        │  (Kibana)   │
                                        └─────────────┘
```

### 日志类型

| 类型          | 用途          | 位置                                   |
| ------------- | ------------- | -------------------------------------- |
| 应用日志      | 应用运行日志  | `/var/log/py-small-admin/app.log`      |
| 访问日志      | HTTP 请求日志 | `/var/log/py-small-admin/access.log`   |
| 错误日志      | 错误和异常    | `/var/log/py-small-admin/error.log`    |
| Celery 日志   | 任务执行日志  | `/var/log/py-small-admin/celery.log`   |
| Gunicorn 日志 | WSGI 日志     | `/var/log/py-small-admin/gunicorn.log` |

## 日志配置

### Python 日志配置

```python
# config/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from pythonjsonlogger import jsonlogger

def setup_logging(app_name='py_small_admin', log_level='INFO'):
    """配置日志系统"""

    # 创建日志目录
    log_dir = os.getenv('LOG_DIR', '/var/log/py-small-admin')
    os.makedirs(log_dir, exist_ok=True)

    # 创建 logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 清除已有的处理器
    logger.handlers.clear()

    # JSON 格式化器
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s',
        timestamp=True
    )

    # 标准格式化器
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器（开发环境）
    if os.getenv('APP_ENV') == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(standard_formatter)
        logger.addHandler(console_handler)

    # 应用日志文件处理器
    app_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(json_formatter)
    logger.addHandler(app_handler)

    # 错误日志文件处理器
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    logger.addHandler(error_handler)

    # 访问日志文件处理器
    access_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(json_formatter)
    logger.addHandler(access_handler)

    # Celery 日志处理器
    celery_handler = RotatingFileHandler(
        os.path.join(log_dir, 'celery.log'),
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    celery_handler.setLevel(logging.INFO)
    celery_handler.setFormatter(json_formatter)
    logger.addHandler(celery_handler)

    return logger
```

### FastAPI 日志配置

```python
# config/fastapi_logging.py
from fastapi import Request
import logging
import time
import json

logger = logging.getLogger('py_small_admin')

async def log_request(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()

    # 记录请求信息
    request.state.start_time = start_time

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 记录访问日志
    access_log = {
        'method': request.method,
        'url': str(request.url),
        'status_code': response.status_code,
        'process_time': process_time,
        'client_ip': request.client.host if request.client else None,
        'user_agent': request.headers.get('user-agent'),
        'path': request.url.path,
        'query_params': dict(request.query_params),
    }

    logger.info(json.dumps(access_log))

    # 添加响应头
    response.headers['X-Process-Time'] = str(process_time)

    return response

async def log_exception(request: Request, exc: Exception):
    """记录异常日志"""
    error_log = {
        'method': request.method,
        'url': str(request.url),
        'error_type': type(exc).__name__,
        'error_message': str(exc),
        'client_ip': request.client.host if request.client else None,
    }

    logger.error(json.dumps(error_log), exc_info=True)
```

### Celery 日志配置

```python
# config/celery_logging.py
import logging
from celery.signals import task_prerun, task_postrun, task_failure, task_success

logger = logging.getLogger('py_small_admin.celery')

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """任务开始前记录"""
    logger.info(json.dumps({
        'event': 'task_prerun',
        'task_id': task_id,
        'task_name': task.name,
        'args': args,
        'kwargs': kwargs,
    }))

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """任务完成后记录"""
    logger.info(json.dumps({
        'event': 'task_postrun',
        'task_id': task_id,
        'task_name': task.name,
        'state': state,
        'retval': str(retval),
    }))

@task_success.connect
def task_success_handler(sender=None, result=None, **kwds):
    """任务成功记录"""
    logger.info(json.dumps({
        'event': 'task_success',
        'task_id': sender.request.id,
        'task_name': sender.name,
        'result': str(result),
    }))

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, einfo=None, **kwds):
    """任务失败记录"""
    logger.error(json.dumps({
        'event': 'task_failure',
        'task_id': task_id,
        'task_name': sender.name if sender else None,
        'exception': str(exception),
        'traceback': str(einfo) if einfo else None,
    }))
```

## 日志使用

### 应用日志

```python
# 在应用中使用日志
from fastapi import APIRouter
import logging

logger = logging.getLogger('py_small_admin')

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户信息"""
    logger.info(f"获取用户信息: {user_id}")

    try:
        user = get_user_from_db(user_id)
        logger.info(f"用户信息获取成功: {user_id}")
        return user
    except Exception as e:
        logger.error(f"获取用户信息失败: {user_id}", exc_info=True)
        raise
```

### 结构化日志

```python
# 使用结构化日志
import logging
import json

logger = logging.getLogger('py_small_admin')

def log_structured(level, message, **kwargs):
    """记录结构化日志"""
    log_data = {
        'message': message,
        **kwargs
    }

    log_method = getattr(logger, level.lower())
    log_method(json.dumps(log_data))

# 使用示例
log_structured(
    'info',
    '用户登录',
    user_id=123,
    username='testuser',
    ip='192.168.1.1'
)

log_structured(
    'error',
    '数据库连接失败',
    error='Connection timeout',
    retry_count=3
)
```

### 上下文日志

```python
# 使用上下文信息
from contextvars import ContextVar
import logging

# 创建上下文变量
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[int] = ContextVar('user_id', default=0)

class ContextFilter(logging.Filter):
    """上下文过滤器"""

    def filter(self, record):
        record.request_id = request_id_var.get('')
        record.user_id = user_id_var.get(0)
        return True

# 配置日志过滤器
logger = logging.getLogger('py_small_admin')
context_filter = ContextFilter()
logger.addFilter(context_filter)

# 在中间件中设置上下文
from fastapi import Request
import uuid

async def set_context(request: Request, call_next):
    """设置请求上下文"""
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    # 处理请求
    response = await call_next(request)

    # 清除上下文
    request_id_var.set('')
    user_id_var.set(0)

    return response
```

## 日志收集

### Logstash 配置

```conf
# /etc/logstash/conf.d/py-small-admin.conf

input {
  # 应用日志
  file {
    path => "/var/log/py-small-admin/app.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => json
    type => "app"
  }

  # 访问日志
  file {
    path => "/var/log/py-small-admin/access.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => json
    type => "access"
  }

  # 错误日志
  file {
    path => "/var/log/py-small-admin/error.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => json
    type => "error"
  }

  # Celery 日志
  file {
    path => "/var/log/py-small-admin/celery.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => json
    type => "celery"
  }
}

filter {
  # 解析时间戳
  date {
    match => [ "asctime", "ISO8601" ]
    target => "@timestamp"
  }

  # 添加字段
  mutate {
    add_field => {
      "environment" => "${ENVIRONMENT}"
      "application" => "py_small_admin"
    }
  }

  # 根据类型添加额外字段
  if [type] == "access" {
    mutate {
      add_field => {
        "log_type" => "access"
      }
    }
  } else if [type] == "error" {
    mutate {
      add_field => {
        "log_type" => "error"
      }
    }
  } else if [type] == "celery" {
    mutate {
      add_field => {
        "log_type" => "celery"
      }
    }
  }
}

output {
  # 输出到 Elasticsearch
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "py-small-admin-%{+YYYY.MM.dd}"
    document_type => "_doc"
  }

  # 可选：输出到文件（调试用）
  # file {
  #   path => "/var/log/logstash/output.log"
  # }
}
```

### 启动 Logstash

```bash
# 启动 Logstash
sudo systemctl start logstash

# 设置开机自启
sudo systemctl enable logstash

# 查看状态
sudo systemctl status logstash

# 查看日志
sudo journalctl -u logstash -f
```

## 日志分析

### Elasticsearch 查询

```python
# scripts/log_analysis.py
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

es = Elasticsearch(['http://localhost:9200'])

def search_logs(index, query, size=100):
    """搜索日志"""
    response = es.search(
        index=index,
        body=query,
        size=size
    )
    return response['hits']['hits']

def get_error_logs(hours=24):
    """获取错误日志"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "levelname": "ERROR"
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": f"now-{hours}h"
                            }
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "@timestamp": {
                    "order": "desc"
                }
            }
        ]
    }

    return search_logs("py-small-admin-*", query)

def get_slow_requests(threshold=1.0, hours=24):
    """获取慢请求"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "process_time": {
                                "gte": threshold
                            }
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": f"now-{hours}h"
                            }
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "process_time": {
                    "order": "desc"
                }
            }
        ]
    }

    return search_logs("py-small-admin-*", query)

def get_task_failures(hours=24):
    """获取任务失败日志"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "event": "task_failure"
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": f"now-{hours}h"
                            }
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "@timestamp": {
                    "order": "desc"
                }
            }
        ]
    }

    return search_logs("py-small-admin-*", query)

def get_error_statistics(hours=24):
    """获取错误统计"""
    query = {
        "query": {
            "range": {
                "@timestamp": {
                    "gte": f"now-{hours}h"
                }
            }
        },
        "aggs": {
            "error_types": {
                "terms": {
                    "field": "levelname",
                    "size": 10
                }
            },
            "error_paths": {
                "terms": {
                    "field": "pathname",
                    "size": 10
                }
            }
        }
    }

    response = es.search(
        index="py-small-admin-*",
        body=query
    )

    return response['aggregations']
```

### Kibana 仪表盘

```json
{
  "dashboard": {
    "title": "日志分析仪表盘",
    "panels": [
      {
        "title": "错误日志趋势",
        "type": "line",
        "query": {
          "bool": {
            "must": [
              {
                "match": {
                  "levelname": "ERROR"
                }
              }
            ]
          }
        }
      },
      {
        "title": "请求延迟分布",
        "type": "histogram",
        "query": {
          "range": {
            "process_time": {
              "gte": 0
            }
          }
        }
      },
      {
        "title": "任务失败统计",
        "type": "pie",
        "query": {
          "match": {
            "event": "task_failure"
          }
        }
      },
      {
        "title": "错误类型分布",
        "type": "bar",
        "query": {
          "match": {
            "levelname": "ERROR"
          }
        }
      }
    ]
  }
}
```

## 日志归档

### 日志轮转配置

```bash
# /etc/logrotate.d/py-small-admin

/var/log/py-small-admin/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 deploy deploy
    sharedscripts

    # 压缩后执行脚本
    postrotate
        # 通知应用重新打开日志文件
        if [ -f /var/run/py-small-admin/gunicorn.pid ]; then
            kill -USR1 $(cat /var/run/py-small-admin/gunicorn.pid)
        fi
    endscript
}
```

### 手动归档脚本

```bash
#!/bin/bash
# scripts/archive_logs.sh

LOG_DIR="/var/log/py-small-admin"
ARCHIVE_DIR="/backup/logs"
DATE=$(date +%Y%m%d)

# 创建归档目录
mkdir -p "$ARCHIVE_DIR/$DATE"

# 归档日志
for log_file in "$LOG_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        filename=$(basename "$log_file")
        cp "$log_file" "$ARCHIVE_DIR/$DATE/$filename"

        # 压缩
        gzip "$ARCHIVE_DIR/$DATE/$filename"
    fi
done

# 清理旧归档（保留 90 天）
find "$ARCHIVE_DIR" -type d -mtime +90 -exec rm -rf {} \;

echo "日志归档完成: $ARCHIVE_DIR/$DATE"
```

## 日志安全

### 敏感信息过滤

```python
# config/sensitive_filter.py
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器"""

    # 敏感字段列表
    SENSITIVE_FIELDS = [
        'password', 'passwd', 'secret', 'token', 'api_key',
        'credit_card', 'ssn', 'phone', 'email'
    ]

    def filter(self, record):
        """过滤敏感信息"""
        if hasattr(record, 'msg'):
            record.msg = self.sanitize(record.msg)

        if hasattr(record, 'args'):
            record.args = tuple(
                self.sanitize(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )

        return True

    def sanitize(self, data):
        """清理敏感数据"""
        if not isinstance(data, str):
            return data

        for field in self.SENSITIVE_FIELDS:
            # 匹配 JSON 格式
            pattern = rf'"{field}":\s*"[^"]*"'
            data = re.sub(pattern, f'"{field}": "***"', data)

            # 匹配表单格式
            pattern = rf'{field}=[^&\s]+'
            data = re.sub(pattern, f'{field}=***', data)

        return data

# 配置过滤器
logger = logging.getLogger('py_small_admin')
sensitive_filter = SensitiveDataFilter()
logger.addFilter(sensitive_filter)
```

### 日志访问控制

```bash
# 设置日志目录权限
sudo chmod 750 /var/log/py-small-admin
sudo chown -R deploy:deploy /var/log/py-small-admin

# 设置日志文件权限
sudo chmod 640 /var/log/py-small-admin/*.log

# 限制日志访问
sudo chgrp deploy /var/log/py-small-admin
```

## 最佳实践

### 1. 日志级别使用

```python
# 日志级别使用指南
log_levels = {
    'DEBUG': '详细的调试信息，开发环境使用',
    'INFO': '一般信息，记录重要操作',
    'WARNING': '警告信息，不影响系统运行',
    'ERROR': '错误信息，需要关注',
    'CRITICAL': '严重错误，系统无法运行'
}
```

### 2. 日志内容规范

```python
# 日志内容规范
log_content = {
    '包含信息': [
        '时间戳',
        '日志级别',
        '消息内容',
        '上下文信息（用户ID、请求ID等）',
        '异常堆栈（错误日志）'
    ],
    '避免信息': [
        '敏感数据（密码、密钥等）',
        '过长的数据',
        '重复信息'
    ]
}
```

### 3. 性能考虑

```python
# 异步日志
import logging
from logging.handlers import QueueHandler, QueueListener
import queue

# 创建队列
log_queue = queue.Queue(-1)

# 创建队列处理器
queue_handler = QueueHandler(log_queue)

# 创建文件处理器
file_handler = logging.FileHandler('/var/log/py-small-admin/app.log')

# 创建监听器
listener = QueueListener(log_queue, file_handler)
listener.start()

# 配置 logger
logger = logging.getLogger('py_small_admin')
logger.addHandler(queue_handler)
```

## 常见问题

### 1. 日志文件过大

**问题**：日志文件占用大量磁盘空间

**解决方案**：

- 配置日志轮转
- 定期清理旧日志
- 压缩归档日志

### 2. 日志丢失

**问题**：部分日志没有记录

**解决方案**：

- 检查日志配置
- 验证文件权限
- 确认日志级别

### 3. 性能影响

**问题**：日志记录影响应用性能

**解决方案**：

- 使用异步日志
- 适当降低日志级别
- 优化日志格式

## 相关文档

- [部署指南](./deployment-guide.md)
- [监控指南](./monitoring.md)
- [故障排查](./troubleshooting.md)
- [Celery 监控](../celery/monitoring.md)
