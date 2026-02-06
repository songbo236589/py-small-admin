# 角色管理 API

本文档介绍了角色管理的 API 接口。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/group/get_group_list` | 获取角色列表（简易） |
| GET | `/api/admin/group/index` | 获取角色列表（分页） |
| POST | `/api/admin/group/add` | 添加角色 |
| GET | `/api/admin/group/edit/{id}` | 获取角色详情 |
| PUT | `/api/admin/group/update/{id}` | 更新角色 |
| PUT | `/api/admin/group/set_status/{id}` | 更新角色状态 |
| DELETE | `/api/admin/group/destroy/{id}` | 删除角色 |
| DELETE | `/api/admin/group/destroy_all` | 批量删除角色 |
| GET | `/api/admin/group/get_access/{id}` | 获取角色权限配置 |
| PUT | `/api/admin/group/access_update/{id}` | 更新角色权限配置 |

## 获取角色列表（简易）

获取所有启用的角色列表，用于下拉选择等场景。

**请求**：
```http
GET /api/admin/group/get_group_list?status=1
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
      "name": "超级管理员组",
      "content": "拥有所有权限",
      "status": 1
    },
    {
      "id": 2,
      "name": "编辑组",
      "content": "只能编辑内容",
      "status": 1
    }
  ]
}
```

## 获取角色列表（分页）

获取角色列表，支持搜索、筛选和分页。

**请求**：
```http
GET /api/admin/group/index?page=1&limit=20&name=管理员&status=1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| name | str | 否 | 角色名称（模糊搜索） |
| content | str | 否 | 角色描述（模糊搜索） |
| status | int | 否 | 状态：0=禁用, 1=启用 |
| sort | str | 否 | 排序规则，如 `-id` |
| created_at[start] | str | 否 | 创建时间开始 |
| created_at[end] | str | 否 | 创建时间结束 |
| updated_at[start] | str | 否 | 更新时间开始 |
| updated_at[end] | str | 否 | 更新时间结束 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "超级管理员组",
        "content": "拥有所有权限",
        "status": 1,
        "rules": "1,2,3,4,5",
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

## 添加角色

创建新的角色。

**请求**：
```http
POST /api/admin/group/add
Content-Type: multipart/form-data
```

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 角色名称 |
| content | str | 否 | 角色描述 |
| status | int | 否 | 状态：0=禁用, 1=启用，默认 1 |

**响应**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 3,
    "name": "测试角色",
    "content": "这是一个测试角色",
    "status": 1
  }
}
```

## 获取角色详情

获取指定角色的详细信息，用于编辑页面。

**请求**：
```http
GET /api/admin/group/edit/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 角色 ID |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "超级管理员组",
    "content": "拥有所有权限",
    "status": 1,
    "rules": "1,2,3,4,5",
    "created_at": "2024-01-01 00:00:00",
    "updated_at": "2024-01-01 00:00:00"
  }
}
```

## 更新角色

更新指定角色的信息。

**请求**：
```http
PUT /api/admin/group/update/{id}
Content-Type: multipart/form-data
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 角色 ID |

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 角色名称 |
| content | str | 否 | 角色描述 |
| status | int | 是 | 状态：0=禁用, 1=启用 |

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "name": "超级管理员组",
    "content": "拥有所有权限",
    "status": 1
  }
}
```

## 更新角色状态

快速切换角色的启用/禁用状态。

**请求**：
```http
PUT /api/admin/group/set_status/{id}
Content-Type: multipart/form-data
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 角色 ID |

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

## 删除角色

删除指定的角色。

**请求**：
```http
DELETE /api/admin/group/destroy/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 角色 ID |

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**注意事项**：
- 如果角色下有关联的管理员，将无法删除
- ID 为 1 的超级管理员组无法删除

## 批量删除角色

批量删除多个角色。

**请求**：
```http
DELETE /api/admin/group/destroy_all
Content-Type: application/json
```

**请求体**：
```json
{
  "id_array": [2, 3, 4]
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

## 获取角色权限配置

获取指定角色的权限配置，用于权限配置页面。

**请求**：
```http
GET /api/admin/group/get_access/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 角色 ID |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "group": {
      "id": 1,
      "name": "超级管理员组"
    },
    "rules": [
      {
        "id": 1,
        "pid": 0,
        "name": "系统管理",
        "checked": true
      },
      {
        "id": 2,
        "pid": 1,
        "name": "管理员管理",
        "checked": true
      }
    ]
  }
}
```

## 更新角色权限配置

更新指定角色的权限配置。

**请求**：
```http
PUT /api/admin/group/access_update/{id}
Content-Type: application/json
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 角色 ID |

**请求体**：
```json
{
  "rules": "1,2,3,4,5,6,7,8"
}
```

**参数说明**：
- rules: 权限规则 ID 列表，用逗号分隔

**响应**：
```json
{
  "code": 200,
  "message": "权限配置更新成功",
  "data": null
}
```

**注意事项**：
- 权限规则对应菜单（Rule）的 ID
- 更新后，该角色的管理员将立即获得新的权限
- 权限变更会在下次登录时生效
