# 环境变量说明

本文档介绍了前端的环境变量配置。

## 环境变量

### 开发环境

```bash
UMI_APP_API_KEY=your-api-key
UMI_APP_API_BASE_URL=http://localhost:8000/api
UMI_APP_ENV=dev
```

### 测试环境

```bash
UMI_APP_API_KEY=your-test-api-key
UMI_APP_API_BASE_URL=http://test-api.example.com/api
UMI_APP_ENV=test
```

### 生产环境

```bash
UMI_APP_API_KEY=your-prod-api-key
UMI_APP_API_BASE_URL=https://api.example.com/api
UMI_APP_ENV=production
```

## 配置说明

### UMI_APP_API_KEY

管理员 API 密钥，必须与后端的 `APP_ADMIN_X_API_KEY` 一致。

### UMI_APP_API_BASE_URL

后端 API 地址，根据环境不同而变化。

### UMI_APP_ENV

环境类型，可以是：
- `dev` - 开发环境
- `test` - 测试环境
- `pre` - 预发布环境
- `production` - 生产环境

## 最佳实践

1. 不要将 .env 文件提交到版本控制
2. 使用不同的密钥用于不同环境
3. 定期更新密钥
4. 使用强密钥
