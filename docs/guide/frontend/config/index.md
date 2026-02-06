# 配置指南

本文档介绍 Py Small Admin 前端项目的配置方法。

## 配置文件结构

```
admin-web/config/
├── config.ts           # 主配置文件
├── defaultSettings.ts  # 布局默认配置
├── proxy.ts           # 开发代理配置
└── routes/            # 路由配置
    ├── index.ts       # 路由入口
    ├── admin.ts       # 管理模块路由
    └── quant.ts       # 量化模块路由
```

## 环境变量配置

### 1. 环境变量文件

在项目根目录创建 `.env` 文件：

```bash
# 开发环境 (.env.development)
UMI_APP_API_BASE_URL=http://localhost:8000/api
UMI_APP_ENV=dev

# 生产环境 (.env.production)
UMI_APP_API_BASE_URL=https://your-domain.com/api
UMI_APP_ENV=production
```

### 2. 可用的环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `UMI_APP_API_BASE_URL` | 后端 API 地址 | `http://localhost:8000/api` |
| `UMI_APP_ENV` | 环境类型 | `dev` / `test` / `production` |
| `UMI_APP_OPEN_API_SCHEMAPATH` | OpenAPI 规范路径 | `http://localhost:8000/openapi.json` |
| `UMI_APP_API_KEY` | API 密钥 | `your-api-key` |

### 3. 在代码中使用环境变量

```typescript
// 读取环境变量
const apiBaseUrl = process.env.UMI_APP_API_BASE_URL;
const isDev = process.env.UMI_APP_ENV === 'dev';

// 在组件中使用
const MyComponent = () => {
  const [config, setConfig] = useState({
    apiUrl: process.env.UMI_APP_API_BASE_URL,
  });

  return <div>{config.apiUrl}</div>;
};
```

## 主配置文件 (config.ts)

### 基础配置

```typescript
import { defineConfig } from '@umijs/max';
import routes from './routes';
import defaultSettings from './defaultSettings';
import proxy from './proxy';

export default defineConfig({
  // 路径配置
  publicPath: '/',
  hash: true,

  // 路由配置
  routes,

  // 代理配置
  proxy: proxy[process.env.UMI_APP_ENV || 'dev'],

  // 快速刷新
  fastRefresh: true,

  // 更多配置...
});
```

### 完整配置选项

```typescript
export default defineConfig({
  // ========== 路径配置 ==========
  /**
   * 部署路径
   * 如果部署在非根目录，需要修改此配置
   */
  publicPath: '/',

  /**
   * 是否启用 hash 模式
   * 用于增量发布和避免浏览器缓存
   */
  hash: true,

  // ========== 路由配置 ==========
  /**
   * 路由配置
   * 只在路由中引入的文件会被编译
   */
  routes: [],

  // ========== 构建配置 ==========
  /**
   * 是否启用 MFSU
   * 大型项目建议开启，可以显著提升构建速度
   */
  mfsu: false,

  /**
   * 是否按需加载 antd
   * 自动引入 antd 组件样式
   */
  antd: {
    // 主题配置
    configProvider: {
      theme: {
        cssVar: true,
        token: {
          fontFamily: 'AlibabaSans, sans-serif',
        },
      },
    },
  },

  // ========== 插件配置 ==========
  /**
   * 数据流插件
   * 用于全局状态管理
   */
  model: {},

  /**
   * 全局初始状态
   * 用于在插件之间共享数据
   */
  initialState: {},

  /**
   * 权限插件
   * 基于 initialState 的权限控制
   */
  access: {},

  /**
   * 国际化插件
   */
  locale: {
    default: 'zh-CN',
    antd: false,
    baseNavigator: true,
  },

  /**
   * moment2dayjs 插件
   * 将 moment 替换为 dayjs，减小包体积
   */
  moment2dayjs: {
    preset: 'antd',
    plugins: ['duration'],
  },

  /**
   * 网络请求配置
   */
  request: {},

  // ========== Layout 配置 ==========
  /**
   * 布局配置
   */
  title: 'Py Small Admin',
  layout: {
    locale: false,
    ...defaultSettings,
  },

  // ========== OpenAPI 配置 ==========
  /**
   * 自动生成 API 服务和 Mock
   */
  openAPI: [
    {
      requestLibPath: "import { request } from '@umijs/max'",
      schemaPath: process.env.UMI_APP_OPEN_API_SCHEMAPATH || '',
      mock: false,
    },
  ],

  // ========== 其他配置 ==========
  /**
   * 忽略 moment 国际化
   * 减小包体积
   */
  ignoreMomentLocale: true,

  /**
   * 额外的 script
   */
  headScripts: [
    { src: '/scripts/loading.js', async: true },
  ],

  /**
   * 预设配置
   */
  presets: ['umi-presets-pro'],

  /**
   * esbuild 压缩
   */
  esbuildMinifyIIFE: true,

  /**
   * 请求记录
   */
  requestRecord: {},

  /**
   * 静态导出
   */
  exportStatic: {},
});
```

