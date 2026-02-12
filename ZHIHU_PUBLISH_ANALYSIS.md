# 知乎文章自动发布模块 - 可行性分析与实现方案

> 基于 ArtiPub 项目的深度分析，为 py-small-admin 项目设计内容管理模块

---

## 📋 目录

- [1. 项目背景](#1-项目背景)
- [2. 项目架构风格分析](#2-项目架构风格分析)
- [3. 知乎平台分析](#3-知乎平台分析)
- [4. 技术方案设计](#4-技术方案设计)
- [5. 数据模型设计](#5-数据模型设计)
- [6. 模块结构设计](#6-模块结构设计)
- [7. 实现步骤](#7-实现步骤)
- [8. 风险与挑战](#8-风险与挑战)
- [9. 后续扩展规划](#9-后续扩展规划)

---

## 1. 项目背景

### 1.1 目标

在 py-small-admin 项目中实现一个内容管理模块，支持文章的创建、编辑和自动发布到知乎平台。

### 1.2 技术栈

| 层级 | 现有技术 | 需要新增 |
|------|----------|----------|
| 后端框架 | FastAPI | - |
| 数据库 | MySQL + SQLModel | - |
| 异步任务 | Celery + RabbitMQ | - |
| 浏览器自动化 | - | Playwright/Selenium |
| AI 集成 | - | Ollama (本地) |
| 前端框架 | React + UmiJS | - |
| UI 组件 | Ant Design | - |

---

## 2. 项目架构风格分析

> 本章节基于对 py-small-admin 项目的深度分析，确保新模块与现有架构完全契合

### 2.1 架构层次与职责

```
┌─────────────────────────────────────────────────────────────────┐
│                         请求流程                                  │
└─────────────────────────────────────────────────────────────────┘

  路由层                控制器层              服务层              模型层
 (routes/)           (controllers/)        (services/)         (models/)
    │                     │                    │                  │
    │ 1. 定义路由          │ 2. 参数验证          │ 3. 业务逻辑        │ 4. 数据持久化
    │ 2. 映射控制器        │ 3. 调用服务          │ 4. 数据操作        │ 5. 关系管理
    │                     │ 4. 返回响应          │ 5. 返回结果        │
    ▼                     ▼                    ▼                  ▼
┌─────────┐          ┌─────────┐         ┌─────────┐        ┌─────────┐
│ APIRouter│────────▶│Controller│────────▶│ Service │────────▶│ SQLModel│
│ prefix  │          │ validate │         │ CRUD   │        │ Table   │
│ tags    │          │ service  │         │ Logic  │        │ Relation│
└─────────┘          └─────────┘         └─────────┘        └─────────┘
```

### 2.2 命名规范对照表

| 层级 | 规范 | 示例 |
|------|------|------|
| **路由文件** | `{模块名}.py` | `admin.py`, `article.py` |
| **路由前缀** | `/{模块名}` | `/admin`, `/content/article` |
| **路由标签** | `["中文描述"]` | `["管理员管理"]`, `["文章管理"]` |
| **控制器文件** | `{模块名}_controller.py` | `admin_controller.py` |
| **控制器类** | `{模块名}Controller` | `AdminController` |
| **控制器方法** | `index/add/edit/update/set_status/destroy` | 统一命名 |
| **服务文件** | `{模块名}_service.py` | `admin_service.py` |
| **服务类** | `{模块名}Service` | `AdminService` (继承 `BaseService`) |
| **验证器文件** | `{模块名}_validator.py` | `admin_validator.py` |
| **验证器类** | `{操作}Request` | `AdminAddRequest` |
| **模型文件** | `{模块前缀}_{表名}.py` | `admin_admin.py` |
| **模型类** | `{模块前缀}{表名}` | `AdminAdmin` (继承 `BaseTableModel`) |

### 2.3 路由定义风格

```python
# 链式调用 + 函数式路由风格
from typing import Any
from fastapi import APIRouter
from Modules.content.controllers.v1.article_controller import ArticleController

router = APIRouter(prefix="/content/article", tags=["文章管理"])
controller = ArticleController()

# 统一响应模型
response_model=dict[str, Any]

# 标准路由定义
router.get("/index", response_model=dict[str, Any], summary="文章列表")(controller.index)
router.post("/add", response_model=dict[str, Any], summary="文章添加")(controller.add)
router.get("/edit/{id}", response_model=dict[str, Any], summary="文章编辑数据")(controller.edit)
router.put("/update/{id}", response_model=dict[str, Any], summary="文章更新")(controller.update)
router.put("/set_status/{id}", response_model=dict[str, Any], summary="文章状态")(controller.set_status)
router.delete("/destroy/{id}", response_model=dict[str, Any], summary="文章删除")(controller.destroy)
router.delete("/destroy_all", response_model=dict[str, Any], summary="批量删除")(controller.destroy_all)
```

### 2.4 控制器层模式

```python
# 控制器职责：
# 1. 参数定义（使用 FastAPI 的 Path/Query/Form/Body）
# 2. 参数验证（使用装饰器）
# 3. 调用服务层
# 4. 返回服务层结果

from fastapi import Path, Query, Form
from fastapi.responses import JSONResponse
from Modules.content.services.article_service import ArticleService
from Modules.content.validators.article_validator import ArticleAddRequest
from Modules.common.libs.validation.decorators import validate_request_data
from Modules.common.libs.validation.pagination_validator import PaginationRequest

class ArticleController:
    def __init__(self):
        self.article_service = ArticleService()

    @validate_request_data(PaginationRequest)  # 分页验证
    @validate_request_data(ArticleAddRequest)    # 业务验证
    async def add(
        self,
        title: str = Form(..., description="文章标题"),
        content: str = Form(..., description="文章内容"),
        category_id: int = Form(..., description="分类ID"),
    ) -> JSONResponse:
        return await self.article_service.add({
            "title": title,
            "content": content,
            "category_id": category_id,
        })
```

### 2.5 服务层模式

```python
# 服务层职责：
# 1. 继承 BaseService 获得通用 CRUD
# 2. 实现具体业务逻辑
# 3. 数据库操作
# 4. 返回统一格式响应

from fastapi.responses import JSONResponse
from Modules.common.services.base_service import BaseService

class ArticleService(BaseService):
    """文章服务"""

    async def add(self, data: dict) -> JSONResponse:
        # 使用通用方法
        return await self.common_add(
            data=data,
            model_class=ContentArticle,
            pre_operation_callback=self._article_add_pre_operation,
        )

    async def _article_add_pre_operation(self, data, session):
        # 前置操作：业务验证和数据处理
        title = data.get("title")
        if not title or len(title.strip()) == 0:
            return error("标题不能为空")

        # 处理数据
        data["title"] = title.strip()
        data["author_id"] = 1  # 从 JWT 获取当前用户

        return data, session
```

### 2.6 模型层模式

```python
# 模型层职责：
# 1. 继承 BaseTableModel
# 2. 定义字段和关系
# 3. 自动生成表名（驼峰→下划线+复数）

from typing import Optional
from sqlmodel import Field, Relationship
from Modules.common.models.base_model import BaseTableModel

class ContentArticle(BaseTableModel, table=True):
    """文章表"""
    __table_comment__ = "文章表"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str = Field(default="")
    status: int = Field(default=0)

    # 关系定义
    category: Optional["ContentCategory"] = Relationship(back_populates="articles")

# 自动生成的表名：content_articles
```

### 2.7 验证器层模式

```python
# 验证器职责：
# 1. 继承 BaseModel (来自 common.models.base_model)
# 2. 定义字段验证规则
# 3. 使用 @field_validator 自定义验证

from pydantic import Field, field_validator
from Modules.common.models.base_model import BaseModel

class ArticleAddRequest(BaseModel):
    """文章添加请求模型"""

    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("标题不能为空")
        if len(v) > 200:
            raise ValueError("标题长度不能超过200个字符")
        return v.strip()
```

### 2.8 内容管理模块目录结构（适配现有架构）

```
server/Modules/content/
├── __init__.py
│
├── routes/                    # 路由层
│   ├── __init__.py
│   ├── article.py            # 文章路由
│   ├── category.py           # 分类路由
│   ├── tag.py                # 标签路由
│   ├── platform_account.py   # 平台账号路由
│   └── publish.py            # 发布路由
│
├── controllers/               # 控制器层
│   ├── __init__.py
│   └── v1/
│       ├── article_controller.py
│       ├── category_controller.py
│       ├── tag_controller.py
│       ├── platform_controller.py
│       └── publish_controller.py
│
├── services/                  # 服务层
│   ├── __init__.py
│   ├── article_service.py
│   ├── category_service.py
│   ├── tag_service.py
│   ├── platform_account_service.py
│   └── publisher/            # 发布器（子模块）
│       ├── __init__.py
│       ├── base_publisher.py
│       └── zhihu_publisher.py
│
├── validators/                # 验证器层
│   ├── __init__.py
│   ├── article_validator.py
│   ├── category_validator.py
│   ├── tag_validator.py
│   └── platform_validator.py
│
├── models/                    # 模型层
│   ├── __init__.py
│   ├── content_article.py
│   ├── content_category.py
│   ├── content_tag.py
│   ├── content_article_tag.py
│   ├── content_platform_account.py
│   └── content_publish_log.py
│
├── queues/                    # 异步任务队列
│   ├── __init__.py
│   └── publish_queue.py
│
└── tasks/                     # 定时任务
    ├── __init__.py
    └── cookie_validator.py
```

### 2.9 与现有架构的契合度

| 方面 | 现有架构 | 内容模块需求 | 契合度 |
|------|----------|-------------|--------|
| 分层架构 | routes → controllers → services → models | 完全匹配 | ✅ 100% |
| 通用 CRUD | BaseService.common_add/update/destroy | 需要基础 CRUD | ✅ 100% |
| 搜索过滤 | apply_search_filters | 需要搜索文章 | ✅ 100% |
| 分页 | CustomParams + paginate | 需要分页列表 | ✅ 100% |
| 参数验证 | @validate_request_data | 需要表单验证 | ✅ 100% |
| 响应格式 | success/error 统一格式 | 保持一致 | ✅ 100% |
| 数据库 | SQLModel + 异步会话 | 完全兼容 | ✅ 100% |
| 关系管理 | Relationship | 文章-分类-标签关系 | ✅ 100% |
| 异步任务 | Celery + RabbitMQ | 发布任务队列 | ✅ 100% |

---

## 3. 知乎平台分析

### 3.1 平台信息

| 项目 | 详情 |
|------|------|
| 平台ID | `zhihu` |
| 编辑器URL | `https://zhuanlan.zhihu.com/write` |
| 编辑器类型 | Markdown |
| 认证方式 | Cookie |
| 发布方式 | Markdown 文件导入 |

### 3.2 知乎发布流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        知乎文章发布流程                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────┐    ┌────────────┐    ┌──────────────┐    ┌─────────┐
│  1.导航  │───▶│ 2.创建临时  │───▶│ 3.上传Markdown│───▶│ 4.发布  │
│ 到编辑器 │    │    文件     │    │     文件      │    │  文章   │
└─────────┘    └────────────┘    └──────────────┘    └─────────┘
                   │                   │                    │
                   ▼                   ▼                    ▼
            ┌────────────┐    ┌──────────────┐    ┌─────────────┐
            │ 添加版权声明│    │ 点击更多按钮 │    │ 两步确认发布 │
            │ (文末追加) │    │ 选择导入文档 │    │ (设置→发布) │
            └────────────┘    └──────────────┘    └─────────────┘
```

### 3.3 关键 DOM 元素

| 操作 | 选择器 | 说明 |
|------|--------|------|
| 标题输入 | `.WriteIndex-titleInput > .Input` | 文章标题 |
| 发布按钮 | `.PublishPanel-triggerButton` | 打开发布面板 |
| 第一步确认 | `.PublishPanel-stepOneButton > button` | 进入发布设置 |
| 最终发布 | `.PublishPanel-stepTwoButton` | 确认发布 |
| 文件上传 | `input[accept=".docx,.doc,.markdown,.mdown,.mkdn,.md"]` | Markdown导入 |

### 3.4 知乎特性

| 特性 | 说明 | 实现要点 |
|------|------|----------|
| **Markdown 导入** | 通过文件上传导入内容 | 创建临时 md 文件 |
| **两步发布** | 先设置后发布 | 两次点击确认 |
| **版权声明** | 文末自动添加 | 内容追加 |
| **分类标签** | 可选择话题分类 | 元数据管理 |

---

## 4. 技术方案设计

### 4.1 浏览器自动化方案对比

| 方案 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| **Playwright** | 官方维护、API现代、支持多浏览器、异步友好 | 相对较新 | ⭐⭐⭐⭐⭐ |
| **Selenium** | 生态成熟、文档丰富 | 同步API、性能一般 | ⭐⭐⭐⭐ |
| **Pyppeteer** | Puppeteer移植版 | 维护不活跃 | ⭐⭐ |

### 4.2 推荐方案：Playwright

```python
# 安装
pip install playwright
playwright install chromium

# 基础使用
from playwright.async_api import async_playwright

async def publish_article():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # ... 发布逻辑
```

**选择理由：**
1. 官方维护，更新活跃
2. 异步 API，与 FastAPI 完美契合
3. 自动等待机制，减少超时问题
4. 内置拦截和监控功能
5. 跨浏览器支持

### 4.3 Cookie 管理方案

```python
# Cookie 存储结构
{
    "zhihu": {
        "cookies": [
            {
                "name": "z_c0",
                "value": "xxx",
                "domain": ".zhihu.com",
                "path": "/",
                "expires": 1234567890
            }
        ],
        "userAgent": "Mozilla/5.0...",
        "lastUpdate": "2025-02-05T10:30:00Z"
    }
}
```

### 4.4 Ollama 集成方案

```python
# AI 内容优化
import ollama

def optimize_for_zhihu(title: str, content: str) -> dict:
    response = ollama.chat(model='qwen2.5', messages=[{
        'role': 'user',
        'content': f'''
        优化以下文章以适应知乎平台的风格：
        标题：{title}
        内容：{content}

        要求：
        1. 生成更吸引人的标题（3个选项）
        2. 优化内容结构（添加小标题、重点标注）
        3. 生成适合的话题标签（3-5个）
        '''
    }])
    return response
```

---

## 5. 数据模型设计

### 5.1 核心数据表

```sql
-- 文章表
fa_content_articles
├── id                BIGINT UNSIGNED PK AUTO_INCREMENT
├── title             VARCHAR(200)  NOT NULL
├── content           TEXT          NOT NULL  (Markdown格式)
├── summary           VARCHAR(500)  NULL
├── cover_image_id    BIGINT UNSIGNED NULL
├── status            SMALLINT      NOT NULL DEFAULT 0  (0=草稿, 1=已发布, 2=审核中, 3=发布失败)
├── author_id         BIGINT UNSIGNED NOT NULL
├── category_id       BIGINT UNSIGNED NULL
├── view_count        BIGINT UNSIGNED NOT NULL DEFAULT 0
├── published_at      DATETIME      NULL
├── created_at        DATETIME      NOT NULL
├── updated_at        DATETIME      NULL
└── 索引: status, author_id, category_id, created_at, updated_at

-- 分类表
fa_content_categories
├── id                BIGINT UNSIGNED PK AUTO_INCREMENT
├── name              VARCHAR(50)   NOT NULL
├── slug              VARCHAR(50)   NOT NULL UNIQUE
├── parent_id         BIGINT UNSIGNED NULL (FK自关联)
├── sort              BIGINT UNSIGNED NOT NULL DEFAULT 0
├── status            SMALLINT      NOT NULL DEFAULT 1  (0=禁用, 1=启用)
├── description       VARCHAR(200)  NULL
├── created_at        DATETIME      NOT NULL
├── updated_at        DATETIME      NULL
└── 索引: slug, parent_id, status, created_at, updated_at

-- 标签表
fa_content_tags
├── id                BIGINT UNSIGNED PK AUTO_INCREMENT
├── name              VARCHAR(30)   NOT NULL UNIQUE
├── slug              VARCHAR(30)   NOT NULL UNIQUE
├── color             VARCHAR(7)    NULL
├── sort              BIGINT UNSIGNED NOT NULL DEFAULT 0
├── status            SMALLINT      NOT NULL DEFAULT 1  (0=禁用, 1=启用)
├── created_at        DATETIME      NOT NULL
├── updated_at        DATETIME      NULL
└── 索引: name, slug, status, created_at, updated_at

-- 文章标签关联表
fa_content_article_tags
├── article_id        BIGINT UNSIGNED NOT NULL (FK)
├── tag_id            BIGINT UNSIGNED NOT NULL (FK)
└── PRIMARY KEY (article_id, tag_id)

-- 平台账号表
fa_content_platform_accounts
├── id                BIGINT UNSIGNED PK AUTO_INCREMENT
├── platform          VARCHAR(20)   NOT NULL  (zhihu, juejin, csdn等)
├── account_name      VARCHAR(50)   NOT NULL
├── cookies           TEXT          NOT NULL  (JSON格式加密存储)
├── user_agent        VARCHAR(500)  NULL
├── status            SMALLINT      NOT NULL DEFAULT 1  (0=失效, 1=有效, 2=过期)
├── last_verified     DATETIME      NULL
├── created_by        BIGINT UNSIGNED NOT NULL
├── created_at        DATETIME      NOT NULL
├── updated_at        DATETIME      NULL
└── 索引: platform, status, created_at, updated_at

-- 发布记录表
fa_content_publish_logs
├── id                BIGINT UNSIGNED PK AUTO_INCREMENT
├── article_id        BIGINT UNSIGNED NOT NULL (FK)
├── platform          VARCHAR(20)   NOT NULL
├── platform_article_id VARCHAR(50)  NULL
├── platform_url      VARCHAR(200)  NULL
├── status            SMALLINT      NOT NULL DEFAULT 0  (0=待发布, 1=发布中, 2=成功, 3=失败)
├── error_message     TEXT          NULL
├── retry_count       INT           NOT NULL DEFAULT 0
├── task_id           VARCHAR(50)   NULL  (Celery任务ID)
├── created_at        DATETIME      NOT NULL
└── 索引: article_id, platform, status
```

### 5.2 SQLModel 数据模型

> 按照项目现有架构风格设计，继承 BaseTableModel，使用 Column 方式定义字段

```python
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, String, Text, Index
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship
from Modules.common.models.base_model import BaseTableModel

# 导入链接表（非 TYPE_CHECKING 块）
from .content_article_tag import ContentArticleTag

if TYPE_CHECKING:
    from .content_category import ContentCategory
    from .content_publish_log import ContentPublishLog
    from .content_tag import ContentTag


class ContentArticle(BaseTableModel, table=True):
    """文章表"""
    __table_comment__ = "文章表，存储文章信息"

    # 主键
    id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 字段定义
    title: str = Field(
        sa_column=Column(String(200), nullable=False, comment="文章标题"),
        default="",
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False, comment="文章内容（Markdown格式）"),
        default="",
    )
    summary: Optional[str] = Field(
        sa_column=Column(String(500), nullable=True, comment="文章摘要"),
        default=None,
    )
    cover_image_id: Optional[int] = Field(
        sa_column=Column(INTEGER(unsigned=True), nullable=True, comment="封面图片ID"),
        default=None,
    )
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="0",
            comment="状态: 0=草稿, 1=已发布, 2=审核中, 3=发布失败",
            index=True,
        ),
        default=0,
    )
    author_id: int = Field(
        sa_column=Column(INTEGER(unsigned=True), nullable=False, comment="作者ID"),
        default=0,
    )
    category_id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_categories.id", ondelete="SET NULL"),
            nullable=True,
            comment="分类ID",
        ),
        default=None,
    )
    view_count: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="浏览次数",
        ),
        default=0,
    )
    published_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=True, comment="发布时间"),
        default=None,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )

    # 关系定义
    category: Mapped[Optional["ContentCategory"]] = Relationship(back_populates="articles")
    tags: Mapped[list["ContentTag"]] = Relationship(
        back_populates="articles",
        link_model=ContentArticleTag,
    )
    publish_logs: Mapped[list["ContentPublishLog"]] = Relationship(back_populates="article")

    # 索引
    __table_args__ = (
        Index("idx_author_status", "author_id", "status"),
        Index("idx_category_status", "category_id", "status"),
        Index("idx_status_created", "status", "created_at"),
    )


