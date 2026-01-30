# 前端开发环境搭建

本文档将帮助你搭建前端开发环境。

## 环境要求

确保你已经满足以下环境要求：

- Node.js 22.12+
- npm 或 yarn
- Git

详细的安装说明请参考 [环境要求](../getting-started/index.md)。

## 克隆项目

```bash
git clone https://github.com/songbo236589/py-small-admin.git
cd py-small-admin
```

## 进入前端目录

```bash
cd admin-web
```

## 安装依赖

### 使用 npm

```bash
npm install
```

### 使用 yarn

```bash
yarn install
```

如果下载速度较慢，可以使用淘宝镜像：

```bash
# npm
npm config set registry https://registry.npmmirror.com
npm install

# yarn
yarn config set registry https://registry.npmmirror.com
yarn install
```

## 配置环境变量

### 创建环境变量文件

```bash
# 开发环境
cp .env.example .env.development

# 生产环境
cp .env.example .env.production
```

### 编辑环境变量

打开 `.env.development` 文件：

```bash
code .env.development
```

### 配置项说明

```bash
# API 地址
UMI_APP_API_BASE_URL=http://localhost:8000/api

# API Key（与后端 APP_ADMIN_X_API_KEY 保持一致）
UMI_APP_API_KEY=your-admin-api-key

# 环境类型
UMI_APP_ENV=dev
```

**重要**：
- `UMI_APP_API_KEY` 必须与后端配置文件中的 `APP_ADMIN_X_API_KEY` 一致
- 开发环境使用后端的本地地址
- 生产环境使用实际的域名

## 启动开发服务器

### 使用 npm

```bash
npm start
```

### 使用 yarn

```bash
yarn start
```

服务将启动在 http://localhost:8000

## 验证安装

### 1. 检查依赖安装

```bash
npm list --depth=0
# 或
yarn list --depth=0
```

应该能看到所有主要依赖：
- react
- antd
- @ant-design/pro-components
- @umijs/max
- typescript
- 等等

### 2. 访问应用

打开浏览器访问 http://localhost:8000

你应该能看到登录页面。

### 3. 测试登录

使用初始账号登录：
- 用户名：`admin`
- 密码：`admin123`

如果登录成功，说明环境配置正确。

## 开发工具配置

### VS Code

#### 安装推荐扩展

1. 打开 VS Code
2. 按 `Ctrl/Cmd + Shift + X` 打开扩展面板
3. 安装以下扩展：

**必需扩展**：
- ESLint - JavaScript 代码检查
- Prettier - 代码格式化
- TypeScript Importer - TypeScript 导入自动补全

**推荐扩展**：
- Auto Rename Tag - 自动重命名 HTML 标签
- Auto Close Tag - 自动闭合 HTML 标签
- GitLens - Git 增强
- Path Intellisense - 路径自动补全

#### 配置 VS Code

创建 `.vscode/settings.json`：

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

#### 配置 VS Code 启动任务

