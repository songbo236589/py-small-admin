# Quant 模块详解

本文档详细介绍 Quant 量化数据模块的功能和实现。

## 概述

Quant 模块负责量化数据的获取、处理和存储，包括股票数据、概念板块、行业数据等。

## 模块结构

```
Modules/quant/
├── controllers/              # 控制器层
│   └── v1/
│       ├── quant_concept_controller.py
│       ├── quant_concept_log_controller.py
│       ├── quant_industry_controller.py
│       ├── quant_industry_log_controller.py
│       ├── quant_stock_controller.py
│       └── quant_stock_kline_controller.py
├── services/                # 服务层
│   ├── quant_concept_service.py
│   ├── quant_concept_log_service.py
│   ├── quant_industry_service.py
│   ├── quant_industry_log_service.py
│   ├── quant_stock_service.py
│   ├── quant_stock_kline_service.py
│   └── quant_data_fetch_service.py
├── models/                  # 模型层
│   ├── quant_concept.py
│   ├── quant_concept_log.py
│   ├── quant_industry.py
│   ├── quant_industry_log.py
│   ├── quant_stock.py
│   ├── quant_stock_concept.py
│   ├── quant_stock_klines_1d.py
│   ├── quant_stock_klines_1m.py
│   ├── quant_stock_klines_5m.py
│   ├── quant_stock_klines_15m.py
│   ├── quant_stock_klines_30m.py
│   ├── quant_stock_klines_60m.py
│   └── quant_stock_klines_1w.py
├── routes/                  # 路由层
│   ├── quant_concept.py
│   ├── quant_concept_log.py
│   ├── quant_industry.py
│   ├── quant_industry_log.py
│   ├── quant_stock.py
│   └── quant_stock_kline.py
├── validators/            # 验证器层
│   ├── quant_concept_validator.py
│   └── quant_industry_validator.py
├── migrations/              # 数据库迁移
│   └── versions/
├── seeds/                  # 数据填充
│   └── quant_seed.py
├── queues/                 # 队列
│   ├── concept_queues.py
│   ├── industry_queues.py
│   └── stock_queues.py
└── tasks/                  # 异步任务
    └── quant_tasks.py
```

## 核心功能

### 1. 股票数据管理

#### 功能列表

- 股票列表（分页、搜索、排序）
- 添加股票
- 编辑股票
- 删除股票
- 批量删除股票
- 同步股票列表
- 股票详情

#### 数据模型

```python
class QuantStock(BaseTableModel, table=True):
    """股票模型"""
    __table_comment__ = "股票表"

    code: str = Field(default="", index=True, unique=True)
    name: str = Field(default="", index=True)
    market: str = Field(default="")
    status: int = Field(default=1)
```

#### API 接口

| 方法   | 路径                          | 说明         |
| ------ | ----------------------------- | ------------ |
| GET    | /api/quant/stock/index        | 获取股票列表 |
| POST   | /api/quant/stock/add          | 添加股票     |
| GET    | /api/quant/stock/edit/{id}    | 获取股票信息 |
| PUT    | /api/quant/stock/update/{id}  | 更新股票     |
| DELETE | /api/quant/stock/destroy/{id} | 删除股票     |
| DELETE | /api/quant/stock/destroy_all  | 批量删除股票 |
| POST   | /api/quant/stock/sync         | 同步股票列表 |

### 2. K线数据管理

#### 功能列表

- K线数据查询
- K线数据同步
- 多周期K线（1分钟、5分钟、15分钟、30分钟、60分钟、日线、周线）

#### 数据模型

```python
class QuantStockKlines1d(BaseTableModel, table=True):
    """日线K线模型"""
    __table_comment__ = "日线K线表"

    stock_id: int = Field(default=0, index=True)
    trade_date: datetime = Field(default=None, index=True)
    open: float = Field(default=0.0)
    high: float = Field(default=0.0)
    low: float = Field(default=0.0)
    close: float = Field(default=0.0)
    volume: int = Field(default=0)
    amount: float = Field(default=0.0)
```

#### API 接口

| 方法 | 路径                         | 说明        |
| ---- | ---------------------------- | ----------- |
| GET  | /api/quant/stock_kline/index | 获取K线数据 |
| POST | /api/quant/stock_kline/sync  | 同步K线数据 |

### 3. 概念板块管理

#### 功能列表

- 概念板块列表
- 添加概念板块
- 编辑概念板块
- 删除概念板块
- 同步概念板块
- 概念板块详情

#### 数据模型

```python
class QuantConcept(BaseTableModel, table=True):
    """概念板块模型"""
    __table_comment__ = "概念板块表"

    code: str = Field(default="", index=True, unique=True)
    name: str = Field(default="", index=True)
    description: str = Field(default="")
    status: int = Field(default=1)
```

#### API 接口

| 方法   | 路径                            | 说明             |
| ------ | ------------------------------- | ---------------- |
| GET    | /api/quant/concept/index        | 获取概念板块列表 |
| POST   | /api/quant/concept/add          | 添加概念板块     |
| GET    | /api/quant/concept/edit/{id}    | 获取概念板块信息 |
| PUT    | /api/quant/concept/update/{id}  | 更新概念板块     |
| DELETE | /api/quant/concept/destroy/{id} | 删除概念板块     |
| POST   | /api/quant/concept/sync         | 同步概念板块     |

