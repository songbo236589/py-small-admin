# 管理员管理 API

本文档介绍了管理员管理的 API 接口。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/admin/index` | 获取管理员列表 |
| POST | `/api/admin/admin/add` | 添加管理员 |
| GET | `/api/admin/admin/edit/{id}` | 获取管理员详情 |
| PUT | `/api/admin/admin/update/{id}` | 更新管理员 |
| PUT | `/api/admin/admin/set_status/{id}` | 更新管理员状态 |
| DELETE | `/api/admin/admin/destroy/{id}` | 删除管理员 |
| DELETE | `/api/admin/admin/destroy_all` | 批量删除管理员 |
| PUT | `/api/admin/admin/reset_pwd/{id}` | 重置管理员密码 |

## 获取管理员列表

**请求**：
```http
GET /api/admin/admin/index?page=1&size=10&keyword=admin&status=1
```

**参数**：
- page: 页码
- size: 每页数量
- keyword: 搜索关键词
- status: 状态

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "超级管理员",
        "username": "admin",
        "phone": "13800138000",
        "status": 1,
        "group_id": 1,
        "group_name": "超级管理员组"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

## 添加管理员

**请求**：
```http
POST /api/admin/admin/add
Content-Type: application/json
```

**请求体**：
```json
{
  "name": "张三",
  "username": "zhangsan",
  "password": "password123",
  "phone": "13800138000",
  "group_id": 1
}
```

**响应**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 2,
    "name": "张三",
    "username": "zhangsan"
  }
}
```

## 更新管理员

**请求**：
```http
PUT /api/admin/admin/update/{id}
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "name": "李四",
  "phone": "13900139000"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "name": "李四"
  }
}
```

## 删除管理员

**请求**：
```http
DELETE /api/admin/admin/destroy/{id}
Authorization: Bearer <token>
```

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

## 批量删除管理员

**请求**：
```http
DELETE /api/admin/admin/destroy_all
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "ids": [1, 2, 3]
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

## 重置管理员密码

重置管理员的密码为系统默认密码。

**请求**：
```http
PUT /api/admin/admin/reset_pwd/{id}
Authorization: Bearer <token>
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | number | 是 | 管理员 ID |

**响应**：
```json
{
  "code": 200,
  "message": "密码重置成功，新密码为{password}",
  "data": null
}
```

**注意事项**：
- 此接口会将密码重置为系统默认密码（配置在 `APP_DEFAULT_ADMIN_PASSWORD`）
- 新密码会在响应消息中返回，请妥善保存
- ID 为 1 的超级管理员无法重置密码
- 建议用户首次登录后立即修改密码