class ContentCategory(BaseTableModel, table=True):
    """分类表"""
    __table_comment__ = "文章分类表，存储文章分类信息"

    id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )
    name: str = Field(
        sa_column=Column(String(50), nullable=False, comment="分类名称"),
        default="",
    )
    slug: str = Field(
        sa_column=Column(
            String(50), nullable=False, unique=True, index=True, comment="分类别名"
        ),
        default="",
    )
    parent_id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_categories.id", ondelete="CASCADE"),
            nullable=True,
            comment="父分类ID",
            index=True,
        ),
        default=None,
    )
    sort: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="排序",
        ),
        default=0,
    )
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="状态: 0=禁用, 1=启用",
            index=True,
        ),
        default=1,
    )
    description: Optional[str] = Field(
        sa_column=Column(String(200), nullable=True, comment="分类描述"),
        default=None,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )

    # 关系定义
    articles: list["ContentArticle"] = Relationship(back_populates="category")


class ContentTag(BaseTableModel, table=True):
    """标签表"""
    __table_comment__ = "文章标签表，存储文章标签信息"

    id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )
    name: str = Field(
        sa_column=Column(
            String(30), nullable=False, unique=True, index=True, comment="标签名称"
        ),
        default="",
    )
    slug: str = Field(
        sa_column=Column(
            String(30), nullable=False, unique=True, index=True, comment="标签别名"
        ),
        default="",
    )
    color: Optional[str] = Field(
        sa_column=Column(String(7), nullable=True, comment="标签颜色"),
        default=None,
    )
    sort: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="排序",
        ),
        default=0,
    )
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="状态: 0=禁用, 1=启用",
            index=True,
        ),
        default=1,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )

    # 关系定义
    articles: Mapped[list["ContentArticle"]] = Relationship(
        back_populates="articles",
        link_model=ContentArticleTag,
    )


