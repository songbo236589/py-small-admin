---
name: py-small-admin-docs
description: 专门用于为 Py Small Admin 项目编写文档。当用户需要创建、编辑或更新 Py Small Admin 的文档时使用此 Skill。支持指南类文档、API 文档、教程类文档的创建，自动遵循项目的文档规范、VitePress 配置和命名约定。适用于：创建新文档页面、编写 API 文档、创建教程、更新现有文档、验证文档格式。
license: Complete terms in LICENSE.txt
---

# Py Small Admin Docs

## Overview

此 Skill 专门用于为 **Py Small Admin** 项目编写高质量文档。它提供完整的工作流程、自动化工具和模板，确保所有文档遵循项目的 VitePress 规范、命名约定和写作标准。

## Project Structure

Py Small Admin 使用 **VitePress** 作为文档站点，目录结构如下：

```
dosc/
├── index.md                    # 首页
├── package.json                # 项目配置
├── .vitepress/
│   ├── config.mts             # VitePress 配置
│   └── theme/                 # 自定义主题
├── guides/                    # 指南类文档
│   └── writing-guide.md       # 文档写作指南
├── server/                    # 服务端文档（待创建）
├── admin-web/                 # 后台管理文档（待创建）
└── public/                    # 静态资源
```

## Document Types

支持三种主要文档类型：

### 1. 指南类文档（Guides）

- **位置**: `guides/` 目录
- **用途**: 安装指南、配置说明、开发教程
- **示例**: 快速开始、配置指南、开发指南

### 2. API 文档（API）

- **位置**: `api/` 目录
- **用途**: 接口说明、参数说明、示例代码
- **示例**: 用户 API、认证 API、数据 API

### 3. 教程类文档（Tutorials）

- **位置**: `tutorials/` 目录
- **用途**: 分步教程、实战案例
- **示例**: 创建第一个应用、集成第三方服务

## Document Creation Workflow

### Step 1: Identify Document Type

根据用户需求确定文档类型：

```
用户需求 → 文档类型
─────────────────────────────
"如何安装" → 指南类（guides/）
"API 说明" → API 文档（api/）
"教程" → 教程类（tutorials/）
"配置" → 指南类（guides/）
```

### Step 2: Determine File Location

根据文档类型选择合适的目录：

| 文档类型 | 目录         | 示例路径                 |
| -------- | ------------ | ------------------------ |
| 指南类   | `guides/`    | `guides/quick-start.md`  |
| API 文档 | `api/`       | `api/user-api.md`        |
| 教程类   | `tutorials/` | `tutorials/first-app.md` |

### Step 3: Create Document File

#### File Naming Rules

- 使用 **kebab-case**（小写字母 + 连字符）
- 使用英文命名
- 文件扩展名为 `.md`
- 避免中文、空格或特殊字符

**正确示例**:

```
quick-start.md
user-guide.md
api-reference.md
installation-guide.md
```

**错误示例**:

```
用户指南.md          # ❌ 使用中文
UserGuide.md        # ❌ 使用驼峰命名
user guide.md       # ❌ 使用空格
user_guide.md       # ❌ 使用下划线
```

### Step 4: Select or Create Template

根据文档类型选择合适的模板：

- **指南类文档**: 使用 `assets/templates/guide-template.md`
- **API 文档**: 使用 `assets/templates/api-template.md`
- **教程类文档**: 使用 `assets/templates/tutorial-template.md`

### Step 5: Write Document Content

遵循以下规范编写内容：

#### Markdown Basic Syntax

**标题层级**（最多 6 级）:

```markdown
# 一级标题（通常每页只有一个）

## 二级标题（主要章节）

### 三级标题（子章节）

#### 四级标题（小节）
```

**代码块**（使用语法高亮）:

```python
def hello_world():
    print("Hello, World!")
```

**表格**:

```markdown
| 参数名 | 类型 | 必填 | 说明    |
| ------ | ---- | ---- | ------- |
| id     | int  | 是   | 用户 ID |
```

#### VitePress Special Syntax

**提示框**:

```markdown
:::tip 提示标题
这是一个提示信息。
:::

:::warning 警告标题
这是一个警告信息。
:::

:::danger 危险标题
这是一个危险信息。
:::

:::note 注意标题
这是一个注意事项。
:::

:::info 信息标题
这是一个信息提示。
:::
```

**详情折叠**:

```markdown
:::details 点击查看详细信息
这里是需要折叠的内容。
:::
```

### Step 6: Register in Config

更新 `.vitepress/config.mts` 注册文档：

#### Add to Navigation

在 `createNav()` 函数中添加：

```typescript
function createNav() {
  return [
    { text: "首页", link: "/" },
    { text: "文档写作指南", link: "/guides/writing-guide" },
    { text: "新文档标题", link: "/guides/new-document" },
  ];
}
```

#### Add to Sidebar

在 `createSidebar()` 函数中添加：

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

### Step 7: Validate Document

使用验证脚本检查文档质量：

```bash
# 验证文档
python scripts/validate-doc.py guides/quick-start.md
```

验证内容包括：

- 文件名规范
- Markdown 语法
- 代码块格式
- 链接有效性
- 术语一致性

## Automation Scripts

### create-doc.py

创建新文档的自动化脚本：

