# 目录结构详解

## 项目整体结构

```
py-small-admin/
├── admin-web/              # 前端管理界面
├── admin-web-templates/    # 前端模板（可选）
├── docs/                   # 项目文档
├── server/                 # 后端服务
├── .git/                   # Git 仓库
└── .claude/               # Claude AI 配置
```

## 后端目录结构（server/）

```
server/
├── Modules/               # 业务模块
│   ├── admin/            # Admin 管理模块
│   │   ├── controllers/  # 控制器（请求处理）
│   │   ├── models/       # 数据模型（SQLModel）
│   │   ├── routes/       # 路由定义
│   │   ├── services/     # 业务逻辑
│   │   ├── validators/  # 数据验证
│   │   ├── migrations/   # 数据库迁移文件
│   │   ├── seeds/        # 初始数据填充
│   │   ├── tasks/        # 异步任务定义
│   │   └── queues/       # Celery 任务队列
│   ├── quant/            # Quant 量化模块
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── validators/
│   │   ├── migrations/
│   │   ├── seeds/
│   │   └── tasks/
│   └── common/           # 公共模块
│       ├── libs/        # 公共库
│       │   ├── app.py           # 应用生命周期
│       │   ├── config.py        # 配置管理
│       │   ├── database/        # 数据库管理
│       │   ├── celery.py        # Celery 配置
│       │   ├── cache.py         # 缓存管理
│       │   ├── auth/            # 认证服务
│       │   ├── upload/          # 文件上传
│       │   ├── captcha.py       # 验证码服务
│       │   ├── validation/      # 数据验证
│       │   └── exception.py     # 异常处理
│       └── services/    # 公共服务
│           └── base_service.py  # 基础服务类
├── config/               # 配置文件
│   ├── app.py          # 应用配置
│   ├── base.py         # 基础配置
│   ├── database.py     # 数据库配置
│   ├── celery.py       # Celery 配置
│   ├── cache.py        # 缓存配置
│   ├── jwt.py          # JWT 配置
│   ├── password.py     # 密码配置
│   ├── captcha.py      # 验证码配置
│   ├── log.py          # 日志配置
│   └── upload.py       # 上传配置
├── commands/            # 命令行工具
│   ├── migrate.py      # 数据库迁移命令
│   ├── seed.py         # 数据填充命令
│   ├── create_module.py # 创建模块命令
│   ├── generate_keys.py # 生成密钥命令
│   └── celery_manager.py # Celery 管理命令
├── logs/                # 日志目录
├── uploads/             # 上传文件目录
├── pids/                # 进程 ID 文件
├── assets/              # 静态资源
├── docker/              # Docker 配置
├── run.py              # 应用启动文件
├── main.py             # 主应用入口
├── requirements.txt    # Python 依赖列表
├── .env                # 环境变量配置
└── venv/               # Python 虚拟环境
```

### 详细说明

#### Modules/admin/ - Admin 管理模块

负责管理员、角色、菜单、系统配置等管理功能。

