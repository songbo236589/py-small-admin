# Content API 文档

本文档提供了 Content 模块所有 API 接口的详细说明。

## 认证方式

### JWT 认证

大多数 API 需要使用 JWT 进行认证。

**请求头格式**：

```
Authorization: Bearer <access_token>
```

**获取 Token**：
调用 `/api/admin/common/login` 接口获取访问令牌。

### API Key 认证

部分 API 支持 API Key 认证。

**请求头格式**：

```
X-API-Key: <api_key>
```

---

## 请求格式

### Content-Type

- JSON 数据：`application/json`
- 表单数据：`multipart/form-data`

### 分页参数

| 参数 | 类型 | 必填 | 说明              |
| ---- | ---- | ---- | ----------------- |
| page | int  | 否   | 页码，默认 1      |
| size | int  | 否   | 每页数量，默认 10 |

### 排序参数

| 参数 | 类型 | 必填 | 说明                               |
| ---- | ---- | ---- | ---------------------------------- |
| sort | str  | 否   | 排序字段和方向，如 `{"id":"desc"}` |

### 搜索参数

| 参数    | 类型 | 必填 | 说明       |
| ------- | ---- | ---- | ---------- |
| keyword | str  | 否   | 搜索关键词 |
| filters | json | 否   | 过滤条件   |

---

## 文章管理 API

### 获取文章列表

```http
GET /api/content/article/index
```

**请求参数**：

| 参数        | 类型 | 必填 | 说明                                         |
| ----------- | ---- | ---- | -------------------------------------------- |
| page        | int  | 否   | 页码，默认 1                                 |
| size        | int  | 否   | 每页数量，默认 10                            |
| keyword     | str  | 否   | 搜索关键词（标题、摘要）                     |
| category_id | int  | 否   | 分类 ID                                      |
| status      | int  | 否   | 状态：0=草稿，1=已发布，2=审核中，3=发布失败 |
| sort        | str  | 否   | 排序参数                                     |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "如何学习 Python 编程？",
        "summary": "本文将介绍 Python 编程的基础知识...",
        "content": "# 如何学习 Python 编程\n\n...",
        "cover_image_id": 1,
        "status": 1,
        "author_id": 1,
        "category_id": 1,
        "category_name": "编程学习",
        "view_count": 100,
        "published_at": "2026-02-01 10:00:00",
        "created_at": "2026-02-01 10:00:00",
        "updated_at": "2026-02-01 10:00:00",
        "tags": [
          {
            "id": 1,
            "name": "Python",
            "color": "#1890ff"
          }
        ]
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10
  }
}
```

---

### 添加文章

```http
POST /api/content/article/add
Content-Type: multipart/form-data
```

**请求参数**：

| 参数           | 类型 | 必填 | 说明                           |
| -------------- | ---- | ---- | ------------------------------ |
| title          | str  | 是   | 文章标题                       |
| content        | str  | 是   | 文章内容（Markdown 格式）      |
| summary        | str  | 否   | 文章摘要                       |
| cover_image_id | int  | 否   | 封面图片 ID                    |
| category_id    | int  | 否   | 分类 ID                        |
| tag_ids        | str  | 否   | 标签 ID，多个用逗号分隔        |
| status         | int  | 否   | 状态：0=草稿，1=已发布，默认 0 |

**响应示例**：

```json
{
  "code": 200,
  "message": "添加成功",
  "data": null
}
```

---

### 获取文章编辑数据

```http
GET /api/content/article/edit/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 文章 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "title": "如何学习 Python 编程？",
    "summary": "本文将介绍 Python 编程的基础知识...",
    "content": "# 如何学习 Python 编程\n\n...",
    "cover_image_id": 1,
    "status": 1,
    "author_id": 1,
    "category_id": 1,
    "tag_ids": [1, 2],
    "created_at": "2026-02-01 10:00:00",
    "updated_at": "2026-02-01 10:00:00"
  }
}
```

---

### 更新文章

```http
PUT /api/content/article/update/{id}
Content-Type: multipart/form-data
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 文章 ID |

**请求参数**：

