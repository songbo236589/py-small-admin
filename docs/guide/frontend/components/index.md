# 组件开发规范

本文档介绍了前端组件的开发规范。

## 组件类型

### 1. 公共组件

通用可复用的 UI 组件。

### 2. 业务组件

与业务逻辑相关的组件。

## 组件目录

```
src/components/
├── common/
│   ├── CDel/           # 删除确认
│   ├── CDelAll/         # 批量删除确认
│   ├── NumberInput/     # 数字输入框
│   ├── ProTableWrapper/ # Pro Table 封装
│   ├── Upload/           # 上传相关
│   ├── Footer/           # 页脚
│   ├── HeaderDropdown/  # 头部下拉菜单
│   └── RightContent/     # 右侧内容区
```

## 组件开发规范

### 1. 使用 TypeScript

```typescript
interface Props {
  title: string;
  onConfirm: () => void;
}

export default function MyComponent({ title, onConfirm }: Props) {
  return <div>{title}</div>;
}
```

### 2. 使用 PropTypes 验证

```typescript
import { bool, node } from 'prop-types';

MyComponent.propTypes = {
  title: string.isRequired,
  disabled: bool,
  children: node,
};
```

### 3. 统一样式

使用 Ant Design 的设计规范。

```typescript
import { theme } from 'antd';

const { token } = theme.useToken();
```

### 4. 组件命名

- 组件文件名使用 PascalCase
- 组件名与文件名保持一致

```
CDel/
  index.tsx       // 组件实现
  index.ts        // 组件导出
```

### 5. Props 定义

使用 TypeScript 定义 Props：

```typescript
interface CDelProps {
  onConfirm: () => void;
  title?: string;
  content?: string;
}

export default function CDel({ onConfirm, title, content }: CDelProps) {
  // ...
}
```

## 公共组件

### CDel - 删除确认

用于单个删除操作的确认弹窗。

```typescript
import CDel from '@/components/common/CDel';

<CDel
  title="确认删除"
  content="删除后无法恢复，是否继续？"
  onConfirm={() => handleDelete(id)}
/>
```

### CDelAll - 批量删除确认

用于批量删除操作的确认弹窗。

```typescript
import CDelAll from '@/components/common/CDelAll';

<CDelAll
  selectedIds={selectedRowKeys}
  onSuccess={handleRefresh}
/>
```

### NumberInput - 数字输入框

带格式化的数字输入框。

```typescript
import NumberInput from '@/components/common/NumberInput';

<NumberInput
  value={amount}
  onChange={setAmount}
  precision={2}
  placeholder="请输入金额"
/>
```

### ProTableWrapper - 表格封装

ProTable 的封装组件，简化表格配置。

```typescript
import ProTableWrapper from '@/components/common/ProTableWrapper';

<ProTableWrapper
  columns={columns}
  request={fetchData}
  rowKey="id"
  search={false}
  toolBarRender={() => [
    <Button type="primary" onClick={handleAdd}>
      新建
    </Button>
  ]}
/>
```

### Upload - 上传组件

文件上传相关组件。

```typescript
import { ImageUpload, FileUpload } from '@/components/common/Upload';

// 图片上传
<ImageUpload
  value={imageUrl}
  onChange={setImageUrl}
  maxCount={1}
/>

// 文件上传
<FileUpload
  value={fileUrl}
  onChange={setFileUrl}
  accept=".pdf,.doc,.docx"
/>
```

## 业务组件

业务组件位于 `src/pages` 目录下，与具体页面功能相关。

### 组件目录结构

```
src/pages/admin/dashboard/
  ├── components/
  │   ├── StatCard/      # 统计卡片
  │   └── ChartPanel/    # 图表面板
  └── index.tsx          # 页面入口
```

### 组件通信

#### 1. Props 向下传递

```typescript
// 父组件
<StatCard title="用户总数" value={userCount} />

// 子组件
interface StatCardProps {
  title: string;
  value: number;
}
```

#### 2. 回调向上传递

```typescript
// 子组件
interface SearchFormProps {
  onSearch: (values: any) => void;
}

// 父组件
<SearchForm onSearch={(values) => fetchData(values)} />
```

#### 3. Context 跨层级传递

```typescript
// 创建 Context
const PageContext = createContext({});

// 提供者
<PageContext.Provider value={{ loading, refresh }}>
  {children}
</PageContext.Provider>

// 消费者
const { loading, refresh } = useContext(PageContext);
```

## 最佳实践

### 1. 组件拆分

- 单一职责：一个组件只做一件事
- 合理拆分：超过 200 行考虑拆分
- 可复用优先：提取公共逻辑

### 2. 性能优化

```typescript
// 使用 React.memo 避免不必要的重渲染
export default React.memo(MyComponent);

// 使用 useMemo 缓存计算结果
const filteredData = useMemo(() => {
  return data.filter(item => item.status === 1);
}, [data]);

// 使用 useCallback 缓存函数
const handleDelete = useCallback((id: number) => {
  // ...
}, [dependency]);
```

### 3. 错误处理

```typescript
// 使用 ErrorBoundary 捕获组件错误
import { ErrorBoundary } from 'react-error-boundary';

<ErrorBoundary fallback={<ErrorPage />}>
  <MyComponent />
</ErrorBoundary>
```

### 4. 代码规范

- 组件使用函数式组件
- 使用 Hooks 管理状态
- 避免在组件中定义嵌套函数
- 导出使用默认导出