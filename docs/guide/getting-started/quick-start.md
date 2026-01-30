# 快速启动指南

本指南将帮助你在 5 分钟内快速启动项目并体验主要功能。

## 启动项目

### 1. 启动后端服务

```bash
cd server
python run.py
```

服务将在 http://localhost:8000 启动。

### 2. 启动前端服务

打开新的终端窗口：

```bash
cd admin-web
npm start
```

前端将在 http://localhost:8000 启动。

## 登录系统

1. 打开浏览器访问 http://localhost:8000
2. 使用初始账号登录：
   - **用户名**：`admin`
   - **密码**：`admin123`
3. 点击登录

## 功能体验

### Admin 模块

#### 1. 查看仪表盘

登录后进入仪表盘，查看系统概览。

#### 2. 管理员管理

- 路径：`/admin/auth/admin`
- 功能：查看、添加、编辑、删除管理员

**添加管理员示例**：
```typescript
// 1. 点击"添加"按钮
// 2. 填写管理员信息（姓名、用户名、密码等）
// 3. 选择角色组
// 4. 点击"确定"提交
```

#### 3. 角色管理

- 路径：`/admin/auth/group`
- 功能：配置角色、分配权限

**配置权限示例**：
```typescript
// 1. 点击"权限配置"按钮
// 2. 勾选需要的菜单权限
// 3. 点击"保存"确认
```

#### 4. 菜单管理

- 路径：`/admin/auth/rule`
- 功能：管理菜单树、配置菜单信息

#### 5. 系统配置

- 路径：`/admin/sys/sys_config`
- 功能：配置系统参数、测试邮件

**测试邮件示例**：
```typescript
// 1. 进入"邮件配置"标签页
// 2. 填写 SMTP 服务器信息
// 3. 点击"测试邮件"按钮
// 4. 输入收件人邮箱
// 5. 点击"发送"
```

#### 6. 文件上传

- 路径：`/admin/sys/upload`
- 功能：上传图片、文档、视频、音频

**上传图片示例**：
```typescript
// 1. 点击"图片上传"按钮
// 2. 选择图片文件
// 3. 等待上传完成
// 4. 查看上传结果和图片 URL
```

### Quant 模块

#### 1. 查看量化仪表盘

- 路径：`/quant/dashboard`
- 功能：查看量化数据概览

#### 2. 股票管理

- 路径：`/quant/data/stock`
- 功能：查看股票列表、同步股票数据

**同步股票数据**：
```python
# 点击"同步股票列表"按钮
# 等待同步完成
# 查看同步结果
```

#### 3. 行业管理

- 路径：`/quant/data/industry`
- 功能：查看行业列表、同步行业数据

**同步行业数据**：
```python
# 点击"同步行业列表"按钮
# 等待同步完成
# 查看同步结果
```

#### 4. 概念管理

- 路径：`/quant/data/concept`
- 功能：查看概念列表、同步概念数据

**同步概念数据**：
```python
# 点击"同步概念列表"按钮
# 等待同步完成
# 查看同步结果
```

#### 5. 行业历史记录

- 路径：`/quant/data/industry_log`
- 功能：查询行业历史数据

#### 6. 概念历史记录

- 路径：`/quant/data/concept_log`
- 功能：查询概念历史数据

## API 文档查看

访问 http://localhost:8000/docs 查看完整的 API 文档。

### 认证接口

- **POST** `/api/admin/common/login` - 用户登录
- **POST** `/api/admin/common/logout` - 用户登出
- **POST** `/api/admin/common/refresh_token` - 刷新令牌

### Admin 接口

- **GET** `/api/admin/admin/index` - 获取管理员列表
- **POST** `/api/admin/admin/add` - 添加管理员
- **PUT** `/api/admin/admin/update/{id}` - 更新管理员
- **DELETE** `/api/admin/admin/destroy/{id}` - 删除管理员

### Quant 接口

- **GET** `/api/quant/stock/index` - 获取股票列表
- **POST** `/api/quant/stock/sync_stock_list` - 同步股票列表
- **GET** `/api/quant/industry/index` - 获取行业列表
- **POST** `/api/quant/industry/sync_industry_list` - 同步行业列表

## 开发模式

### 后端热重载

后端默认启用了热重载，修改代码后会自动重启服务。

### 前端热重载

前端默认启用了热重载，修改代码后会自动刷新页面。

## 数据库操作

### 查看数据库

```bash
mysql -u root -p py_small_admin
```

### 查看表结构

```sql
SHOW TABLES;
DESC fa_admin_admins;
```

### 手动执行 SQL

```sql
-- 查询所有管理员
SELECT * FROM fa_admin_admins;

-- 查询所有股票
SELECT * FROM fa_quant_stocks LIMIT 10;
```

## 常用命令

### 后端命令

```bash
# 启动服务
python run.py

# 数据库迁移
alembic upgrade head

# 填充初始数据
python commands/seed.py

# 启动 Celery Worker
celery -A Modules.common.libs.celery.celery_service.celery worker -l info

# 启动 Celery Beat
celery -A Modules.common.libs.celery.celery_service.celery beat -l info
```

### 前端命令

```bash
# 启动开发服务器
npm start

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint
```

## 调试技巧

### 后端调试

1. 在代码中添加断点或 `print` 语句
2. 查看控制台输出
3. 使用日志系统：

```python
from loguru import logger

logger.info("这是一条信息日志")
logger.error("这是一条错误日志")
```

### 前端调试

1. 打开浏览器开发者工具（F12）
2. 查看 Console 面板
3. 查看 Network 面板查看请求
4. 使用 React DevTools 调试组件