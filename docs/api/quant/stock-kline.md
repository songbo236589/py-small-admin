# 股票 K 线数据 API

本文档介绍了股票 K 线数据同步的 API 接口。K 线数据是股票技术分析的基础数据。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/quant/kline/sync_kline_1d` | 同步所有股票日 K 线数据 |
| POST | `/api/quant/kline/sync_single_kline_1d` | 同步单个股票日 K 线数据 |

## 同步所有股票日 K 线数据

同步所有 A 股的日 K 线数据。该操作会获取每只股票的历史 K 线数据并存储到数据库。

**请求**：
```http
POST /api/quant/kline/sync_kline_1d
Content-Type: application/json
```

**请求体**（可选）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | str | 否 | 指定同步日期，格式：YYYY-MM-DD |
| force_update | bool | 否 | 是否强制更新已有数据，默认 false |

**请求示例**：
```json
{
  "date": "2024-01-15",
  "force_update": false
}
```

**响应**：
```json
{
  "code": 200,
  "message": "同步任务已提交",
  "data": {
    "task_id": "abc123def456",
    "total_stocks": 5000,
    "estimated_time": "约30分钟",
    "status": "processing"
  }
}
```

**响应字段说明**：
- `task_id`: 异步任务 ID，可用于查询任务进度
- `total_stocks`: 需要同步的股票总数
- `estimated_time`: 预计完成时间
- `status`: 任务状态

**注意事项**：
- 该操作为异步任务，立即返回任务 ID
- 同步大量股票数据可能需要较长时间
- 建议在非高峰期执行全量同步
- 可以通过任务 ID 查询同步进度

## 同步单个股票日 K 线数据

同步指定股票的日 K 线数据。

**请求**：
```http
POST /api/quant/kline/sync_single_kline_1d
Content-Type: application/json
```

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| stock_id | int | 是 | 股票 ID |
| stock_code | str | 否 | 股票代码（与 stock_id 二选一） |
| start_date | str | 否 | 开始日期，格式：YYYY-MM-DD |
| end_date | str | 否 | 结束日期，格式：YYYY-MM-DD |
| force_update | bool | 否 | 是否强制更新已有数据 |

**请求示例 1**（使用股票 ID）：
```json
{
  "stock_id": 1,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**请求示例 2**（使用股票代码）：
```json
{
  "stock_code": "000001",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "stock_id": 1,
    "stock_code": "000001",
    "stock_name": "平安银行",
    "sync_count": 20,
    "new_count": 5,
    "update_count": 15
  }
}
```

**响应字段说明**：
- `stock_id`: 股票 ID
- `stock_code`: 股票代码
- `stock_name`: 股票名称
- `sync_count`: 同步的 K 线数据条数
- `new_count`: 新增的 K 线数据条数
- `update_count`: 更新的 K 线数据条数

## K 线数据结构

每条 K 线数据包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 ID |
| stock_id | int | 股票 ID |
| trade_date | date | 交易日期 |
| open | decimal | 开盘价 |
| high | decimal | 最高价 |
| low | decimal | 最低价 |
| close | decimal | 收盘价 |
| volume | bigint | 成交量 |
| amount | decimal | 成交额 |
| turnover_rate | decimal | 换手率 |
| pe_ratio | decimal | 市盈率（动态） |
| pb_ratio | decimal | 市净率 |
| total_market_cap | decimal | 总市值 |
| circulating_market_cap | decimal | 流通市值 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 错误响应

### 股票不存在

```json
{
  "code": 404,
  "message": "股票不存在",
  "data": null
}
```

### 日期格式错误

```json
{
  "code": 422,
  "message": "日期格式错误",
  "data": {
    "start_date": ["日期格式必须为 YYYY-MM-DD"]
  }
}
```

### 数据源错误

```json
{
  "code": 500,
  "message": "数据源请求失败",
  "data": {
    "error": "连接超时"
  }
}
```

## 注意事项

1. **数据来源**：K 线数据从第三方数据源获取，需确保网络连接正常
2. **同步频率**：建议每个交易日收盘后执行一次同步
3. **数据完整性**：同步失败的数据会在下次同步时重试
4. **存储限制**：历史 K 线数据占用大量存储空间，请定期清理
5. **API 限制**：第三方数据源可能有 API 调用频率限制
6. **数据延迟**：数据源可能存在 15-30 分钟的延迟

## 使用建议

### 定时同步

建议使用 Celery 定时任务每天自动同步：

```python
from celery import Celery
from datetime import datetime

celery = Celery('tasks')

@celery.task
def daily_kline_sync():
    """每天收盘后同步 K 线数据"""
    # 判断是否为交易日
    if is_trading_day():
        sync_all_kline_1d()

# 每天下午 3 点 30 分执行
celery.conf.beat_schedule = {
    'daily-kline-sync': {
        'task': 'daily_kline_sync',
        'schedule': crontab(hour=15, minute=30),
    },
}
```

### 增量同步

对于更新频率要求高的场景，可以每分钟同步一次最新数据：

```python
@celery.task
def minute_kline_sync():
    """每分钟同步最新 K 线"""
    sync_realtime_kline()
```

### 数据校验

同步完成后建议进行数据校验：

```python
def validate_kline_data(stock_id, date):
    """校验 K 线数据完整性"""
    kline = get_kline(stock_id, date)
    if not kline:
        return False
    # 检查必要字段
    required_fields = ['open', 'high', 'low', 'close', 'volume']
    for field in required_fields:
        if getattr(kline, field) is None:
            return False
    return True
```
