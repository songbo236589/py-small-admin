# 环境变量说明

本文档介绍了前端的环境变量配置。

## 简介

前端项目使用 Umi 框架，支持通过环境变量来配置不同环境下的行为。

## 环境变量文件

### 文件位置

```
admin-web/
├── .env                    # 默认环境变量（所有环境共享）
├── .env.development        # 开发环境
├── .env.production         # 生产环境
└── .env.test              # 测试环境
```

## UMI 环境变量

### 基础配置

| 变量名 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `UMI_APP_API_KEY` | API 密钥 | - | your-api-key |
| `UMI_APP_API_BASE_URL` | API 基础地址 | http://localhost:8000/api | http://localhost:8000/api |
| `UMI_APP_ENV` | 环境类型 | development | dev/test/production |
| `UMI_APP_TITLE` | 应用标题 | Py Small Admin | Py Small Admin |
| `UMI_APP_LOGO` | 应用 Logo | /logo.svg | /logo.svg |

### 认证配置

| 变量名 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `UMI_APP_TOKEN_KEY` | Token 存储键 | access_token | access_token |
| `UMI_APP_REFRESH_TOKEN_KEY` | 刷新 Token 存储键 | refresh_token | refresh_token |
| `UMI_APP_USER_INFO_KEY` | 用户信息存储键 | user_info | user_info |

### 功能开关

| 变量名 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `UMI_APP_ENABLE_MOCK` | 启用 Mock 数据 | false | true/false |
| `UMI_APP_ENABLE_DEBUG` | 启用调试模式 | false | true/false |
| `UMI_APP_ENABLE_ANALYTICS` | 启用数据分析 | false | true/false |

### 上传配置

| 变量名 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `UMI_APP_UPLOAD_SIZE_LIMIT` | 上传文件大小限制（MB） | 10 | 10 |
| `UMI_APP_UPLOAD_IMAGE_TYPES` | 允许的图片类型 | jpg,jpeg,png,gif | jpg,jpeg,png,gif,webp |
| `UMI_APP_UPLOAD_DOCUMENT_TYPES` | 允许的文档类型 | pdf,doc,docx | pdf,doc,docx,xls,xlsx |

### 分页配置

| 变量名 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `UMI_APP_PAGE_SIZE` | 默认每页数量 | 20 | 20 |
| `UMI_APP_PAGE_SIZE_OPTIONS` | 每页数量选项 | 10,20,50,100 | 10,20,50,100 |

## 环境配置示例

### 开发环境 (.env.development)

```bash
# API 配置
UMI_APP_API_KEY=dev-api-key-12345
UMI_APP_API_BASE_URL=http://localhost:8000/api
UMI_APP_ENV=development

# 功能开关
UMI_APP_ENABLE_MOCK=false
UMI_APP_ENABLE_DEBUG=true

# 上传配置
UMI_APP_UPLOAD_SIZE_LIMIT=50
UMI_APP_UPLOAD_IMAGE_TYPES=jpg,jpeg,png,gif,webp
```

### 生产环境 (.env.production)

```bash
# API 配置
UMI_APP_API_KEY=prod-api-key-67890
UMI_APP_API_BASE_URL=https://api.example.com/api
UMI_APP_ENV=production

# 功能开关
UMI_APP_ENABLE_MOCK=false
UMI_APP_ENABLE_DEBUG=false

# 上传配置
UMI_APP_UPLOAD_SIZE_LIMIT=10
UMI_APP_UPLOAD_IMAGE_TYPES=jpg,jpeg,png,gif
```

### 测试环境 (.env.test)

```bash
# API 配置
UMI_APP_API_KEY=test-api-key-11111
UMI_APP_API_BASE_URL=http://test-api.example.com/api
UMI_APP_ENV=test

# 功能开关
UMI_APP_ENABLE_MOCK=true
UMI_APP_ENABLE_DEBUG=true
```

## 使用环境变量

### 在代码中使用

```typescript
// 读取环境变量
const apiKey = process.env.UMI_APP_API_KEY;
const apiBaseUrl = process.env.UMI_APP_API_BASE_URL;

// 在配置文件中使用
export const request = {
  baseURL: process.env.UMI_APP_API_BASE_URL,
  headers: {
    'X-API-Key': process.env.UMI_APP_API_KEY,
  },
};
```

### 在 Umi 配置中使用

```typescript
// config/config.ts
export default defineConfig({
  define: {
    'process.env.UMI_APP_API_KEY': process.env.UMI_APP_API_KEY,
    'process.env.UMI_APP_API_BASE_URL': process.env.UMI_APP_API_BASE_URL,
  },
});
```

## 最佳实践

### 1. 环境变量命名规范

- 使用 `UMI_APP_` 前缀
- 使用大写字母和下划线
- 名称要有描述性

### 2. 敏感信息保护

- 不要将 `.env.*` 文件提交到版本控制
- 使用 `.env.example` 作为模板
- 不同环境使用不同的密钥

### 3. 类型安全

```typescript
// typings.d.ts
declare namespace NodeJS {
  interface ProcessEnv {
    UMI_APP_API_KEY: string;
    UMI_APP_API_BASE_URL: string;
    UMI_APP_ENV: 'development' | 'production' | 'test';
    UMI_APP_TITLE?: string;
  }
}
```

### 4. 环境变量验证

```typescript
// config/env.ts
const requiredEnvVars = [
  'UMI_APP_API_KEY',
  'UMI_APP_API_BASE_URL',
  'UMI_APP_ENV',
];

const missingEnvVars = requiredEnvVars.filter(
  (key) => !process.env[key]
);

if (missingEnvVars.length > 0) {
  throw new Error(
    `缺少必需的环境变量: ${missingEnvVars.join(', ')}`
  );
}
```

### 5. 提供默认值

```typescript
// 使用默认值
const apiBaseUrl = process.env.UMI_APP_API_BASE_URL || 'http://localhost:8000/api';
const pageSize = parseInt(process.env.UMI_APP_PAGE_SIZE || '20', 10);
```

## 常见问题

### 环境变量不生效

**问题**：修改了 `.env` 文件，但环境变量没有变化

**解决方案**：
1. 重启开发服务器
2. 检查 `.env` 文件是否在正确的目录
3. 确认环境变量名称拼写正确

### 类型提示缺失

**问题**：使用环境变量时没有类型提示

**解决方案**：在 `typings.d.ts` 中声明类型：

```typescript
declare const process: {
  env: {
    UMI_APP_API_KEY: string;
    UMI_APP_API_BASE_URL: string;
    // ...
  };
};
```

## 相关文档

- [后端环境变量](../../backend/config/env-variables.md)
- [配置指南](./index.md)
