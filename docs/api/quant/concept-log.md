# 概念日志 API

本文档介绍了概念数据同步日志的 API 接口。概念日志记录了每次数据同步操作的详细信息。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/concept_log/index` | 获取概念日志列表 |
| DELETE | `/api/quant/concept_log/destroy_all` | 批量删除概念日志 |

## 获取概念日志列表

获取概念数据同步日志列表，支持分页和筛选。

**请求**：
```http
GET /api/quant/concept_log/index?page=1&limit=20
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| concept_id | int | 否 | 概念 ID 筛选 |
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
        "concept_id": 1,
        "concept_name": "人工智能",
        "sync_type": "list",
        "status": "success",
        "start_time": "2024-01-15 10:00:00",
        "end_time": "2024-01-15 10:03:15",
        "duration": 195,
        "created_count": 2,
        "updated_count": 8,
        "deleted_count": 0,
        "error_message": null,
        "created_at": "2024-01-15 10:03:15"
      },
      {
        "id": 2,
        "concept_id": 1,
        "concept_name": "人工智能",
        "sync_type": "relation",
        "status": "success",
        "start_time": "2024-01-15 10:04:00",
        "end_time": "2024-01-15 10:06:30",
        "duration": 150,
        "created_count": 85,
        "updated_count": 12,
        "deleted_count": 5,
        "error_message": null,
        "created_at": "2024-01-15 10:06:30"
      }
    ],
    "total": 200,
    "page": 1,
    "limit": 20
  }
}
```

**字段说明**：
- `id`: 日志 ID
- `concept_id`: 概念 ID
- `concept_name`: 概念名称
- `sync_type`: 同步类型（list=概念列表同步, relation=关联关系同步）
- `status`: 状态（success=成功, failed=失败, running=进行中）
- `start_time`: 开始时间
- `end_time`: 结束时间
- `duration`: 执行时长（秒）
- `created_count`: 新增记录数
- `updated_count`: 更新记录数
- `deleted_count`: 删除记录数
- `error_message`: 错误信息（失败时）
- `created_at`: 创建时间

## 批量删除概念日志

批量删除指定的概念日志记录。

**请求**：
```http
DELETE /api/quant/concept_log/destroy_all
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
| list | 概念列表同步 |
| relation | 概念-股票关联关系同步 |

## 使用场景

### 查看同步历史

通过日志可以查看历史同步记录：

```http
GET /api/quant/concept_log/index?concept_id=1&sync_type=list
```

### 排查同步失败

查看失败的同步记录：

```http
GET /api/quant/concept_log/index?status=failed
```

### 清理旧日志

定期清理超过 30 天的日志：

```bash
DELETE /api/quant/concept_log/destroy_all
Body: {
  "id_array": [1, 2, ..., 2000]
}
```

## 与行业日志的区别

概念日志与行业日志的结构和功能基本相同，主要区别在于：

| 特性 | 行业日志 | 概念日志 |
|------|----------|----------|
| 记录对象 | 行业数据同步 | 概念数据同步 |
| 数据量 | 相对较少 | 通常较多 |
| 更新频率 | 较低 | 较高 |
| 关联股票数 | 每个行业约几十只 | 每个概念可达上百只 |

概念数据通常比行业数据更新更频繁，因为市场热点概念变化较快。建议更密切地关注概念同步日志，及时发现和解决同步问题。