## 布局配置 (defaultSettings.ts)

### Layout 配置项

```typescript
import type { ProLayoutProps } from '@ant-design/pro-components';

const Settings: ProLayoutProps = {
  // ========== 基础配置 ==========
  /**
   * 系统名称
   */
  title: 'Py Small Admin',

  /**
   * Logo 地址
   */
  logo: '/logo.svg',

  /**
   * 布局模式
   * @side 侧边栏布局
   * @top 顶部栏布局
   * @mix 混合布局
   */
  layout: 'mix',

  /**
   * 内容宽度
   * @Fluid 流式布局
   * @Fixed 定宽布局
   */
  contentWidth: 'Fluid',

  // ========== 菜单配置 ==========
  /**
   * 分割菜单
   * 将第一级菜单放置到顶栏
   */
  splitMenus: true,

  // ========== 固定配置 ==========
  /**
   * 固定侧边栏
   */
  fixSiderbar: true,

  /**
   * 固定 Header
   */
  fixedHeader: true,

  // ========== 主题配置 ==========
  /**
   * 色弱模式
   */
  colorWeak: false,

  /**
   * 主题 Token 配置
   */
  token: {
    header: {
      // Header 背景色
      colorBgHeader: '#292f33',
      // 标题字体颜色
      colorHeaderTitle: '#fff',
      // 菜单项字体颜色
      colorTextMenu: '#dfdfdf',
      // 菜单项选中字体颜色
      colorTextMenuSelected: '#fff',
      // 菜单项 hover 背景色
      colorBgMenuItemHover: '#292f33',
      // 菜单项选中背景色
      colorBgMenuItemSelected: '#1890ff',
      // Header 高度
      heightLayoutHeader: 56,
    },
    sider: {
      // 菜单背景色
      colorMenuBackground: '#ffffff',
      // 菜单项 hover 背景色
      colorBgMenuItemHover: '#f6f6f6',
      // 菜单项字体颜色
      colorTextMenu: '#595959',
      // 菜单项选中颜色
      colorTextMenuSelected: '#1890ff',
    },
  },

  // ========== PWA 配置 ==========
  /**
   * 是否启用 PWA
   */
  pwa: false,
};

export default Settings;
```

### 主题定制

```typescript
// 在 config.ts 中配置主题
export default defineConfig({
  antd: {
    configProvider: {
      theme: {
        // 全局主题变量
        cssVar: true,
        token: {
          // 主色调
          colorPrimary: '#1890ff',
          // 圆角
          borderRadius: 4,
          // 字体
          fontFamily: 'AlibabaSans, sans-serif',
          // 字体大小
          fontSize: 14,
        },
        // 组件级主题
        components: {
          Button: {
            colorPrimary: '#00b96b',
            algorithm: true, // 启用算法
          },
          Input: {
            colorBgContainer: '#f5f5f5',
          },
        },
      },
    },
  },
});
```

## 运行配置

### 开发环境命令

```bash
# 启动开发服务器（使用 Mock）
npm start

# 启动开发服务器（不使用 Mock）
npm run start:no-mock

# 启动开发服务器（连接测试环境）
npm run start:test

# 启动开发服务器（连接预发布环境）
npm run start:pre
```

### 构建命令

