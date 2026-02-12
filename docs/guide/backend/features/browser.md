# 浏览器自动化

本系统使用 Playwright 实现浏览器自动化功能，主要用于：
- Cookie 有效性验证
- 文章自动发布到第三方平台

## Playwright 简介

Playwright 是微软开发的浏览器自动化框架，支持 Chromium、Firefox、WebKit 三大浏览器引擎。

### 主要特性

- ✅ **跨浏览器支持**：Chromium、Firefox、WebKit
- ✅ **异步 API**：与 FastAPI 完美契合
- ✅ **自动等待**：减少超时问题，提高稳定性
- ✅ **无头模式**：可在服务器上运行
- ✅ **拦截和监控**：支持网络请求拦截

## 功能特性

### 1. Cookie 验证

自动验证存储的平台账号 Cookie 是否仍然有效：

```bash
POST /api/content/platform_account/verify/{id}
```

验证流程：
1. 从数据库获取平台账号的 Cookie
2. 使用 Playwright 启动浏览器
3. 加载 Cookie 到浏览器上下文
4. 访问平台页面检查登录状态
5. 更新账号状态和验证时间

### 2. 文章发布

自动登录第三方平台并发布文章：

```bash
POST /api/content/publish/article/{article_id}
Content-Type: application/x-www-form-urlencoded

platform=zhihu&platform_account_id=1
```

发布流程：
1. 从数据库获取文章和平台账号信息
2. 使用 Playwright 启动浏览器
3. 加载 Cookie 到浏览器上下文
4. 访问发布页面验证登录状态
5. 填写文章内容并提交
6. 保存发布结果（文章链接、ID 等）

## 配置说明

### 环境变量配置

在 `.env` 文件中添加：

```bash
# ========== 内容模块配置 ==========

# Playwright 浏览器配置
CONTENT_PLAYWRIGHT_HEADLESS=True        # 是否无头模式
CONTENT_PLAYWRIGHT_TIMEOUT=30000         # 超时时间（毫秒）
CONTENT_PLAYWRIGHT_WIDTH=1920           # 窗口宽度
CONTENT_PLAYWRIGHT_HEIGHT=1080          # 窗口高度

# 知乎平台配置
CONTENT_ZHIHU_VERIFY_URL=https://www.zhihu.com
CONTENT_ZHIHU_LOGIN_SELECTOR=.AppHeader-login
CONTENT_ZHIHU_LOGGED_IN_SELECTOR=.AppHeader-notifications
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `PLAYWRIGHT_HEADLESS` | bool | True | 是否无头模式，开发时设为 False 可看到浏览器 |
| `PLAYWRIGHT_TIMEOUT` | int | 30000 | 浏览器操作超时时间（毫秒） |
| `PLAYWRIGHT_WIDTH` | int | 1920 | 浏览器窗口宽度（像素） |
| `PLAYWRIGHT_HEIGHT` | int | 1080 | 浏览器窗口高度（像素） |

### User-Agent 说明

User-Agent（浏览器标识字符串）的获取优先级：

1. **优先使用**：浏览器扩展获取的真实 UA（存储在数据库）
2. **备用方案**：代码中的硬编码默认值

**浏览器扩展会自动获取当前浏览器的 User-Agent**，无需手动配置。

## 使用方式

### 安装浏览器

```bash
# 进入后端目录
cd server

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 下载 Chromium 浏览器
playwright install chromium
```

### 开发调试

设置 `PLAYWRIGHT_HEADLESS=False` 可以看到浏览器操作过程：

```bash
# .env 文件
CONTENT_PLAYWRIGHT_HEADLESS=False
```

这样可以在屏幕上看到浏览器的操作过程，方便调试。

### 代码示例

```python
from Modules.content.services.publisher import ZhihuHandler

# 验证 Cookie
handler = ZhihuHandler(
    cookies=[{"name": "z_c0", "value": "xxx", "domain": ".zhihu.com"}],
    user_agent="Mozilla/5.0..."
)
result = await handler.verify()
# {"success": True, "message": "验证成功，Cookie 有效"}

