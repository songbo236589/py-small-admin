---
title: 教程标题
description: 教程的简要描述
---

# 教程标题

本教程将指导您完成某个任务，从零开始构建某物。

:::tip 提示
预计完成时间：30 分钟
难度等级：初级
:::

## 学习目标

完成本教程后，您将能够：

- 目标 1：描述具体的学习目标
- 目标 2：描述具体的学习目标
- 目标 3：描述具体的学习目标

## 前置知识

在开始之前，您应该具备以下知识：

- 知识点 1：Python 基础知识
- 知识点 2：了解 HTTP 请求
- 知识点 3：熟悉命令行操作

:::info 信息
如果您不熟悉某些前置知识，请先查看[相关文档](./prerequisites.md)。
:::

## 准备工作

### 环境要求

- Python 3.8+
- Node.js 16+
- 互联网连接

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/songbo236589/py-small-admin.git

# 进入项目目录
cd py-small-admin

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖
cd admin-web
npm install
```

:::warning 警告
确保使用 Python 3.8 或更高版本。
:::

## 第一步：步骤标题

### 步骤说明

详细说明这一步的目的和操作。

### 操作步骤

1. 子步骤 1
2. 子步骤 2
3. 子步骤 3

### 代码示例

```bash
# 命令示例
command
```

```python
# Python 代码示例
def example():
    print("Hello, World!")
```

:::details 查看详细说明

这里是更详细的说明内容，包括：

- 细节 1
- 细节 2
- 细节 3

:::

### 验证步骤

确保这一步成功完成：

```bash
# 验证命令
verify_command
```

:::tip 提示
如果验证失败，请检查：

1. 是否正确执行了所有步骤
2. 环境配置是否正确
3. 是否有权限问题
   :::

## 第二步：步骤标题

### 步骤说明

详细说明这一步的目的和操作。

### 操作步骤

1. 子步骤 1
2. 子步骤 2
3. 子步骤 3

### 代码示例

```python
# 完整的代码示例
import os
from pathlib import Path

def create_config():
    """创建配置文件"""
    config_dir = Path.home() / '.py-small-admin'
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / 'config.yaml'
    if not config_file.exists():
        with open(config_file, 'w') as f:
            f.write('debug: false\n')
        print(f"配置文件已创建: {config_file}")
    else:
        print(f"配置文件已存在: {config_file}")

# 调用函数
create_config()

# 输出：配置文件已创建: /home/user/.py-small-admin/config.yaml
```

:::info 信息
配置文件使用 YAML 格式，便于编辑。
:::

### 验证步骤

```bash
# 检查配置文件
cat ~/.py-small-admin/config.yaml
```

## 第三步：步骤标题

### 步骤说明

详细说明这一步的目的和操作。

### 操作步骤

1. 子步骤 1
2. 子步骤 2
3. 子步骤 3

### 代码示例

```javascript
// JavaScript 代码示例
const express = require("express");
const app = express();

app.get("/api/users", (req, res) => {
  res.json({ users: [] });
});

app.listen(3000, () => {
  console.log("Server running on port 3000");
});
```

### 验证步骤

```bash
# 启动服务器
node server.js

# 测试 API
curl http://localhost:3000/api/users
```

:::details 查看完整代码

```javascript
// 完整的服务器代码
const express = require("express");
const cors = require("cors");
const helmet = require("helmet");

const app = express();

// 中间件
app.use(helmet());
app.use(cors());
app.use(express.json());

// 路由
app.get("/api/users", (req, res) => {
  res.json({
    code: 200,
    message: "success",
    data: [
      { id: 1, name: "张三" },
      { id: 2, name: "李四" },
    ],
  });
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

:::

## 进阶功能

### 功能 1

说明进阶功能...

```python
# 进阶功能代码示例
def advanced_function():
    pass
```

### 功能 2

说明进阶功能...

```python
# 进阶功能代码示例
def advanced_function_2():
    pass
```

:::tip 提示
这些进阶功能是可选的，可以根据需要选择使用。
:::

## 故障排除

### 问题 1：问题描述

**症状**：描述问题的症状

**原因**：分析问题的原因

**解决方案**：

1. 解决方案 1
2. 解决方案 2
3. 解决方案 3

### 问题 2：问题描述

**症状**：描述问题的症状

**原因**：分析问题的原因

**解决方案**：

1. 解决方案 1
2. 解决方案 2

## 总结

完成本教程后，您已经学会了：

- 总结 1：回顾学习目标 1
- 总结 2：回顾学习目标 2
- 总结 3：回顾学习目标 3

:::info 信息
您现在已经掌握了基础用法，可以开始构建自己的应用了！
:::

## 下一步

### 进阶教程

- [进阶教程 1](./advanced-tutorial-1.md)
- [进阶教程 2](./advanced-tutorial-2.md)

### 相关文档

- [API 文档](../api/overview.md)
- [配置指南](../guides/configuration.md)
- [常见问题](../guides/faq.md)

### 实战项目

- [实战项目 1](../projects/project-1.md)
- [实战项目 2](../projects/project-2.md)

## 完整代码

:::details 查看完整项目代码

```python
"""
完整的示例代码
"""

import os
import sys
from pathlib import Path

class ExampleApp:
    """示例应用类"""

    def __init__(self):
        """初始化应用"""
        self.config_dir = Path.home() / '.py-small-admin'
        self.config_file = self.config_dir / 'config.yaml'

    def setup(self):
        """设置应用"""
        print("开始设置应用...")
        self.create_config_dir()
        self.create_config_file()
        print("设置完成！")

    def create_config_dir(self):
        """创建配置目录"""
        self.config_dir.mkdir(exist_ok=True)
        print(f"配置目录: {self.config_dir}")

    def create_config_file(self):
        """创建配置文件"""
        if not self.config_file.exists():
            with open(self.config_file, 'w') as f:
                f.write('debug: false\n')
            print(f"配置文件已创建: {self.config_file}")
        else:
            print(f"配置文件已存在: {self.config_file}")

    def run(self):
        """运行应用"""
        print("运行应用...")
        # 应用逻辑
        print("应用运行完成")

def main():
    """主函数"""
    app = ExampleApp()
    app.setup()
    app.run()

if __name__ == '__main__':
    main()
```

:::

## 常见问题

### 如何修改配置？

编辑配置文件：

```bash
# 使用文本编辑器
nano ~/.py-small-admin/config.yaml

# 或使用 VS Code
code ~/.py-small-admin/config.yaml
```

### 如何卸载？

删除配置文件：

```bash
# 删除配置目录
rm -rf ~/.py-small-admin
```

:::danger 危险
删除配置目录将清除所有配置，无法恢复！
:::

## 反馈与支持

如果您在完成本教程时遇到问题：

- 查看[常见问题](../guides/faq.md)
- 提交 [GitHub Issue](https://github.com/songbo236589/py-small-admin/issues)
- 加入[社区讨论](https://github.com/songbo236589/py-small-admin/discussions)

## 更新日志

### v1.0 (2024-01-01)

- 初始版本发布
- 完成基础教程
- 添加故障排除章节

---

祝您学习愉快！如有任何问题，请随时反馈。
