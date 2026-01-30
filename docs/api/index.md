# API 概览

本文档提供了 Py Small Admin 所有 API 接口的概览。

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

## 请求格式

### Content-Type

- JSON 数据：`application/json`
- 表单数据：`multipart/form-data`

### 分页参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页数量，默认 10 |

### 排序参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sort_field | str | 否 | 排序字段 |
| sort_order | str | 否 | 排序方向，asc/desc，默认 desc |

### 搜索参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | str | 否 | 搜索关键词 |
| filters | json | 否 | 过滤条件 |

## 响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 响应数据
  }
}
```

### 分页响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "error message",
  "data": null
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

详细的错误码说明请参考 [错误码说明](./error-codes.md)。

## API 列表

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/common/login` | 用户登录 |
| POST | `/api/admin/common/logout` | 用户登出 |
| POST | `/api/admin/common/refresh_token` | 刷新令牌 |

### Admin 模块

#### 管理员管理

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

#### 角色管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/group/get_group_list` | 获取角色列表 |
| GET | `/api/admin/group/index` | 获取角色列表或搜索角色 |
| POST | `/api/admin/group/add` | 添加角色 |
| GET | `/api/admin/group/edit/{id}` | 获取角色详情 |
| PUT | `/api/admin/group/update/{id}` | 更新角色 |
| PUT | `/api/admin/group/set_status/{id}` | 更新角色状态 |
| DELETE | `/api/admin/group/destroy/{id}` | 删除角色 |
| DELETE | `/api/admin/group/destroy_all` | 批量删除角色 |
| GET | `/api/admin/group/get_access/{id}` | 配置权限规则页面数据 |
| PUT | `/api/admin/group/access_update/{id}` | 配置权限规则 |

#### 菜单管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/rule/index` | 获取菜单列表 |
| POST | `/api/admin/rule/add` | 添加菜单 |
| GET | `/api/admin/rule/edit/{id}` | 获取菜单详情 |
| PUT | `/api/admin/rule/update/{id}` | 更新菜单 |
| PUT | `/api/admin/rule/set_status/{id}` | 更新菜单状态 |
| DELETE | `/api/admin/rule/destroy/{id}` | 删除菜单 |
| DELETE | `/api/admin/rule/destroy_all` | 批量删除菜单 |

#### 系统配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/sys_config/index` | 获取系统配置 |
| PUT | `/api/admin/sys_config/update` | 更新系统配置 |
| POST | `/api/admin/sys_config/test_email` | 测试邮件发送 |

#### 文件上传

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/upload/image` | 图片上传 |
| POST | `/api/admin/upload/document` | 文档上传 |
| POST | `/api/admin/upload/video` | 视频上传 |
| POST | `/api/admin/upload/audio` | 音频上传 |
| GET | `/api/admin/upload/index` | 获取文件列表 |
| DELETE | `/api/admin/upload/destroy/{id}` | 删除文件 |

### Quant 模块

#### 股票管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/stock/index` | 获取股票列表 |
| POST | `/api/quant/stock/add` | 添加股票 |
| GET | `/api/quant/stock/edit/{id}` | 获取股票详情 |
| PUT | `/api/quant/stock/update/{id}` | 更新股票信息 |
| PUT | `/api/quant/stock/set_status/{id}` | 更新股票状态 |
| DELETE | `/api/quant/stock/destroy/{id}` | 删除股票 |
| DELETE | `/api/quant/stock/destroy_all` | 批量删除股票 |
| POST | `/api/quant/stock/sync_stock_list` | 手动同步股票列表 |

#### 行业管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/industry/index` | 获取行业列表 |
| POST | `/api/quant/industry/add` | 添加行业 |
| GET | `/api/quant/industry/edit/{id}` | 获取行业详情 |
| PUT | `/api/quant/industry/update/{id}` | 更新行业信息 |
| PUT | `/api/quant/industry/set_status/{id}` | 更新行业状态 |
| DELETE | `/api/quant/industry/destroy/{id}` | 删除行业 |
| DELETE | `/api/quant/industry/destroy_all` | 批量删除行业 |
| POST | `/api/quant/industry/sync_industry_list` | 手动同步行业列表 |

#### 概念管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/concept/index` | 获取概念列表 |
| POST | `/api/quant/concept/add` | 添加概念 |
| GET | `/api/quant/concept/edit/{id}` | 获取概念详情 |
| PUT | `/api/quant/concept/update/{id}` | 更新概念信息 |
| PUT | `/api/quant/concept/set_status/{id}` | 更新概念状态 |
| DELETE | `/api/quant/concept/destroy/{id}` | 删除概念 |
| DELETE | `/api/quant/concept/destroy_all` | 批量删除概念 |
| POST | `/api/quant/concept/sync_concept_list` | 手动同步概念列表 |

#### 历史记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/industry_log/index` | 获取行业历史记录 |
| GET | `/api/quant/concept_log/index` | 获取概念历史记录 |

#### K线数据

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/quant/stock_kline/index` | 获取K线数据 |
| POST | `/api/quant/stock_kline/add` | 添加K线数据 |
| GET | `/api/quant/stock_kline/edit/{id}` | 获取K线数据详情 |
| PUT | `/api/quant/stock_kline/update/{id}` | 更新K线数据 |
| DELETE | `/api/quant/stock_kline/destroy/{id}` | 删除K线数据 |
| DELETE | `/api/quant/stock_kline/destroy_all` | 批量删除K线数据 |

## 在线文档

完整的交互式 API 文档可以通过以下方式访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API 测试工具

### 使用 Swagger UI

访问 http://localhost:8000/docs，直接在浏览器中测试 API。

### 使用 curl

```bash
# 登录获取 Token
curl -X POST http://localhost:8000/api/admin/common/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# 使用 Token 访问受保护的接口
curl -X GET http://localhost:8000/api/admin/admin/index \
  -H "Authorization: Bearer <access_token>"
```

### 使用 Postman

1. 导入 OpenAPI 规范：http://localhost:8000/openapi.json
2. 配置环境变量
3. 测试接口

### 使用 Python requests

```python
import requests

# 登录获取 Token
response = requests.post(
    "http://localhost:8000/api/admin/common/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["data"]["access_token"]

# 使用 Token 访问受保护的接口
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/admin/admin/index",
    headers=headers
)
print(response.json())
```

## 速率限制

为了避免滥用，API 有速率限制：

- 每个用户每分钟最多 100 次请求
- 超过限制将返回 429 错误

## 版本控制

当前 API 版本：v1

API 版本通过 URL 路径标识：`/api/v1/...`

未来可能会引入新版本，旧版本会继续维护一段时间。

## 变更日志

### v1.0.0 (2024-01-30)

- 初始版本发布
- Admin 模块 API
- Quant 模块 API

## 支持

如果你在使用 API 时遇到问题：

1. 查看 [错误码说明](./error-codes.md)
2. 查看 [常见问题](../faq/)
3. 提交 [GitHub Issue](https://github.com/songbo236589/py-small-admin/issues)
