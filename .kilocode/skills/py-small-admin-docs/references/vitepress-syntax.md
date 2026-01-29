# VitePress 特殊语法参考

本文档详细说明了 Py Small Admin 项目中使用的 VitePress 特殊语法。

## 提示框（Alerts）

VitePress 支持多种类型的提示框，用于强调重要信息。

### Tip（提示）

用于给出有用的建议或最佳实践。

```markdown
:::tip 提示标题
这是一个提示信息，用于给出有用的建议。
:::
```

**渲染效果**:

> 💡 **提示标题**
> 这是一个提示信息，用于给出有用的建议。

**使用场景**:

- 最佳实践建议
- 优化技巧
- 快捷方式
- 有用的提示

### Warning（警告）

用于提醒用户注意潜在问题或注意事项。

```markdown
:::warning 警告标题
这是一个警告信息，用于提醒用户注意潜在问题。
:::
```

**渲染效果**:

> ⚠️ **警告标题**
> 这是一个警告信息，用于提醒用户注意潜在问题。

**使用场景**:

- 潜在问题
- 注意事项
- 需要小心的地方
- 可能的错误

### Danger（危险）

用于警告可能导致严重后果的操作。

```markdown
:::danger 危险标题
这是一个危险信息，用于警告可能导致严重后果的操作。
:::
```

**渲染效果**:

> 🔴 **危险标题**
> 这是一个危险信息，用于警告可能导致严重后果的操作。

**使用场景**:

- 数据丢失风险
- 不可逆操作
- 安全风险
- 系统损坏

### Note（注意）

用于补充说明或额外信息。

```markdown
:::note 注意标题
这是一个注意事项，用于补充说明。
:::
```

**渲染效果**:

> 📝 **注意标题**
> 这是一个注意事项，用于补充说明。

**使用场景**:

- 补充说明
- 额外信息
- 细节说明
- 补充内容

### Info（信息）

用于提供额外信息或参考。

```markdown
:::info 信息标题
这是一个信息提示，用于提供额外信息。
:::
```

**渲染效果**:

> ℹ️ **信息标题**
> 这是一个信息提示，用于提供额外信息。

**使用场景**:

- 参考信息
- 补充资料
- 相关链接
- 背景信息

## 详情折叠（Details）

使用 `:::details` 创建可折叠的内容。

### 基本用法

```markdown
:::details 点击查看详细信息
这里是需要折叠的内容。
:::
```

### 嵌套代码块

````markdown
:::details 查看完整代码

```python
def complex_function():
    # 长代码内容...
    pass
```
````

:::

````

### 多层嵌套

```markdown
:::details 第一层

这里是第一层内容。

:::details 第二层
这里是第二层内容。
:::

:::
````

**使用场景**:

- 长代码块
- 详细的技术说明
- 可选的配置选项
- 补充信息
- 不影响主要内容的细节

## 代码组（Code Groups）

使用 `:::code-group` 创建多个代码块的选项卡。

### 基本用法

````markdown
:::code-group

```bash
npm install
```
````

```bash
yarn add
```

```bash
pnpm add
```

:::

````

**渲染效果**: 三个代码块以选项卡形式展示，用户可以切换查看。

**使用场景**:
- 多种安装方式
- 不同语言的示例
- 多种解决方案

## 自定义容器（Custom Containers）

VitePress 支持创建自定义容器。

### 定义自定义容器

在 `.vitepress/theme/index.ts` 中定义：

```typescript
import DefaultTheme from 'vitepress/theme-without-fonts'
import type { Theme } from 'vitepress'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.provide('custom-containers', {
      'my-container': {
        render: (slots) => h('div', { class: 'my-container' }, slots.default())
      }
    })
  }
} satisfies Theme
````

### 使用自定义容器

```markdown
:::my-container
自定义容器内容。
:::
```

## 组件插槽（Component Slots）

### Badge（徽章）

用于标记状态或版本。

```markdown
:::badge 稳定
:::

:::badge v1.0
:::
```

**渲染效果**: 彩色的徽章标签。

### Icon（图标）

使用图标增强视觉效果。

```markdown
:::icon{name="info-circle"}
这是一个提示。
:::
```

## 语法高亮

### 支持的语言

- `python`：Python
- `javascript`：JavaScript
- `typescript`：TypeScript
- `bash`：Shell 脚本
- `json`：JSON 数据
- `sql`：SQL 查询
- `yaml`：YAML 配置
- `markdown`：Markdown
- `html`：HTML
- `css`：CSS

### 行号显示

在代码块中添加 `showLineNumbers`：

