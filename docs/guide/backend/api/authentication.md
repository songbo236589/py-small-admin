# 认证 API 文档

本文档介绍了用户认证相关的 API 接口，包括登录、登出、令牌刷新等。

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/login` | 用户登录 |
| POST | `/api/logout` | 用户登出 |
| POST | `/api/refresh_token` | 刷新访问令牌 |
| GET | `/api/get_user_info` | 获取当前用户信息 |
| PUT | `/api/change_password` | 修改当前用户密码 |
| GET | `/api/get_menu_tree` | 获取当前用户菜单树 |
| GET | `/api/captcha` | 获取验证码 |

## 用户登录

使用用户名和密码登录系统。

**请求**：
```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123",
  "captcha": "1234",
  "captcha_id": "uuid-string"
}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| captcha | string | 是 | 验证码 |
| captcha_id | string | 是 | 验证码 ID |

**响应**：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 7200,
    "refresh_expires_in": 604800,
    "access_expires_at": "2024-01-01T14:00:00Z",
    "refresh_expires_at": "2024-01-08T12:00:00Z"
  }
}
```

## 用户登出

退出登录，将当前令牌加入黑名单。

**请求**：
```http
POST /api/logout
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | 是 | 刷新令牌 |

**响应**：
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

## 刷新访问令牌

使用刷新令牌获取新的访问令牌。

**请求**：
```http
POST /api/refresh_token
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | 是 | 刷新令牌 |

**响应**：
```json
{
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access_expires_in": 7200,
    "access_expires_at": "2024-01-01T14:00:00Z"
  }
}
```

## 获取当前用户信息

获取当前登录用户的详细信息。

**请求**：
```http
GET /api/get_user_info
Authorization: Bearer {access_token}
```

**响应**：
```json
{
  "code": 200,
  "message": "获取用户信息成功",
  "data": {
    "id": 1,
    "username": "admin",
    "name": "超级管理员",
    "phone": "13800138000",
    "group_id": 1,
    "group_name": "超级管理员组",
    "status": 1
  }
}
```

## 修改当前用户密码

修改当前登录用户的密码。

**请求**：
```http
PUT /api/change_password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "old_password123",
  "new_password": "new_password456"
}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 旧密码 |
| new_password | string | 是 | 新密码 |

**响应**：
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

## 获取当前用户菜单树

获取当前用户有权访问的菜单树结构。

**请求**：
```http
GET /api/get_menu_tree
Authorization: Bearer {access_token}
```

**响应**：
```json
{
  "code": 200,
  "message": "获取菜单树成功",
  "data": [
    {
      "id": 1,
      "path": "/admin",
      "component": "",
      "redirect": "/admin/dashboard",
      "name": "系统管理",
      "type": 1,
      "status": 1,
      "icon": "SettingOutlined",
      "pid": 0,
      "target": "_self",
      "children": [
        {
          "id": 2,
          "path": "/admin/dashboard",
          "component": "admin/dashboard/index",
          "name": "仪表盘",
          "type": 3,
          "status": 1,
          "icon": "DashboardOutlined",
          "pid": 1,
          "target": "_self",
          "children": []
        }
      ]
    }
  ]
}
```

## 获取验证码

获取图形验证码，用于登录验证。

**请求**：
```http
GET /api/captcha
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "captcha_id": "uuid-string",
    "captcha_image": "data:image/png;base64,iVBORw0KGgoAAAANS..."
  }
}
```

## 认证流程

### 1. 登录流程

```
客户端 → 获取验证码 → 服务器
客户端 → 提交登录信息 + 验证码 → 服务器验证 → 返回令牌
客户端 → 存储令牌 → 后续请求携带令牌
```

### 2. 令牌刷新流程

```
客户端 → 检测令牌即将过期
客户端 → 使用 refresh_token 请求刷新 → 服务器验证 → 返回新 access_token
客户端 → 更新存储的 access_token
```

### 3. 令牌使用

所有需要认证的接口都需要在请求头中携带令牌：

```http
Authorization: Bearer {access_token}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权或令牌无效 |
| 403 | 无权限访问 |
| 422 | 数据验证失败（如用户名密码错误） |
| 500 | 服务器错误 |

## 安全建议

1. **HTTPS**: 生产环境必须使用 HTTPS 传输
2. **令牌存储**: 前端应安全存储令牌（推荐使用 httpOnly cookie）
3. **令牌刷新**: 在令牌过期前自动刷新
4. **密码强度**: 建议密码长度不少于 8 位，包含字母、数字和特殊字符
5. **验证码**: 登录时应使用验证码防止暴力破解
