# 系统配置 API

本文档介绍了系统配置管理的 API 接口。系统配置用于管理系统的各种配置项。

## 配置分组说明

系统配置按分组进行管理，常见的配置分组如下：

| 分组代码 | 说明 | 示例配置项 |
|----------|------|------------|
| basic | 基础配置 | 站点名称、描述、关键词 |
| upload | 上传配置 | 文件大小限制、允许的文件类型 |
| storage | 存储配置 | 存储类型、云服务配置 |
| email | 邮件配置 | SMTP 服务器、发件人信息 |
| sms | 短信配置 | 短信服务商、签名、模板 |

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/sys_config/edit/{group_code}` | 获取配置分组数据 |
| PUT | `/api/admin/sys_config/update/{group_code}` | 更新配置分组数据 |

## 获取配置分组数据

获取指定分组的配置数据，用于配置编辑页面。

**请求**：
```http
GET /api/admin/sys_config/edit/basic
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| group_code | str | 是 | 配置分组代码 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "group_name": "基础配置",
    "group_code": "basic",
    "configs": [
      {
        "id": 1,
        "config_key": "site_name",
        "config_value": "Py Small Admin",
        "value_type": "string",
        "description": "站点名称"
      },
      {
        "id": 2,
        "config_key": "site_description",
        "config_value": "一个轻量级的后台管理系统",
        "value_type": "string",
        "description": "站点描述"
      },
      {
        "id": 3,
        "config_key": "site_keywords",
        "config_value": "后台,管理系统,Python",
        "value_type": "string",
        "description": "站点关键词"
      },
      {
        "id": 4,
        "config_key": "enable_register",
        "config_value": "false",
        "value_type": "bool",
        "description": "是否开启注册"
      },
      {
        "id": 5,
        "config_key": "max_upload_size",
        "config_value": "10485760",
        "value_type": "int",
        "description": "最大上传大小（字节）"
      }
    ]
  }
}
```

**字段说明**：
- `config_key`: 配置键（唯一标识）
- `config_value`: 配置值
- `value_type`: 值类型（string/int/bool/json）
- `description`: 配置说明

## 更新配置分组数据

更新指定分组的配置数据。

**请求**：
```http
PUT /api/admin/sys_config/update/basic
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| group_code | str | 是 | 配置分组代码 |

**请求体**：
```json
{
  "site_name": "Py Small Admin",
  "site_description": "一个轻量级的后台管理系统",
  "site_keywords": "后台,管理系统,Python",
  "enable_register": false,
  "max_upload_size": 10485760
}
```

**响应**：
```json
{
  "code": 200,
  "message": "配置更新成功",
  "data": null
}
```

## 配置类型说明

### String 类型

字符串类型的配置，用于存储文本内容。

```json
{
  "config_key": "site_name",
  "config_value": "Py Small Admin",
  "value_type": "string",
  "description": "站点名称"
}
```

### Int 类型

整数类型的配置，用于存储数值。

```json
{
  "config_key": "max_upload_size",
  "config_value": "10485760",
  "value_type": "int",
  "description": "最大上传大小（字节）"
}
```

### Bool 类型

布尔类型的配置，用于存储开关状态。

```json
{
  "config_key": "enable_register",
  "config_value": "true",
  "value_type": "bool",
  "description": "是否开启注册"
}
```

**注意事项**：
- 布尔值在请求中使用 `true` 或 `false`
- 存储时会被转换为字符串 `"true"` 或 `"false"`

### JSON 类型

JSON 类型的配置，用于存储复杂结构。

```json
{
  "config_key": "allowed_file_types",
  "config_value": "[\"jpg\",\"png\",\"gif\",\"pdf\",\"doc\",\"docx\"]",
  "value_type": "json",
  "description": "允许的文件类型"
}
```

## 常见配置分组示例

### 基础配置 (basic)

```json
{
  "site_name": "Py Small Admin",
  "site_description": "一个轻量级的后台管理系统",
  "site_keywords": "后台,管理系统,Python",
  "site_logo": "/uploads/logo.png",
  "site_favicon": "/uploads/favicon.ico",
  "enable_register": false
}
```

### 上传配置 (upload)

```json
{
  "max_upload_size": 10485760,
  "allowed_image_types": ["jpg", "jpeg", "png", "gif", "webp"],
  "allowed_document_types": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"],
  "allowed_video_types": ["mp4", "avi", "mov"],
  "allowed_audio_types": ["mp3", "wav", "ogg"],
  "thumbnail_width": 200,
  "thumbnail_height": 200
}
```

### 存储配置 (storage)

```json
{
  "storage_type": "local",
  "local_path": "/uploads",
  "aliyun_oss_bucket": "",
  "aliyun_oss_access_key": "",
  "aliyun_oss_secret_key": "",
  "aliyun_oss_endpoint": "",
  "aliyun_oss_domain": "",
  "tencent_cos_bucket": "",
  "tencent_cos_secret_id": "",
  "tencent_cos_secret_key": "",
  "tencent_cos_region": "",
  "tencent_cos_domain": ""
}
```

### 邮件配置 (email)

```json
{
  "email_host": "smtp.example.com",
  "email_port": 465,
  "email_username": "noreply@example.com",
  "email_password": "password",
  "email_encryption": "ssl",
  "email_from_address": "noreply@example.com",
  "email_from_name": "Py Small Admin"
}
```

## 错误响应

### 配置分组不存在

```json
{
  "code": 404,
  "message": "配置分组不存在",
  "data": null
}
```

### 配置项验证失败

```json
{
  "code": 422,
  "message": "配置项验证失败",
  "data": {
    "max_upload_size": ["必须是正整数"],
    "enable_register": ["必须是布尔值"]
  }
}
```

## 注意事项

1. **配置缓存**：系统会对配置进行缓存，更新配置后可能需要清除缓存才能生效
2. **类型验证**：更新配置时会根据 `value_type` 进行类型验证
3. **配置分组**：建议按功能模块对配置进行分组
4. **敏感信息**：密码等敏感信息应该使用加密存储
5. **默认值**：每个配置项都应该有合理的默认值