| 参数           | 类型 | 必填 | 说明                      |
| -------------- | ---- | ---- | ------------------------- |
| title          | str  | 否   | 文章标题                  |
| content        | str  | 否   | 文章内容（Markdown 格式） |
| summary        | str  | 否   | 文章摘要                  |
| cover_image_id | int  | 否   | 封面图片 ID               |
| category_id    | int  | 否   | 分类 ID                   |
| tag_ids        | str  | 否   | 标签 ID，多个用逗号分隔   |
| status         | int  | 否   | 状态：0=草稿，1=已发布    |

**响应示例**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

### 更新文章状态

```http
PUT /api/content/article/set_status/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 文章 ID |

**请求参数**：

| 参数   | 类型 | 必填 | 说明                                         |
| ------ | ---- | ---- | -------------------------------------------- |
| status | int  | 是   | 状态：0=草稿，1=已发布，2=审核中，3=发布失败 |

**响应示例**：

```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null
}
```

---

### 删除文章

```http
DELETE /api/content/article/destroy/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 文章 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 批量删除文章

```http
DELETE /api/content/article/destroy_all
Content-Type: application/json
```

**请求参数**：

| 参数     | 类型  | 必填 | 说明         |
| -------- | ----- | ---- | ------------ |
| id_array | array | 是   | 文章 ID 数组 |

**请求示例**：

```json
{
  "id_array": [1, 2, 3]
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "成功删除3条记录",
  "data": null
}
```

---

## 分类管理 API

### 获取分类列表

```http
GET /api/content/category/index
```

**请求参数**：

| 参数      | 类型 | 必填 | 说明                 |
| --------- | ---- | ---- | -------------------- |
| page      | int  | 否   | 页码，默认 1         |
| size      | int  | 否   | 每页数量，默认 10    |
| keyword   | str  | 否   | 搜索关键词（名称）   |
| status    | int  | 否   | 状态：0=禁用，1=启用 |
| parent_id | int  | 否   | 父分类 ID            |
| sort      | str  | 否   | 排序参数             |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "编程学习",
        "slug": "programming",
        "parent_id": null,
        "sort": 0,
        "status": 1,
        "description": "编程相关文章",
        "created_at": "2026-02-01 10:00:00",
        "updated_at": "2026-02-01 10:00:00",
        "children": [
          {
            "id": 2,
            "name": "Python",
            "slug": "python",
            "parent_id": 1,
            "sort": 0,
            "status": 1
          }
        ]
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

---

### 添加分类

```http
POST /api/content/category/add
Content-Type: application/json
```

**请求参数**：

| 参数        | 类型 | 必填 | 说明                         |
| ----------- | ---- | ---- | ---------------------------- |
| name        | str  | 是   | 分类名称                     |
| slug        | str  | 是   | 分类别名                     |
| parent_id   | int  | 否   | 父分类 ID                    |
| sort        | int  | 否   | 排序，默认 0                 |
| status      | int  | 否   | 状态：0=禁用，1=启用，默认 1 |
| description | str  | 否   | 分类描述                     |

**响应示例**：

```json
{
  "code": 200,
  "message": "添加成功",
  "data": null
}
```

---

### 获取分类编辑数据

```http
GET /api/content/category/edit/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 分类 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "编程学习",
    "slug": "programming",
    "parent_id": null,
    "sort": 0,
    "status": 1,
    "description": "编程相关文章"
  }
}
```

---

### 更新分类

```http
PUT /api/content/category/update/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 分类 ID |

**请求参数**：

| 参数        | 类型 | 必填 | 说明                 |
| ----------- | ---- | ---- | -------------------- |
| name        | str  | 否   | 分类名称             |
| slug        | str  | 否   | 分类别名             |
| parent_id   | int  | 否   | 父分类 ID            |
| sort        | int  | 否   | 排序                 |
| status      | int  | 否   | 状态：0=禁用，1=启用 |
| description | str  | 否   | 分类描述             |

**响应示例**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

### 更新分类状态

```http
PUT /api/content/category/set_status/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 分类 ID |

**请求参数**：

| 参数   | 类型 | 必填 | 说明                 |
| ------ | ---- | ---- | -------------------- |
| status | int  | 是   | 状态：0=禁用，1=启用 |

