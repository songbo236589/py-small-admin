# 前端构建指南

本文档介绍如何构建 Py Small Admin 前端项目。

## 构建环境要求

- Node.js 22.12+
- npm 或 yarn
- 至少 2GB 可用内存

## 开发环境构建

### 1. 安装依赖

```bash
cd admin-web
npm install
```

### 2. 配置环境变量

创建 `.env.development`：

```bash
# API 地址
UMI_APP_API_BASE_URL=http://localhost:8000/api

# API Key
UMI_APP_API_KEY=your-admin-api-key

# 环境类型
UMI_APP_ENV=dev
```

### 3. 启动开发服务器

```bash
npm start
```

应用将在 http://localhost:8000 启动。

### 4. 可用的开发命令

```bash
# 启动开发服务器
npm start

# 启动开发服务器（不使用 Mock）
npm run start:no-mock

# 启动开发服务器（测试环境）
npm run start:test

# 代码检查
npm run lint

# 代码检查并自动修复
npm run lint:fix

# 类型检查
npm run tsc
```

## 生产环境构建

### 1. 配置生产环境变量

创建 `.env.production`：

```bash
# API 地址（修改为实际域名）
UMI_APP_API_BASE_URL=https://your-domain.com/api

# API Key
UMI_APP_API_KEY=your-production-api-key

# 环境类型
UMI_APP_ENV=production
```

### 2. 构建生产版本

```bash
npm run build
```

构建产物将生成在 `dist` 目录。

### 3. 分析构建产物

```bash
npm run analyze
```

这会打开一个可视化分析页面，显示各模块的大小。

## 构建产物

### 目录结构

```
dist/
├── index.html              # HTML 入口
├── umi.js                  # 主入口文件
├── umi.css                 # 主样式文件
├── __assets__/             # 静态资源
│   ├── *.js                # 按路由拆分的 JS 文件
│   ├── *.css               # 按路由拆分的 CSS 文件
│   ├── images/            # 图片资源
│   └── fonts/             # 字体资源
└── static/                # 其他静态文件
```

### 文件命名

构建产物使用哈希命名，例如：
- `umi.df8a9b.js`
- `umi.7c2d1e.css`

这样可以实现长期缓存。

## 高级配置

### 1. 自定义构建配置

在 `config/config.ts` 中添加自定义配置：

```typescript
export default defineConfig({
  // 自定义构建选项
  chainWebpack(config) {
    // 添加自定义 webpack 配置
    config.resolve.alias.set('@', '/path/to/alias');
    return config;
  },

  // 环境变量
  define: {
    process.env.CUSTOM_VAR: '"custom_value"',
  },
});
```

### 2. 代理配置

在 `config/proxy.ts` 中配置开发环境代理：

```typescript
export default {
  // API 代理
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    pathRewrite: { '^/api': '/api' },
  },
};
```

### 3. 路由配置

路由配置位于 `config/routes/` 目录：

```typescript
export default [
  {
    path: '/admin',
    component: './admin',
    routes: [
      {
        path: '/dashboard',
        component: './admin/dashboard',
      },
    ],
  },
];
```

### 4. 按需加载

组件自动按需加载，无需额外配置：

```typescript
// 使用 dynamic import
const Dashboard = React.lazy(() => import('./admin/dashboard'));
```

## 优化构建

### 1. 启用代码分割

代码分割已默认启用。检查 `config/config.ts` 中的配置：

```typescript
mfsu: {},
```

### 2. 压缩资源

启用 Gzip 压缩（在 Nginx 中配置）：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### 3. 使用 CDN

配置静态资源 CDN：

```typescript
export default defineConfig({
  publicPath: 'https://cdn.example.com/',
});
```

### 4. Tree Shaking

Tree Shaking 已默认启用，确保只导入使用的代码：

```typescript
// 好的做法
import { Button } from 'antd';

// 避免
import * as antd from 'antd';
```

## 构建问题排查

### 1. 构建失败

```bash
# 清除缓存
rm -rf .umi
rm -rf node_modules/.cache

# 重新安装依赖
npm install

# 重新构建
npm run build
```

### 2. 内存不足

```bash
# 增加 Node.js 内存限制
NODE_OPTIONS="--max_old_space_size=4096" npm run build
```

### 3. 依赖冲突

```bash
# 清理依赖
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 4. 类型错误

```bash
# 重新生成类型
npm run openapi

# 类型检查
npm run tsc
```

### 5. 环境变量问题

检查环境变量是否正确设置：

```bash
# 验证环境变量
echo $UMI_APP_API_BASE_URL
```

## 持续集成

### GitHub Actions 配置

创建 `.github/workflows/build.yml`：

```yaml
name: Build

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '22'

    - name: Install dependencies
      run: npm ci
      working-directory: ./admin-web

    - name: Build
      run: npm run build
      working-directory: ./admin-web

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: build-artifacts
        path: admin-web/dist/
```

## 部署构建产物

### 1. 复制到服务器

```bash
# 本地构建
npm run build

# 上传到服务器
scp -r dist/* user@server:/var/www/py-small-admin/
```

### 2. 使用 CI/CD

配置 CI/CD 管道自动构建和部署。

### 3. Docker 构建

在 Dockerfile 中添加构建步骤：

```dockerfile
FROM node:22-alpine as builder
WORKDIR /app
COPY admin-web/package*.json ./
RUN npm install
COPY admin-web/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/admin-web/dist /usr/share/nginx/html
```

## 最佳实践

1. **定期更新依赖**：保持依赖包最新版本
2. **使用固定版本**：在 package.json 中锁定版本号
3. **优化图片**：压缩图片，使用 WebP 格式
4. **代码分割**：合理拆分代码，减少首屏加载时间
5. **缓存策略**：配置合适的缓存头
6. **监控构建**：记录构建时间和产物大小
7. **自动化**：使用 CI/CD 自动化构建流程
