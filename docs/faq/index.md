# 常见问题

## 开发问题

### 后端开发

#### 如何启动后端服务？

```bash
cd server
python run.py
```

服务将在 http://localhost:8000 启动。

#### 如何创建新模块？

```bash
python commands/create_module.py your_module
```

这将自动创建完整的模块目录结构和基础文件。

#### 如何执行数据库迁移？

```bash
cd server
alembic upgrade head
```

### 前端开发

#### 如何启动前端开发服务器？

```bash
cd admin-web
npm start
```

服务将在 http://localhost:8000 启动。

#### 如何添加新页面？

1. 在 `src/pages/` 下创建页面组件
2. 在 `config/routes/` 中添加路由配置
3. 在 `config/routes/` 中配置菜单

## 部署问题

### 如何部署到生产环境？

1. 修改 `.env` 文件，关闭调试模式
2. 构建前端：`npm run build`
3. 配置 Nginx 反向代理
4. 启动后端服务
5. 启动 Celery Worker 和 Beat
6. 配置 HTTPS

### 如何配置数据库连接？

编辑 `.env` 文件：

```bash
DB_CONNECTIONS__MYSQL__HOST=your-mysql-host
DB_CONNECTIONS__MYSQL__DATABASE=py_small_admin
DB_CONNECTIONS__MYSQL__USERNAME=root
DB_CONNECTIONS__MIN__MYSQL__PASSWORD=your-password
```

### 如何配置 Redis 连接？

编辑 `.env` 文件：

```bash
DB_REDIS__DEFAULT__HOST=your-redis-host
DB_REDIS__DEFAULT__PASSWORD=your-redis-password
```

## 业务问题

### 如何同步股票数据？

通过前端页面：
1. 进入"股票管理"
2. 点击"同步股票列表"按钮
3. 等待同步完成

或通过 API：
```bash
curl -X POST http://localhost:8000/api/quant/stock/sync_stock_list \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

### 如何配置邮件发送？

在 `.env` 文件中配置：

```bash
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

在"系统配置"中测试邮件发送。

### 如何启用云存储？

在 `.env` 文件中配置对应的云存储信息：

**阿里云 OSS**：
```bash
ALIYUN_OSS_ACCESS_KEY_ID=your-access-key-id
ALIYUN_OSS_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_OSS_BUCKET_NAME=your-bucket-name
```

然后在"系统配置"中选择存储类型。

## 最佳实践

### 1. 使用环境变量

不要硬编码敏感信息，始终使用环境变量。

### 2. 定期备份数据

设置定时任务自动备份数据库和文件。

### 3. 监控日志和性能

使用日志和监控工具监控系统运行状态。

### 4. 定期更新依赖

定期更新依赖包，修复安全漏洞。

## 获取更多帮助

- 查看 [API 文档](../api/)
- 查看 [开发指南](../guide/)
- 提交 [GitHub Issue](https://github.com/songbo236589/py-small-admin/issues)
