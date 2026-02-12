# 内容发布功能

本系统支持将文章自动发布到第三方平台（如知乎、掘金等）。

## 功能概述

### 支持的平台

| 平台 | Cookie 验证 | 文章发布 | 备注 |
|------|------------|---------|------|
| 知乎 | ✅ 已支持 | 🚧 开发中 | 使用 Cookie 认证 + 完整反检测机制 |
| 掘金 | 🚧 计划中 | 🚧 计划中 | - |
| CSDN | 🚧 计划中 | 🚧 计划中 | - |

### 发布流程

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 创建文章 │───▶│ 获取账号 │───▶│ 发布文章 │───▶│ 记录日志 │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                            │
                            ▼
                      ┌─────────┐
                      │ Cookie  │
                      │ 验证    │
                      └─────────┘
```

## 使用方法

### 1. 获取平台 Cookie

使用浏览器扩展获取各平台的登录 Cookie：

1. 安装浏览器扩展（[下载](/downloads/py-small-admin-extension.zip)）
2. 在目标平台登录（如知乎）
3. 点击扩展图标，获取并发送 Cookie 到后端

### 2. 验证账号

验证 Cookie 是否仍然有效：

```bash
POST /api/content/platform_account/verify/{id}
```

返回示例：

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

**验证限制**：

- 为防止频繁验证，同一账号两次验证之间必须间隔至少 5 分钟（可配置）
- 验证过程会启动无头浏览器访问平台页面
- 完整的反检测机制确保验证安全
- 验证结果会更新账号状态和最后验证时间

**Windows 用户注意**：

在 Windows 系统上使用 Cookie 验证功能需要特殊配置，详见 [浏览器自动化功能文档 - Windows 系统特殊配置](./browser.md#windows-系统特殊配置)。

### 3. 发布文章

发布文章到指定平台：

```bash
POST /api/content/publish/article/{article_id}
Content-Type: application/json

{
  "platform": "zhihu",
  "account_id": 1
}
```

## 浏览器扩展

### 功能特性

| 功能 | 说明 |
|------|------|
| 本地 Cookie 获取 | 使用 Chrome Cookies API |
| 平台列表展示 | 显示支持的平台列表 |
| 按平台分组显示 | 显示每个平台获取到的 Cookie 数量 |
| 点击复制 JSON | 复制 Cookie 详情 |
| 选择性发送 | 只有指定平台可发送到后端 |
| 重新获取 | 支持刷新获取最新 Cookies |

### 安装方式

1. 下载扩展包：[py-small-admin-extension.zip](/downloads/py-small-admin-extension.zip)
2. 解压到本地目录
3. 打开 Chrome 扩展管理页面：`chrome://extensions/`
4. 开启"开发者模式"
5. 点击"加载已解压的扩展程序"
6. 选择解压后的目录

### 扩展界面

```
┌─────────────────────────────────────┐
│  Py Small Admin Login Helper   ⚙️  │
├─────────────────────────────────────┤
│  一键获取各技术平台的登录信息        │
├─────────────────────────────────────┤
│                                     │
│  [一键获取登录信息]                 │
│                                     │
│  获取到的平台：                     │
│                                     │
│  知乎                               │
│  已获取 15 个 Cookie 📋              │
│                      [发送到后端]   │
└─────────────────────────────────────┘
```

## API 接口

### 平台账号管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/content/platform_account/index` | GET | 获取账号列表 |
| `/api/content/platform_account/add` | POST | 添加账号 |
| `/api/content/platform_account/update/{id}` | PUT | 更新账号 |
| `/api/content/platform_account/destroy/{id}` | DELETE | 删除账号 |
| `/api/content/platform_account/verify/{id}` | POST | 验证 Cookie |

### 浏览器扩展接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/content/extension/platform/index` | GET | 获取支持的平台列表 |
| `/api/content/extension/platform_account/import_cookies` | POST | 导入 Cookies |

### 发布管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/content/publish/article/{id}` | POST | 发布文章 |
| `/api/content/publish/batch` | POST | 批量发布 |
| `/api/content/publish/logs` | GET | 发布记录 |
| `/api/content/publish/retry/{id}` | PUT | 重试发布 |

## 技术实现

### 技术栈

- **浏览器自动化**：Playwright
- **Cookie 存储**：JSON 格式加密存储
- **异步任务**：Celery + RabbitMQ
- **日志记录**：完整的发布日志
- **反检测机制**：随机延迟、人类行为模拟

### 反检测配置

为降低平台封号风险，系统实现了完整的反检测机制：

#### 反检测特性