**响应示例**：

```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null
}
```

---

### 更新分类排序

```http
PUT /api/content/category/set_sort/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 分类 ID |

**请求参数**：

| 参数 | 类型 | 必填 | 说明   |
| ---- | ---- | ---- | ------ |
| sort | int  | 是   | 排序值 |

**响应示例**：

```json
{
  "code": 200,
  "message": "排序更新成功",
  "data": null
}
```

---

### 删除分类

```http
DELETE /api/content/category/destroy/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 分类 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 批量删除分类

```http
DELETE /api/content/category/destroy_all
Content-Type: application/json
```

**请求参数**：

| 参数     | 类型  | 必填 | 说明         |
| -------- | ----- | ---- | ------------ |
| id_array | array | 是   | 分类 ID 数组 |

**请求示例**：

```json
{
  "id_array": [1, 2, 3]
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "成功删除3条记录",
  "data": null
}
```

---

## 标签管理 API

### 获取标签列表

```http
GET /api/content/tag/index
```

**请求参数**：

| 参数    | 类型 | 必填 | 说明                 |
| ------- | ---- | ---- | -------------------- |
| page    | int  | 否   | 页码，默认 1         |
| size    | int  | 否   | 每页数量，默认 10    |
| keyword | str  | 否   | 搜索关键词（名称）   |
| status  | int  | 否   | 状态：0=禁用，1=启用 |
| sort    | str  | 否   | 排序参数             |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Python",
        "slug": "python",
        "color": "#1890ff",
        "sort": 0,
        "status": 1,
        "created_at": "2026-02-01 10:00:00",
        "updated_at": "2026-02-01 10:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

---

### 添加标签

```http
POST /api/content/tag/add
Content-Type: application/json
```

**请求参数**：

| 参数   | 类型 | 必填 | 说明                         |
| ------ | ---- | ---- | ---------------------------- |
| name   | str  | 是   | 标签名称                     |
| slug   | str  | 是   | 标签别名                     |
| color  | str  | 否   | 标签颜色，如 #1890ff         |
| sort   | int  | 否   | 排序，默认 0                 |
| status | int  | 否   | 状态：0=禁用，1=启用，默认 1 |

**响应示例**：

```json
{
  "code": 200,
  "message": "添加成功",
  "data": null
}
```

---

### 获取标签编辑数据

```http
GET /api/content/tag/edit/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 标签 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "Python",
    "slug": "python",
    "color": "#1890ff",
    "sort": 0,
    "status": 1
  }
}
```

---

### 更新标签

```http
PUT /api/content/tag/update/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 标签 ID |

**请求参数**：

| 参数   | 类型 | 必填 | 说明                 |
| ------ | ---- | ---- | -------------------- |
| name   | str  | 否   | 标签名称             |
| slug   | str  | 否   | 标签别名             |
| color  | str  | 否   | 标签颜色             |
| sort   | int  | 否   | 排序                 |
| status | int  | 否   | 状态：0=禁用，1=启用 |

**响应示例**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

### 更新标签状态

```http
PUT /api/content/tag/set_status/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 标签 ID |

**请求参数**：

| 参数   | 类型 | 必填 | 说明                 |
| ------ | ---- | ---- | -------------------- |
| status | int  | 是   | 状态：0=禁用，1=启用 |

**响应示例**：

```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null
}
```

---

### 更新标签排序

```http
PUT /api/content/tag/set_sort/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 标签 ID |

**请求参数**：

| 参数 | 类型 | 必填 | 说明   |
| ---- | ---- | ---- | ------ |
| sort | int  | 是   | 排序值 |

**响应示例**：

```json
{
  "code": 200,
  "message": "排序更新成功",
  "data": null
}
```

---

### 删除标签

```http
DELETE /api/content/tag/destroy/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 标签 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 批量删除标签

```http
DELETE /api/content/tag/destroy_all
Content-Type: application/json
```

**请求参数**：

| 参数     | 类型  | 必填 | 说明         |
| -------- | ----- | ---- | ------------ |
| id_array | array | 是   | 标签 ID 数组 |

**请求示例**：

```json
{
  "id_array": [1, 2, 3]
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "成功删除3条记录",
  "data": null
}
```

