# 行业日志 API

本文档介绍了行业数据同步日志的 API 接口。行业日志记录了每次数据同步操作的详细信息。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/industry_log/index` | 获取行业日志列表 |
| DELETE | `/api/quant/industry_log/destroy_all` | 批量删除行业日志 |

## 获取行业日志列表

获取行业数据同步日志列表，支持分页和筛选。

**请求**：
```http
GET /api/quant/industry_log/index?page=1&limit=20
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| industry_id | int | 否 | 行业 ID 筛选 |
| sync_type | str | 否 | 同步类型：list/relation |
| status | str | 否 | 状态：success/failed/running |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "industry_id": 1,
        "industry_name": "银行",
        "sync_type": "list",
        "status": "success",
        "start_time": "2024-01-15 10:00:00",
        "end_time": "2024-01-15 10:05:23",
        "duration": 323,
        "created_count": 0,
        "updated_count": 5,
        "deleted_count": 0,
        "error_message": null,
        "created_at": "2024-01-15 10:05:23"
      },
      {
        "id": 2,
        "industry_id": 1,
        "industry_name": "银行",
        "sync_type": "relation",
        "status": "success",
        "start_time": "2024-01-15 10:06:00",
        "end_time": "2024-01-15 10:08:15",
        "duration": 135,
        "created_count": 42,
        "updated_count": 0,
        "deleted_count": 3,
        "error_message": null,
        "created_at": "2024-01-15 10:08:15"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

**字段说明**：
- `id`: 日志 ID
- `industry_id`: 行业 ID
- `industry_name`: 行业名称
- `sync_type`: 同步类型（list=行业列表同步, relation=关联关系同步）
- `status`: 状态（success=成功, failed=失败, running=进行中）
- `start_time`: 开始时间
- `end_time`: 结束时间
- `duration`: 执行时长（秒）
- `created_count`: 新增记录数
- `updated_count`: 更新记录数
- `deleted_count`: 删除记录数
- `error_message`: 错误信息（失败时）
- `created_at`: 创建时间

## 批量删除行业日志

批量删除指定的行业日志记录。

**请求**：
```http
DELETE /api/quant/industry_log/destroy_all
Content-Type: application/json
```

**请求体**：
```json
{
  "id_array": [1, 2, 3, 4, 5]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": {
    "deleted_count": 5
  }
}
```

**注意事项**：
- 删除日志不会影响实际数据
- 建议定期清理旧日志以节省存储空间
- 可以保留最近 30 天的日志用于问题排查

## 同步状态说明

| 状态 | 说明 |
|------|------|
| running | 同步任务正在执行 |
| success | 同步任务执行成功 |
| failed | 同步任务执行失败 |

## 同步类型说明

| 类型 | 说明 |
|------|------|
| list | 行业列表同步 |
| relation | 行业-股票关联关系同步 |

## 使用场景

### 查看同步历史

通过日志可以查看历史同步记录：

```http
GET /api/quant/industry_log/index?industry_id=1&sync_type=list
```

### 排查同步失败

查看失败的同步记录：

```http
GET /api/quant/industry_log/index?status=failed
```

### 清理旧日志

定期清理超过 30 天的日志：

```bash
DELETE /api/quant/industry_log/destroy_all
Body: {
  "id_array": [1, 2, ..., 1000]
}
```