### 4. 行业板块管理

#### 功能列表

- 行业板块列表
- 添加行业板块
- 编辑行业板块
- 删除行业板块
- 同步行业板块
- 行业板块详情

#### 数据模型

```python
class QuantIndustry(BaseTableModel, table=True):
    """行业板块模型"""
    __table_comment__ = "行业板块表"

    code: str = Field(default="", index=True, unique=True)
    name: str = Field(default="", index=True)
    description: str = Field(default="")
    status: int = Field(default=1)
```

#### API 接口

| 方法   | 路径                             | 说明             |
| ------ | -------------------------------- | ---------------- |
| GET    | /api/quant/industry/index        | 获取行业板块列表 |
| POST   | /api/quant/industry/add          | 添加行业板块     |
| GET    | /api/quant/industry/edit/{id}    | 获取行业板块信息 |
| PUT    | /api/quant/industry/update/{id}  | 更新行业板块     |
| DELETE | /api/quant/industry/destroy/{id} | 删除行业板块     |
| POST   | /api/quant/industry/sync         | 同步行业板块     |

## 核心服务

### QuantDataFetchService

数据获取服务，负责从外部数据源获取量化数据。

```python
class QuantDataFetchService:
    """数据获取服务"""

    async def fetch_stock_list(self):
        """获取股票列表"""

    async def fetch_kline_data(self, stock_code: str, period: str):
        """获取K线数据"""

    async def fetch_concept_list(self):
        """获取概念板块列表"""

    async def fetch_industry_list(self):
        """获取行业板块列表"""
```

### QuantStockService

股票服务，提供股票相关的业务逻辑。

```python
class QuantStockService(BaseService):
    """股票服务"""

    async def index(self, data: dict) -> JSONResponse:
        """获取股票列表"""

    async def add(self, data: dict) -> JSONResponse:
        """添加股票"""

    async def sync_stock_list(self) -> JSONResponse:
        """同步股票列表"""
```

### QuantStockKlineService

K线服务，提供K线相关的业务逻辑。

```python
class QuantStockKlineService(BaseService):
    """K线服务"""

    async def index(self, data: dict) -> JSONResponse:
        """获取K线数据"""

    async def sync_kline_data(self, stock_code: str, period: str) -> JSONResponse:
        """同步K线数据"""
```

## 异步任务

### QuantTasks

量化数据任务，使用 Celery 异步处理数据同步。

```python
@shared_task
def sync_stock_list_task():
    """同步股票列表任务"""

@shared_task
def sync_kline_data_task(stock_code: str, period: str):
    """同步K线数据任务"""

@shared_task
def sync_concept_list_task():
    """同步概念板块任务"""

@shared_task
def sync_industry_list_task():
    """同步行业板块任务"""
```

## 队列定义

### StockQueues

股票相关队列。

```python
stock_sync_queue = Queue("stock_sync")
kline_sync_queue = Queue("kline_sync")
```

### ConceptQueues

概念板块相关队列。

```python
concept_sync_queue = Queue("concept_sync")
```

### IndustryQueues

行业板块相关队列。

```python
industry_sync_queue = Queue("industry_sync")
```

## 数据同步

### 同步策略

- **定时同步**: 使用 Celery Beat 定时同步数据
- **手动同步**: 通过 API 接口手动触发同步
- **增量同步**: 只同步新增或变更的数据

### 同步流程

```
1. 触发同步任务
   ↓
2. 从外部数据源获取数据
   ↓
3. 数据清洗和转换
   ↓
4. 保存到数据库
   ↓
5. 记录同步日志
```

## 分表设计

### K线数据分表

K线数据按周期分表，提高查询性能：

```
quant_stock_klines_1m   # 1分钟K线
quant_stock_klines_5m   # 5分钟K线
quant_stock_klines_15m  # 15分钟K线
quant_stock_klines_30m  # 30分钟K线
quant_stock_klines_60m  # 60分钟K线
quant_stock_klines_1d   # 日线K线
quant_stock_klines_1w   # 周线K线
```

### 分表优势

- **查询性能**: 每个表数据量小，查询快
- **维护方便**: 可以单独维护每个周期的数据
- **扩展灵活**: 可以轻松添加新的周期

## 最佳实践

### 1. 数据同步

- 使用异步任务避免阻塞
- 设置合理的同步频率
- 记录同步日志

### 2. 数据验证

- 验证数据完整性
- 验证数据格式
- 处理异常数据

### 3. 性能优化

- 使用索引加速查询
- 使用缓存减少数据库访问
- 批量操作提高效率

## 常见问题

### 1. 如何添加新的K线周期？

创建新的模型类，如 `QuantStockKlinesXm`，然后创建相应的服务和控制器。

### 2. 如何修改数据源？

修改 `QuantDataFetchService` 中的数据获取逻辑。

### 3. 如何查看同步日志？

查看 `quant_concept_log` 和 `quant_industry_log` 表中的同步记录。

## 相关链接

- [项目结构说明](./project-structure.md)
- [模块开发指南](./module-development.md)
- [Admin 模块详解](./admin-module.md)
- [Common 模块详解](./common-module.md)

---

Quant 模块负责量化数据的获取和管理，支持多种数据源和同步策略。