class ContentArticleTag(BaseTableModel, table=True):
    """文章标签关联表"""
    __table_comment__ = "文章标签关联表，存储文章与标签的多对多关系"

    article_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_articles.id", ondelete="CASCADE"),
            primary_key=True,
            comment="文章ID",
        ),
        default=0,
    )
    tag_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_tags.id", ondelete="CASCADE"),
            primary_key=True,
            comment="标签ID",
        ),
        default=0,
    )


class ContentPlatformAccount(BaseTableModel, table=True):
    """平台账号表"""
    __table_comment__ = "第三方平台账号表，存储第三方平台账号信息"

    id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )
    platform: str = Field(
        sa_column=Column(
            String(20), nullable=False, comment="平台标识：zhihu, juejin, csdn等", index=True
        ),
        default="",
    )
    account_name: str = Field(
        sa_column=Column(String(50), nullable=False, comment="账号名称"),
        default="",
    )
    cookies: str = Field(
        sa_column=Column(Text, nullable=False, comment="Cookie信息（JSON格式加密存储）"),
        default="",
    )
    user_agent: Optional[str] = Field(
        sa_column=Column(String(500), nullable=True, comment="浏览器UA"),
        default=None,
    )
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="状态: 0=失效, 1=有效, 2=过期",
            index=True,
        ),
        default=1,
    )
    last_verified: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=True, comment="最后验证时间"),
        default=None,
    )
    created_by: int = Field(
        sa_column=Column(INTEGER(unsigned=True), nullable=False, comment="创建人ID"),
        default=0,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )


