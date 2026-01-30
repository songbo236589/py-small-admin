# 股票管理 API

本文档介绍了股票管理的 API 接口。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/stock/index` | 获取股票列表 |
| POST | `/api/quant/stock/add` | 添加股票 |
| GET | `/api/quant/stock/edit/{id}` | 获取股票详情 |
| PUT | `/api/quant/stock/update/{id}` | 更新股票信息 |
| PUT | `/api/quant/stock/set_status/{id}` | 更新股票状态 |
| DELETE | `/api/quant/stock/destroy/{id}` | 删除股票 |
| DELETE | `/api/quant/stock/destroy_all` | 批量删除股票 |
| POST | `/api/quant/stock/sync_stock_list` | 同步股票列表 |

## 获取股票列表

**请求**：
```http
GET /api/quant/stock/index?page=1&size=10&keyword=600000&market=1
```

**参数**：
- page: 页码
- size: 每页数量
- keyword: 搜索关键词（股票代码/名称）
- market: 市场类型（1=上海，2=深圳，3=北京，4=港股，5=美股）
- status: 上市状态

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "stock_code": "600000.SH",
        "stock_name": "浦发银行",
        "market": 1,
        "industry_id": 1,
        "industry_name": "银行",
        "list_status": 1,
        "trade_status": 1,
        "is_st": 0,
        "stock_type": 1,
        "latest_price": 10.50,
        "change_percent": 1.23,
        "change_amount": 0.13
      }
    ],
    "total": 10000,
    "page": 1,
    "size": 10
  }
}
```

## 同步股票列表

**请求**：
```http
POST /api/quant/stock/sync_stock_list
Content-Type: application/json
Authorization: Bearer <token>
```

**响应**：
```json
{
  "code": 200,
  "message": "同步任务已提交",
  "data": {
    "task_id": "task_1234567890",
    "message": "股票数据同步任务已添加到队列"
  }
}
```

## 添加股票

**请求**：
```http
POST /api/quant/stock/add
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "stock_code": "600000.SH",
  "stock_name": "浦发银行",
  "market": 1,
  "industry_id": 1,
  "description": "浦发银行简介"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 1,
    "stock_code": "600000.SH",
    "stock_name": "浦发银行"
  }
}
```

## 更新股票

**请求**：
```http
PUT /api/quant/stock/update/{id}
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "stock_name": "浦发银行",
  "description": "更新后的简介"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "stock_name": "浦发银行"
  }
}
```
