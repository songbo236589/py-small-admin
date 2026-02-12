# Content API 文档

本文档介绍了内容管理模块的 API 接口。

## 接口列表

### 平台账号管理

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/content/platform_account/index` | 获取平台账号列表（分页） | ✅ |
| POST | `/api/content/platform_account/add` | 添加平台账号 | ✅ |
| GET | `/api/content/platform_account/edit/{id}` | 获取平台账号详情 | ✅ |
| PUT | `/api/content/platform_account/update/{id}` | 更新平台账号信息 | ✅ |
| DELETE | `/api/content/platform_account/destroy/{id}` | 删除平台账号 | ✅ |
| POST | `/api/content/platform_account/verify/{id}` | 验证 Cookie 有效性 | ✅ |

### 浏览器扩展接口（公开）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/content/extension/platform/index` | 获取平台列表 | ❌ |
| POST | `/api/content/extension/platform_account/import_cookies` | 从浏览器扩展导入 Cookies | ❌ |

---

## 平台账号管理

### 获取平台账号列表

获取平台账号列表，支持搜索、筛选和分页。

**请求**：
```http
GET /api/content/platform_account/index?page=1&limit=20&platform=zhihu&status=1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| platform | string | 否 | 平台标识筛选：zhihu |
| account_name | string | 否 | 账号名称模糊搜索 |
| status | int | 否 | 状态筛选：0=失效, 1=有效, 2=过期 |
| sort | string | 否 | 排序规则，如 `id desc` |
| created_at[start] | string | 否 | 创建时间开始 |
| created_at[end] | string | 否 | 创建时间结束 |
| updated_at[start] | string | 否 | 更新时间开始 |
| updated_at[end] | string | 否 | 更新时间结束 |
| last_verified[start] | string | 否 | 验证时间开始 |
| last_verified[end] | string | 否 | 验证时间结束 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "platform": "zhihu",
        "account_name": "zhihu_账号",
        "cookies": "***HIDDEN***",
        "user_agent": "Mozilla/5.0...",
        "status": 1,
        "last_verified": "2024-01-01 12:00:00",
        "created_at": "2024-01-01 12:00:00",
        "updated_at": "2024-01-01 12:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

### 添加平台账号

手动添加第三方平台账号。

**请求**：
```http
POST /api/content/platform_account/add
Content-Type: multipart/form-data

platform: zhihu
account_name: 我的知乎账号
cookies: [{"name": "z_c0", "value": "xxx", "domain": ".zhihu.com"}]
user_agent: Mozilla/5.0...
status: 1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 是 | 平台标识：zhihu, juejin, csdn |
| account_name | string | 是 | 账号名称 |
| cookies | string | 是 | Cookie 信息（JSON 格式） |
| user_agent | string | 否 | 浏览器 UA |
| status | int | 是 | 状态：0=失效, 1=有效, 2=过期 |

**响应**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 1,
    "platform": "zhihu",
    "account_name": "我的知乎账号"
  }
}
```

### 获取平台账号详情

获取指定平台账号的详细信息，用于编辑。

**请求**：
```http
GET /api/content/platform_account/edit/1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 平台账号 ID（路径参数） |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "platform": "zhihu",
    "account_name": "我的知乎账号",
    "cookies": "[{\"name\": \"z_c0\", ...}]",
    "user_agent": "Mozilla/5.0...",
    "status": 1
  }
}
```

### 更新平台账号信息

更新指定平台账号的信息。

**请求**：
```http
PUT /api/content/platform_account/update/1
Content-Type: multipart/form-data

platform: zhihu
account_name: 我的知乎账号
cookies: [{"name": "z_c0", "value": "yyy", "domain": ".zhihu.com"}]
user_agent: Mozilla/5.0...
status: 1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 平台账号 ID（路径参数） |
| platform | string | 是 | 平台标识 |
| account_name | string | 是 | 账号名称 |
| cookies | string | 是 | Cookie 信息（JSON 格式） |
| user_agent | string | 否 | 浏览器 UA |
| status | int | 是 | 状态：0=失效, 1=有效, 2=过期 |

**响应**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 删除平台账号

删除指定的平台账号。

**请求**：
```http
DELETE /api/content/platform_account/destroy/1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 平台账号 ID（路径参数） |

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 验证 Cookie 有效性

使用 Playwright 自动验证平台账号的 Cookie 是否仍然有效。

**请求**：
```http
POST /api/content/platform_account/verify/1
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 平台账号 ID（路径参数） |

**响应**：
```json
{
  "code": 200,
  "message": "验证成功",
  "data": {
    "id": 1,
    "platform": "zhihu",
    "account_name": "我的知乎账号",
    "status": 1,
    "last_verified": "2024-01-01 12:00:00",
    "message": "验证成功，Cookie 有效"
  }
}
```

---

## 浏览器扩展接口（公开）

### 获取平台列表

获取所有支持的平台配置，供浏览器扩展显示。

**请求**：
```http
GET /api/content/extension/platform/index
```

