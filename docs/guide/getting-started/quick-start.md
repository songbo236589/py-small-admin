# 快速启动指南

本指南将帮助你在 5 分钟内快速启动项目并体验主要功能。

## 启动项目

::: warning Windows 用户注意事项
如果您使用的是 Windows 系统，在使用平台账号验证功能前，请确保：

1. 将 `.env` 文件中的 `APP_RELOAD` 设置为 `false`
2. 使用 `python run.py` 启动服务（不要使用 `uvicorn` 命令直接启动）

详细说明请参考 [浏览器自动化功能文档](../backend/features/browser.md#windows-系统特殊配置)。
:::

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

### Content 模块

#### 1. 查看内容仪表盘

- 路径：`/content/dashboard`
- 功能：查看内容概览、统计数据

#### 2. 文章管理

- 路径：`/content/manage/article`
- 功能：创建、编辑、删除文章

**创建文章示例**：

```typescript
// 1. 点击"新建文章"按钮
// 2. 填写文章标题
// 3. 选择分类和标签
// 4. 编辑文章内容（TinyMCE）
// 5. 点击"确定"提交
```

#### 3. 话题管理

- 路径：`/content/manage/topic`
- 功能：抓取知乎话题、使用话题创建文章

**抓取话题示例**：

```typescript
// 1. 点击"抓取话题"按钮
// 2. 选择知乎账号
// 3. 设置抓取数量（10/20/50个）
// 4. 点击"开始抓取"
// 5. 等待抓取完成
```

**使用话题创建文章示例**：

```typescript
// 1. 在话题列表中选择感兴趣的话题
// 2. 点击"使用"按钮
// 3. 系统自动填充标题和描述
// 4. 编辑文章内容
// 5. 点击"确定"提交
```

#### 4. 平台账号管理

- 路径：`/content/manage/platform-account`
- 功能：管理各平台账号、验证 Cookie

**添加账号示例**：

```typescript
// 1. 点击"添加账号"按钮
// 2. 选择平台（知乎）
// 3. 填写账号名称
// 4. 使用浏览器扩展获取 Cookie
// 5. 点击"验证"按钮验证 Cookie
// 6. 点击"确定"提交
```

**验证账号示例**：

```typescript
// 1. 在账号列表中点击"验证"按钮
// 2. 等待验证完成（约 10-30 秒）
// 3. 查看验证结果
```

**Windows 用户注意**：
在 Windows 系统上使用 Cookie 验证功能需要特殊配置：

1. 将 `.env` 文件中的 `APP_RELOAD` 设置为 `false`
2. 完全重启后端服务（使用 `python run.py`）
3. 确保使用 `run.py` 启动，而不是直接用 `uvicorn` 命令

详见：[浏览器自动化功能文档 - Windows 系统特殊配置](../backend/features/browser.md#windows-系统特殊配置)

#### 5. 发布管理

- 路径：`/content/manage/publish`
- 功能：查看发布记录、重试失败发布

**发布文章示例**：

```typescript
// 1. 在文章列表中找到要发布的文章
// 2. 点击"发布"按钮
// 3. 选择平台和账号
// 4. 点击"确定"开始发布
// 5. 等待发布完成
```

**查看发布记录示例**：

```typescript
// 1. 进入发布管理页面
// 2. 查看所有发布记录
// 3. 查看发布状态（待发布/发布中/成功/失败）
// 4. 查看错误信息（如果发布失败）
// 5. 点击"重试"按钮重试失败发布
```

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

### Content 接口

- **GET** `/api/content/article/index` - 获取文章列表
- **POST** `/api/content/article/add` - 添加文章
- **PUT** `/api/content/article/update/{id}` - 更新文章
- **DELETE** `/api/content/article/destroy/{id}` - 删除文章
- **GET** `/api/content/topic/index` - 获取话题列表
- **GET** `/api/content/topic/fetch` - 抓取话题
- **POST** `/api/content/topic/{id}/use` - 使用话题
- **POST** `/api/content/topic/{id}/favorite` - 收藏话题
- **GET** `/api/content/platform_account/index` - 获取账号列表
- **POST** `/api/content/platform_account/add` - 添加账号
- **POST** `/api/content/platform_account/verify/{id}` - 验证账号
- **GET** `/api/content/publish/logs` - 获取发布记录
- **POST** `/api/content/publish/article/{id}` - 发布文章
- **PUT** `/api/content/publish/retry/{id}` - 重试发布

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