---

## 平台账号管理 API

### 获取账号列表

```http
GET /api/content/platform_account/index
```

**请求参数**：

| 参数     | 类型 | 必填 | 说明                         |
| -------- | ---- | ---- | ---------------------------- |
| page     | int  | 否   | 页码，默认 1                 |
| size     | int  | 否   | 每页数量，默认 10            |
| keyword  | str  | 否   | 搜索关键词（账号名称）       |
| platform | str  | 否   | 平台筛选（zhihu、xiaohongshu 等） |
| status   | int  | 否   | 状态：0=失效，1=有效，2=过期 |
| sort     | str  | 否   | 排序参数                     |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "platform": "zhihu",
        "account_name": "我的知乎账号",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "status": 1,
        "last_verified": "2026-02-09 12:00:00",
        "created_by": 1,
        "created_at": "2026-02-01 10:00:00",
        "updated_at": "2026-02-09 12:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

---

### 添加账号

```http
POST /api/content/platform_account/add
Content-Type: application/json
```

**请求参数**：

| 参数         | 类型 | 必填 | 说明                                 |
| ------------ | ---- | ---- | ------------------------------------ |
| platform     | str  | 是   | 平台标识（zhihu、juejin 等）         |
| account_name | str  | 是   | 账号名称                             |
| cookies      | str  | 是   | Cookie 信息（JSON 格式）             |
| user_agent   | str  | 否   | 浏览器 UA                            |
| status       | int  | 否   | 状态：0=失效，1=有效，2=过期，默认 1 |

**请求示例**：

```json
{
  "platform": "zhihu",
  "account_name": "我的知乎账号",
  "cookies": "[{\"name\":\"z_c0\",\"value\":\"xxx\",\"domain\":\".zhihu.com\",\"path\":\"/\"}]",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "添加成功",
  "data": null
}
```

---

### 获取账号编辑数据

```http
GET /api/content/platform_account/edit/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 账号 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "platform": "zhihu",
    "account_name": "我的知乎账号",
    "cookies": "[{\"name\":\"z_c0\",\"value\":\"xxx\",\"domain\":\".zhihu.com\",\"path\":\"/\"}]",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "status": 1,
    "created_by": 1,
    "created_at": "2026-02-01 10:00:00",
    "updated_at": "2026-02-09 12:00:00"
  }
}
```

---

### 更新账号

```http
PUT /api/content/platform_account/update/{id}
Content-Type: application/json
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 账号 ID |

**请求参数**：

| 参数         | 类型 | 必填 | 说明                         |
| ------------ | ---- | ---- | ---------------------------- |
| platform     | str  | 否   | 平台标识                     |
| account_name | str  | 否   | 账号名称                     |
| cookies      | str  | 否   | Cookie 信息（JSON 格式）     |
| user_agent   | str  | 否   | 浏览器 UA                    |
| status       | int  | 否   | 状态：0=失效，1=有效，2=过期 |

**响应示例**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

### 验证账号

```http
POST /api/content/platform_account/verify/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 账号 ID |

**说明**：

- 验证过程会启动 Playwright 浏览器访问平台页面
- 验证过程需要 10-30 秒
- 同一账号两次验证之间必须间隔至少 5 分钟
- Windows 用户需要特殊配置，详见浏览器自动化文档

**响应示例**：

```json
{
  "code": 200,
  "message": "验证成功，Cookie 有效",
  "data": {
    "id": 1,
    "platform": "zhihu",
    "account_name": "我的知乎账号",
    "status": 1,
    "last_verified": "2026-02-09 12:00:00"
  }
}
```

**错误响应示例**：

```json
{
  "code": 400,
  "message": "验证失败：Cookie 已失效，请重新获取",
  "data": null
}
```

---

### 删除账号