**controllers/** - 控制器层
- 处理 HTTP 请求
- 参数验证
- 调用服务层
- 返回响应

**models/** - 数据模型层
- 定义数据表结构
- 使用 SQLModel
- 自动生成 Alembic 迁移

**routes/** - 路由层
- 定义 API 路由
- 组合控制器
- 中间件配置

**services/** - 服务层
- 业务逻辑处理
- 数据库操作
- 缓存管理

**validators/** - 验证器层
- 请求参数验证
- 响应数据验证

**tasks/** - 异步任务
- Celery 任务定义
- 定时任务配置

**queues/** - 任务队列
- Celery 队列定义
- 任务路由配置

#### Modules/quant/ - Quant 量化模块

负责股票、行业、概念、K线等量化数据管理。

**数据表**：
- `fa_quant_stocks` - 股票表
- `fa_quant_industrys` - 行业表
- `fa_quant_concepts` - 概念表
- `fa_quant_stock_concepts` - 股票-概念关联表
- `fa_quant_stock_kline1ds` - 日K线表
- `fa_quant_stock_kline1ws` - 周K线表
- `fa_quant_stock_kline1ms` - 月K线表
- `fa_quant_stock_kline1m_mins` - 1分钟K线表
- `fa_quant_stock_kline5ms` - 5分钟K线表
- `fa_quant_stock_kline15ms` - 15分钟K线表
- `fa_quant_stock_kline30ms` - 30分钟K线表
- `fa_quant_stock_kline60ms` - 60分钟K线表
- `fa_quant_industry_logs` - 行业历史记录表
- `fa_quant_concept_logs` - 概念历史记录表

#### Modules/common/ - 公共模块

提供公共功能和工具。

**libs/** - 公共库
- `config.py` - 配置管理（基于 Pydantic Settings）
- `database/` - 数据库管理
  - `sql.py` - SQL 引擎和会话
  - `redis.py` - Redis 客户端
  - `sharding.py` - 分表策略
- `celery.py` - Celery 配置
- `cache.py` - Redis 缓存封装
- `auth/` - 认证服务
  - `jwt_service.py` - JWT 令牌管理
  - `auth_helper.py` - 认证辅助
- `upload/` - 文件上传
  - `upload_lib.py` - 上传处理逻辑
  - `upload_handler.py` - 上传处理器
  - `storage/` - 存储适配器
    - `local.py` - 本地存储
    - `aliyun_oss.py` - 阿里云 OSS
    - `tencent_cos.py` - 腾讯云 COS
    - `qiniu_oss.py` - 七牛云 Kodo
  - `image_processor.py` - 图片处理
  - `thumbnail.py` - 缩略图生成
  - `watermark.py` - 水印添加
- `captcha.py` - 验证码服务
- `validation/` - 数据验证
  - `pagination_validator.py` - 分页验证
  - `decorators.py` - 装饰器
  - `exceptions.py` - 异常定义

**services/** - 公共服务
- `base_service.py` - 基础服务类
  - `common_add()` - 通用添加
  - `common_update()` - 通用更新
  - `common_destroy()` - 通用删除
  - `common_destroy_all()` - 批量删除
  - `apply_search_filters()` - 应用搜索筛选
  - `apply_sorting()` - 应用排序

#### config/ - 配置文件

使用 Pydantic Settings 管理配置，支持环境变量、嵌套配置、类型转换。

**配置分类**：
- `app.py` - 应用配置（名称、版本、端口、CORS 等）
- `database.py` - 数据库配置（MySQL、Redis）
- `celery.py` - Celery 配置（Broker、Worker、Beat）
- `cache.py` - 缓存配置
- `jwt.py` - JWT 配置（密钥、算法、过期时间）
- `password.py` - 密码配置（策略、长度）
- `captcha.py` - 验证码配置
- `log.py` - 日志配置
- `upload.py` - 上传配置

#### commands/ - 命令行工具

提供便捷的命令行操作。

- `migrate.py` - 数据库迁移
  - `upgrade head` - 升级到最新版本
  - `downgrade base` - 回滚到初始版本
  - `revision` - 创建新的迁移
- `seed.py` - 数据填充
  - 填充初始管理员数据
  - 填充菜单数据
- `create_module.py` - 创建新模块
  - 自动创建目录结构
  - 自动生成基础文件
- `generate_keys.py` - 生成密钥
  - JWT 密钥
  - API 密钥
- `celery_manager.py` - Celery 管理
  - 启动 Worker
  - 启动 Beat
  - 启动 Flower

## 前端目录结构（admin-web/）

```
admin-web/
├── config/               # 配置文件
│   ├── config.ts        # 主配置文件
│   ├── routes/          # 路由配置
│   │   ├── index.ts     # 主路由入口
│   │   ├── admin.ts    # Admin 模块路由
│   │   └── quant.ts    # Quant 模块路由
│   ├── defaultSettings.ts # 默认设置
│   └── proxy.ts        # 代理配置
├── src/                  # 源代码
│   ├── pages/           # 页面组件
│   │   ├── admin/      # Admin 模块页面
│   │   │   ├── dashboard/
│   │   │   ├── auth/
│   │   │   │   ├── admin/
│   │   │   │   ├── group/
│   │   │   │   └── rule/
│   │   │   └── sys/
│   │   │       ├── sys_config/
│   │   │       └── upload/
│   │   ├── quant/     # Quant 模块页面
│   │   │   ├── dashboard/
│   │   │   └── data/
│   │   │       ├── stock/
│   │   │       ├── industry/
│   │   │       ├── concept/
│   │   │       ├── industry_log/
│   │   │       └── concept_log/
│   │   ├── login/
│   │   └── 404.tsx
│   ├── services/        # API 服务
│   │   ├── admin/
│   │   │   ├── auth/
│   │   │   │   ├── admin/
│   │   │   │   ├── group/
│   │   │   │   └── rule/
│   │   │   ├── common/
│   │   │   └── sys/
│   │   │       ├── sys_config/
│   │   │       └── upload/
│   │   └── quant/
│   │       └── data/
│   │           ├── stock/
│   │           ├── industry/
│   │           ├── concept/
│   │           ├── industry_log/
│   │           ├── concept_log/
│   │           └── kline/
│   ├── components/      # 公共组件
│   │   ├── common/
│   │   │   ├── CDel/
│   │   │   ├── CDelAll/
│   │   │   ├── NumberInput/
│   │   │   ├── ProFormTinyMCE/
│   │   │   ├── ProTableWrapper/
│   │   │   └── Upload/
│   │   │       ├── ImageUpload/
│   │   │       ├── DocumentUpload/
│   │   │       ├── VideoUpload/
│   │   │       ├── AudiosUpload/
│   │   │       └── MediaLibraryModal/
│   │   ├── Footer/
│   │   ├── HeaderDropdown/
│   │   └── RightContent/
│   │       ├── AvatarDropdown/
│   │       └── ChangePasswordModal/
│   ├── utils/           # 工具函数
│   │   ├── request.ts   # 请求封装
│   │   ├── storage.ts   # 本地存储
│   │   ├── utils.ts     # 通用工具
│   │   └── exportExcel.ts
│   ├── app.tsx          # 应用入口
│   ├── global.tsx       # 全局样式
│   ├── global.less      # 全局样式
│   ├── access.ts        # 权限控制
│   ├── loading.tsx      # 加载组件
│   └── typings.d.ts      # TypeScript 类型定义
├── public/               # 静态资源
│   ├── favicon.ico
│   ├── tinymce/         # TinyMCE 编辑器资源
│   └── ...
├── .env                  # 环境变量
├── .umirc.ts            # Umi 配置
├── package.json         # 依赖配置
├── tsconfig.json        # TypeScript 配置
├── .eslintrc.js         # ESLint 配置
├── .prettierrc.js       # Prettier 配置
└── docker/              # Docker 配置
```

### 详细说明

#### config/ - 配置文件

**config.ts** - 主配置文件
- 定义插件
- 定义路由
- 配置代理
- 配置主题
- 配置国际化
- 配置请求
- 配置权限

**routes/** - 路由配置
- 按模块组织路由
- 定义路由守卫
- 配置路由元信息

**proxy.ts** - 代理配置
- 开发环境代理
- 测试环境代理
- 预发布环境代理

#### src/pages/ - 页面组件

**admin/** - Admin 模块页面
- `dashboard/` - 仪表盘
- `auth/` - 认证管理（管理员、角色、菜单）
- `sys/` - 系统管理（系统配置、文件上传）

**quant/** - Quant 模块页面
- `dashboard/` - 量化仪表盘
- `data/` - 数据管理（股票、行业、概念、历史记录）

**login/** - 登录页面
**404.tsx** - 404 页面

#### src/services/ - API 服务

按模块组织 API 服务，每个服务包含：
- API 接口定义
- 请求参数类型
- 响应数据类型
- 统一错误处理

#### src/components/ - 公共组件

**common/** - 通用组件
- `ProTableWrapper` - Pro Table 封装
- `CDel` - 单个删除确认
- `CDelAll` - 批量删除确认
- `NumberInput` - 数字输入框
- `ProFormTinyMCE` - 富文本编辑器

**Upload/** - 上传组件
- `ImageUpload` - 图片上传
- `DocumentUpload` - 文档上传
- `VideoUpload` - 视频上传
- `AudiosUpload` - 音频上传
- `MediaLibraryModal` - 媒体库模态框

**RightContent/** - 右侧内容区
- `AvatarDropdown` - 头像下拉菜单
- `ChangePasswordModal` - 修改密码模态框

#### src/utils/ - 工具函数

- `request.ts` - 请求封装
  - 统一请求方法（GET、POST、PUT、DELETE、DOWNLOAD）
  - 自动添加 Token
  - 自动添加 API Key
  - 令牌刷新机制
  - 错误处理

- `storage.ts` - 本地存储
  - Token 存储
  - 用户信息存储
  - 系统配置存储

- `utils.ts` - 通用工具
  - 格式化函数
  - 日期处理
  - 数据转换

- `exportExcel.ts` - Excel 导出

#### src/app.tsx - 应用入口

- 应用初始化
- 全局状态管理
- 全局配置

#### src/access.ts - 权限控制

- 定义权限规则
- 权限验证函数

## 文档目录结构（docs/）

```
docs/
├── .vitepress/          # VitePress 配置
│   ├── cache/
│   ├── config.mts      # 主配置文件
│   └── theme/          # 自定义主题
├── guide/              # 开发指南
│   ├── introduction/   # 项目介绍
│   ├── getting-started/ # 快速开始
│   ├── backend/        # 后端开发指南
│   └── frontend/       # 前端开发指南
├── api/                # API 参考
├── deploy/             # 部署运维
├── faq/                # 常见问题
├── public/             # 静态资源
├── index.md            # 首页
├── package.json        # 依赖配置
└── yarn.lock
```

## 最佳实践

### 目录组织原则

1. **按功能模块组织**：相关功能放在一起
2. **分层清晰**：控制器、服务、模型、路由分离
3. **公共提取**：公共功能提取到 common 模块
4. **命名规范**：统一使用小写字母和下划线

### 文件命名规范

- **Python**：`snake_case.py`
- **TypeScript**：`PascalCase.ts` / `kebab-case.ts`
- **组件**：`PascalCase.tsx`
- **配置文件**：`snake_case.ts` / `kebab-case.ts`

### 代码组织规范

1. **导入顺序**：标准库 → 第三方库 → 本地模块
2. **类和方法**：先公共后私有
3. **常量定义**：文件顶部定义
4. **注释说明**：复杂逻辑添加注释

## 扩展建议

### 添加新模块

使用命令行工具快速创建：

```bash
python commands/create_module.py my_module
```

这会自动创建完整的目录结构和基础文件。

### 添加新页面

1. 在 `pages/` 下创建页面组件
2. 在 `services/` 下创建 API 服务
3. 在 `config/routes/` 下添加路由配置

### 添加新 API

1. 在 `models/` 下创建数据模型
2. 在 `services/` 下创建服务
3. 在 `controllers/` 下创建控制器
4. 在 `routes/` 下添加路由

## 总结

良好的目录结构是项目成功的基础，遵循上述规范可以使项目更加清晰、易于维护。
