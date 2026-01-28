# Admin-Web Docker 部署指南

本目录包含前端项目的 Docker 配置，支持开发环境和生产环境的容器化部署。

## 目录结构

```
docker/
├── .dockerignore              # Docker 构建忽略文件
├── .env.production.example    # 生产环境变量示例
├── Dockerfile.dev             # 开发环境 Dockerfile
├── Dockerfile.prod            # 生产环境 Dockerfile（多阶段构建）
├── nginx/
│   └── default.conf           # Nginx 配置文件
├── docker-compose.yml         # 开发环境编排文件
├── docker-compose.prod.yml    # 生产环境编排文件
└── README.md                  # 本文档
```

## 前置要求

1. **Docker 和 Docker Compose 已安装**
   - Docker >= 20.10
   - Docker Compose >= 2.0

2. **后端服务已启动**
   - 确保后端服务在 `../server/docker` 目录下已启动
   - 后端网络名称为 `py-small-admin-network`（开发环境）或 `py-small-admin-network-prod`（生产环境）

3. **网络配置**
   ```bash
   # 如果后端网络不存在，需要先创建
   docker network create py-small-admin-network
   docker network create py-small-admin-network-prod
   ```

## 开发环境

### 启动开发环境

1. **启动后端服务**（如果尚未启动）
   ```bash
   cd ../server/docker
   docker-compose up -d
   ```

2. **启动前端开发服务**
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **访问应用**
   - 前端地址：http://localhost:8000
   - 后端API：http://localhost:8009

### 开发环境特性

- ✅ 支持热更新（代码修改自动刷新）
- ✅ 源代码挂载到容器
- ✅ 使用 UmiJS 开发服务器
- ✅ 自动代理 API 请求到后端
- ✅ 实时编译和错误提示

### 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建镜像
docker-compose build --no-cache

# 进入容器
docker-compose exec admin-web-dev sh

# 清理所有资源
docker-compose down -v
```

### 开发环境配置

开发环境的环境变量在 `docker-compose.yml` 中配置：

```yaml
environment:
  UMI_APP_API_BASE_URL: http://fastapi:8009
  UMI_APP_API_KEY: "123456"
  MOCK: none
```

如需修改，编辑 `docker/docker-compose.yml` 文件。

## 生产环境

### 启动生产环境

1. **配置环境变量**
   ```bash
   cd docker
   cp .env.production.example .env.production
   # 编辑 .env.production 文件，修改相关配置
   ```

2. **构建并启动生产服务**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

3. **访问应用**
   - 前端地址：http://localhost:80
   - 健康检查：http://localhost/health

### 生产环境特性

- ✅ 多阶段构建，镜像体积小
- ✅ 使用 Nginx 提供静态文件服务
- ✅ Gzip 压缩
- ✅ 静态资源缓存优化
- ✅ API 请求代理到后端
- ✅ 健康检查
- ✅ 资源限制
- ✅ 日志管理

### 常用命令

```bash
# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 重新构建镜像
docker-compose -f docker-compose.prod.yml build --no-cache

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看资源使用情况
docker stats admin-web-prod
```

### 生产环境配置

编辑 `docker/.env.production` 文件：

```env
# API 配置
UMI_APP_API_BASE_URL=http://fastapi:8009
UMI_APP_API_KEY=your_api_key_here

# 环境配置
UMI_APP_ENV=production
UMI_ENV=production
```

## Nginx 配置说明

Nginx 配置文件位于 `docker/nginx/default.conf`，主要功能：

### 1. 静态文件服务

```nginx
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
}
```

### 2. API 代理

```nginx
location /api/ {
    proxy_pass http://fastapi_backend;
    # ... 代理配置
}
```

### 3. 缓存策略

- 静态资源（js, css, 图片等）：1年缓存
- HTML 文件：不缓存
- API 请求：不缓存

### 4. 安全头

- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: no-referrer-when-downgrade

## 故障排查

### 问题1：容器无法启动

**症状**：`docker-compose up` 失败

**解决方案**：
```bash
# 查看详细日志
docker-compose logs

# 检查端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# 修改端口配置
# 编辑 docker-compose.yml 或 docker-compose.prod.yml
```

### 问题2：API 请求失败

**症状**：前端无法访问后端 API

**解决方案**：
```bash
# 检查后端服务是否运行
docker ps | grep fastapi

# 检查网络连接
docker network inspect py-small-admin-network

# 检查环境变量
docker-compose exec admin-web-dev env | grep API

# 查看 Nginx 日志
docker-compose logs admin-web-dev | grep error
```

### 问题3：热更新不生效

**症状**：代码修改后页面不刷新

**解决方案**：
```bash
# 检查 volume 挂载
docker-compose exec admin-web-dev ls -la /app/src

# 重启开发服务器
docker-compose restart

# 清理并重新构建
docker-compose down
docker-compose up -d --build
```

### 问题4：生产环境构建失败

**症状**：`docker-compose -f docker-compose.prod.yml build` 失败

**解决方案**：
```bash
# 查看构建日志
docker-compose -f docker-compose.prod.yml build --no-cache

# 检查 Node.js 版本
docker-compose -f docker-compose.prod.yml run --rm admin-web node --version

# 检查依赖安装
docker-compose -f docker-compose.prod.yml run --rm admin-web npm ci
```

## 性能优化

### 1. 镜像优化

- 使用多阶段构建减小镜像体积
- 使用 Alpine Linux 基础镜像
- 清理不必要的依赖和缓存

### 2. 构建优化

```bash
# 使用构建缓存
docker-compose build

# 并行构建
docker-compose build --parallel
```

### 3. 运行时优化

- 生产环境设置资源限制
- 使用健康检查
- 配置日志轮转

## 安全建议

1. **不要在镜像中包含敏感信息**
   - 使用环境变量配置密钥
   - 不要提交 `.env` 文件到版本控制

2. **定期更新基础镜像**
   ```bash
   docker pull node:20-alpine
   docker pull nginx:alpine
   ```

3. **使用非 root 用户运行**
   - 当前配置使用 nginx 用户运行

4. **限制容器权限**
   - 生产环境已设置资源限制
   - 不要使用 `--privileged` 标志

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          cd docker
          docker-compose -f docker-compose.prod.yml build

      - name: Push to registry
        run: |
          docker tag admin-web:latest registry.example.com/admin-web:${{ github.sha }}
          docker push registry.example.com/admin-web:${{ github.sha }}
```

## 维护和更新

### 更新依赖

```bash
# 进入容器
docker-compose exec admin-web-dev sh

# 更新依赖
npm update

# 退出容器
exit

# 重新构建镜像
docker-compose build --no-cache
```

### 备份配置

```bash
# 备份配置文件
tar -czf docker-config-backup.tar.gz docker/
```

## 联系支持

如有问题，请联系开发团队或提交 Issue。

## 许可证

本项目遵循项目的整体许可证。
