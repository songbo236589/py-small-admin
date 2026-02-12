# AI 生成功能

本系统集成了 Ollama AI 服务，支持使用本地大语言模型生成文章内容。

## 功能概述

### 支持的 AI 模型

通过 Ollama，系统支持多种开源大语言模型：

| 模型 | 大小 | 说明 |
|------|------|------|
| qwen2.5:7b | ~4.5GB | 通义千问 2.5，默认模型 |
| qwen2.5:14b | ~9GB | 更大更准确 |
| llama3.2:8b | ~4.7GB | Meta Llama 3.2 |
| mistral:7b | ~4.1GB | Mistral AI |

更多模型请访问：https://ollama.com/library

### 生成模式

系统提供三种文章生成模式：

| 模式 | 说明 | 输入 |
|------|------|------|
| `title` | 仅根据标题生成 | 问题标题 |
| `description` | 根据标题和描述生成 | 问题标题 + 问题描述 |
| `full` | 完整生成（包含标题和描述） | 问题标题 + 问题描述 |

## 使用方法

### 1. 安装 Ollama

详见 [安装指南 - Ollama 安装](../../getting-started/install.md#42-安装-ollama可选)

### 2. 拉取模型

```bash
ollama pull qwen2.5:7b
```

### 3. 配置环境变量

在 `.env` 文件中配置（可选，有默认值）：

```bash
# Ollama 服务地址
CONTENT_OLLAMA_BASE_URL=http://localhost:11434

# Ollama 默认模型
CONTENT_OLLAMA_MODEL=qwen2.5:7b

# AI 生成超时时间（秒）
CONTENT_OLLAMA_TIMEOUT=120

# 是否启用 AI 功能
CONTENT_OLLAMA_ENABLED=true
```

### 4. 使用 AI 生成文章

#### 获取可用模型列表

```bash
GET /api/content/ai/models
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "models": [
      {
        "name": "qwen2.5:7b",
        "size": 4705159863,
        "modified_at": "2026-02-10T10:00:00Z"
      },
      {
        "name": "llama3.2:8b",
        "size": 4935775934,
        "modified_at": "2026-02-09T15:30:00Z"
      }
    ]
  }
}
```

#### AI 生成文章

```bash
POST /api/content/ai/generate_article
Content-Type: multipart/form-data

id: 1
mode: description
title: 如何学习 Python 编程？
description: 我是一名编程初学者，想系统地学习 Python，请提供学习路线和建议。
model: qwen2.5:7b
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 话题 ID |
| mode | string | 是 | 生成模式：title/description/full |
| title | string | 是 | 问题标题 |
| description | string | 否 | 问题描述 |
| model | string | 否 | 指定模型（可选，不指定则使用配置文件中的默认模型） |

**响应示例**：
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "topic_id": 1,
    "title": "如何学习 Python 编程？",
    "content": "# 如何学习 Python 编程\n\n作为一名编程初学者，系统性地学习 Python 需要循序渐进...\n\n## 第一阶段：基础语法\n\n...",
    "model": "qwen2.5:7b"
  }
}
```

## 技术实现

### 技术栈

- **AI 服务**：Ollama（本地大语言模型运行工具）
- **HTTP 客户端**：httpx（异步 HTTP 请求）
- **数据验证**：Pydantic（参数验证）

### 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  前端请求    │───▶│  AI 控制器  │───▶│  AI 服务    │───▶│  Ollama API │
│             │    │  参数验证    │    │  构建 Prompt │    │  模型推理    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │  返回结果    │
                                        │  格式化响应  │
                                        └─────────────┘
```

### Prompt 构建

系统根据不同的生成模式构建不同的 Prompt：

**title 模式**：
```
你是一位专业的内容创作者。请根据以下问题标题，撰写一篇详细的回答文章。

问题标题：{title}

要求：
1. 内容结构清晰，有明确的标题层级
2. 语言通俗易懂，适合大众阅读
3. 提供实用、有价值的信息
4. 使用 Markdown 格式输出
```

**description 模式**：
```
你是一位专业的内容创作者。请根据以下问题标题和描述，撰写一篇详细的回答文章。

问题标题：{title}
问题描述：{description}

要求：
1. 内容结构清晰，有明确的标题层级
2. 语言通俗易懂，适合大众阅读
3. 针对问题描述提供具体、实用的回答
4. 使用 Markdown 格式输出
```

**full 模式**：
```
你是一位专业的内容创作者。请根据以下问题，撰写一篇全面、深入的文章。

问题标题：{title}
问题描述：{description}

要求：
1. 内容全面深入，从多个角度分析问题
2. 提供具体的案例和数据支持
3. 给出可操作的建议和解决方案
4. 使用 Markdown 格式输出，结构清晰
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/content/ai/models` | GET | 获取可用模型列表 |
| `/api/content/ai/generate_article` | POST | AI 生成文章 |

## 最佳实践

### 1. 模型选择

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 日常使用 | qwen2.5:7b | 速度快，质量好 |
| 长文章 | qwen2.5:14b | 理解能力更强 |
| 英文内容 | llama3.2:8b | 英文语料更好 |
| 资源受限 | mistral:7b | 内存占用较少 |

### 2. 生成模式选择

- **title 模式**：适合简单、明确的问题
- **description 模式**：适合有具体背景的问题（推荐）
- **full 模式**：适合需要深度分析的专业话题

### 3. 超时配置

不同模型需要的生成时间不同：

| 模型大小 | 建议超时时间 |
|----------|--------------|
| 7b 参数 | 60-120 秒 |
| 14b 参数 | 120-180 秒 |
| 30b+ 参数 | 180-300 秒 |

## 常见问题

### 1. Ollama 连接失败

**问题**：`Cannot connect to Ollama service`

**解决方案**：
- 检查 Ollama 服务是否运行：`ollama list`
- 检查服务地址配置：`CONTENT_OLLAMA_BASE_URL`
- 检查防火墙设置

### 2. 模型不存在

**问题**：`Model not found`

**解决方案**：
```bash
# 查看已安装的模型
ollama list

# 拉取需要的模型
ollama pull qwen2.5:7b
```

### 3. 生成超时

**问题**：`AI generation timeout`

**解决方案**：
- 增加超时配置：`CONTENT_OLLAMA_TIMEOUT=180`
- 使用更小的模型
- 检查系统资源使用情况

### 4. 生成质量不佳

**建议**：
- 使用 description 或 full 模式，提供更多上下文
- 使用更大的模型（如 14b 参数）
- 优化问题标题和描述的清晰度

## 相关文档

- [Ollama 官方文档](https://ollama.com/docs)
- [安装指南 - Ollama 安装](../../getting-started/install.md#42-安装-ollama可选)
- [环境变量配置 - Ollama AI 配置](../config/env-variables.md#ollama-ai-配置)
- [Content API 文档](../api/content-api.md#ai-生成接口)
