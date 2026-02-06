# 菜单管理 API

本文档介绍了菜单管理的 API 接口。菜单用于构建系统的导航结构，支持多级菜单。

## 菜单类型说明

菜单分为三种类型：

| 类型值 | 说明 | 特点 |
|--------|------|------|
| 1 | 模块 | 顶级模块，通常作为功能分组 |
| 2 | 目录 | 可展开的目录，包含子菜单 |
| 3 | 菜单 | 具体的页面或操作 |

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/rule/index` | 获取菜单列表（树形结构） |
| POST | `/api/admin/rule/add` | 添加菜单 |
| GET | `/api/admin/rule/edit/{id}` | 获取菜单详情 |
| PUT | `/api/admin/rule/update/{id}` | 更新菜单 |
| PUT | `/api/admin/rule/set_status/{id}` | 更新菜单状态 |
| PUT | `/api/admin/rule/set_sort/{id}` | 更新菜单排序 |
| DELETE | `/api/admin/rule/destroy/{id}` | 删除菜单 |

## 获取菜单列表

获取所有菜单，返回树形结构数据。

**请求**：
```http
GET /api/admin/rule/index
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "pid": 0,
      "name": "系统管理",
      "path": "/admin",
      "component": "",
      "redirect": "/admin/dashboard",
      "type": 1,
      "status": 1,
      "icon": "SettingOutlined",
      "sort": 1,
      "level": 1,
      "target": "_self",
      "children": [
        {
          "id": 2,
          "pid": 1,
          "name": "仪表盘",
          "path": "/admin/dashboard",
          "component": "admin/dashboard/index",
          "redirect": "",
          "type": 3,
          "status": 1,
          "icon": "DashboardOutlined",
          "sort": 1,
          "level": 2,
          "target": "_self",
          "children": []
        },
        {
          "id": 3,
          "pid": 1,
          "name": "认证管理",
          "path": "/admin/auth",
          "component": "",
          "redirect": "",
          "type": 2,
          "status": 1,
          "icon": "LockOutlined",
          "sort": 2,
          "level": 2,
          "target": "_self",
          "children": [
            {
              "id": 4,
              "pid": 3,
              "name": "管理员管理",
              "path": "/admin/auth/admin",
              "component": "admin/auth/admin/index",
              "type": 3,
              "status": 1,
              "sort": 1,
              "level": 3
            }
          ]
        }
      ]
    }
  ]
}
```

**字段说明**：
- `id`: 菜单 ID
- `pid`: 父级 ID，0 表示顶级菜单
- `name`: 菜单名称
- `path`: 路由路径
- `component`: 组件路径
- `redirect`: 重定向路径
- `type`: 菜单类型（1=模块, 2=目录, 3=菜单）
- `status`: 显示状态（0=隐藏, 1=显示）
- `icon`: 图标名称
- `sort`: 排序
- `level`: 层级
- `target`: 链接打开方式（_self/_blank）
- `children`: 子菜单列表

## 添加菜单

创建新的菜单。

**请求**：
```http
POST /api/admin/rule/add
Content-Type: multipart/form-data
```

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 菜单名称 |
| path | str | 否 | 路由路径 |
| component | str | 否 | 组件路径 |
| redirect | str | 否 | 重定向路径 |
| type | int | 否 | 菜单类型：1=模块, 2=目录, 3=菜单，默认 1 |
| status | int | 否 | 显示状态：0=隐藏, 1=显示，默认 1 |
| icon | str | 否 | 图标名称 |
| pid | int | 否 | 父级 ID，默认 0 |
| sort | int | 否 | 排序，默认 1 |
| target | str | 否 | 链接打开方式：_self/_blank |

**请求示例**：
```bash
curl -X POST http://localhost:8000/api/admin/rule/add \
  -H "Authorization: Bearer <token>" \
  -F "name=测试菜单" \
  -F "path=/admin/test" \
  -F "component=admin/test/index" \
  -F "type=3" \
  -F "pid=1" \
  -F "icon=TestOutlined"
```

**响应**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 10,
    "name": "测试菜单",
    "path": "/admin/test",
    "component": "admin/test/index",
    "type": 3,
    "status": 1,
    "pid": 1,
    "sort": 1,
    "icon": "TestOutlined"
  }
}
```

## 获取菜单详情

获取指定菜单的详细信息，用于编辑页面。

**请求**：
```http
GET /api/admin/rule/edit/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 菜单 ID |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 2,
    "pid": 1,
    "name": "仪表盘",
    "path": "/admin/dashboard",
    "component": "admin/dashboard/index",
    "redirect": "",
    "type": 3,
    "status": 1,
    "icon": "DashboardOutlined",
    "sort": 1,
    "level": 2,
    "target": "_self",
    "created_at": "2024-01-01 00:00:00",
    "updated_at": "2024-01-01 00:00:00"
  }
}
```

## 更新菜单

更新指定菜单的信息。

**请求**：
```http
PUT /api/admin/rule/update/{id}
Content-Type: multipart/form-data
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 菜单 ID |

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 是 | 菜单名称 |
| path | str | 否 | 路由路径 |
| component | str | 否 | 组件路径 |
| redirect | str | 否 | 重定向路径 |
| type | int | 否 | 菜单类型：1=模块, 2=目录, 3=菜单 |
| status | int | 否 | 显示状态：0=隐藏, 1=显示 |
| icon | str | 否 | 图标名称 |
| pid | int | 否 | 父级 ID |
| sort | int | 否 | 排序 |
| target | str | 否 | 链接打开方式：_self/_blank |

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 2,
    "name": "仪表盘",
    "path": "/admin/dashboard",
    "component": "admin/dashboard/index",
    "type": 3,
    "status": 1
  }
}
```

## 更新菜单状态

快速切换菜单的显示/隐藏状态。

**请求**：
```http
PUT /api/admin/rule/set_status/{id}
Content-Type: multipart/form-data
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 菜单 ID |

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | int | 是 | 显示状态：0=隐藏, 1=显示 |

**响应**：
```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null
}
```

## 更新菜单排序

更新菜单的排序值。

**请求**：
```http
PUT /api/admin/rule/set_sort/{id}
Content-Type: multipart/form-data
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 菜单 ID |

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

## 删除菜单

删除指定的菜单。

**请求**：
```http
DELETE /api/admin/rule/destroy/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 菜单 ID |

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**注意事项**：
- 如果菜单下有子菜单，将无法删除
- 删除菜单后，关联的角色权限也会被清除
- 建议先将菜单状态设置为隐藏，而不是直接删除

## 图标列表

系统使用 Ant Design Icons，常用图标如下：

| 图标名称 | 说明 | 适用场景 |
|----------|------|----------|
| DashboardOutlined | 仪表盘 | 首页、控制台 |
| SettingOutlined | 设置 | 系统设置 |
| UserOutlined | 用户 | 用户管理 |
| LockOutlined | 锁 | 权限管理 |
| FileOutlined | 文件 | 文件管理 |
| DatabaseOutlined | 数据库 | 数据管理 |
| BarChartOutlined | 图表 | 数据统计 |
| TeamOutlined | 团队 | 角色管理 |
| MenuOutlined | 菜单 | 菜单管理 |
| AppstoreOutlined | 应用 | 模块管理 |

更多图标请参考 [Ant Design Icons](https://ant.design/components/icon-cn/)。
