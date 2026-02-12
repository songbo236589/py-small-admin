# 浏览器扩展使用指南

Py Small Admin 浏览器扩展用于一键获取各技术平台（知乎、掘金、CSDN 等）的登录 Cookie，并自动保存到后端系统。

## 目录

- [快速开始](#快速开始)
- [功能介绍](#功能介绍)
- [安装步骤](#安装步骤)
- [使用方法](#使用方法)
- [支持的平台](#支持的平台)
- [常见问题](#常见问题)
- [技术说明](#技术说明)

---

## 快速开始

### 1. 安装扩展

1. 下载扩展包：[py-small-admin-extension.zip](/downloads/py-small-admin-extension.zip)
2. 解压到本地目录
3. 打开 Chrome 扩展管理页面：`chrome://extensions/`
4. 开启右上角的"开发者模式"
5. 点击"加载已解压的扩展程序"
6. 选择解压后的目录

### 2. 配置后端地址

1. 点击浏览器工具栏中的扩展图标
2. 点击右上角的设置按钮 ⚙️
3. 输入后端 API 地址（如：`http://localhost:8009`）
4. 点击"保存"

### 3. 获取平台 Cookie

1. 在浏览器中登录目标平台（如知乎）
2. 点击扩展图标，选择对应平台
3. 点击"发送到后端"按钮
4. 等待成功提示

---

## 功能介绍

### 扩展界面

```
┌─────────────────────────────────────┐
│  Py Small Admin          ⚙️ 设置    │
├─────────────────────────────────────┤
│                                     │
│  支持的平台                          │
│  ┌─────────────────────────────┐    │
│  │ 知乎         (5)   [发送]   │    │
│  │ 掘金         (3)   [发送]   │    │
│  │ CSDN         (8)   [发送]   │    │
│  └─────────────────────────────┘    │
│                                     │
│  [刷新获取] [全部发送]              │
│                                     │
└─────────────────────────────────────┘
```

### 功能说明

| 功能 | 说明 |
|------|------|
| **平台列表** | 显示所有支持的平台，每个平台显示当前获取到的 Cookie 数量 |
| **刷新获取** | 重新从浏览器获取所有平台的最新 Cookie |
| **单独发送** | 只将选中平台的 Cookie 发送到后端 |
| **全部发送** | 将所有平台的 Cookie 一次性发送到后端 |
| **查看详情** | 点击平台可查看 Cookie 详细信息（JSON 格式） |
| **复制 JSON** | 一键复制 Cookie 数据，方便调试 |

### 扩展权限

扩展需要以下权限才能正常工作：

| 权限 | 说明 |
|------|------|
| `cookies` | 读取各平台的登录 Cookie |
| `activeTab` | 获取当前浏览器 User-Agent |
| `storage` | 保存后端地址等配置信息 |

---

## 安装步骤

### Chrome / Edge (Chromium 内核)

1. **下载扩展包**
   - 从后端管理系统的"平台账号"页面下载扩展包
   - 或从项目 releases 页面下载

2. **解压扩展包**
   ```bash
   unzip py-small-admin-extension.zip -d browser-extension
   ```

3. **加载扩展**
   - 打开 `chrome://extensions/` 或 `edge://extensions/`
   - 开启"开发者模式"（右上角开关）
   - 点击"加载已解压的扩展程序"
   - 选择解压后的 `browser-extension` 目录

4. **确认安装**
   - 扩展图标会出现在浏览器工具栏
   - 可能需要固定图标以便快速访问

### Firefox

1. **下载扩展包**
   - 下载 `.xpi` 文件

2. **安装扩展**
   - 打开 `about:debugging#/runtime/this-firefox`
   - 点击"临时加载附加组件"
   - 选择 `.xpi` 文件

---

## 使用方法

### 配置后端地址

首次使用需要配置后端 API 地址：

1. 点击扩展图标打开弹出窗口
2. 点击右上角的设置按钮 ⚙️
3. 在弹出框中输入后端地址：
   - 本地开发：`http://localhost:8009`
   - 生产环境：`https://your-domain.com`
4. 点击"保存"

### 获取单个平台 Cookie

1. **登录平台**
   - 在浏览器新标签页中打开目标平台（如知乎）
   - 使用您的账号登录

2. **获取 Cookie**
   - 点击扩展图标
   - 找到对应平台（如"知乎"）
   - 确认显示的 Cookie 数量大于 0
   - 点击"发送到后端"按钮

3. **确认结果**
   - 等待发送完成提示
   - 成功：显示"Cookie 导入成功"
   - 失败：检查错误信息，见[常见问题](#常见问题)

### 批量获取所有平台

1. **登录所有需要的平台**
   - 在浏览器中分别登录知乎、掘金、CSDN 等

2. **一键获取**
   - 点击扩展图标
   - 点击"全部发送"按钮
   - 等待批量导入完成

3. **查看结果**
   - 扩展会显示导入摘要：
     - 成功更新：X 个
     - 新增账号：X 个
     - 失败：X 个

### 查看 Cookie 详情

1. 点击扩展图标
2. 点击任意平台卡片（非按钮区域）
3. 弹出 Cookie 详情窗口，显示：
   - Cookie JSON 数据
   - 一键复制按钮

---

## 支持的平台

| 平台 | 域名 | Cookie 验证 | 文章发布 |
|------|------|------------|---------|
| 知乎 | `zhihu.com` | ✅ 已支持 | 🚧 开发中 |
| 掘金 | `juejin.cn` | 🚧 计划中 | 🚧 计划中 |
| CSDN | `csdn.net` | 🚧 计划中 | 🚧 计划中 |
| 思否 | `segmentfault.com` | 🚧 计划中 | 🚧 计划中 |

### 添加新平台

如需添加新平台支持，需要修改以下文件：

1. **后端配置**：`server/Modules/content/services/extension_service.py`
   ```python
   PLATFORM_DOMAIN_MAP = {
       "new_platform": {
           "name": "新平台",
           "domains": ["example.com"],
           "icon": "https://example.com/favicon.ico",
       },
   }
   ```

2. **扩展配置**：`browser-extension/source/Popup/constants.ts`
   ```typescript
   export const PLATFORM_DOMAIN_MAP = {
       new_platform: {
           name: "新平台",
           domains: ["example.com"],
       },
   };
   ```

---

## 常见问题

### 扩展无法连接到后端

**症状**：发送 Cookie 时提示"网络错误"或"连接失败"

**排查步骤**：

1. **检查后端地址**
   - 点击设置 ⚙️，确认后端地址正确
   - 确保地址包含协议（`http://` 或 `https://`）

2. **检查后端状态**
   - 确认后端服务正在运行
   - 访问后端地址确认可访问

3. **检查 CORS 配置**
   - 后端需要允许跨域请求
   - 检查 `.env` 中的 `APP_CORS_ALLOW_ALL=true`

4. **检查网络连接**
   - 确认电脑网络正常
   - 尝试在浏览器中访问后端 API

### Cookie 获取失败

**症状**：平台显示 Cookie 数量为 0

**排查步骤**：

1. **确认已登录**
   - 在新标签页中打开目标平台
   - 确认已成功登录（能看到用户头像）

2. **检查扩展权限**
   - 打开 `chrome://extensions/`
   - 找到 Py Small Admin 扩展
   - 确认"读取和更改您在所有网站上的数据"权限已启用

3. **刷新 Cookie**
   - 点击扩展中的"刷新获取"按钮
   - 重新登录目标平台后再试

### 发送失败但提示成功

**症状**：扩展显示发送成功，但后端没有新增账号

**排查步骤**：

1. **检查后端日志**
   - 查看后端控制台是否有错误信息
   - 检查数据库连接是否正常

2. **手动测试 API**
   ```bash
   curl -X POST http://localhost:8009/api/content/extension/platform_account/import_cookies \
     -H "Content-Type: application/json" \
     -d '{"cookies": [], "userAgent": "test"}'
   ```

3. **检查平台识别**
   - 某些平台域名可能未配置
   - 查看后端日志确认平台识别情况

### User-Agent 获取失败

**症状**：发送的 Cookie 没有包含 User-Agent

**解决方案**：

- User-Agent 是从当前浏览器标签页自动获取的
- 确保在目标平台页面打开扩展
- 如果获取失败，后端会使用默认 User-Agent

### Cookie 验证失败（Windows）

**症状**：在后端平台账号管理页面点击"验证"按钮时，提示"验证过程出错: NotImplementedError"

**原因**：Windows 系统的默认事件循环不支持 Playwright 创建子进程

**解决方案**：

1. 将 `.env` 文件中的 `APP_RELOAD` 设置为 `false`
2. 完全重启后端服务（使用 `python run.py`）
3. 确保使用 `run.py` 启动，而不是直接用 `uvicorn` 命令

详细说明请参考 [浏览器自动化功能文档 - Windows 系统特殊配置](./backend/features/browser.md#windows-系统特殊配置)

---

## 技术说明

### 数据流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  浏览器扩展  │────▶│   后端 API   │────▶│   数据库    │
│             │     │             │     │             │
│  Cookie 获取│     │  数据验证   │     │  账号存储   │
│  UA 获取    │     │  平台识别   │     │  加密存储   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 安全机制

| 安全措施 | 说明 |
|---------|------|
| **本地获取** | Cookie 直接从浏览器获取，不经过第三方 |
| **HTTPS 传输** | 生产环境强制使用 HTTPS 传输 |
| **加密存储** | 后端对 Cookie 数据进行加密存储 |
| **权限最小化** | 扩展只请求必要的浏览器权限 |
| **无外传** | Cookie 只发送到用户配置的后端地址 |

### API 接口

扩展使用以下后端 API：

#### 获取平台列表

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

#### 导入 Cookies

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
      "expirationDate": 1735660800
    }
  ],
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
}
```

**响应**：
```json
{
  "code": 200,
  "message": "Cookies导入成功",
  "data": {
    "updated": [{"id": 1, "platform": "zhihu", "account_name": "zhihu_账号"}],
    "created": [{"id": 2, "platform": "zhihu", "account_name": "zhihu_z_c0"}],
    "errors": [],
    "summary": {
      "updated_count": 1,
      "created_count": 1,
      "error_count": 0
    }
  }
}
```

### 开发者信息

扩展技术栈：
- **框架**: React 18 + TypeScript
- **UI**: Ant Design 5
- **构建**: Webpack 5
- **清单**: Manifest V3
- **HTTP**: Axios

源码位置：`browser-extension/`

开发指南：[browser-extension/README.md](https://github.com/songbo236589/py-small-admin/tree/main/browser-extension)

---

## 相关文档

- [浏览器自动化功能](./backend/features/browser.md)
- [内容发布功能](./backend/features/content-publish.md)
- [平台账号 API](./backend/api/content-api.md)
- [Cookie 验证流程](./backend/features/browser.md#cookie-验证)