````markdown
```python {showLineNumbers}
def hello():
    print("Hello")
```
````

````

### 高亮特定行

使用 `// [!code focus]` 注释高亮特定行：

```markdown
```python
def hello():
    print("Hello")  // [!code focus]
    print("World")
````

````

## Frontmatter（前置元数据）

### 基本元数据

```markdown
---
title: 文档标题
description: 文档描述
---
````

### 自定义元数据

```markdown
---
title: 文档标题
description: 文档描述
author: 作者名
date: 2024-01-01
tags:
  - Python
  - Flask
  - Tutorial
---
```

### VitePress 特定元数据

```markdown
---
title: 文档标题
description: 文档描述
outline: [2, 3] # 目录显示层级
editLink: false # 禁用编辑链接
lastUpdated: true # 显示最后更新时间
---
```

## 链接和路径

### 相对路径

```markdown
[链接](./relative-path.md)
[链接](../parent-dir/file.md)
```

### 绝对路径

```markdown
[链接](/absolute-path.md)
```

### 外部链接

```markdown
[Python 官网](https://www.python.org/)
```

### 锚点链接

```markdown
[跳转到标题](#标题名称)
```

## 图片和媒体

### 基本图片

```markdown
![图片说明](/images/logo.png)
```

### 带尺寸的图片

```markdown
![图片说明](/images/logo.png){width=200}
```

### 暗黑模式图片

```markdown
![图片说明](/images/logo.png#dark)
```

## 表格

### 基本表格

```markdown
| 列1   | 列2   | 列3   |
| ----- | ----- | ----- |
| 内容1 | 内容2 | 内容3 |
```

### 对齐方式

```markdown
| 左对齐 | 居中 | 右对齐 |
| :----- | :--: | -----: |
| 内容   | 内容 |   内容 |
```

### 复杂表格

```markdown
| 表头1         | 表头2     |
| ------------- | --------- |
| 内容1<br>换行 | 内容2     |
| **粗体**      | _斜体_    |
| `代码`        | [链接](#) |
```

## 列表

### 无序列表

```markdown
- 第一项
- 第二项
  - 子项
  - 子项
- 第三项
```

### 有序列表

```markdown
1. 第一步
2. 第二步
3. 第三步
```

### 任务列表

```markdown
- [ ] 未完成任务
- [x] 已完成任务
```

### 自定义列表标记

```markdown
- 使用星号

* 使用连字符

- 使用加号
```

## 引用块

### 基本引用

```markdown
> 这是一个引用块
```

### 嵌套引用

```markdown
> 第一层引用
>
> > 第二层引用
```

### 带作者的引用

```markdown
> 引用内容
>
> — 作者名
```

## 代码行内

### 基本代码

```markdown
这是一段 `inline code` 代码。
```

### 语法高亮

```markdown
这是一个 Python 函数 `print()` 的示例。
```

## 水平线

```markdown
---
```

或

```markdown
---
```

## 转义字符

某些字符需要转义：

```markdown
\\ 反斜杠 \* 星号
\_ 下划线
\# 井号
\{ \} 大括号
\[ \] 中括号
\( \) 小括号
\# 井号
\+ 加号
\- 连字符
\. 点号
\! 感叹号
\| 竖线
```

## 数学公式

### 行内公式

```markdown
$E = mc^2$
```

### 块级公式

```markdown
$$
E = mc^2
$$
```

## 脚注

```markdown
这是一段文字[^1]。

[^1]: 这是脚注内容。
```

## 定义列表

```markdown
术语 1
: 定义 1

术语 2
: 定义 2
```

## 删除线

```markdown
~~删除的文本~~
```

## 任务清单

```markdown
- [ ] 未完成任务
- [x] 已完成任务
```

## Emoji 支持

```markdown
:smile:
:heart:
:thumbsup:
```

## 最佳实践

### 提示框使用

- **Tip**: 用于最佳实践和有用建议
- **Warning**: 用于潜在问题和注意事项
- **Danger**: 仅用于严重后果的操作
- **Note**: 用于补充说明
- **Info**: 用于额外信息

### 详情折叠使用

- 用于长代码块
- 用于详细的技术说明
- 用于不影响主要内容的细节
- 避免过度使用

### 代码块使用

- 始终指定语言类型
- 为长代码添加折叠
- 为关键行添加高亮
- 添加必要的注释

### 链接使用

- 优先使用相对路径
- 外部链接添加 title 属性
- 锚点链接使用描述性文本

---

遵循这些 VitePress 语法规范，确保文档的正确渲染和良好体验。