**响应**：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": "zhihu",
      "name": "知乎",
      "domains": ["zhihu.com", "www.zhihu.com"],
      "icon": "https://static.zhihu.com/heifetz/favicon.ico"
    }
  ]
}
```

### 从浏览器扩展导入 Cookies

浏览器扩展调用此接口，自动识别平台并导入 Cookies。

**请求**：
```http
POST /api/content/extension/platform_account/import_cookies
Content-Type: application/json

{
  "cookies": [
    {
      "name": "z_c0",
      "value": "xxx",
      "domain": ".zhihu.com",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "expirationDate": 1234567890
    }
  ],
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| cookies | array | 是 | Cookie 数组 |
| cookies[].name | string | 是 | Cookie 名称 |
| cookies[].value | string | 是 | Cookie 值 |
| cookies[].domain | string | 是 | Cookie 域名 |
| cookies[].path | string | 否 | Cookie 路径 |
| cookies[].secure | boolean | 否 | 是否仅 HTTPS |
| cookies[].httpOnly | boolean | 否 | 是否 HttpOnly |
| cookies[].expirationDate | int | 否 | 过期时间戳 |
| userAgent | string | 是 | 浏览器 User-Agent |

**响应**：
```json
{
  "code": 200,
  "message": "Cookies导入成功",
  "data": {
    "message": "Cookies导入成功",
    "updated": [
      {
        "id": 1,
        "platform": "zhihu",
        "account_name": "zhihu_账号",
        "domain": "zhihu.com"
      }
    ],
    "created": [
      {
        "id": 2,
        "platform": "zhihu",
        "account_name": "zhihu_z_c0",
        "domain": "zhihu.com"
      }
    ],
    "errors": ["未知平台: example.com"],
    "summary": {
      "updated_count": 1,
      "created_count": 1,
      "error_count": 1
    }
  }
}
```

---

## AI 生成接口

### 获取可用 AI 模型列表

获取 Ollama 服务中已安装的 AI 模型列表。

**请求**：
```http
GET /api/content/ai/models
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "models": [
      {
        "name": "qwen2.5:7b",
        "size": 4705159863,
        "modified_at": "2026-02-10T10:00:00Z"
      },
      {
        "name": "llama3.2:8b",
        "size": 4935775934,
        "modified_at": "2026-02-09T15:30:00Z"
      }
    ]
  }
}
```

### AI 生成文章

使用指定的 AI 模型根据话题内容生成文章。

**请求**：
```http
POST /api/content/ai/generate_article
Content-Type: multipart/form-data

id: 1
mode: description
title: 如何学习 Python 编程？
description: 我是一名编程初学者，想系统地学习 Python，请提供学习路线和建议。
model: qwen2.5:7b
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 话题 ID |
| mode | string | 是 | 生成模式：title/description/full |
| title | string | 是 | 问题标题 |
| description | string | 否 | 问题描述 |
| model | string | 否 | 指定模型（可选，不指定则使用配置文件中的默认模型） |

**生成模式说明**：

| 模式 | 说明 | 输入 |
|------|------|------|
| title | 仅根据标题生成 | 仅使用 title |
| description | 根据标题和描述生成 | 使用 title + description |
| full | 完整生成（包含标题和描述） | 使用 title + description，生成更深入的内容 |

**响应**：
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "topic_id": 1,
    "title": "如何学习 Python 编程？",
    "content": "# 如何学习 Python 编程\n\n作为一名编程初学者，系统性地学习 Python 需要循序渐进...\n\n## 第一阶段：基础语法\n\n...",
    "model": "qwen2.5:7b"
  }
}
```

**错误响应**：
```json
{
  "code": 422,
  "message": "生成模式只能是: title, description, full",
  "data": null
}
```

**使用说明**：
- 使用前需要先安装并启动 Ollama 服务
- 需要提前拉取 AI 模型（如 `ollama pull qwen2.5:7b`）
- 生成时间取决于模型大小和内容复杂度，通常需要 10-60 秒
- 详细使用说明请参考 [AI 生成功能文档](../features/ai.md)

---

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录） |
| 403 | 无权限 |
| 404 | 记录不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器错误 |

---

## Cookie 格式说明

### Cookie JSON 格式

平台账号的 `cookies` 字段存储的是 JSON 格式的 Cookie 数组：

```json
[
  {
    "name": "z_c0",
    "value": "xxxxxx",
    "domain": ".zhihu.com",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "expirationDate": 1735660800
  }
]
```

### 如何获取 Cookie

1. **使用浏览器扩展**（推荐）
   - 安装项目提供的浏览器扩展
   - 登录目标平台（如知乎）
   - 点击扩展图标，选择平台，点击"导入 Cookies"

2. **手动获取**
   - 打开浏览器开发者工具（F12）
   - 切换到 Application > Cookies
   - 复制需要的 Cookie 并转换为 JSON 格式

---

## 相关文档

- [浏览器自动化功能](../features/browser.md)
- [内容发布功能](../features/content-publish.md)
- [AI 生成功能](../features/ai.md)
- [浏览器扩展使用指南](../../browser-extension.md)