```http
DELETE /api/content/platform_account/destroy/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 账号 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## 发布管理 API

### 发布文章

```http
POST /api/content/publish/article/{article_id}
Content-Type: application/json
```

**路径参数**：

| 参数       | 类型 | 必填 | 说明    |
| ---------- | ---- | ---- | ------- |
| article_id | int  | 是   | 文章 ID |

**请求参数**：

| 参数       | 类型 | 必填 | 说明                              |
| ---------- | ---- | ---- | --------------------------------- |
| platform   | str  | 是   | 发布平台（zhihu、xiaohongshu 等） |
| account_id | int  | 是   | 平台账号 ID                  |

**请求示例**：

```json
{
  "platform": "zhihu",
  "account_id": 1
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "发布任务已创建",
  "data": {
    "task_id": "celery-task-id",
    "article_id": 1,
    "platform": "zhihu",
    "account_id": 1,
    "status": "待发布"
  }
}
```

---

### 批量发布

```http
POST /api/content/publish/batch
Content-Type: application/json
```

**请求参数**：

| 参数        | 类型  | 必填 | 说明         |
| ----------- | ----- | ---- | ------------ |
| article_ids | array | 是   | 文章 ID 数组 |
| platform    | str   | 是   | 发布平台     |
| account_id  | int   | 是   | 平台账号 ID  |

**请求示例**：

```json
{
  "article_ids": [1, 2, 3],
  "platform": "zhihu",
  "account_id": 1
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "批量发布任务已创建",
  "data": {
    "total": 3,
    "task_ids": ["task-id-1", "task-id-2", "task-id-3"]
  }
}
```

---

### 获取发布记录

```http
GET /api/content/publish/logs
```

**请求参数**：

| 参数       | 类型 | 必填 | 说明                                     |
| ---------- | ---- | ---- | ---------------------------------------- |
| page       | int  | 否   | 页码，默认 1                             |
| size       | int  | 否   | 每页数量，默认 10                        |
| article_id | int  | 否   | 文章 ID                                  |
| platform   | str  | 否   | 平台筛选                                 |
| status     | int  | 否   | 状态：0=待发布，1=发布中，2=成功，3=失败 |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "article_id": 1,
        "article_title": "如何学习 Python 编程？",
        "platform": "zhihu",
        "platform_article_id": "12345678",
        "platform_url": "https://zhuanlan.zhihu.com/p/12345678",
        "status": 2,
        "error_message": null,
        "retry_count": 0,
        "task_id": "celery-task-id",
        "created_at": "2026-02-01 10:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

---

### 获取发布记录详情

```http
GET /api/content/publish/logs/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明        |
| ---- | ---- | ---- | ----------- |
| id   | int  | 是   | 发布记录 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "article_id": 1,
    "article_title": "如何学习 Python 编程？",
    "platform": "zhihu",
    "platform_article_id": "12345678",
    "platform_url": "https://zhuanlan.zhihu.com/p/12345678",
    "status": 2,
    "error_message": null,
    "retry_count": 0,
    "task_id": "celery-task-id",
    "created_at": "2026-02-01 10:00:00"
  }
}
```

---

### 重试发布

```http
PUT /api/content/publish/retry/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明        |
| ---- | ---- | ---- | ----------- |
| id   | int  | 是   | 发布记录 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "重试任务已创建",
  "data": {
    "task_id": "celery-task-id-new",
    "retry_count": 1
  }
}
```

---

## 话题管理 API

### 获取话题列表

```http
GET /api/content/topic/index
```

**请求参数**：

| 参数     | 类型 | 必填 | 说明                               |
| -------- | ---- | ---- | ---------------------------------- |
| page     | int  | 否   | 页码，默认 1                       |
| size     | int  | 否   | 每页数量，默认 10                  |
| keyword  | str  | 否   | 搜索关键词（标题）                 |
| platform | str  | 否   | 平台筛选（zhihu、xiaohongshu 等）  |
| status   | int  | 否   | 状态：0=未使用，1=已使用，2=已收藏 |
| category | str  | 否   | 分类筛选                           |
| sort     | str  | 否   | 排序参数                           |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "platform": "zhihu",
        "platform_question_id": "12345678",
        "title": "如何学习 Python 编程？",
        "description": "我是编程初学者，想学习 Python...",
        "url": "https://www.zhihu.com/question/12345678",
        "view_count": 12500,
        "answer_count": 156,
        "follower_count": 89,
        "category": "编程学习",
        "hot_score": 14060,
        "author_name": "张三",
        "author_url": "https://www.zhihu.com/people/zhangsan",
        "status": 0,
        "fetched_at": "2026-02-01 10:00:00",
        "created_at": "2026-02-01 10:00:00",
        "updated_at": "2026-02-01 10:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10
  }
}
```