```bash
# 生产构建
npm run build

# 分析构建产物
npm run analyze

# 预览构建产物
npm run preview
```

### 代码检查

```bash
# 代码检查
npm run lint

# 类型检查
npm run tsc

# 运行测试
npm test
```

## 主题切换配置

### 支持主题切换

```typescript
// config/config.ts
export default defineConfig({
  layout: {
    // 启用主题切换
    settings: {
      theme: {
        // 支持的主题
        list: [
          {
            key: 'light',
            label: '亮色模式',
            // 主题配置
          },
          {
            key: 'dark',
            label: '暗色模式',
            // 主题配置
          },
        ],
      },
    },
  },
});
```

### 自定义主题

```typescript
// 在 src/app.tsx 中配置运行时主题
import { RuntimeConfig } from '@umijs/max';

export const layout: RuntimeConfig['layout'] = ({
  initialState,
  setInitialState,
}) => {
  return {
    theme: {
      // 动态主题配置
      token: {
        colorPrimary: initialState?.settings?.colorPrimary || '#1890ff',
      },
    },
  };
};
```

## PWA 配置

### 启用 PWA

```typescript
// config/config.ts
export default defineConfig({
  // 开启 PWA
  pwa: true, // or { name: 'Py Small Admin' }

  layout: {
    pwa: true,
  },
});
```

### PWA 配置项

```typescript
export default defineConfig({
  pwa: {
    // PWA 名称
    name: 'Py Small Admin',
    // 简短名称
    shortName: 'Py Admin',
    // 描述
    description: 'Python 小型管理系统',
    // 主题色
    themeColor: '#1890ff',
    // 背景色
    backgroundColor: '#ffffff',
    // 图标
    icon: '/logo.png',
  },
});
```

## 构建优化配置

### 代码分割

```typescript
export default defineConfig({
  // 启用 MFSU
  mfsu: {
    // MFSU 配置
    cacheDirectory: './node_modules/.cache/mfsu',
    development: {
      output: '.mfsu-dev',
    },
    production: {
      output: '.mfsu-prod',
    },
  },

  // 按需加载
  chainWebpack(config) {
    config.optimization.splitChunks({
      chunks: 'all',
      cacheGroups: {
        vendor: {
          name: 'vendors',
          test: /[\\/]node_modules[\\/]/,
          priority: 10,
        },
      },
    });
  },
});
```

### 性能优化

```typescript
export default defineConfig({
  // 压缩配置
  codeSplitting: {
    jsStrategy: 'granularChunks',
  },

  // 图片优化
  inlineLimit: 10000, // 10KB 以下图片转 base64

  // CDN 配置
  publicPath: 'https://cdn.example.com/',

  // 忽略一些构建时的警告
  ignoreMomentLocale: true,
});
```

## 常见问题

### Q: 如何修改端口号？

创建 `.env` 文件：

```bash
PORT=8000
```

或在 `package.json` 中修改启动脚本：

```json
{
  "scripts": {
    "start": "max dev --port 8000"
  }
}
```

### Q: 如何配置多个环境？

创建多个环境文件：

```bash
.env.development   # 开发环境
.env.test          # 测试环境
.env.production    # 生产环境
```

然后使用不同的命令启动：

```bash
UMI_ENV=development npm start
UMI_ENV=test npm run start:test
UMI_ENV=production npm run build
```

### Q: 如何禁用某个功能？

```typescript
export default defineConfig({
  // 禁用国际化
  locale: false,

  // 禁用布局
  layout: false,

  // 禁用权限
  access: false,

  // 禁用请求配置
  request: false,
});
```

### Q: 如何添加全局样式？

```typescript
// config/config.ts
export default defineConfig({
  // 全局样式
  styles: [
    'src/global.less',
    'src/global.css',
  ],

  // 主题变量
  theme: {
    '@primary-color': '#1890ff',
  },
});
```

### Q: 如何配置别名？

```typescript
export default defineConfig({
  alias: {
    '@': './src',
    '@components': './src/components',
    '@utils': './src/utils',
    '@services': './src/services',
  },
});
```

### Q: 如何配置代理？

请参考 [代理配置文档](./proxy.md)。