class ContentPublishLog(BaseTableModel, table=True):
    """发布日志表"""
    __table_comment__ = "文章发布日志表，存储文章发布记录"

    id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )
    article_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_articles.id", ondelete="CASCADE"),
            nullable=False,
            comment="文章ID",
            index=True,
        ),
        default=0,
    )
    platform: str = Field(
        sa_column=Column(String(20), nullable=False, comment="发布平台", index=True),
        default="",
    )
    platform_article_id: Optional[str] = Field(
        sa_column=Column(String(50), nullable=True, comment="平台文章ID"),
        default=None,
    )
    platform_url: Optional[str] = Field(
        sa_column=Column(String(200), nullable=True, comment="平台文章链接"),
        default=None,
    )
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="0",
            comment="状态: 0=待发布, 1=发布中, 2=成功, 3=失败",
            index=True,
        ),
        default=0,
    )
    error_message: Optional[str] = Field(
        sa_column=Column(Text, nullable=True, comment="错误信息"),
        default=None,
    )
    retry_count: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="重试次数",
        ),
        default=0,
    )
    task_id: Optional[str] = Field(
        sa_column=Column(String(50), nullable=True, comment="Celery任务ID"),
        default=None,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间"),
        default=None,
    )

    # 关系定义
    article: Mapped["ContentArticle"] = Relationship(back_populates="publish_logs")
```

### 5.3 状态字段说明

| 表名 | 状态字段 | 状态值说明 |
|------|----------|-----------|
| `content_articles` | `status` | 0=草稿，1=已发布，2=审核中，3=发布失败 |
| `content_categories` | `status` | 0=禁用，1=启用 |
| `content_tags` | `status` | 0=禁用，1=启用 |
| `content_platform_accounts` | `status` | 0=失效，1=有效，2=过期 |
| `content_publish_logs` | `status` | 0=待发布，1=发布中，2=成功，3=失败 |

### 5.4 字段说明

| 字段 | 说明 |
|------|------|
| **sort** | 排序字段，用于自定义列表展示顺序，值越小越靠前 |
| **status** | 状态字段，控制记录的启用/禁用状态 |
| **created_at** | 创建时间，所有表都有此字段且带索引 |
| **updated_at** | 更新时间，大部分表都有此字段且带索引 |
| **跨模块引用** | `author_id`、`created_by`、`cover_image_id` 等跨模块字段不使用数据库外键约束 |

---

## 6. 模块结构设计

> 目录结构已整合到「2.8 内容管理模块目录结构」，本章聚焦核心类设计

### 6.1 基础发布器设计

```python
# services/publisher/base_platform_handler.py
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page

class BasePlatformHandler(ABC):
    """平台处理器基类（融合验证和发布）"""

    def __init__(self, cookies: list[dict], user_agent: str | None = None,
                 article_data: dict[str, Any] | None = None):
        self.cookies = cookies
        self.user_agent = user_agent
        self.article_data = article_data
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名称"""
        pass

    @abstractmethod
    async def verify(self) -> dict:
        """验证 Cookie"""
        pass

    @abstractmethod
    async def publish(self) -> PublishResult:
        """发布文章"""
        pass

    # ... 其他辅助方法
```

```python
# services/publisher/zhihu_handler.py
from .base_platform_handler import BasePlatformHandler

class ZhihuHandler(BasePlatformHandler):
    """知乎处理器（融合验证和发布）"""

    @property
    def platform_name(self) -> str:
        return "zhihu"

    @property
    def platform_domain(self) -> str:
        return "zhuanlan.zhihu.com"

    async def publish(self, article: Article) -> PublishResult:
        """发布文章到知乎"""
        try:
            # 1. 初始化浏览器
            await self._init_browser()
            await self._load_cookies()

            # 2. 导航到编辑器
            await self.page.goto("https://zhuanlan.zhihu.com/write")
            await self.page.wait_for_load_state("networkidle")

            # 3. 验证登录状态
            if not await self._verify_login():
                raise Exception("Cookie已失效，请重新登录")

            # 4. 创建临时Markdown文件
            temp_file = await self._create_temp_md(article)

            # 5. 上传文件
            await self._upload_markdown(temp_file)

            # 6. 发布文章
            article_url = await self._do_publish()

            return PublishResult(
                success=True,
                platform_article_id=self._extract_zhihu_id(article_url),
                platform_url=article_url
            )

        except Exception as e:
            return PublishResult(success=False, error=str(e))
        finally:
            await self.close()

    async def _verify_login(self) -> bool:
        """验证知乎登录状态"""
        try:
            # 检查是否存在登录后的元素
            await self.page.wait_for_selector(
                ".WriteIndex-titleInput",
                timeout=5000
            )
            return True
        except:
            return False

    async def _create_temp_md(self, article: Article) -> str:
        """创建临时Markdown文件"""
        import tempfile

        content = f"""# {article.title}

{article.content}

