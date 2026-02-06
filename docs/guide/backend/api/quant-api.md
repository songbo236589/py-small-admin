# Quant API 文档

本文档介绍了量化数据管理模块的 API 接口。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/stock/index` | 获取股票列表 |
| POST | `/api/quant/stock/add` | 添加股票 |
| GET | `/api/quant/stock/edit/{id}` | 获取股票详情 |
| PUT | `/api/quant/stock/update/{id}` | 更新股票信息 |
| DELETE | `/api/quant/stock/destroy/{id}` | 删除股票 |
| POST | `/api/quant/stock/sync` | 同步股票数据 |
| GET | `/api/quant/industry/index` | 获取行业列表 |
| POST | `/api/quant/industry/add` | 添加行业 |
| PUT | `/api/quant/industry/update/{id}` | 更新行业信息 |
| DELETE | `/api/quant/industry/destroy/{id}` | 删除行业 |
| POST | `/api/quant/industry/sync` | 同步行业数据 |
| GET | `/api/quant/concept/index` | 获取概念列表 |
| POST | `/api/quant/concept/add` | 添加概念 |
| PUT | `/api/quant/concept/update/{id}` | 更新概念信息 |
| DELETE | `/api/quant/concept/destroy/{id}` | 删除概念 |
| POST | `/api/quant/concept/sync` | 同步概念数据 |

## 股票管理

### 获取股票列表

**请求**：
```http
GET /api/quant/stock/index?page=1&limit=20&code=000001
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| code | string | 否 | 股票代码 |
| name | string | 否 | 股票名称 |
| industry_id | int | 否 | 行业 ID |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "000001",
        "name": "平安银行",
        "pinyin": "payh",
        "industry_id": 1,
        "industry_name": "银行",
        "status": 1
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

### 同步股票数据

**请求**：
```http
POST /api/quant/stock/sync
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "total": 5000,
    "synced": 5000,
    "failed": 0
  }
}
```

## 行业管理

### 获取行业列表

**请求**：
```http
GET /api/quant/industry/index?page=1&limit=20
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "银行",
        "code": "yh",
        "stock_count": 42,
        "status": 1
      }
    ],
    "total": 50,
    "page": 1,
    "limit": 20
  }
}
```

### 同步行业数据

**请求**：
```http
POST /api/quant/industry/sync
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "total": 50,
    "synced": 50,
    "failed": 0
  }
}
```

## 概念管理

### 获取概念列表

**请求**：
```http
GET /api/quant/concept/index?page=1&limit=20
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "新能源汽车",
        "code": "xnyqc",
        "stock_count": 158,
        "status": 1
      }
    ],
    "total": 200,
    "page": 1,
    "limit": 20
  }
}
```

### 同步概念数据

**请求**：
```http
POST /api/quant/concept/sync
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "total": 200,
    "synced": 200,
    "failed": 0
  }
}
```

## 历史数据查询

### 获取行业历史记录

**请求**：
```http
GET /api/quant/industry_log/index?page=1&limit=20&date=2024-01-01
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "date": "2024-01-01",
        "industry_id": 1,
        "industry_name": "银行",
        "stock_count": 42,
        "change": 1.5
      }
    ],
    "total": 1000,
    "page": 1,
    "limit": 20
  }
}
```

### 获取概念历史记录

**请求**：
```http
GET /api/quant/concept_log/index?page=1&limit=20&date=2024-01-01
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "date": "2024-01-01",
        "concept_id": 1,
        "concept_name": "新能源汽车",
        "stock_count": 158,
        "change": 2.3
      }
    ],
    "total": 2000,
    "page": 1,
    "limit": 20
  }
}
```

## K 线数据

### 获取股票 K 线数据

**请求**：
```http
GET /api/quant/stock/kline?code=000001&period=day&start=2024-01-01&end=2024-01-31
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码 |
| period | string | 否 | 周期：day/week/month，默认 day |
| start | string | 否 | 开始日期 |
| end | string | 否 | 结束日期 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "code": "000001",
    "name": "平安银行",
    "klines": [
      {
        "date": "2024-01-01",
        "open": 12.50,
        "close": 12.80,
        "high": 12.90,
        "low": 12.45,
        "volume": 12345678
      }
    ]
  }
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 数据不存在 |
| 500 | 服务器错误 |
