---
title: API 名称
description: API 的简要描述
---

# API 名称

API 的简要描述，说明其用途和功能。

:::info 信息
API 基础 URL：`http://localhost:5000/api`
:::

## 请求

### 请求方法

`GET` /api/users

### 请求参数

| 参数名 | 类型 | 必填 | 说明    | 示例   |
| ------ | ---- | ---- | ------- | ------ |
| id     | int  | 是   | 用户 ID | 1      |
| name   | str  | 否   | 用户名  | "张三" |
| page   | int  | 否   | 页码    | 1      |

:::tip 提示
所有参数都应该进行验证和清理。
:::

### 请求示例

#### cURL

```bash
curl -X GET "http://localhost:5000/api/users?id=1&page=1" \
  -H "Content-Type: application/json"
```

#### Python

```python
import requests

# 发送 GET 请求
response = requests.get(
    'http://localhost:5000/api/users',
    params={'id': 1, 'page': 1}
)

# 输出：{"code": 200, "message": "success", "data": [...]}
print(response.json())
```

#### JavaScript

```javascript
// 使用 fetch API
fetch("http://localhost:5000/api/users?id=1&page=1")
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## 响应

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "张三",
    "email": "zhangsan@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 响应参数

| 参数名     | 类型   | 说明     | 示例      |
| ---------- | ------ | -------- | --------- |
| code       | int    | 状态码   | 200       |
| message    | str    | 提示信息 | "success" |
| data       | object | 数据对象 | {...}     |
| pagination | object | 分页信息 | {...}     |

#### data 对象

| 参数名     | 类型 | 说明     | 示例                   |
| ---------- | ---- | -------- | ---------------------- |
| id         | int  | 用户 ID  | 1                      |
| name       | str  | 用户名   | "张三"                 |
| email      | str  | 邮箱地址 | "zhangsan@example.com" |
| created_at | str  | 创建时间 | "2024-01-01T00:00:00Z" |

#### pagination 对象

| 参数名    | 类型 | 说明       | 示例 |
| --------- | ---- | ---------- | ---- |
| total     | int  | 总记录数   | 100  |
| page      | int  | 当前页码   | 1    |
| page_size | int  | 每页记录数 | 20   |

## 错误码

| 错误码 | 说明         | 解决方案           |
| ------ | ------------ | ------------------ |
| 200    | 请求成功     | -                  |
| 400    | 参数错误     | 检查请求参数       |
| 401    | 未授权       | 提供有效的认证令牌 |
| 404    | 资源不存在   | 检查资源 ID        |
| 429    | 请求过于频繁 | 降低请求频率       |
| 500    | 服务器错误   | 联系管理员         |

### 错误响应示例

```json
{
  "code": 400,
  "message": "参数错误：id 不能为空",
  "errors": [
    {
      "field": "id",
      "message": "id 不能为空"
    }
  ]
}
```

:::warning 警告
错误响应可能包含多个错误，需要逐一处理。
:::

## 认证

### Bearer Token 认证

在请求头中添加认证令牌：

```bash
curl -X GET "http://localhost:5000/api/users" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### API Key 认证

在请求头中添加 API Key：

```bash
curl -X GET "http://localhost:5000/api/users" \
  -H "X-API-Key: YOUR_API_KEY"
```

:::danger 危险
不要在客户端代码中暴露 API Key 或 Token。
:::

## 速率限制

- **免费用户**: 每小时 100 次请求
- **付费用户**: 每小时 1000 次请求

### 速率限制响应

```json
{
  "code": 429,
  "message": "请求过于频繁",
  "retry_after": 3600
}
```

## 版本控制

### 当前版本

`v1.0`

### 版本历史

| 版本 | 发布日期   | 主要变更 |
| ---- | ---------- | -------- |
| v1.0 | 2024-01-01 | 初始版本 |

## 相关 API

- [创建用户 API](./create-user-api.md)
- [更新用户 API](./update-user-api.md)
- [删除用户 API](./delete-user-api.md)

## 示例代码

### 完整示例

```python
import requests
import time

class UserAPI:
    """用户 API 客户端"""

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_user(self, user_id):
        """获取用户信息"""
        url = f'{self.base_url}/api/users'
        params = {'id': user_id}

        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_users(self, page=1, page_size=20):
        """获取用户列表"""
        url = f'{self.base_url}/api/users'
        params = {'page': page, 'page_size': page_size}

        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

# 使用示例
api = UserAPI('http://localhost:5000', 'your_token_here')

# 获取单个用户
user = api.get_user(1)
if user:
    print(f"用户: {user['data']['name']}")

# 获取用户列表
users = api.get_users(page=1)
if users:
    print(f"总用户数: {users['pagination']['total']}")
```

## 常见问题

### 如何处理速率限制？

实现指数退避策略：

```python
import time

def make_request_with_retry(url, max_retries=3):
    """带重试的请求"""
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 60)
            print(f"速率限制，等待 {retry_after} 秒...")
            time.sleep(retry_after)
        else:
            return response
    return None
```

### 如何处理分页？

使用 `pagination` 对象：

```python
def get_all_users(api):
    """获取所有用户"""
    all_users = []
    page = 1

    while True:
        result = api.get_users(page=page)
        if not result:
            break

        all_users.extend(result['data'])

        # 检查是否还有更多数据
        if len(all_users) >= result['pagination']['total']:
            break

        page += 1

    return all_users
```

## 更新日志

### v1.0 (2024-01-01)

- 初始版本发布
- 支持基本的 CRUD 操作
- 实现分页功能
- 添加认证支持

## 支持与反馈

如果遇到问题或有建议，请：

- 提交 [GitHub Issue](https://github.com/songbo236589/py-small-admin/issues)
- 发送邮件到 support@example.com
- 查看[常见问题](../guides/faq.md)