> 本文章由 py-small-admin 内容管理系统自动发布
"""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.md',
            delete=False,
            encoding='utf-8'
        )
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    async def _upload_markdown(self, file_path: str):
        """上传Markdown文件"""
        # 点击"更多"按钮
        await self.page.click("#Popover3-toggle")
        await self.page.wait_for_timeout(500)

        # 点击"导入文档"
        await self.page.click("text=导入文档")

        # 等待文件输入框
        file_input = await self.page.wait_for_selector(
            'input[accept*=".md"]'
        )

        # 上传文件
        await file_input.set_input_files(file_path)

        # 等待导入完成
        await self.page.wait_for_selector(".WriteIndex-titleInput", timeout=30000)

    async def _do_publish(self) -> str:
        """执行发布操作"""
        # 点击发布按钮
        await self.page.click(".PublishPanel-triggerButton")
        await self.page.wait_for_timeout(1000)

        # 点击下一步
        await self.page.click(".PublishPanel-stepOneButton button")
        await self.page.wait_for_timeout(1000)

        # 最终发布
        await self.page.click(".PublishPanel-stepTwoButton")

        # 等待跳转
        await self.page.wait_for_url("**/p/**")

        return self.page.url
```

---

## 7. 实现步骤

### 阶段一：基础内容管理 (2-3天)

```
Week 1: 数据模型与基础CRUD
├── Day 1: 数据模型设计与数据库迁移
│   ├── 创建 Article, Category, Tag 模型
│   ├── 编写 Alembic 迁移脚本
│   └── 创建种子数据
│
├── Day 2: 后端API开发
│   ├── 文章CRUD接口
│   ├── 分类管理接口
│   └── 标签管理接口
│
└── Day 3: 前端页面开发
    ├── 文章列表页
    ├── 文章编辑页（TinyMCE）
    └── 分类/标签管理页
```

### 阶段二：知乎发布器 (5-7天)

```
Week 2-3: 知乎发布功能
├── Day 4-5: Playwright 集成
│   ├── 安装和配置 Playwright
│   ├── 基础浏览器封装
│   └── Cookie管理功能
│
├── Day 6-7: 知乎发布器开发
│   ├── 实现知乎发布流程
│   ├── 临时文件处理
│   └── 错误处理与重试
│
├── Day 8: Celery 异步任务
│   ├── 创建发布任务队列
│   ├── 实现任务状态追踪
│   └── Flower 监控集成
│
└── Day 9: 平台账号管理
    ├── 账号CRUD接口
    ├── Cookie导入功能
    └── Cookie有效性检测
```

### 阶段三：发布记录与监控 (3-4天)

```
Week 3: 监控与优化
├── Day 10: 发布记录管理
│   ├── 发布日志表
│   ├── 发布历史查询
│   └── 错误信息展示
│
├── Day 11: 批量发布功能
│   ├── 多文章批量选择
│   ├── 批量任务创建
│   └── 进度实时显示
│
└── Day 12: Cookie 自动检测
    ├── 定时检测任务
    ├── 过期提醒
    └── 一键重新登录指引
```

### 阶段四：Ollama AI 优化 (可选, 5-7天)

```
Week 4-5: AI 内容优化
├── Day 13-14: Ollama 集成
│   ├── 安装 Ollama
│   ├── 拉取 Qwen 模型
│   └── Python API 封装
│
├── Day 15-16: AI 内容优化
│   ├── 标题优化建议
│   ├── 内容结构优化
│   └── 标签推荐
│
└── Day 17: 智能功能
    ├── 自动生成摘要
    ├── SEO 优化建议
    └── 平台风格适配
```

---

## 8. 风险与挑战

### 8.1 技术风险

| 风险 | 等级 | 应对措施 |
|------|------|----------|
| **知乎反爬虫** | 🔴 高 | 1. 使用真实浏览器<br>2. 限制发布频率<br>3. 模拟人工操作 |
| **Cookie 过期** | 🟡 中 | 1. 定期检测有效性<br>2. 过期自动提醒<br>3. 提供重新登录指引 |
| **DOM 结构变化** | 🟡 中 | 1. 使用多种选择器<br>2. 增加等待机制<br>3. 实时监控告警 |
| **并发资源占用** | 🟡 中 | 1. 限制并发数量<br>2. 使用Celery控制<br>3. 任务超时机制 |

### 8.2 合规风险

| 风险 | 说明 | 建议 |
|------|------|------|
| **服务条款** | 大规模自动发布可能违反知乎服务条款 | 1. 仅用于个人账号<br>2. 控制发布频率<br>3. 添加来源声明 |
| **内容版权** | 转发内容需有版权授权 | 1. 仅发布原创内容<br>2. 自动添加来源<br>3. 用户确认机制 |

### 8.3 运维风险

| 风险 | 应对措施 |
|------|----------|
| **浏览器资源占用** | 1. 设置超时自动关闭<br>2. 任务完成后清理 |
| **临时文件堆积** | 1. 定时清理任务<br>2. 发布完成后删除 |
| **任务队列堵塞** | 1. 优先级队列<br>2. 失败任务自动重试 |

---

## 9. 后续扩展规划

### 9.1 多平台扩展

在知乎功能稳定后，可以扩展支持更多平台：

| 平台 | 优先级 | 难度 | 说明 |
|------|--------|------|------|
| **掘金** | P0 | ⭐⭐ | 支持 Markdown，API 相对简单 |
| **CSDN** | P1 | ⭐⭐⭐ | HTML 格式，有验证码风险 |
| **简书** | P1 | ⭐⭐ | 流程简单，Markdown 支持 |
| **SegmentFault** | P2 | ⭐⭐ | 技术社区，Markdown 支持 |
| **开源中国** | P2 | ⭐⭐ | 流程相对简单 |

### 9.2 高级功能

```
内容管理模块高级功能
├── AI 功能
│   ├── 自动生成配图
│   ├── 内容质量评分
│   ├── 智能排版优化
│   └── 多语言翻译
│
├── 发布策略
│   ├── 定时发布
│   ├── 多平台同步
│   ├── 发布效果统计
│   └── A/B 测试
│
└── 数据分析
    ├── 阅读量统计
    ├── 互动数据追踪
    ├── 平台效果对比
    └── 热门话题分析
```

### 9.3 架构演进

```
当前架构 (单体应用)
    ↓
微服务拆分 (未来规划)
    ├── content-service (内容管理)
    ├── publisher-service (发布服务)
    ├── ai-service (AI 优化)
    └── analytics-service (数据分析)
```

---

## 附录

- [A. 依赖清单](#a-依赖清单)
- [B. 配置示例](#b-配置示例)
- [C. API 接口设计](#c-api-接口设计)
- [D. 前端页面设计](#d-前端页面设计)
- [E. 数据库迁移](#e-数据库迁移)
- [F. 错误处理规范](#f-错误处理规范)

### A. 依赖清单

```txt
# 新增依赖
playwright==1.48.0          # 浏览器自动化
ollama==0.4.1               # Ollama API 客户端
pydantic==2.10.4            # 数据验证
aiofiles==24.1.0            # 异步文件操作
```

### B. 配置示例

```python
# config/content.py
class ContentConfig(BaseSettings):
    # 内容配置
    ENABLE_AI_OPTIMIZE: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5"

    # 发布配置
    PUBLISH_TIMEOUT: int = 300  # 秒
    MAX_RETRY_COUNT: int = 3
    HEADLESS_BROWSER: bool = True

    # Cookie 配置
    COOKIE_CHECK_INTERVAL: int = 3600  # 秒

    # 临时文件
    TEMP_DIR: str = "tmp/content"
    TEMP_FILE_CLEANUP: bool = True
```

### C. API 接口设计

> 遵循项目现有架构风格：/index, /add, /edit/{id}, /update/{id}, /set_status/{id}, /destroy/{id}

#### 文章管理 API

| 方法 | 路径 | 说明 | 控制器方法 |
|------|------|------|-----------|
| GET | `/content/article/index` | 文章列表（支持搜索、分页、排序） | `index` |
| POST | `/content/article/add` | 文章添加 | `add` |
| GET | `/content/article/edit/{id}` | 文章编辑数据 | `edit` |
| PUT | `/content/article/update/{id}` | 文章更新 | `update` |
| PUT | `/content/article/set_status/{id}` | 文章状态变更 | `set_status` |
| DELETE | `/content/article/destroy/{id}` | 文章删除 | `destroy` |
| DELETE | `/content/article/destroy_all` | 文章批量删除 | `destroy_all` |

#### 分类管理 API

| 方法 | 路径 | 说明 | 控制器方法 |
|------|------|------|-----------|
| GET | `/content/category/index` | 分类列表（支持树形结构） | `index` |
| POST | `/content/category/add` | 分类添加 | `add` |
| GET | `/content/category/edit/{id}` | 分类编辑数据 | `edit` |
| PUT | `/content/category/update/{id}` | 分类更新 | `update` |
| PUT | `/content/category/set_status/{id}` | 分类状态变更 | `set_status` |
| **PUT** | **`/content/category/set_sort/{id}`** | **分类排序** | **`set_sort`** |
| DELETE | `/content/category/destroy/{id}` | 分类删除 | `destroy` |
| DELETE | `/content/category/destroy_all` | 批量删除 | `destroy_all` |

#### 标签管理 API

| 方法 | 路径 | 说明 | 控制器方法 |
|------|------|------|-----------|
| GET | `/content/tag/index` | 标签列表（支持搜索、分页、排序） | `index` |
| POST | `/content/tag/add` | 标签添加 | `add` |
| GET | `/content/tag/edit/{id}` | 标签编辑数据 | `edit` |
| PUT | `/content/tag/update/{id}` | 标签更新 | `update` |
| **PUT** | **`/content/tag/set_status/{id}`** | **标签状态变更** | **`set_status`** |
| **PUT** | **`/content/tag/set_sort/{id}`** | **标签排序** | **`set_sort`** |
| DELETE | `/content/tag/destroy/{id}` | 标签删除 | `destroy` |
| DELETE | `/content/tag/destroy_all` | 批量删除 | `destroy_all` |

#### 平台账号管理 API

| 方法 | 路径 | 说明 | 控制器方法 |
|------|------|------|-----------|
| GET | `/content/platform_account/index` | 账号列表 | `index` |
| POST | `/content/platform_account/add` | 添加账号 | `add` |
| GET | `/content/platform_account/edit/{id}` | 账号编辑数据 | `edit` |
| PUT | `/content/platform_account/update/{id}` | 更新账号 | `update` |
| DELETE | `/content/platform_account/destroy/{id}` | 删除账号 | `destroy` |
| POST | `/content/platform_account/verify/{id}` | 验证Cookie有效性 | `verify` |

#### 发布管理 API

| 方法 | 路径 | 说明 | 控制器方法 |
|------|------|------|-----------|
| POST | `/content/publish/article/{id}` | 发布文章到指定平台 | `publish_article` |
| POST | `/content/publish/batch` | 批量发布多篇文章 | `publish_batch` |
| GET | `/content/publish/logs` | 发布记录列表 | `logs` |
| GET | `/content/publish/logs/{id}` | 发布记录详情 | `log_detail` |
| PUT | `/content/publish/retry/{id}` | 重试失败发布 | `retry` |

#### AI 优化 API（可选）

| 方法 | 路径 | 说明 | 控制器方法 |
|------|------|------|-----------|
| POST | `/content/ai/optimize/{id}` | AI 内容优化（标题、摘要、结构） | `optimize` |
| POST | `/content/ai/summary` | 生成文章摘要 | `generate_summary` |
| POST | `/content/ai/tags` | 推荐适合的标签 | `recommend_tags` |

#### 完整路由定义示例

```python
# content/tag.py
from typing import Any
from fastapi import APIRouter
from Modules.content.controllers.v1.tag_controller import TagController

router = APIRouter(prefix="/content/tag", tags=["标签管理"])
controller = TagController()

router.get("/index", response_model=dict[str, Any], summary="标签列表")(controller.index)
router.post("/add", response_model=dict[str, Any], summary="标签添加")(controller.add)
router.get("/edit/{id}", response_model=dict[str, Any], summary="标签编辑数据")(controller.edit)
router.put("/update/{id}", response_model=dict[str, Any], summary="标签更新")(controller.update)
router.put("/set_status/{id}", response_model=dict[str, Any], summary="标签状态")(controller.set_status)
router.put("/set_sort/{id}", response_model=dict[str, Any], summary="标签排序")(controller.set_sort)
router.delete("/destroy/{id}", response_model=dict[str, Any], summary="标签删除")(controller.destroy)
router.delete("/destroy_all", response_model=dict[str, Any], summary="批量删除")(controller.destroy_all)
```

#### 注意事项

1. **API 前缀**：所有路由会自动添加配置的 `api_prefix`（如 `/api`）
2. **响应格式**：统一使用 `dict[str, Any]` 作为响应模型
3. **参数验证**：使用 `@validate_request_data` 装饰器进行参数验证
4. **权限控制**：根据需要添加权限验证中间件

---

### D. 前端页面设计

> 基于 React + UmiJS + Ant Design 技术栈

#### D.1 页面结构

```
admin-web/src/pages/content/
├── article/
│   ├── index.tsx           # 文章列表页
│   ├── add.tsx             # 文章添加页
│   ├── edit.tsx            # 文章编辑页
│   └── components/
│       ├── ArticleTable.tsx     # 文章表格组件
│       ├── ArticleForm.tsx      # 文章表单组件
│       └── ArticleModal.tsx     # 文章弹窗组件
│
├── category/
│   ├── index.tsx           # 分类列表页
│   └── components/
│       ├── CategoryTree.tsx     # 分类树组件
│       └── CategoryForm.tsx     # 分类表单组件
│
├── tag/
│   ├── index.tsx           # 标签列表页
│   └── components/
│       └── TagForm.tsx          # 标签表单组件
│
├── publish/
│   ├── index.tsx           # 发布管理页
│   ├── logs.tsx            # 发布记录页
│   └── components/
│       ├── PublishModal.tsx     # 发布弹窗
│       └── LogTable.tsx         # 日志表格
│
└── platform/
    ├── index.tsx           # 平台账号管理页
    └── components/
        └── PlatformForm.tsx     # 账号表单组件
```

#### D.2 文章列表页示例

```tsx
// admin-web/src/pages/content/article/index.tsx
import { ProTable } from '@ant-design/pro-components';
import { Button, Popconfirm, Space, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined } from '@ant-design/icons';
import { request } from '@umijs/max';
import { useRef, useState } from 'react';

export default () => {
  const actionRef = useRef();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 80, search: false },
    { title: '标题', dataIndex: 'title', ellipsis: true },
    {
      title: '分类',
      dataIndex: 'category_name',
      width: 120,
      search: false,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueType: 'select',
      valueEnum: {
        0: { text: '草稿', status: 'Default' },
        1: { text: '已发布', status: 'Success' },
        2: { text: '审核中', status: 'Processing' },
        3: { text: '失败', status: 'Error' },
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      valueType: 'dateTime',
      width: 180,
      search: false,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 200,
      render: (_, record) => [
        <a key="edit" href={`/content/article/edit/${record.id}`}>
          <EditOutlined /> 编辑
        </a>,
        record.status === 0 && (
          <Popconfirm
            key="publish"
            title="确定要发布这篇文章吗？"
            onConfirm={async () => {
              await request(`/content/publish/article/${record.id}`, { method: 'POST' });
              actionRef.current?.reload();
            }}
          >
            <a><SendOutlined /> 发布</a>
          </Popconfirm>
        ),
        <Popconfirm
          key="delete"
          title="确定要删除吗？"
          onConfirm={async () => {
            await request(`/content/article/destroy/${record.id}`, { method: 'DELETE' });
            actionRef.current?.reload();
          }}
        >
          <a style={{ color: 'red' }}><DeleteOutlined /> 删除</a>
        </Popconfirm>,
      ],
    },
  ];

  return (
    <ProTable
      actionRef={actionRef}
      rowKey="id"
      request={async (params) => {
        const { data } = await request('/content/article/index', {
          method: 'GET',
          params,
        });
        return {
          data: data.items,
          success: true,
          total: data.total,
        };
      }}
      columns={columns}
      rowSelection={{
        selectedRowKeys,
        onChange: setSelectedRowKeys,
      }}
      tableAlertRender={({ selectedRowKeys }) => (
        <Space size={24}>
          <span>
            已选择 <a style={{ fontWeight: 600 }}>{selectedRowKeys.length}</a> 项
          </span>
        </Space>
      )}
      toolBarRender={() => [
        <Button
          key="add"
          type="primary"
          icon={<PlusOutlined />}
          href="/content/article/add"
        >
          新建文章
        </Button>,
        <Popconfirm
          key="batchPublish"
          title="确定要批量发布选中的文章吗？"
          onConfirm={async () => {
            await request('/content/publish/batch', {
              method: 'POST',
              data: { ids: selectedRowKeys },
            });
            actionRef.current?.reload();
            setSelectedRowKeys([]);
          }}
          disabled={selectedRowKeys.length === 0}
        >
          <Button icon={<SendOutlined />} disabled={selectedRowKeys.length === 0}>
            批量发布
          </Button>
        </Popconfirm>,
      ]}
    />
  );
};
```

#### D.3 文章编辑页示例

```tsx
// admin-web/src/pages/content/article/add.tsx
import { ProForm, ProFormText, ProFormTextArea, ProFormSelect } from '@ant-design/pro-components';
import { Card, Button, message } from 'antd';
import { history, request } from '@umijs/max';
import TinyMCE from '@/components/TinyMCE';

export default () => {
  const [form] = Form.useForm();

  const handleSubmit = async (values: any) => {
    try {
      await request('/content/article/add', {
        method: 'POST',
        data: values,
      });
      message.success('文章创建成功');
      history.push('/content/article');
    } catch (error) {
      message.error('创建失败');
    }
  };

  return (
    <ProForm
      form={form}
      onFinish={handleSubmit}
      submitter={{
        render: (props) => (
          <Button type="primary" onClick={props.submit} loading={props.loading}>
            提交
          </Button>
        ),
      }}
    >
      <Card title="文章信息" style={{ marginBottom: 16 }}>
        <ProFormText
          name="title"
          label="文章标题"
          rules={[{ required: true, message: '请输入文章标题' }]}
          placeholder="请输入文章标题"
        />
        <ProFormSelect
          name="category_id"
          label="文章分类"
          rules={[{ required: true, message: '请选择分类' }]}
          request={async () => {
            const { data } = await request('/content/category/index');
            return data.items.map((item: any) => ({
              label: item.name,
              value: item.id,
            }));
          }}
        />
        <ProForm.Item
          name="content"
          label="文章内容"
          rules={[{ required: true, message: '请输入文章内容' }]}
        >
          <TinyMCE height={500} />
        </ProForm.Item>
      </Card>
    </ProForm>
  );
};
```

---

### E. 数据库迁移

> 使用 Alembic 进行数据库版本管理和迁移

#### E.1 创建迁移文件

```bash
# 生成迁移文件
alembic revision --autogenerate -m "add content module tables"
```

#### E.2 迁移文件示例

```python
# alembic/versions/xxx_add_content_module_tables.py
"""add content module tables

