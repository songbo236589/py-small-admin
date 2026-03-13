# 快速参考

本文档提供 Py Small Admin 的常用命令、配置和参考信息。

## 目录

- [常用命令](#常用命令)
- [端口配置](#端口配置)
- [默认账号](#默认账号)
- [常用链接](#常用链接)
- [环境变量](#环境变量)
- [文件路径](#文件路径)
- [数据库表](#数据库表)
- [API 端点](#api-端点)
- [状态码](#状态码)

## 常用命令

### 后端命令

```bash
# 启动后端服务
cd server
python run.py

# 数据库迁移
alembic upgrade head

# 回滚数据库
alembic downgrade -1

# 创建新的迁移
alembic revision --autogenerate -m "描述信息"

# 填充初始数据
python commands/seed.py

# 启动 Celery Worker
celery -A Modules.common.libs.celery.app worker --loglevel=info

# 启动 Celery Beat
celery -A Modules.common.libs.celery.app beat --loglevel=info

# 启动 Flower 监控
celery -A Modules.common.libs.celery.app flower

# 启动 Celery Manager
python -m commands.celery_manager worker start
python -m commands.celery_manager beat start
python -m commands.celery_manager flower start
```

### 前端命令

```bash
# 启动开发服务器
cd admin-web
npm start

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format

# 安装依赖
npm install

# 更新依赖
npm update
```

### 浏览器扩展命令

```bash
# 安装依赖
cd browser-extension
npm install

# Chrome 开发模式
npm run dev:chrome

# Firefox 开发模式
npm run dev:firefox

# 构建 Chrome 版本
npm run build:chrome

# 构建 Firefox 版本
npm run build:firefox

# 构建所有版本
npm run build
```

### 文档命令

```bash
# 启动文档开发服务器
cd docs
npm run dev

# 构建文档
npm run build

# 预览文档
npm run preview
```

### Docker 命令

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 进入容器
docker-compose exec server bash
```

## 端口配置

| 服务          | 端口  | 说明                  |
| ------------- | ----- | --------------------- |
| 后端 API      | 8000  | FastAPI 服务端口      |
| 前端          | 8000  | UmiJS 开发服务器端口  |
| MySQL         | 3306  | MySQL 数据库端口      |
| Redis         | 6379  | Redis 缓存端口        |
| RabbitMQ      | 5672  | RabbitMQ 消息队列端口 |
| RabbitMQ 管理 | 15672 | RabbitMQ 管理界面端口 |
| Flower        | 5555  | Celery 监控端口       |
| 文档          | 5173  | VitePress 文档端口    |

## 默认账号

### 管理员账号

| 字段   | 值                |
| ------ | ----------------- |
| 用户名 | admin             |
| 密码   | admin123          |
| 邮箱   | admin@example.com |

### 数据库账号

| 字段   | 值             |
| ------ | -------------- |
| 用户名 | root           |
| 密码   | （安装时设置） |
| 数据库 | py_small_admin |

### RabbitMQ 账号

| 字段   | 值    |
| ------ | ----- |
| 用户名 | guest |
| 密码   | guest |

## 常用链接

### 本地链接

| 服务          | 链接                       |
| ------------- | -------------------------- |
| 后端 API      | http://localhost:8000      |
| API 文档      | http://localhost:8000/docs |
| 前端          | http://localhost:8000      |
| 文档          | http://localhost:5173      |
| RabbitMQ 管理 | http://localhost:15672     |
| Flower 监控   | http://localhost:5555      |

### 在线链接

| 服务            | 链接                                           |
| --------------- | ---------------------------------------------- |
| GitHub 仓库     | https://github.com/songbo236589/py-small-admin |
| FastAPI 文档    | https://fastapi.tiangolo.com/                  |
| UmiJS 文档      | https://umijs.org/                             |
| Ant Design 文档 | https://ant.design/                            |
| Celery 文档     | https://docs.celeryq.dev/                      |

## 环境变量

### 后端环境变量

```bash
# 应用配置
APP_NAME=Py Small Admin
APP_ENV=development
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000
APP_RELOAD=true

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=py_small_admin

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT 配置
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Celery 配置
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 前端环境变量

```bash
# API 地址
REACT_APP_API_URL=http://localhost:8000

# 应用配置
REACT_APP_APP_NAME=Py Small Admin
```

## 文件路径

### 项目结构

```
py-small-admin/
├── server/                    # 后端代码
│   ├── Modules/               # 模块目录
│   │   ├── admin/           # Admin 模块
│   │   ├── quant/           # Quant 模块
│   │   ├── content/         # Content 模块
│   │   └── common/         # 公共模块
│   ├── config/              # 配置文件
│   ├── commands/            # 命令行工具
│   └── run.py              # 启动文件
│
├── admin-web/               # 前端代码
│   ├── src/                # 源代码
│   │   ├── pages/         # 页面
│   │   ├── components/    # 组件
│   │   └── services/      # API 服务
│   └── config/            # 配置文件
│
├── browser-extension/       # 浏览器扩展
│   ├── source/            # 源代码
│   └── dist/              # 构建输出
│
└── docs/                  # 文档
    ├── .vitepress/       # VitePress 配置
    ├── guide/            # 指南文档
    ├── api/              # API 文档
    └── deploy/           # 部署文档
```

### 配置文件

| 文件         | 路径                         | 说明               |
| ------------ | ---------------------------- | ------------------ |
| 后端配置     | `server/.env`                | 后端环境变量配置   |
| 前端配置     | `admin-web/.env`             | 前端环境变量配置   |
| 数据库配置   | `server/config/database.py`  | 数据库连接配置     |
| Celery 配置  | `server/config/celery.py`    | Celery 配置        |
| UmiJS 配置   | `admin-web/config/config.ts` | UmiJS 配置         |
| Webpack 配置 | `admin-web/.umirc.ts`        | UmiJS Webpack 配置 |

## 数据库表

### Admin 模块表

| 表名                 | 说明                |
| -------------------- | ------------------- |
| fa_admin_admins      | 管理员表            |
| fa_admin_groups      | 角色组表            |
| fa_admin_rules       | 菜单规则表          |
| fa_admin_auth_groups | 管理员-角色组关联表 |

### Quant 模块表

| 表名                   | 说明       |
| ---------------------- | ---------- |
| fa_quant_stocks        | 股票表     |
| fa_quant_industries    | 行业表     |
| fa_quant_concepts      | 概念表     |
| fa_quant_industry_logs | 行业历史表 |
| fa_quant_concept_logs  | 概念历史表 |
| fa_quant_stock_klines  | K线数据表  |

### Content 模块表

| 表名                      | 说明            |
| ------------------------- | --------------- |
| content_articles          | 文章表          |
| content_categories        | 分类表          |
| content_tags              | 标签表          |
| content_article_tags      | 文章-标签关联表 |
| content_topics            | 话题表          |
| content_platform_accounts | 平台账号表      |
| content_publish_logs      | 发布日志表      |

## API 端点

### 认证接口

| 方法 | 端点                              | 说明     |
| ---- | --------------------------------- | -------- |
| POST | `/api/admin/common/login`         | 用户登录 |
| POST | `/api/admin/common/logout`        | 用户登出 |
| POST | `/api/admin/common/refresh_token` | 刷新令牌 |

### Admin 模块接口

| 方法   | 端点                            | 说明           |
| ------ | ------------------------------- | -------------- |
| GET    | `/api/admin/admin/index`        | 获取管理员列表 |
| POST   | `/api/admin/admin/add`          | 添加管理员     |
| PUT    | `/api/admin/admin/update/{id}`  | 更新管理员     |
| DELETE | `/api/admin/admin/destroy/{id}` | 删除管理员     |
| GET    | `/api/admin/group/index`        | 获取角色组列表 |
| POST   | `/api/admin/group/add`          | 添加角色组     |
| PUT    | `/api/admin/group/update/{id}`  | 更新角色组     |
| DELETE | `/api/admin/group/destroy/{id}` | 删除角色组     |

### Content 模块接口

| 方法   | 端点                                        | 说明         |
| ------ | ------------------------------------------- | ------------ |
| GET    | `/api/content/article/index`                | 获取文章列表 |
| POST   | `/api/content/article/add`                  | 添加文章     |
| PUT    | `/api/content/article/update/{id}`          | 更新文章     |
| DELETE | `/api/content/article/destroy/{id}`         | 删除文章     |
| GET    | `/api/content/topic/index`                  | 获取话题列表 |
| GET    | `/api/content/topic/fetch`                  | 抓取话题     |
| POST   | `/api/content/topic/{id}/use`               | 使用话题     |
| GET    | `/api/content/platform_account/index`       | 获取账号列表 |
| POST   | `/api/content/platform_account/add`         | 添加账号     |
| POST   | `/api/content/platform_account/verify/{id}` | 验证账号     |
| GET    | `/api/content/publish/logs`                 | 获取发布记录 |
| POST   | `/api/content/publish/article/{id}`         | 发布文章     |
| PUT    | `/api/content/publish/retry/{id}`           | 重试发布     |

## 状态码

### HTTP 状态码

| 状态码 | 说明           |
| ------ | -------------- |
| 200    | 请求成功       |
| 201    | 创建成功       |
| 400    | 请求参数错误   |
| 401    | 未授权         |
| 403    | 禁止访问       |
| 404    | 资源不存在     |
| 500    | 服务器内部错误 |

### 业务状态码

| 状态码 | 说明           |
| ------ | -------------- |
| 200    | 操作成功       |
| 400    | 请求参数错误   |
| 401    | 未授权         |
| 403    | 禁止访问       |
| 404    | 资源不存在     |
| 500    | 服务器内部错误 |
| 1001   | 参数验证失败   |
| 1002   | 数据已存在     |
| 1003   | 数据不存在     |
| 1004   | 操作失败       |

### 文章状态

| 状态值 | 说明     |
| ------ | -------- |
| 0      | 草稿     |
| 1      | 已发布   |
| 2      | 审核中   |
| 3      | 发布失败 |

### 分类/标签状态

| 状态值 | 说明 |
| ------ | ---- |
| 0      | 禁用 |
| 1      | 启用 |

### 平台账号状态

| 状态值 | 说明 |
| ------ | ---- |
| 0      | 失效 |
| 1      | 有效 |
| 2      | 过期 |

### 发布日志状态

| 状态值 | 说明   |
| ------ | ------ |
| 0      | 待发布 |
| 1      | 发布中 |
| 2      | 成功   |
| 3      | 失败   |

## 常见问题速查

### 后端启动失败

```bash
# 检查端口是否被占用
netstat -ano | findstr :8000

# 检查数据库连接
mysql -u root -p -h localhost -e "SELECT 1"

# 检查环境变量
cat server/.env
```

### 前端启动失败

```bash
# 清除缓存
rm -rf node_modules package-lock.json
npm install

# 检查端口是否被占用
netstat -ano | findstr :8000
```

### 数据库连接失败

```bash
# 检查 MySQL 是否启动
docker ps | grep mysql

# 检查数据库是否存在
mysql -u root -p -e "SHOW DATABASES;"

# 检查数据库权限
mysql -u root -p -e "SHOW GRANTS FOR 'root'@'localhost';"
```

### Celery 任务不执行

```bash
# 检查 Worker 是否启动
celery -A Modules.common.libs.celery.app inspect active

# 检查任务是否注册
celery -A Modules.common.libs.celery.app inspect registered

# 检查队列
celery -A Modules.common.libs.celery.app inspect active_queues
```

## 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [UmiJS 官方文档](https://umijs.org/)
- [Ant Design 官方文档](https://ant.design/)
- [Celery 官方文档](https://docs.celeryq.dev/)
- [SQLModel 官方文档](https://sqlmodel.tiangolo.com/)
- [VitePress 官方文档](https://vitepress.dev/)