# 发布文章
handler = ZhihuHandler(
    cookies=[{"name": "z_c0", "value": "xxx", "domain": ".zhihu.com"}],
    user_agent="Mozilla/5.0...",
    article_data={"title": "标题", "content": "内容"}
)
result = await handler.publish()
# PublishResult(success=True, message="文章发布成功", platform_url="...")
```

## 支持的平台

| 平台 | Cookie 验证 | 文章发布 | 备注 |
|------|------------|---------|------|
| 知乎 | ✅ 已支持 | ✅ 已支持 | 使用登录按钮检测 |
| 掘金 | 🚧 计划中 | 🚧 计划中 | - |
| CSDN | 🚧 计划中 | 🚧 计划中 | - |

## 架构设计

### 处理器架构（统一验证和发布）

```
BasePlatformHandler (抽象基类)
    ├── ZhihuHandler (知乎处理器) - 验证 + 发布
    ├── JuejinHandler (掘金处理器) - 待实现
    └── CSDNHandler (CSDN处理器) - 待实现
```

每个处理器都支持两种操作：
- `verify()` - 验证 Cookie 有效性
- `publish()` - 发布文章到平台

### 目录结构

```
server/Modules/content/services/publisher/
├── __init__.py
├── base_platform_handler.py    # 处理器基类（融合验证和发布）
└── zhihu_handler.py             # 知乎处理器（融合验证和发布）
```

## Windows 系统特殊配置

### 问题描述

在 Windows 系统上，Python 的默认事件循环（`ProactorEventLoop`）不支持创建子进程，导致 Playwright 无法启动浏览器，会抛出 `NotImplementedError` 异常。

### 错误信息

```
NotImplementedError
File "asyncio\base_events.py", line 528, in _make_subprocess_transport
```

### 解决方案

项目已在 `run.py` 和 `Modules/main.py` 中配置了事件循环策略，但需要额外的配置：

#### 1. 禁用热重载模式

将 `.env` 文件中的 `APP_RELOAD` 设置为 `false`：

```bash
APP_RELOAD=false
```

**原因**：uvicorn 的 reload 模式会创建新进程，新进程不会继承事件循环策略设置。

#### 2. 使用正确的启动方式

确保使用 `run.py` 启动服务：

```bash
# 正确的启动方式
python run.py

# ❌ 错误的方式（会导致事件循环策略设置失效）
uvicorn Modules.main:app --reload
```

#### 3. 完全重启服务

修改配置后需要完全停止并重新启动服务，不能依赖热重载。

### 开发建议

- 如果需要热重载功能，建议使用 IDE 的自动重启功能
- 或者使用专门的开发工具（如 `watchdog`）配合手动重启

### 技术细节

Windows 有两种事件循环实现：

| 事件循环 | 优点 | 缺点 |
|---------|------|------|
| **ProactorEventLoop** (默认) | 高性能 I/O | 不支持 subprocess |
| **SelectorEventLoop** | 完整支持 subprocess | I/O 性能略低 |

Playwright 需要创建子进程来启动浏览器驱动，因此必须使用 `SelectorEventLoop`。

项目在以下位置配置了事件循环策略：

- `run.py` (第 7-8 行) - 服务启动入口
- `Modules/main.py` (第 9-10 行) - 应用初始化

---

## 常见问题

### Windows 上 NotImplementedError

参见上面的 [Windows 系统特殊配置](#windows-系统特殊配置)。

### 浏览器下载失败

**问题**：`playwright install chromium` 下载失败

**解决方案**：使用国内镜像

```bash
# 设置环境变量
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 依赖缺失（Linux）

**问题**：Linux 系统缺少系统依赖

**解决方案**：安装系统依赖

```bash
playwright install-deps chromium
```

### 验证超时

**问题**：验证过程超时

**解决方案**：增加超时时间

```bash
# .env 文件
CONTENT_PLAYWRIGHT_TIMEOUT=60000
```

### Cookie 格式错误

**问题**：`Cookie 格式错误，无法解析`

**解决方案**：确保 Cookie 是有效的 JSON 格式

```json
[
  {
    "name": "z_c0",
    "value": "xxx",
    "domain": ".zhihu.com",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "expirationDate": 1234567890
  }
]
```

## 相关文档

- [内容发布功能](./content-publish.md)
- [平台账号管理](../../api/content/platform-account.md)
- [浏览器扩展使用指南](../../browser-extension.md)
