# 概念管理 API

本文档介绍了概念管理的 API 接口。概念数据用于股票主题分类和热点分析。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/concept/index` | 获取概念列表 |
| GET | `/api/quant/concept/simple` | 获取概念简单列表 |
| POST | `/api/quant/concept/add` | 添加概念 |
| GET | `/api/quant/concept/edit/{id}` | 获取概念详情 |
| PUT | `/api/quant/concept/update/{id}` | 更新概念 |
| PUT | `/api/quant/concept/set_status/{id}` | 更新概念状态 |
| PUT | `/api/quant/concept/set_sort/{id}` | 更新概念排序 |
| DELETE | `/api/quant/concept/destroy/{id}` | 删除概念 |
| DELETE | `/api/quant/concept/destroy_all` | 批量删除概念 |
| POST | `/api/quant/concept/sync_list` | 同步概念列表 |
| POST | `/api/quant/concept/sync_relation` | 同步概念-股票关联关系 |

## 获取概念列表

获取概念列表，支持分页和搜索。

**请求**：
```http
GET /api/quant/concept/index?page=1&limit=20&name=人工智能
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| name | str | 否 | 概念名称（模糊搜索） |
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
        "name": "人工智能",
        "description": "人工智能相关概念股票",
        "status": 1,
        "sort": 1,
        "stock_count": 85,
        "created_at": "2024-01-01 00:00:00",
        "updated_at": "2024-01-01 00:00:00"
      },
      {
        "id": 2,
        "name": "新能源汽车",
        "description": "新能源汽车相关概念股票",
        "status": 1,
        "sort": 2,
        "stock_count": 62,
        "created_at": "2024-01-01 00:00:00",
        "updated_at": "2024-01-01 00:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

## 获取概念简单列表

获取所有启用的概念简单列表，用于下拉选择等场景。

**请求**：
```http
GET /api/quant/concept/simple?status=1
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
      "name": "人工智能"
    },
    {
      "id": 2,
      "name": "新能源汽车"
    },
    {
      "id": 3,
      "name": "5G概念"
    }
  ]
}
```

## 添加概念

创建新的概念。

**请求**：
```http
POST /api/quant/concept/add
Content-Type: application/json
```

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 概念名称 |
| description | str | 否 | 概念描述 |
| status | int | 否 | 状态：0=禁用, 1=启用，默认 1 |
| sort | int | 否 | 排序，默认 0 |

**请求示例**：
```json
{
  "name": "元宇宙",
  "description": "元宇宙相关概念股票",
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
    "id": 20,
    "name": "元宇宙",
    "description": "元宇宙相关概念股票",
    "status": 1,
    "sort": 10
  }
}
```

## 获取概念详情

获取指定概念的详细信息。

**请求**：
```http
GET /api/quant/concept/edit/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 概念 ID |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "人工智能",
    "description": "人工智能相关概念股票",
    "status": 1,
    "sort": 1,
    "stock_count": 85,
    "created_at": "2024-01-01 00:00:00",
    "updated_at": "2024-01-01 00:00:00"
  }
}
```

## 更新概念

更新指定概念的信息。

**请求**：
```http
PUT /api/quant/concept/update/{id}
Content-Type: application/json
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 概念 ID |

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 概念名称 |
| description | str | 否 | 概念描述 |
| status | int | 是 | 状态：0=禁用, 1=启用 |
| sort | int | 否 | 排序 |

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "name": "AI芯片",
    "description": "AI芯片相关概念股票",
    "status": 1
  }
}
```

## 更新概念状态

快速切换概念的启用/禁用状态。

**请求**：
```http
PUT /api/quant/concept/set_status/{id}
Content-Type: application/json
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 概念 ID |

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

## 更新概念排序

更新概念的排序值。

**请求**：
```http
PUT /api/quant/concept/set_sort/{id}
Content-Type: application/json
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 概念 ID |

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

## 删除概念

删除指定的概念。

**请求**：
```http
DELETE /api/quant/concept/destroy/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 概念 ID |

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**注意事项**：
- 删除概念后，关联的股票-概念关系也会被删除
- 建议先将概念状态设置为禁用，而不是直接删除

## 批量删除概念

批量删除多个概念。

**请求**：
```http
DELETE /api/quant/concept/destroy_all
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

## 同步概念列表

从数据源同步概念列表数据。该操作会创建或更新概念记录。

**请求**：
```http
POST /api/quant/concept/sync_list
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "created": 10,
    "updated": 25,
    "total": 35
  }
}
```

**响应字段说明**：
- `created`: 新创建的概念数量
- `updated`: 更新的概念数量
- `total`: 处理的概念总数

## 同步概念-股票关联关系

从数据源同步概念与股票的关联关系。

**请求**：
```http
POST /api/quant/concept/sync_relation
```

**响应**：
```json
{
  "code": 200,
  "message": "同步成功",
  "data": {
    "created": 320,
    "deleted": 45,
    "total": 365
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
