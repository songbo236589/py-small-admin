# Py Small Admin 文档写作标准

本文档详细说明了 Py Small Admin 项目的文档写作标准和规范。

## 目录结构规范

### 标准目录结构

```
dosc/
├── index.md              # 首页
├── guides/               # 指南类文档
├── api/                  # API 文档
├── tutorials/            # 教程类文档
├── server/               # 服务端开发文档
├── admin-web/            # 后台管理开发文档
└── public/               # 静态资源
```

### 目录用途说明

- **guides/**：存放指南、教程类文档，如安装指南、配置说明、开发教程等
- **api/**：存放 API 文档，包括接口说明、参数说明、示例代码等
- **tutorials/**：存放分步教程和实战案例
- **server/**：服务端开发文档
- **admin-web/**：后台管理开发文档
- **public/**：存放文档中引用的图片、图标等静态资源

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
quick-start.md
authentication.md
```

### 错误示例

```bash
用户指南.md          # ❌ 使用中文
UserGuide.md        # ❌ 使用驼峰命名
user guide.md       # ❌ 使用空格
user_guide.md       # ❌ 使用下划线
```

### 命名建议

- **指南类文档**: `quick-start.md`, `installation-guide.md`, `configuration.md`
- **API 文档**: `user-api.md`, `auth-api.md`, `data-api.md`
- **教程类文档**: `first-app.md`, `integration-tutorial.md`, `advanced-usage.md`

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

**使用建议**:

- 每个文档只有一个一级标题
- 二级标题用于主要章节
- 三级标题用于子章节
- 避免过深的标题层级（不超过 4 级）

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

**表格规范**:

- 表头使用加粗
- 对齐方式：文本左对齐，数字右对齐
- 避免过宽的表格，考虑拆分

### 图片引用

图片存放在 `public/` 目录，使用绝对路径引用：

```markdown
![图片说明](/logo.png)
![示例图片](/images/example.png)
```

**图片规范**:

- 图片大小控制在 500KB 以内
- 使用适当的格式（PNG、JPG、SVG）
- 提供清晰的图片说明
- 图片文件名使用 kebab-case

## 代码块规范

### 语法高亮

使用三个反引号包裹代码，并指定语言类型：

```python
def hello_world():
    print("Hello, World!")
```

**支持的语言**:

- `python`：Python 代码
- `bash`：Shell 脚本
- `javascript`：JavaScript 代码
- `json`：JSON 数据
- `sql`：SQL 查询
- `yaml`：YAML 配置
- `typescript`：TypeScript 代码

### 代码注释

示例代码应包含必要的注释：

```python
# 创建用户实例
user = User(name="张三", email="zhangsan@example.com")

# 保存到数据库
user.save()
```

**注释规范**:

- 解释关键步骤
- 说明复杂逻辑
- 标注输出结果
- 避免过度注释

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

#### 警告（Warning）

```markdown
:::warning 警告标题
这是一个警告信息，用于提醒用户注意潜在问题。
:::
```

#### 危险（Danger）

```markdown
:::danger 危险标题
这是一个危险信息，用于警告可能导致严重后果的操作。
:::
```

#### 注意（Note）

```markdown
:::note 注意标题
这是一个注意事项，用于补充说明。
:::
```

#### 信息（Info）

```markdown
:::info 信息标题
这是一个信息提示，用于提供额外信息。
:::
```

### 详情折叠

使用 `:::details` 创建可折叠的内容：

```markdown
:::details 点击查看详细信息
这里是需要折叠的内容。
:::
```

**使用场景**:

- 长代码块
- 详细的技术说明
- 可选的配置选项
- 补充信息

## 链接引用规范

### 相对路径链接

链接到项目内的其他文档：

```markdown
[快速开始](./quick-start.md)
[API 文档](../api/overview.md)
[配置指南](./configuration.md)
```

### 外部链接

链接到外部网站：

```markdown
[Python 官网](https://www.python.org/)
[VitePress 文档](https://vitepress.dev/)
[GitHub 仓库](https://github.com/songbo236589/py-small-admin)
```

### 页面内锚点

链接到当前页面的某个章节：

```markdown
[跳转到标题](#标题名称)
[安装说明](#安装)
[配置选项](#配置选项)
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

**常用术语**:

- 用户（User）
- 数据库（Database）
- 接口（Interface/API）
- 配置（Configuration）
- 权限（Permission）
- 角色（Role）
- 日志（Log）

### 英文术语使用场景

以下情况使用英文术语：

- **编程语言**：Python、JavaScript、SQL、TypeScript
- **技术框架**：Flask、Vue、VitePress、React
- **技术名词**：API、REST、JSON、URL、HTTP
- **代码相关**：变量名、函数名、文件名、类名

### 标点符号规范

- **中文内容**使用中文标点：`，。！？；：""''`
- **英文内容**使用英文标点：`,.!?;:""`
- **代码块内**使用英文标点

**示例**:

````markdown
中文内容，使用中文标点。

English content, use English punctuation.

```python
# Code blocks use English punctuation
def function():
    pass
```
````

````

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
    '/guides/': [
      {
        text: '指南',
        items: [
          { text: "文档写作指南", link: "/guides/writing-guide" },
          { text: "新文档标题", link: "/guides/new-document" },
        ],
      },
    ],
  };
}
````

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

## 最佳实践

### 文档长度建议

- 单个文档页面不超过 2000 字
- 内容过多时考虑拆分为多个文档
- 使用折叠功能隐藏次要内容

### 内容组织方式

- 从简到繁，循序渐进
- 先讲概念，再讲实践
- 提供完整的示例代码
- 使用清晰的章节结构

### 代码示例使用

- 确保代码可运行
- 添加必要的注释
- 标注输出结果
- 提供完整的上下文

### 注意事项添加

- 使用 `:::danger` 标记危险操作
- 使用 `:::warning` 标记潜在问题
- 使用 `:::tip` 提供有用建议
- 使用 `:::note` 补充说明

### 图片使用

- 图片放在 `public/` 目录
- 使用 `/` 开头的绝对路径
- 图片大小控制在 500KB 以内
- 使用适当的格式（PNG、JPG、SVG）

## 检查清单

提交文档前，请确认以下事项：

### 内容检查

- [ ] 文件名符合规范（kebab-case）
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

---

遵循这些标准和规范，确保 Py Small Admin 文档的质量和一致性。
