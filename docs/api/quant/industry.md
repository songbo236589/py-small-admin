# 行业管理 API

本文档介绍了行业管理的 API 接口。行业数据用于股票分类和分析。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/industry/index` | 获取行业列表 |
| GET | `/api/quant/industry/simple` | 获取行业简单列表 |
| POST | `/api/quant/industry/add` | 添加行业 |
| GET | `/api/quant/industry/edit/{id}` | 获取行业详情 |
| PUT | `/api/quant/industry/update/{id}` | 更新行业 |
| PUT | `/api/quant/industry/set_status/{id}` | 更新行业状态 |
| PUT | `/api/quant/industry/set_sort/{id}` | 更新行业排序 |
| DELETE | `/api/quant/industry/destroy/{id}` | 删除行业 |
| DELETE | `/api/quant/industry/destroy_all` | 批量删除行业 |
| POST | `/api/quant/industry/sync_list` | 同步行业列表 |
| POST | `/api/quant/industry/sync_relation` | 同步行业-股票关联关系 |

## 获取行业列表

获取行业列表，支持分页和搜索。

**请求**：
```http
GET /api/quant/industry/index?page=1&limit=20&name=金融
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| name | str | 否 | 行业名称（模糊搜索） |
| status | int | 否 | 状态：0=禁用, 1=启用 |

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
        "description": "银行业股票",
        "status": 1,
        "sort": 1,
        "stock_count": 42,
        "created_at": "2024-01-01 00:00:00",
        "updated_at": "2024-01-01 00:00:00"
      },
      {
        "id": 2,
        "name": "房地产",
        "description": "房地产行业股票",
        "status": 1,
        "sort": 2,
        "stock_count": 35,
        "created_at": "2024-01-01 00:00:00",
        "updated_at": "2024-01-01 00:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "limit": 20
  }
}
```

## 获取行业简单列表

获取所有启用的行业简单列表，用于下拉选择等场景。

**请求**：
```http
GET /api/quant/industry/simple?status=1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | int | 否 | 状态筛选：0=禁用, 1=启用 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "银行"
    },
    {
      "id": 2,
      "name": "房地产"
    },
    {
      "id": 3,
      "name": "电子信息"
    }
  ]
}
```

## 添加行业

创建新的行业。

**请求**：
```http
POST /api/quant/industry/add
Content-Type: application/json
```

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 行业名称 |
| description | str | 否 | 行业描述 |
| status | int | 否 | 状态：0=禁用, 1=启用，默认 1 |
| sort | int | 否 | 排序，默认 0 |

**请求示例**：
```json
{
  "name": "新能源汽车",
  "description": "新能源汽车相关股票",
  "status": 1,
  "sort": 10
}
```

**响应**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 10,
    "name": "新能源汽车",
    "description": "新能源汽车相关股票",
    "status": 1,
    "sort": 10
  }
}
```

## 获取行业详情

获取指定行业的详细信息。

**请求**：
```http
GET /api/quant/industry/edit/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 行业 ID |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "银行",
    "description": "银行业股票",
    "status": 1,
    "sort": 1,
    "stock_count": 42,
    "created_at": "2024-01-01 00:00:00",
    "updated_at": "2024-01-01 00:00:00"
  }
}
```

## 更新行业

更新指定行业的信息。

**请求**：
```http
PUT /api/quant/industry/update/{id}
Content-Type: application/json
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 行业 ID |

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 行业名称 |
| description | str | 否 | 行业描述 |
| status | int | 是 | 状态：0=禁用, 1=启用 |
| sort | int | 否 | 排序 |

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "name": "银行业",
    "description": "银行业相关股票",
    "status": 1
  }
}
```

## 更新行业状态

快速切换行业的启用/禁用状态。

**请求**：
```http
PUT /api/quant/industry/set_status/{id}
Content-Type: application/json
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 行业 ID |

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | int | 是 | 状态：0=禁用, 1=启用 |

**响应**：
```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null
}
```

## 更新行业排序

更新行业的排序值。

**请求**：
```http
PUT /api/quant/industry/set_sort/{id}
Content-Type: application/json
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 行业 ID |

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sort | int | 是 | 排序值 |

**响应**：
```json
{
  "code": 200,
  "message": "排序更新成功",
  "data": null
}
```

## 删除行业

删除指定的行业。

**请求**：
```http
DELETE /api/quant/industry/destroy/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 行业 ID |

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**注意事项**：
- 删除行业后，关联的股票-行业关系也会被删除
- 建议先将行业状态设置为禁用，而不是直接删除

## 批量删除行业

批量删除多个行业。

**请求**：
```http
DELETE /api/quant/industry/destroy_all
Content-Type: application/json
```

**请求体**：
```json
{
  "id_array": [1, 2, 3]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": null
}
```

## 同步行业列表

从数据源同步行业列表数据。该操作会创建或更新行业记录。

**请求**：
```http
POST /api/quant/industry/sync_list
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "created": 5,
    "updated": 10,
    "total": 15
  }
}
```

**响应字段说明**：
- `created`: 新创建的行业数量
- `updated`: 更新的行业数量
- `total`: 处理的行业总数

## 同步行业-股票关联关系

从数据源同步行业与股票的关联关系。

**请求**：
```http
POST /api/quant/industry/sync_relation
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "created": 150,
    "deleted": 20,
    "total": 170
  }
}
```

**响应字段说明**：
- `created`: 新创建的关联关系数量
- `deleted`: 删除的关联关系数量
- `total`: 处理的关联关系总数

**注意事项**：
- 同步操作可能需要较长时间，建议使用异步任务
- 同步期间请勿重复提交请求
- 同步数据来源由系统配置决定