---

### 获取话题详情

```http
GET /api/content/topic/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 话题 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "platform": "zhihu",
    "platform_question_id": "12345678",
    "title": "如何学习 Python 编程？",
    "description": "我是编程初学者，想学习 Python...",
    "url": "https://www.zhihu.com/question/12345678",
    "view_count": 12500,
    "answer_count": 156,
    "follower_count": 89,
    "category": "编程学习",
    "hot_score": 14060,
    "author_name": "张三",
    "author_url": "https://www.zhihu.com/people/zhangsan",
    "status": 0,
    "fetched_at": "2026-02-01 10:00:00",
    "created_at": "2026-02-01 10:00:00",
    "updated_at": "2026-02-01 10:00:00"
  }
}
```

---

### 抓取话题

```http
GET /api/content/topic/fetch
```

**请求参数**：

| 参数                | 类型 | 必填 | 说明              |
| ------------------- | ---- | ---- | ----------------- |
| platform            | str  | 是   | 平台标识（zhihu） |
| platform_account_id | int  | 是   | 平台账号 ID       |
| limit               | int  | 否   | 抓取数量，默认 20 |

**说明**：

- 抓取过程需要 10-30 秒
- 前端需要设置超时时间为 60 秒
- 抓取期间请显示 Loading 状态

**响应示例**：

```json
{
  "code": 200,
  "message": "成功抓取 20 个话题（新增 15 个，更新 5 个）",
  "data": {
    "total": 20,
    "created": 15,
    "updated": 5,
    "skipped": 0,
    "platform": "zhihu"
  }
}
```

**错误响应示例**：

```json
{
  "code": 400,
  "message": "抓取失败：知乎账号未登录，请先验证账号状态",
  "data": null
}
```

---

### 使用话题

```http
POST /api/content/topic/{id}/use
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 话题 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "话题已标记为使用，可以开始写作",
  "data": {
    "id": 1,
    "title": "如何学习 Python 编程？",
    "description": "我是编程初学者，想学习 Python...",
    "url": "https://www.zhihu.com/question/12345678"
  }
}
```

---

### 收藏话题

```http
POST /api/content/topic/{id}/favorite
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 话题 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "话题已收藏",
  "data": {
    "id": 1,
    "status": 2
  }
}
```

---

### 删除话题

```http
DELETE /api/content/topic/{id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明    |
| ---- | ---- | ---- | ------- |
| id   | int  | 是   | 话题 ID |

**响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## AI 生成 API

### 获取可用模型

```http
GET /api/content/ai/models
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
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

---

### AI 生成文章

```http
POST /api/content/ai/generate_article
Content-Type: multipart/form-data
```

**请求参数**：

| 参数        | 类型 | 必填 | 说明                             |
| ----------- | ---- | ---- | -------------------------------- |
| id          | int  | 是   | 话题 ID                          |
| mode        | str  | 是   | 生成模式：title/description/full |
| title       | str  | 是   | 问题标题                         |
| description | str  | 否   | 问题描述                         |
| model       | str  | 是   | 指定 AI 模型                     |

**请求示例**：

```
id: 1
mode: description
title: 如何学习 Python 编程？
description: 我是一名编程初学者，想系统地学习 Python，请提供学习路线和建议。
model: qwen2.5:7b
```

**响应示例**：

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

---

## 错误码

| 错误码 | 说明         |
| ------ | ------------ |
| 200    | 成功         |
| 400    | 请求参数错误 |
| 401    | 未认证       |
| 403    | 无权限       |
| 404    | 资源不存在   |
| 500    | 服务器错误   |

---

## 相关文档

- [API 概览](./index.md)
- [内容发布功能](../guide/backend/features/content-publish.md)
- [话题管理功能](../guide/backend/features/topic-fetch.md)
- [AI 生成功能](../guide/backend/features/ai.md)
- [浏览器自动化](../guide/backend/features/browser.md)
