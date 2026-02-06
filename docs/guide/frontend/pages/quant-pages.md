# Quant 模块页面

本文档介绍了 Quant 模块的页面。

## 页面列表

| 页面 | 路由 | 功能 |
|------|------|------|
| 量化仪表盘 | `/quant/dashboard` | 量化数据概览 |
| 股票管理 | `/quant/data/stock` | 股票管理 |
| 行业管理 | `/quant/data/industry` | 行业管理 |
| 概念管理 | `/quant/data/concept` | 概念管理 |
| 行业历史记录 | `/quant/data/industry_log` | 行业历史数据 |
| 概念历史记录 | `/quant/data/concept_log` | 概念历史数据 |

## 量化仪表盘

### 功能说明

量化数据概览，展示股票、行业、概念的统计信息。

### 主要功能

- 显示股票总数
- 显示行业数量
- 显示概念数量
- 显示 K 线数据统计
- 数据图表展示

### 组件结构

```
dashboard/
  ├── components/
  │   ├── StatCard.tsx      # 统计卡片
  │   └── DataChart.tsx     # 数据图表
  └── index.tsx             # 页面入口
```

### API 接口

```typescript
// 获取统计数据
GET /api/quant/dashboard/stats
```

## 股票管理

### 功能说明

管理股票基础信息，支持从数据源同步。

### 主要功能

- 查看股票列表（支持搜索、分页、排序）
- 添加股票
- 编辑股票信息
- 删除股票
- 批量删除股票
- 同步股票列表

### 表格列配置

| 列名 | 字段 | 说明 |
|------|------|------|
| ID | id | 主键 |
| 股票代码 | code | 股票代码 |
| 股票名称 | name | 股票名称 |
| 拼音代码 | pinyin | 拼音首字母 |
| 行业 | industry | 所属行业 |
| 概念 | concepts | 所属概念 |
| 状态 | status | 启用/禁用 |
| 创建时间 | created_at | 创建时间 |

### API 接口

```typescript
// 获取列表
GET /api/quant/stock/index

// 创建
POST /api/quant/stock/add

// 编辑
PUT /api/quant/stock/update/:id

// 删除
DELETE /api/quant/stock/destroy/:id

// 批量删除
DELETE /api/quant/stock/destroy_all

// 同步股票
POST /api/quant/stock/sync
```

## 行业管理

### 功能说明

管理行业分类信息。

### 主要功能

- 查看行业列表
- 添加行业
- 编辑行业信息
- 删除行业
- 批量删除行业
- 同步行业列表

### 表格列配置

| 列名 | 字段 | 说明 |
|------|------|------|
| ID | id | 主键 |
| 行业名称 | name | 行业名称 |
| 行业代码 | code | 行业代码 |
| 股票数量 | stock_count | 包含股票数 |
| 状态 | status | 启用/禁用 |
| 创建时间 | created_at | 创建时间 |

### API 接口

```typescript
// 获取列表
GET /api/quant/industry/index

// 创建
POST /api/quant/industry/add

// 编辑
PUT /api/quant/industry/update/:id

// 删除
DELETE /api/quant/industry/destroy/:id

// 批量删除
DELETE /api/quant/industry/destroy_all

// 同步行业
POST /api/quant/industry/sync
```

## 概念管理

### 功能说明

管理概念分类信息。

### 主要功能

- 查看概念列表
- 添加概念
- 编辑概念信息
- 删除概念
- 批量删除概念
- 同步概念列表

### 表格列配置

| 列名 | 字段 | 说明 |
|------|------|------|
| ID | id | 主键 |
| 概念名称 | name | 概念名称 |
| 概念代码 | code | 概念代码 |
| 股票数量 | stock_count | 包含股票数 |
| 状态 | status | 启用/禁用 |
| 创建时间 | created_at | 创建时间 |

### API 接口

```typescript
// 获取列表
GET /api/quant/concept/index

// 创建
POST /api/quant/concept/add

// 编辑
PUT /api/quant/concept/update/:id

// 删除
DELETE /api/quant/concept/destroy/:id

// 批量删除
DELETE /api/quant/concept/destroy_all

// 同步概念
POST /api/quant/concept/sync
```

## 行业历史记录

### 功能说明

记录行业数据的历史变化，用于数据分析。

### 主要功能

- 查看行业历史记录
- 按日期筛选
- 按行业筛选
- 数据对比

### 表格列配置

| 列名 | 字段 | 说明 |
|------|------|------|
| ID | id | 主键 |
| 日期 | date | 记录日期 |
| 行业 | industry | 行业名称 |
| 股票数量 | stock_count | 股票总数 |
| 涨跌 | change | 涨跌幅 |
| 记录时间 | created_at | 记录时间 |

### API 接口

```typescript
// 获取列表
GET /api/quant/industry_log/index

// 导出数据
GET /api/quant/industry_log/export
```

## 概念历史记录

### 功能说明

记录概念数据的历史变化，用于数据分析。

### 主要功能

- 查看概念历史记录
- 按日期筛选
- 按概念筛选
- 数据对比

### 表格列配置

| 列名 | 字段 | 说明 |
|------|------|------|
| ID | id | 主键 |
| 日期 | date | 记录日期 |
| 概念 | concept | 概念名称 |
| 股票数量 | stock_count | 股票总数 |
| 涨跌 | change | 涨跌幅 |
| 记录时间 | created_at | 记录时间 |

### API 接口

```typescript
// 获取列表
GET /api/quant/concept_log/index

// 导出数据
GET /api/quant/concept_log/export
```

## 通用组件

### 同步按钮

用于触发数据同步：

```typescript
import { Button, message } from 'antd';
import { useRequest } from 'ahooks';

const SyncButton = () => {
  const { loading, run } = useRequest(syncData, {
    manual: true,
    onSuccess: () => {
      message.success('同步成功');
      actionRef.current?.reload();
    },
  });

  return (
    <Button type="primary" loading={loading} onClick={run}>
      同步数据
    </Button>
  );
};
```

### 数据对比

用于对比不同时期的数据：

```typescript
const ComparisonChart = ({ data }) => {
  const config = {
    data,
    xField: 'date',
    yField: 'value',
    seriesField: 'type',
  };

  return <Line {...config} />;
};
```

## 数据刷新

Quant 模块支持定时任务自动同步数据：

```typescript
// 手动触发同步
const handleSync = async () => {
  await syncStocks();
  await syncIndustries();
  await syncConcepts();
  message.success('数据同步完成');
};
```
