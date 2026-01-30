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