创建 `.vscode/tasks.json`：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Dev Server",
      "type": "npm",
      "script": "start",
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Build",
      "type": "npm",
      "script": "build",
      "problemMatcher": []
    },
    {
      "label": "Lint",
      "type": "npm",
      "script": "lint",
      "problemMatcher": []
    }
  ]
}
```

### WebStorm

#### 配置 Node.js

1. 打开 Settings → Languages & Frameworks → Node.js
2. 配置 Node interpreter 为项目的 Node.js
3. 启用 Coding assistance for Node.js

#### 配置 ESLint

1. 打开 Settings → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint
2. 勾选 Automatic ESLint configuration
3. 勾选 Run eslint --fix on save

#### 配置 Prettier

1. 打开 Settings → Languages & Frameworks → JavaScript → Prettier
2. 配置 Prettier package 为项目的 node_modules/prettier
3. 勾选 On save 选项

### Chrome DevTools

#### 安装 React DevTools

1. 打开 Chrome 浏览器
2. 访问 https://chrome.google.com/webstore
3. 搜索 "React Developer Tools"
4. 点击 "添加至 Chrome"

#### 使用 React DevTools

1. 按 F12 打开开发者工具
2. 点击 "React" 标签
3. 查看 React 组件树和状态

## 项目结构

### 目录说明

```
admin-web/
├── config/               # 配置文件
│   ├── config.ts        # 主配置文件
│   ├── routes/          # 路由配置
│   └── proxy.ts         # 代理配置
├── src/                 # 源代码
│   ├── pages/          # 页面组件
│   ├── services/       # API 服务
│   ├── components/     # 公共组件
│   ├── utils/          # 工具函数
│   ├── app.tsx         # 应用入口
│   └── global.tsx      # 全局样式
├── public/             # 静态资源
├── .env                # 环境变量
├── package.json        # 依赖配置
└── tsconfig.json       # TypeScript 配置
```

详细的目录结构请参考 [目录结构](../getting-started/directory.md)。

## 常用命令

### 开发命令

```bash
# 启动开发服务器
npm start

# 启动开发服务器（不使用 Mock）
npm run start:no-mock

# 启动开发服务器（测试环境）
npm run start:test
```

### 构建命令

```bash
# 构建生产版本
npm run build

# 分析构建产物
npm run analyze

# 预览生产版本
npm run preview
```

### 代码检查命令

```bash
# 代码检查
npm run lint

# 代码检查并自动修复
npm run lint:fix

# 类型检查
npm run tsc
```

### 测试命令

```bash
# 运行测试
npm test

# 测试覆盖率
npm run test:coverage

# 更新测试快照
npm run test:update
```

## 调试技巧

### 1. 使用浏览器调试

在 VS Code 中配置 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome against localhost",
      "url": "http://localhost:8000",
      "webRoot": "${workspaceFolder}"
    }
  ]
}
```

### 2. 查看网络请求

1. 按 F12 打开开发者工具
2. 点击 "Network" 标签
3. 刷新页面
4. 查看所有网络请求

### 3. 查看控制台日志

1. 按 F12 打开开发者工具
2. 点击 "Console" 标签
3. 查看控制台输出

### 4. 使用 React DevTools

1. 安装 React DevTools 扩展
2. 按 F12 打开开发者工具
3. 点击 "React" 标签
4. 查看组件树和状态

## 常见问题

### 1. 依赖安装失败

**问题**：`npm install` 时报错

**解决方案**：

```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 2. 端口被占用

**问题**：`Address already in use`

**解决方案**：

```bash
# 修改端口
# 在 .env 文件中添加：
PORT=8001
```

### 3. 代理配置不生效

**问题**：API 请求失败

**解决方案**：

检查 `config/proxy.ts` 中的代理配置是否正确。

### 4. TypeScript 类型错误

**问题**：TypeScript 报错

**解决方案**：

```bash
# 重新生成类型
npm run openapi

# 检查 TypeScript 配置
cat tsconfig.json
```

### 5. 样式不生效

**问题**：修改样式后没有生效

**解决方案**：

```bash
# 清除缓存并重启
rm -rf .umi
npm start
```

## 性能优化

### 1. 启用代码分割

在 `config/config.ts` 中：

```typescript
export default {
  mfsu: {},
  chainWebpack(config) {
    config.optimization.splitChunks({
      chunks: 'all',
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          priority: -10,
        },
      },
    });
  },
};
```

### 2. 启用 Gzip 压缩

在 `config/config.ts` 中：

```typescript
export default {
  chainWebpack(config) {
    config.plugins.push(
      new CompressionPlugin({
        filename: '[path].gz[query]',
        algorithm: 'gzip',
        test: new RegExp('\\.(js|css)$'),
        threshold: 10240,
        minRatio: 0.8,
      })
    );
  },
};
```

### 3. 优化图片

- 使用 WebP 格式
- 使用图片懒加载
- 使用 CDN 加速