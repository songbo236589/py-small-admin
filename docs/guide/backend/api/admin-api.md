# Admin API 文档

本文档介绍了管理员管理模块的 API 接口。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/index` | 获取管理员列表（分页） |
| POST | `/api/admin/add` | 添加管理员 |
| GET | `/api/admin/edit/{id}` | 获取管理员详情 |
| PUT | `/api/admin/update/{id}` | 更新管理员信息 |
| PUT | `/api/admin/set_status/{id}` | 更新管理员状态 |
| DELETE | `/api/admin/destroy/{id}` | 删除管理员 |
| DELETE | `/api/admin/destroy_all` | 批量删除管理员 |
| PUT | `/api/admin/reset_pwd/{id}` | 重置管理员密码 |

## 获取管理员列表

获取管理员列表，支持搜索、筛选和分页。

**请求**：
```http
GET /api/admin/index?page=1&limit=20&username=admin&status=1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| username | string | 否 | 用户名模糊搜索 |
| name | string | 否 | 真实姓名模糊搜索 |
| phone | string | 否 | 手机号模糊搜索 |
| status | int | 否 | 状态筛选：0=禁用, 1=启用 |
| group_id | int | 否 | 角色组 ID |
| sort | string | 否 | 排序规则，如 `id desc` |
| created_at[start] | string | 否 | 创建时间开始 |
| created_at[end] | string | 否 | 创建时间结束 |
| updated_at[start] | string | 否 | 更新时间开始 |
| updated_at[end] | string | 否 | 更新时间结束 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "name": "超级管理员",
        "phone": "13800138000",
        "group_id": 1,
        "group_name": "超级管理员组",
        "status": 1,
        "created_at": "2024-01-01 12:00:00",
        "updated_at": "2024-01-01 12:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

## 添加管理员

创建新的管理员账号。

**请求**：
```http
POST /api/admin/add
Content-Type: multipart/form-data

username: new_admin
name: 新管理员
password: password123
phone: 13900139000
status: 1
group_id: 2
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，唯一 |
| name | string | 是 | 真实姓名 |
| password | string | 是 | 密码 |
| phone | string | 否 | 手机号 |
| status | int | 是 | 状态：0=禁用, 1=启用 |
| group_id | int | 是 | 角色组 ID |

**响应**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 2,
    "username": "new_admin",
    "name": "新管理员"
  }
}
```

## 获取管理员详情

获取指定管理员的详细信息，用于编辑。

**请求**：
```http
GET /api/admin/edit/1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 管理员 ID（路径参数） |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "name": "超级管理员",
    "phone": "13800138000",
    "group_id": 1,
    "status": 1
  }
}
```

## 更新管理员信息

更新指定管理员的信息。

**请求**：
```http
PUT /api/admin/update/1
Content-Type: multipart/form-data

username: admin
name: 超级管理员
phone: 13800138000
status: 1
group_id: 1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 管理员 ID（路径参数） |
| username | string | 是 | 用户名 |
| name | string | 是 | 真实姓名 |
| phone | string | 否 | 手机号 |
| status | int | 是 | 状态：0=禁用, 1=启用 |
| group_id | int | 是 | 角色组 ID |

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

## 更新管理员状态

快速切换管理员的启用/禁用状态。

**请求**：
```http
PUT /api/admin/set_status/1
Content-Type: multipart/form-data

status: 0
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 管理员 ID（路径参数） |
| status | int | 是 | 状态：0=禁用, 1=启用 |

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

## 删除管理员

删除指定的管理员（软删除）。

**请求**：
```http
DELETE /api/admin/destroy/1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 管理员 ID（路径参数） |

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

## 批量删除管理员

批量删除多个管理员。

**请求**：
```http
DELETE /api/admin/destroy_all
Content-Type: application/json

{
  "id_array": [1, 2, 3]
}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id_array | array | 是 | 管理员 ID 数组 |

**响应**：
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": null
}
```

## 重置管理员密码

重置指定管理员的密码为默认密码。

**请求**：
```http
PUT /api/admin/reset_pwd/1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 管理员 ID（路径参数） |

**响应**：
```json
{
  "code": 200,
  "message": "密码重置成功",
  "data": {
    "new_password": "123456"
  }
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 无权限 |
| 404 | 记录不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器错误 |
