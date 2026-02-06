# Py Small Admin 浏览器扩展

一键获取各技术平台（知乎、掘金、CSDN 等）的登录信息。

## 功能特性

- 支持多平台 Cookie 一键获取
- 自动识别平台并保存到后端
- Manifest V3 规范
- React + Ant Design UI

## 支持的平台

| 平台 | 域名 |
|------|------|
| 知乎 | zhihu.com |
| 掘金 | juejin.cn |
| CSDN | csdn.net |
| 思否 | segmentfault.com |

## 开发指南

### 安装依赖

```bash
cd browser-extension
npm install
```

### 开发模式

```bash
# Chrome 开发
npm run dev:chrome

# Firefox 开发
npm run dev:firefox
```

### 生产构建

```bash
# Chrome 构建
npm run build:chrome

# Firefox 构建
npm run build:firefox

# 构建所有
npm run build
```

### 加载扩展（开发者模式）

#### Chrome

1. 打开 `chrome://extensions/`
2. 开启"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 `dist/chrome` 目录

#### Firefox

1. 打开 `about:debugging#/runtime/this-firefox`
2. 点击"临时加载附加组件"
3. 选择 `dist/firefox` 目录中的 `.xpi` 文件

## 使用说明

### 用户使用流程

1. **安装扩展**
   - 在平台账号管理页面下载扩展包
   - 解压并加载到浏览器

2. **配置后端地址**
   - 点击扩展图标
   - 点击设置按钮
   - 输入后端 API 地址（如：`http://localhost:8000`）

3. **获取登录信息**
   - 在浏览器中登录目标平台（如知乎）
   - 点击扩展图标
   - 点击"一键获取登录信息"
   - 系统自动保存 Cookie 到后端

### 前端集成

前端页面已集成扩展下载功能，位于：

```
admin-web/src/pages/content/platform_account/index.tsx
```

## 目录结构

```
browser-extension/
├── package.json              # NPM 配置
├── tsconfig.json             # TypeScript 配置
├── webpack.config.js         # Webpack 配置
├── webpack.common.js         # 通用配置
├── webpack.dev.js            # 开发配置
├── webpack.prod.js           # 生产配置
│
├── source/                   # 源代码目录
│   ├── manifest.json         # 扩展清单
│   ├── Popup/                # 弹出窗口组件
│   │   ├── index.tsx
│   │   ├── Popup.tsx
│   │   └── styles.less
│   ├── Background/           # 后台脚本
│   │   └── index.ts
│   ├── assets/               # 静态资源
│   │   └── icons/
│   └── styles/               # 全局样式
│
├── views/                    # HTML 模板
│   └── popup.html
│
└── dist/                     # 构建输出目录
    ├── chrome/
    └── firefox/
```

## 后端 API

### 导入 Cookie 接口

```
POST /api/content/platform_account/import_cookies
```

**请求体：**

```json
[
  {
    "name": "sessionid",
    "value": "xxx",
    "domain": ".juejin.cn",
    "path": "/",
    "secure": true,
    "httpOnly": true
  }
]
```

**响应：**

```json
{
  "code": 200,
  "message": "Cookies导入成功",
  "data": {
    "updated": [...],
    "created": [...],
    "errors": [],
    "summary": {
      "updated_count": 2,
      "created_count": 1,
      "error_count": 0
    }
  }
}
```

## 技术栈

- **框架**: React 18 + TypeScript
- **UI**: Ant Design 5
- **构建**: Webpack 5
- **清单**: Manifest V3
- **HTTP**: Axios

## 注意事项

1. **图标资源**：需要准备 16x16、32x32、48x48、128x128 的 PNG 图标
2. **CORS 配置**：确保后端 API 允许扩展的跨域请求
3. **认证 Token**：扩展需要获取用户的认证 Token 才能调用后端 API
4. **Cookie 安全**：Cookie 数据通过 HTTPS 传输，后端加密存储

## 常见问题

### Q: 扩展无法连接到后端？

A: 检查以下项：
- 后端地址配置是否正确
- 后端是否启动
- CORS 是否正确配置
- 网络连接是否正常

### Q: Cookie 导入失败？

A: 检查以下项：
- 是否已登录目标网站
- 扩展是否有 Cookie 读取权限
- 后端接口是否正常

### Q: 如何调试扩展？

A:
1. Chrome: 右键扩展图标 → 检查弹出内容
2. Firefox: 关于调试 → 临时附加组件 → 调试

## 许可证

MIT
