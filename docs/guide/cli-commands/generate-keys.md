# 密钥生成

密钥生成工具用于生成和更新 `.env` 文件中的安全密钥，包括 API 密钥和 JWT 密钥。

## 基本用法

### 生成所有密钥

```bash
python -m commands.generate_keys --all
```

这将生成以下密钥并更新到 `.env` 文件：
- `APP_ADMIN_X_API_KEY` - 管理员接口验证的 API 密钥
- `JWT_SECRET_KEY` - JWT 认证密钥

### 只生成 API 密钥

```bash
python -m commands.generate_keys --api-key
```

### 只生成 JWT 密钥

```bash
python -m commands.generate_keys --jwt-secret
```

## 预览模式

使用 `--dry-run` 参数预览将要生成的密钥，不实际修改文件：

```bash
python -m commands.generate_keys --all --dry-run
```

输出示例：

```
将要生成的密钥:
--------------------------------------------------
配置项: APP_ADMIN_X_API_KEY
新值:   kxY9************pL2m
长度:   32
--------------------------------------------------
配置项: JWT_SECRET_KEY
新值:   aB3************xY7************9Zq
长度:   64
--------------------------------------------------

预览模式，未实际修改文件
```

## 自定义密钥长度

使用 `--length` 参数指定密钥长度：

```bash
# 生成 64 位 API 密钥
python -m commands.generate_keys --api-key --length 64

# 生成 128 位 JWT 密钥
python -m commands.generate_keys --jwt-secret --length 128
```

## 自动确认

使用 `--yes` 或 `-y` 参数跳过确认步骤：

```bash
python -m commands.generate_keys --all --yes
```

## 指定环境文件

使用 `--env` 参数指定 `.env` 文件路径：

```bash
python -m commands.generate_keys --all --env /path/to/.env.production
```

## 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `--all` | 生成所有密钥 | `python -m commands.generate_keys --all` |
| `--api-key` | 只生成 API 密钥 | `python -m commands.generate_keys --api-key` |
| `--jwt-secret` | 只生成 JWT 密钥 | `python -m commands.generate_keys --jwt-secret` |
| `--dry-run` | 预览模式 | `python -m commands.generate_keys --all --dry-run` |
| `--length <n>` | 指定密钥长度 | `python -m commands.generate_keys --api-key --length 64` |
| `--yes` | 跳过确认 | `python -m commands.generate_keys --all --yes` |
| `--env <path>` | 指定环境文件 | `python -m commands.generate_keys --all --env .env.production` |

## 安全建议

### 生产环境

1. **使用强密钥**：默认长度已足够（API 密钥 32 位，JWT 密钥 64 位）
2. **定期更换**：建议定期更换密钥
3. **妥善保管**：不要将密钥提交到版本控制系统
4. **使用环境变量**：考虑使用密钥管理服务

### 密钥复杂度

生成的密钥满足以下安全要求：
- 包含大小写字母和数字
- 使用加密安全的随机数生成器
- 长度满足安全最佳实践

## 常见问题

### .env 文件不存在

**问题**：执行命令时提示 ".env 文件不存在"

**解决方案**：
1. 先创建 `.env` 文件：
   ```bash
   cp .env.example .env
   ```
2. 然后再生成密钥

### 配置项不存在

**问题**：提示"未找到 xxx，将在文件末尾添加"

**解决方案**：工具会自动将新配置项添加到 `.env` 文件末尾。

### 密钥显示已遮蔽

**说明**：为保护密钥安全，输出中只显示密钥的前 4 位和后 4 位，中间用 `*` 代替。这是正常行为。

## 详细文档

更多详细用法请参考 [密钥生成工具使用文档](../../../server/docs/密钥生成工具使用文档.md)