| 特性 | 默认值 | 说明 |
|------|--------|------|
| 随机延迟 | 1-3 秒 | 每个操作之间随机延迟，模拟人类操作节奏 |
| 页面滚动 | 1-3 次 | 随机滚动页面，模拟浏览行为 |
| 鼠标移动 | 2-4 次 | 随机移动鼠标位置，增加真实性 |
| 停留时间 | 成功 5-8 秒 / 失败 2-4 秒 | 根据验证结果停留不同时长 |
| 验证间隔 | 最小 5 分钟 | 防止频繁验证被检测 |

#### 环境变量配置

在 `.env` 文件中配置反检测参数：

```bash
# 反检测配置（降低平台封号风险）
CONTENT_HUMAN_BEHAVIOR_ENABLED=true        # 是否启用人类行为模拟
CONTENT_RANDOM_DELAY_MIN=1.0               # 操作间最小随机延迟时间（秒）
CONTENT_RANDOM_DELAY_MAX=3.0               # 操作间最大随机延迟时间（秒）
CONTENT_VERIFY_INTERVAL_MIN=300            # 最小验证间隔（秒），默认 5 分钟
CONTENT_STAY_TIME_SUCCESS_MIN=5.0          # 验证成功后最小停留时间（秒）
CONTENT_STAY_TIME_SUCCESS_MAX=8.0          # 验证成功后最大停留时间（秒）
CONTENT_STAY_TIME_FAILED_MIN=2.0           # 验证失败后最小停留时间（秒）
CONTENT_STAY_TIME_FAILED_MAX=4.0           # 验证失败后最大停留时间（秒）
CONTENT_SCROLL_COUNT_MIN=1                 # 最小滚动次数
CONTENT_SCROLL_COUNT_MAX=3                 # 最大滚动次数
CONTENT_MOUSE_MOVE_COUNT_MIN=2             # 最小鼠标移动次数
CONTENT_MOUSE_MOVE_COUNT_MAX=4             # 最大鼠标移动次数
```

#### 人类行为模拟

Cookie 验证过程会模拟真实用户的浏览行为：

1. **随机延迟**：每个操作之间随机延迟 1-3 秒
2. **页面滚动**：随机滚动 1-3 次，每次滚动 100-500 像素
3. **鼠标移动**：随机移动鼠标 2-4 次，模拟用户浏览
4. **停留时间**：根据验证结果停留不同时长（成功 5-8 秒，失败 2-4 秒）

这些行为会自动执行，无需额外配置。如需禁用，将 `CONTENT_HUMAN_BEHAVIOR_ENABLED` 设置为 `false`。

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      内容发布架构                            │
└─────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  浏览器扩展    │────▶│   后端 API    │────▶│  Playwright  │
  │              │     │              │     │   验证器      │
  │  Cookie 获取 │     │  Cookie 存储 │     │              │
  │              │     │              │     │  登录检测     │
  └──────────────┘     └──────────────┘     └──────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Celery     │
                         │  异步任务队列 │
                         └──────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  发布日志     │
                         └──────────────┘
```

### 数据模型

#### 平台账号表 (content_platform_accounts)

| 字段 | 说明 |
|------|------|
| id | 主键 ID |
| platform | 平台标识（zhihu、juejin 等） |
| account_name | 账号名称 |
| cookies | Cookie 信息（JSON 格式） |
| user_agent | 浏览器 UA |
| status | 状态（0=失效，1=有效，2=过期） |
| last_verified | 最后验证时间 |

#### 发布日志表 (content_publish_logs)

| 字段 | 说明 |
|------|------|
| id | 主键 ID |
| article_id | 文章 ID |
| platform | 发布平台 |
| platform_article_id | 平台文章 ID |
| platform_url | 平台文章链接 |
| status | 发布状态（0=待发布，1=发布中，2=成功，3=失败） |
| error_message | 错误信息 |
| task_id | Celery 任务 ID |

## 状态说明

### 账号状态 (status)

| 值 | 状态 | 说明 |
|----|------|------|
| 0 | 失效 | Cookie 已失效，需要重新获取 |
| 1 | 有效 | Cookie 有效，可以使用 |
| 2 | 过期 | Cookie 即将过期或已过期 |

### 发布状态 (status)

| 值 | 状态 | 说明 |
|----|------|------|
| 0 | 待发布 | 等待发布 |
| 1 | 发布中 | 正在发布 |
| 2 | 成功 | 发布成功 |
| 3 | 失败 | 发布失败 |

## 相关文档

- [浏览器自动化](./browser.md)
- [Content API 文档](../api/content-api.md)
- [浏览器扩展使用指南](../browser-extension.md)
