# 文档写作指南

欢迎参与 Py Small Admin 文档的贡献！本指南将帮助您了解如何编写高质量的文档。

## 目录结构

项目文档采用以下目录结构：

```
dosc/
├── index.md              # 首页
├── guides/               # 指南类文档
│   └── writing-guide.md  # 文档写作指南
├── server/               # 服务端端开发文档
├── admin-web/            # 后台管理开发文档
├── public/               # 静态资源（图片、图标等）
└── .vitepress/
    └── config.mts        # VitePress 配置文件
```

### 目录用途说明

- **guides/**：存放指南、教程类文档，如安装指南、配置说明、开发教程等
- **server/**：服务端端开发文档
- **admin-web/**：后台管理开发文档
- **public/**：存放文档中引用的图片、图标等静态资源

### 文件放置规则

- 指南类文档放在 `guides/` 目录
- API 文档放在 `api/` 目录
- 示例代码放在 `examples/` 目录
- 图片资源放在 `public/` 目录

## 文件命名规范

### 基本规则

- 使用 **kebab-case**（小写字母 + 连字符）
- 使用英文命名
- 文件扩展名为 `.md`
- 避免使用中文、空格或特殊字符

### 正确示例

```bash
user-guide.md
api-reference.md
installation-guide.md
configuration.md
```

### 错误示例

```bash
用户指南.md          # ❌ 使用中文
UserGuide.md        # ❌ 使用驼峰命名
user guide.md       # ❌ 使用空格
user_guide.md       # ❌ 使用下划线
```

## Markdown 基础写作规范

### 标题层级

使用 `#` 表示标题，最多支持 6 级标题：

```markdown
# 一级标题（通常每页只有一个）

## 二级标题（主要章节）

### 三级标题（子章节）

#### 四级标题（小节）

##### 五级标题

###### 六级标题
```

### 段落和列表

段落之间使用空行分隔：

```markdown
这是第一段内容。

这是第二段内容。
```

无序列表使用 `-` 或 `*`：

```markdown
- 第一项
- 第二项
  - 子项
  - 子项
- 第三项
```

有序列表使用数字：

```markdown
1. 第一步
2. 第二步
3. 第三步
```

### 表格使用

使用标准 Markdown 表格语法：

```markdown
| 参数名 | 类型 | 必填 | 说明     |
| ------ | ---- | ---- | -------- |
| id     | int  | 是   | 用户 ID  |
| name   | str  | 是   | 用户名   |
| email  | str  | 否   | 邮箱地址 |
```

### 图片引用

图片存放在 `public/` 目录，使用绝对路径引用：

```markdown
![图片说明](/logo.png)
```

## 代码块规范

### 语法高亮

使用三个反引号包裹代码，并指定语言类型：

````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

````

支持的语言包括：`python`、`bash`、`javascript`、`json`、`sql`、`yaml` 等。

### 代码注释

示例代码应包含必要的注释：

```python
# 创建用户实例
user = User(name="张三", email="zhangsan@example.com")

# 保存到数据库
user.save()
````

### 长代码块处理

超过 20 行的代码块，建议使用 `:::details` 折叠：

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

### 代码示例要求

- 代码示例应完整可运行
- 包含必要的导入语句
- 添加清晰的注释
- 输出结果使用注释标注

```python
import requests

# 发送 GET 请求
response = requests.get('https://api.example.com/users')

# 输出：{"users": [...]}
print(response.json())
````

## VitePress 特殊语法

### 提示框

使用自定义容器来创建提示框：

#### 提示（Tip）

```markdown
:::tip 提示标题
这是一个提示信息，用于给出有用的建议。
:::
```

:::tip 提示标题
这是一个提示信息，用于给出有用的建议。
:::

#### 警告（Warning）

```markdown
:::warning 警告标题
这是一个警告信息，用于提醒用户注意潜在问题。
:::
```

:::warning 警告标题
这是一个警告信息，用于提醒用户注意潜在问题。
:::

#### 危险（Danger）

```markdown
:::danger 危险标题
这是一个危险信息，用于警告可能导致严重后果的操作。
:::
```

:::danger 危险标题
这是一个危险信息，用于警告可能导致严重后果的操作。
:::

#### 注意（Note）

```markdown
:::note 注意标题
这是一个注意事项，用于补充说明。
:::
```

:::note 注意标题
这是一个注意事项，用于补充说明。
:::

#### 信息（Info）

```markdown
:::info 信息标题
这是一个信息提示，用于提供额外信息。
:::
```

:::info 信息标题
这是一个信息提示，用于提供额外信息。
:::

### 详情折叠

使用 `:::details` 创建可折叠的内容：

```markdown
:::details 点击查看详细信息
这里是需要折叠的内容。
:::
```

:::details 点击查看详细信息
这里是需要折叠的内容。
:::

## 链接引用规范

### 相对路径链接

链接到项目内的其他文档：

```markdown
[快速开始](./getting-started.md)
[API 文档](../api/overview.md)
```

### 外部链接

链接到外部网站：

```markdown
[Python 官网](https://www.python.org/)
[VitePress 文档](https://vitepress.dev/)
```

### 页面内锚点

链接到当前页面的某个章节：

```markdown
[跳转到标题](#标题名称)
```

### 图片链接

图片存放在 `public/` 目录，使用 `/` 开头的绝对路径：

```markdown
![Logo](/logo.png)
![示例图片](/images/example.png)
```

## 语言和术语规范

### 中文技术术语统一

保持术语一致性：

```markdown
✅ 用户、数据库、接口、配置
❌ 使用者、资料库、API、设定
```

### 英文术语使用场景

以下情况使用英文术语：

- 编程语言：Python、JavaScript、SQL
- 技术框架：Flask、Vue、VitePress
- 技术名词：API、REST、JSON、URL
- 代码相关：变量名、函数名、文件名

### 标点符号规范

- 中文内容使用中文标点：`，。！？；：""''`
- 英文内容使用英文标点：`,.!?;:""`
- 代码块内使用英文标点

## 文档更新规范

### 添加新文档

1. 在相应目录创建 `.md` 文件
2. 按照规范编写内容
3. 更新 `.vitepress/config.mts` 注册到导航

### 更新现有文档

1. 直接修改对应的 `.md` 文件
2. 检查所有链接是否有效
3. 确保代码示例可运行

### 在侧边栏注册

编辑 `.vitepress/config.mts`，在 `createSidebar()` 函数中添加：

```typescript
function createSidebar() {
  return {
    "/guides/": [
      {
        text: "指南",
        items: [
          { text: "文档写作指南", link: "/guides/writing-guide" },
          { text: "新文档标题", link: "/guides/new-document" },
        ],
      },
    ],
  };
}
```

### 在顶部导航注册

编辑 `.vitepress/config.mts`，在 `createNav()` 函数中添加：

```typescript
function createNav() {
  return [
    { text: "首页", link: "/" },
    { text: "文档写作指南", link: "/guides/writing-guide" },
    { text: "新文档", link: "/guides/new-document" },
  ];
}
```

## 完整示例模板

### 指南类文档模板

````markdown
---
# 可选的 frontmatter
title: 文档标题
description: 文档描述
---

# 文档标题

简短的文档介绍，说明本文档的目的和适用场景。

## 前置要求

- 要求 1
- 要求 2

## 主要章节

### 子章节

内容描述...

:::tip 提示
有用的提示信息。
:::

### 代码示例

```python
# 示例代码
def example():
    pass
```
````

## 常见问题

### 问题 1

**问题**：问题描述

**答案**：问题解答

## 相关链接

- [相关文档 1](./related-doc-1.md)
- [相关文档 2](./related-doc-2.md)

````

### API 文档模板

```markdown
# API 名称

API 的简要描述。

## 请求

### 请求方法

`GET` /api/users

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id     | int  | 是   | 用户 ID |

### 请求示例

```bash
curl -X GET "http://localhost:5000/api/users?id=1"
````

## 响应

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "张三"
  }
}
```

### 响应参数

| 参数名  | 类型   | 说明     |
| ------- | ------ | -------- |
| code    | int    | 状态码   |
| message | str    | 提示信息 |
| data    | object | 数据对象 |

## 错误码

| 错误码 | 说明       |
| ------ | ---------- |
| 400    | 参数错误   |
| 404    | 资源不存在 |
| 500    | 服务器错误 |

````

### 教程类文档模板

```markdown
# 教程标题

本教程将指导您完成某个任务。

## 学习目标

完成本教程后，您将能够：

- 目标 1
- 目标 2
- 目标 3

## 前置知识

- 知识点 1
- 知识点 2

## 第一步：步骤标题

步骤说明...

```bash
# 命令示例
command
````

:::info 信息
补充说明信息。
:::

## 第二步：步骤标题

步骤说明...

## 总结

完成本教程后，您已经学会了...

## 下一步

````

## 最佳实践

### 文档长度建议

- 单个文档页面不超过 2000 字
- 内容过多时考虑拆分为多个文档
- 使用折叠功能隐藏次要内容

### 内容组织方式

- 从简到繁，循序渐进
- 先讲概念，再讲实践
- 提供完整的示例代码

### 代码示例使用

- 确保代码可运行
- 添加必要的注释
- 标注输出结果
- 提供完整的上下文

### 注意事项添加

- 使用 `:::danger` 标记危险操作
- 使用 `:::warning` 标记潜在问题
- 使用 `:::tip` 提供有用建议

### 图片使用

- 图片放在 `public/` 目录
- 使用 `/` 开头的绝对路径
- 图片大小控制在 500KB 以内
- 使用适当的格式（PNG、JPG、SVG）

## 常见问题

### 如何调试文档渲染？

使用 VitePress 开发服务器：

```bash
npm run dev
````

访问 `http://localhost:5173` 查看实时效果。

### 如何处理特殊字符？

某些字符需要转义：

```markdown
\\ 反斜杠 \* 星号
\_ 下划线
\# 井号
```

### 如何添加目录导航？

VitePress 会自动根据标题生成目录导航，无需手动添加。

### 如何设置最后更新时间？

在 `.vitepress/config.mts` 中配置：

```typescript
lastUpdated: true;
```

## 检查清单

提交文档前，请确认以下事项：

### 内容检查

- [ ] 文件名符合规范
- [ ] 标题层级正确
- [ ] 内容逻辑清晰
- [ ] 术语使用一致

### 技术检查

- [ ] 所有链接可访问
- [ ] 代码示例可运行
- [ ] 图片路径正确
- [ ] 语法高亮正确

### 格式检查

- [ ] 使用了正确的提示框
- [ ] 标点符号正确
- [ ] 代码格式规范
- [ ] 表格格式正确

### 配置检查

- [ ] 已在侧边栏注册
- [ ] 已在顶部导航注册（如需要）
- [ ] 配置文件语法正确

## 参考资源

- [VitePress 官方文档](https://vitepress.dev/)
- [Markdown 基础语法](https://www.markdownguide.org/basic-syntax/)
- [项目 GitHub 仓库](https://github.com/yourusername/py-small-admin)

---

感谢您为 Py Small Admin 文档做出的贡献！如有疑问，请提交 Issue 或 Pull Request。