Revision ID: 001
Revises:
Create Date: 2026-02-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建文章分类表
    op.create_table(
        'content_categories',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # 创建文章标签表
    op.create_table(
        'content_tags',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('slug', sa.String(length=30), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # 创建文章表
    op.create_table(
        'content_articles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.String(length=500), nullable=True),
        sa.Column('cover_image_id', sa.BigInteger(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('author_id', sa.BigInteger(), nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['author_id'], ['admin_admins.id']),
        sa.ForeignKeyConstraint(['category_id'], ['content_categories.id']),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # 创建文章标签关联表
    op.create_table(
        'content_article_tags',
        sa.Column('article_id', sa.BigInteger(), nullable=False),
        sa.Column('tag_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('article_id', 'tag_id'),
        sa.ForeignKeyConstraint(['article_id'], ['content_articles.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['content_tags.id']),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )


def downgrade():
    op.drop_table('content_article_tags')
    op.drop_table('content_articles')
    op.drop_table('content_tags')
    op.drop_table('content_categories')
```

#### E.3 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 降级一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看版本历史
alembic history
```

---

### F. 错误处理规范

> 统一使用项目中的 `success()` 和 `error()` 函数返回响应

#### F.1 导入方式

```python
from Modules.common.libs.responses.response import success, error
from fastapi.responses import JSONResponse
```

#### F.2 成功响应

```python
# 简单成功消息
return success(None, message="操作成功")

# 带数据的成功响应
return success({"id": 1, "title": "测试文章"}, message="获取成功")

# 自定义状态码
return success(data, message="创建成功", code=201)
```

#### F.3 错误响应

```python
# 简单错误消息
return error("操作失败")

# 带详细信息的错误
return error("用户名已存在", code=400)

# 业务验证错误
async def _article_add_pre_operation(self, data, session):
    title = data.get("title")
    if not title or len(title.strip()) == 0:
        return error("标题不能为空")

    # 检查标题是否重复
    existing = await session.execute(
        select(ContentArticle).where(ContentArticle.title == title)
    )
    if existing.scalar_one_or_none():
        return error("标题已存在")

    return data, session
```

#### F.4 异常处理

```python
try:
    result = await self.common_add(...)
    return result
except ValidationError as e:
    return error(f"参数验证失败: {str(e)}")
except Exception as e:
    logger.error(f"添加文章失败: {str(e)}")
    return error("系统错误，请稍后重试")
```

---

## 总结

### 可行性评估：✅ 高度可行

**现有优势：**
- 完善的 FastAPI + Celery 架构
- 成熟的权限和文件管理系统
- Ant Design 前端组件库

**需要新增：**
- Playwright 浏览器自动化
- 知乎平台适配器
- Ollama AI 集成

**预计工作量：**
- 基础功能（不含AI）：12-15 天
- 完整功能（含AI）：18-22 天

**建议：**
1. 先实现基础内容管理
2. 再实现知乎单平台发布
3. 验证可行性后扩展多平台
4. 最后添加 AI 优化功能

---

> 文档版本：v8.0
> 创建日期：2026-02-05
> 更新日期：2026-02-09
> 更新内容：
>   - ✅ 完成 Cookie 验证功能（后端 API + Playwright 集成）
>   - ✅ 实现知乎平台 Cookie 验证器
>   - ✅ 添加完整的反检测机制（随机延迟、人类行为模拟）
>   - ✅ 解决 Windows 系统 Playwright 兼容性问题
>   - ✅ 添加验证间隔限制（防止频繁验证）
>   - ✅ 完成浏览器自动化配置文档
>   - v7.2 内容：Content 模块全部代码实现、数据库迁移、前端页面开发、浏览器扩展等
> 分析基于：ArtiPub 项目 + py-small-admin 项目架构深度分析

## 实现进度

### 已完成 ✅
- [x] 数据模型设计 (6个模型)
- [x] 路由定义 (5个路由模块)
- [x] 控制器层 (5个控制器)
- [x] 服务层 (5个服务)
- [x] 验证器层 (5个验证器)
- [x] BaseService 扩展 (post_operation_callback)
- [x] 主应用路由注册
- [x] 数据库迁移
- [x] 种子数据 (菜单规则 - 三层结构)
- [x] 前端页面开发 (6个模块：控制台+5个管理模块)

### 待实现 ⏳
- [ ] 知乎发布器开发
- [ ] Celery 异步发布任务
- [ ] 文章自动发布功能
- [ ] 批量发布功能

### Cookie 验证功能 ✅ 已完成

**实现时间**：2026-02-09

**功能概述**：
- 使用 Playwright 浏览器自动化验证平台账号 Cookie 有效性
- 支持知乎平台的登录状态检测和文章发布
- 完整的反检测机制，降低平台封号风险
- Windows 系统兼容性解决方案

**核心实现**：

1. **BasePlatformHandler 基类** ([base_platform_handler.py](server/Modules/content/services/publisher/base_platform_handler.py))
   - 融合验证和发布功能的统一处理器基类
   - 实现通用的浏览器初始化、Cookie 加载、登录检测逻辑
   - 提供人类行为模拟方法（随机延迟、滚动、鼠标移动）
   - 支持 `verify()` 和 `publish()` 两种操作模式

2. **ZhihuHandler 处理器** ([zhihu_handler.py](server/Modules/content/services/publisher/zhihu_handler.py))
   - 实现知乎特定的登录状态检测和文章发布
   - 使用知乎专用的 DOM 选择器进行验证和发布
   - 融合了之前 ZhihuVerifier 和 ZhihuPublisher 的所有功能

3. **验证 API** ([platform_account_controller.py](server/Modules/content/controllers/v1/platform_account_controller.py))
   - `/api/content/platform_account/verify/{id}` - 验证指定账号的 Cookie
   - 验证间隔限制（默认 5 分钟最小间隔）
   - 验证结果实时更新到数据库

**反检测特性**：

| 特性 | 默认值 | 说明 |
|------|--------|------|
| 随机延迟 | 1-3 秒 | 每个操作之间随机延迟，模拟人类操作节奏 |
| 页面滚动 | 1-3 次 | 随机滚动页面，模拟浏览行为 |
| 鼠标移动 | 2-4 次 | 随机移动鼠标位置，增加真实性 |
| 停留时间 | 成功 5-8 秒 / 失败 2-4 秒 | 根据验证结果停留不同时长 |
| 验证间隔 | 最小 5 分钟 | 防止频繁验证被检测 |

**环境变量配置**：

```bash
# 内容模块配置（.env）
# Playwright 浏览器自动化
CONTENT_PLAYWRIGHT_HEADLESS=True
CONTENT_PLAYWRIGHT_TIMEOUT=30000
CONTENT_PLAYWRIGHT_WIDTH=1920
CONTENT_PLAYWRIGHT_HEIGHT=1080

# 知乎平台配置
CONTENT_ZHIHU_VERIFY_URL=https://www.zhihu.com
CONTENT_ZHIHU_LOGIN_SELECTOR=.AppHeader-login
CONTENT_ZHIHU_LOGGED_IN_SELECTOR=.AppHeader-notifications

# Cookie 验证配置
CONTENT_COOKIE_VERIFY_INTERVAL=3600
CONTENT_COOKIE_EXPIRE_WARNING_DAYS=7

# 反检测配置（降低平台封号风险）
CONTENT_HUMAN_BEHAVIOR_ENABLED=true
CONTENT_RANDOM_DELAY_MIN=1.0
CONTENT_RANDOM_DELAY_MAX=3.0
CONTENT_VERIFY_INTERVAL_MIN=300
CONTENT_STAY_TIME_SUCCESS_MIN=5.0
CONTENT_STAY_TIME_SUCCESS_MAX=8.0
CONTENT_STAY_TIME_FAILED_MIN=2.0
CONTENT_STAY_TIME_FAILED_MAX=4.0
CONTENT_SCROLL_COUNT_MIN=1
CONTENT_SCROLL_COUNT_MAX=3
CONTENT_MOUSE_MOVE_COUNT_MIN=2
CONTENT_MOUSE_MOVE_COUNT_MAX=4
```

**Windows 系统特殊配置**：

在 Windows 系统上使用 Playwright 需要特殊配置：

1. **设置事件循环策略**：
   在 `run.py` 和 `Modules/main.py` 的最顶部（所有导入之前）添加：
   ```python
   import asyncio
   import sys

   # Windows 系统下使用 SelectorEventLoop 以支持 Playwright 子进程
   if sys.platform == "win32":
       asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
   ```

2. **禁用热重载**：
   将 `.env` 文件中的 `APP_RELOAD` 设置为 `false`

3. **使用正确的启动方式**：
   必须使用 `python run.py` 启动服务，不能直接使用 `uvicorn` 命令

**验证流程**：

```
┌─────────────────────────────────────────────────────────────────┐
│                      Cookie 验证流程                              │
└─────────────────────────────────────────────────────────────────┘

1. 验证间隔检查
   │
   ▼
2. 启动 Playwright 浏览器（Chromium）
   │
   ▼
3. 创建浏览器上下文（设置 User-Agent、Viewport）
   │
   ▼
4. 访问平台域名（如 https://www.zhihu.com）
   │
   ▼
5. 添加 Cookies 到浏览器上下文
   │
   ▼
6. 访问验证页面
   │
   ▼
7. 等待页面加载完成
   │
   ▼
8. 模拟人类行为（随机滚动、鼠标移动）
   │
   ▼
9. 检查登录状态（通过 DOM 选择器）
   │
   ▼
10. 更新数据库状态（status、last_verified）
    │
    ▼
11. 关闭浏览器，返回结果
```

**调试日志**：

验证过程会输出详细的调试日志：

```
[Cookie验证] ===== 开始验证 =====
[Cookie验证] 平台: 知乎
[Cookie验证] Cookie 数量: 15
[Cookie验证] User-Agent: Mozilla/5.0...
[Cookie验证] 正在启动 Playwright...
[Cookie验证] ✓ 浏览器启动成功
[Cookie验证] 创建浏览器上下文...
[Cookie验证] ✓ 页面创建成功
[Cookie验证] ✓ 延迟 2.34 秒
[Cookie验证] 访问平台域名: https://www.zhihu.com
[Cookie验证] ✓ 延迟 1.87 秒
[Cookie验证] 添加 15 个 Cookie...
[Cookie验证] ✓ Cookie 添加完成
[Cookie验证] ✓ 延迟 2.12 秒
[Cookie验证] 访问验证页面: https://www.zhihu.com
[Cookie验证] ✓ 页面加载完成
[Cookie验证] ✓ 延迟 2.56 秒
[Cookie验证] 开始模拟人类行为...
[Cookie验证] 滚动 1/2: 324px
[Cookie验证] 鼠标移动 1/3: (1243, 567)
[Cookie验证] ✓ 人类行为模拟完成
[Cookie验证] 检查登录状态...
[Cookie验证] ✓ 验证成功，停留 6.23 秒
[Cookie验证] ===== 验证结束 =====
```

**相关文件**：

- 配置类：[server/config/content.py](server/config/content.py)
- 验证器基类：[server/Modules/content/services/publisher/base_verifier.py](server/Modules/content/services/publisher/base_verifier.py)
- 知乎验证器：[server/Modules/content/services/publisher/zhihu_verifier.py](server/Modules/content/services/publisher/zhihu_verifier.py)
- 服务层：[server/Modules/content/services/platform_account_service.py](server/Modules/content/services/platform_account_service.py)
- 启动文件：[server/run.py](server/run.py)、[server/Modules/main.py](server/Modules/main.py)

## 浏览器扩展状态

### 已完成 ✅
浏览器扩展用于获取各平台的登录 Cookies，支持一键获取和选择性发送。

| 功能 | 状态 | 说明 |
|------|------|------|
| 本地 Cookie 获取 | ✅ | 使用 Chrome Cookies API 获取所有平台 Cookies |
| 平台列表展示 | ✅ | 从后端 API 获取支持的平台列表 |
| 按平台分组显示 | ✅ | 显示每个平台获取到的 Cookie 数量 |
| 点击复制 JSON | ✅ | 点击 Cookie 数量复制 JSON 格式详情 |
| 选择性发送后端 | ✅ | 只有知乎平台可以发送到后端 |
| 重新获取功能 | ✅ | 支持刷新获取最新 Cookies |
| CSS 样式 | ✅ | 完整的 UI 样式和交互效果 |

### 扩展文件结构
```
browser-extension/
├── source/
│   ├── manifest.json         # Chrome 扩展配置
│   ├── Popup/
│   │   ├── Popup.tsx         # 弹窗组件（React）
│   │   └── styles.less       # 样式文件
│   ├── Background/index.ts   # 后台脚本
│   └── assets/icons/         # 图标资源
├── dist/chrome/              # 构建输出
└── package.json
```

### 后端 API 扩展
为浏览器扩展新增了专门的 API 路由：

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/content/extension/platform/index` | GET | 获取支持的平台列表 |
| `/api/content/extension/platform_account/import_cookies` | POST | 导入 Cookies 到后端 |

### 下一步：文章发布功能

Cookie 验证功能已完成 ✅，接下来需要实现文章自动发布功能：

```python
# zhihu_publisher.py（待实现）
async def publish(self, article: Article) -> PublishResult:
    """发布文章到知乎"""
    # 1. 初始化浏览器
    # 2. 加载 Cookie
    # 3. 导航到编辑器
    # 4. 创建临时 Markdown 文件
    # 5. 上传文件到知乎
    # 6. 设置发布参数
    # 7. 执行发布
    # 8. 返回文章链接
```

## 前端页面说明

Content 模块采用**三层菜单结构**，包含以下6个页面：

| 模块 | 层级 | 路径 | 说明 |
|------|------|------|------|
| 控制台 | 2 | /content/dashboard | 内容概览、数据统计 |
| 内容管理 | 2 | /content/manage | 分组菜单（type=2） |
| 文章管理 | 3 | /content/manage/article | 富文本编辑、标签关联、发布功能 |
| 分类管理 | 3 | /content/manage/category | 树形分类、拖拽排序 |
| 标签管理 | 3 | /content/manage/tag | 标签颜色、排序 |
| 平台账号 | 3 | /content/manage/platform-account | 多平台账号管理、Cookie验证 |
| 发布管理 | 3 | /content/manage/publish | 发布记录、失败重试 |

### 菜单结构（三层）

```
内容管理 (type=1, level=1)
├── 控制台 (type=3, level=2) → /content/dashboard
└── 内容管理 (type=2, level=2) → /content/manage (分组)
    ├── 文章管理 (type=3, level=3) → /content/manage/article
    ├── 分类管理 (type=3, level=3) → /content/manage/category
    ├── 标签管理 (type=3, level=3) → /content/manage/tag
    ├── 平台账号 (type=3, level=3) → /content/manage/platform-account
    └── 发布管理 (type=3, level=3) → /content/manage/publish
```

### 前端文件结构

```
admin-web/src/
├── services/content/
│   ├── category/
│   │   ├── api.ts
│   │   └── typings.d.ts
│   ├── tag/
│   │   ├── api.ts
│   │   └── typings.d.ts
│   ├── article/
│   │   ├── api.ts
│   │   └── typings.d.ts
│   ├── platform-account/
│   │   ├── api.ts
│   │   └── typings.d.ts
│   └── publish/
│       ├── api.ts
│       └── typings.d.ts
│
└── pages/content/
    ├── category/
    │   ├── index.tsx
    │   └── components/
    │       └── FormIndex.tsx
    ├── tag/
    │   ├── index.tsx
    │   └── components/
    │       └── FormIndex.tsx
    ├── article/
    │   ├── index.tsx
    │   └── components/
    │       └── FormIndex.tsx
    ├── platform-account/
    │   ├── index.tsx
    │   └── components/
    │       └── FormIndex.tsx
    └── publish/
        ├── index.tsx
        └── components/
            └── PublishModal.tsx
```

## 种子数据说明

Content 模块种子数据只包含菜单规则：

| 菜单规则 | 路径 | 说明 |
|----------|------|------|
| 内容管理 | /content | 主菜单（一级） |
| 文章管理 | /content/article | 文章管理页面 |
| 分类管理 | /content/category | 分类管理页面 |
| 标签管理 | /content/tag | 标签管理页面 |
| 平台账号 | /content/platform-account | 平台账号管理页面 |
| 发布管理 | /content/publish | 发布管理页面 |

### 运行种子数据

```bash
# 运行所有模块的种子数据
python -m commands.seed run-all

# 仅运行 content 模块的种子数据
python -m commands.seed run --module content

# 查看所有模块的种子数据状态
python -m commands.seed list
```