```bash
# 创建指南类文档
python scripts/create-doc.py --type guide --title "快速开始" --path guides/quick-start.md

# 创建 API 文档
python scripts/create-doc.py --type api --title "用户API" --path api/user-api.md

# 创建教程
python scripts/create-doc.py --type tutorial --title "创建第一个应用" --path tutorials/first-app.md
```

### register-doc.py

注册文档到配置文件：

```bash
python scripts/register-doc.py --path guides/quick-start.md --title "快速开始"
```

### validate-doc.py

验证文档质量：

```bash
python scripts/validate-doc.py guides/quick-start.md
```

## Writing Standards

### Language and Terminology

**中文技术术语统一**:

```
✅ 用户、数据库、接口、配置
❌ 使用者、资料库、API、设定
```

**英文术语使用场景**:

- 编程语言：Python、JavaScript、SQL
- 技术框架：Flask、Vue、VitePress
- 技术名词：API、REST、JSON、URL
- 代码相关：变量名、函数名、文件名

**标点符号规范**:

- 中文内容使用中文标点：`，。！？；：""''`
- 英文内容使用英文标点：`,.!?;:""`
- 代码块内使用英文标点

### Code Examples

**代码示例要求**:

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
```

### Image Usage

**图片使用规范**:

- 图片放在 `public/` 目录
- 使用 `/` 开头的绝对路径
- 图片大小控制在 500KB 以内
- 使用适当的格式（PNG、JPG、SVG）

```markdown
![Logo](/logo.png)
![示例图片](/images/example.png)
```

## Best Practices

### Document Length

- 单个文档页面不超过 2000 字
- 内容过多时考虑拆分为多个文档
- 使用折叠功能隐藏次要内容

### Content Organization

- 从简到繁，循序渐进
- 先讲概念，再讲实践
- 提供完整的示例代码

### Adding Notes

- 使用 `:::danger` 标记危险操作
- 使用 `:::warning` 标记潜在问题
- 使用 `:::tip` 提供有用建议

## Checklist

提交文档前，请确认以下事项：

### Content Check

- [ ] 文件名符合规范（kebab-case）
- [ ] 标题层级正确
- [ ] 内容逻辑清晰
- [ ] 术语使用一致

### Technical Check

- [ ] 所有链接可访问
- [ ] 代码示例可运行
- [ ] 图片路径正确
- [ ] 语法高亮正确

### Format Check

- [ ] 使用了正确的提示框
- [ ] 标点符号正确
- [ ] 代码格式规范
- [ ] 表格格式正确

### Configuration Check

- [ ] 已在侧边栏注册
- [ ] 已在顶部导航注册（如需要）
- [ ] 配置文件语法正确

## Resources

### scripts/

**create-doc.py**: 创建新文档的自动化脚本
**register-doc.py**: 注册文档到配置文件
**validate-doc.py**: 验证文档质量

### references/

**writing-standards.md**: 详细的写作标准和规范
**vitepress-syntax.md**: VitePress 特殊语法参考
**templates.md**: 文档模板索引和使用指南

### assets/

**templates/**: 文档模板文件

- `guide-template.md`: 指南类文档模板
- `api-template.md`: API 文档模板
- `tutorial-template.md`: 教程类文档模板

## Common Issues

### How to debug document rendering?

使用 VitePress 开发服务器：

```bash
cd dosc
npm run docs:dev
```

访问 `http://localhost:5173` 查看实时效果。

### How to handle special characters?

某些字符需要转义：

```markdown
\\ 反斜杠 \* 星号
\_ 下划线
\# 井号
```

### How to add table of contents?

VitePress 会自动根据标题生成目录导航，无需手动添加。

## Integration with Other Skills

### doc-coauthoring

对于复杂的文档编写任务，可以结合使用 `doc-coauthoring` Skill：

1. 使用 `py-small-admin-docs` 创建文档框架
2. 使用 `doc-coauthoring` 的三阶段工作流优化内容
   - 阶段 1：上下文收集
   - 阶段 2：优化与结构
   - 阶段 3：读者测试

### Example Workflow

```
用户: "为 Py Small Admin 编写 API 文档"

1. 触发 py-small-admin-docs Skill
   - 创建符合项目规范的文档
   - 应用项目模板
   - 注册到配置

2. 触发 doc-coauthoring Skill（可选）
   - 如果文档内容复杂，使用三阶段工作流
   - 上下文收集 → 优化结构 → 读者测试
```

## Quick Reference

### File Paths

| 文档类型 | 基础路径          | 示例                          |
| -------- | ----------------- | ----------------------------- |
| 指南类   | `dosc/guides/`    | `dosc/guides/quick-start.md`  |
| API 文档 | `dosc/api/`       | `dosc/api/user-api.md`        |
| 教程类   | `dosc/tutorials/` | `dosc/tutorials/first-app.md` |

### Config File

**位置**: `dosc/.vitepress/config.mts`
**主要函数**:

- `createNav()`: 顶部导航配置
- `createSidebar()`: 侧边栏配置

### Development Commands

```bash
# 启动开发服务器
cd dosc && npm run docs:dev

# 构建生产版本
cd dosc && npm run docs:build

# 预览构建结果
cd dosc && npm run docs:preview
```

---

此 Skill 专门为 Py Small Admin 项目优化，确保所有文档遵循项目的规范和标准。
