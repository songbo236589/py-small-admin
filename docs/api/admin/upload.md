# 文件管理 API

本文档介绍了文件上传和管理的 API 接口。系统支持多种存储方式（本地存储、阿里云 OSS、腾讯云 COS、七牛云 OSS）。

## 文件分类说明

文件按类型进行分类管理：

| 类型 | 说明 | 扩展名 |
|------|------|--------|
| image | 图片文件 | jpg, jpeg, png, gif, webp, bmp, svg |
| document | 文档文件 | pdf, doc, docx, xls, xlsx, ppt, pptx, txt |
| video | 视频文件 | mp4, avi, mov, wmv, flv, mkv |
| audio | 音频文件 | mp3, wav, ogg, aac, flac |
| other | 其他文件 | zip, rar, 7z, tar, gz |

## 存储类型说明

系统支持多种存储方式：

| 类型 | 说明 | 配置 |
|------|------|------|
| local | 本地存储 | 文件保存在服务器本地磁盘 |
| aliyun_oss | 阿里云 OSS | 需要配置阿里云 OSS 相关参数 |
| tencent_cos | 腾讯云 COS | 需要配置腾讯云 COS 相关参数 |
| qiniu_oss | 七牛云 OSS | 需要配置七牛云 OSS 相关参数 |

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/upload/file` | 上传文件 |
| GET | `/api/admin/upload/index` | 获取文件列表（分页） |
| DELETE | `/api/admin/upload/destroy/{id}` | 删除文件 |
| DELETE | `/api/admin/upload/destroy_all` | 批量删除文件 |

## 上传文件

上传文件到服务器或云存储。

**请求**：
```http
POST /api/admin/upload/file
Content-Type: multipart/form-data
```

**请求体**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 上传的文件 |
| file_type | str | 是 | 文件类型：image/document/video/audio/other |

**请求示例（curl）**：
```bash
curl -X POST http://localhost:8000/api/admin/upload/file \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/image.jpg" \
  -F "file_type=image"
```

**请求示例（JavaScript）**：
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('file_type', 'image');

fetch('/api/admin/upload/file', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <token>'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**响应**：
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "id": 1,
    "original_name": "example.jpg",
    "filename": "20240101/abc123.jpg",
    "file_path": "uploads/20240101/abc123.jpg",
    "url": "http://localhost:8000/uploads/20240101/abc123.jpg",
    "file_size": 102400,
    "mime_type": "image/jpeg",
    "file_ext": "jpg",
    "file_type": "image",
    "file_hash": "a1b2c3d4e5f6...",
    "storage_type": "local",
    "width": 1920,
    "height": 1080,
    "thumbnail_filename": "20240101/thumb_abc123.jpg",
    "thumbnail_path": "uploads/20240101/thumb_abc123.jpg",
    "thumbnail_url": "http://localhost:8000/uploads/20240101/thumb_abc123.jpg",
    "created_at": "2024-01-01 00:00:00"
  }
}
```

**字段说明**：
- `id`: 文件 ID
- `original_name`: 原始文件名
- `filename`: 存储文件名（按规则生成）
- `file_path`: 文件存储路径（相对路径）
- `url`: 文件访问 URL
- `file_size`: 文件大小（字节）
- `mime_type`: MIME 类型
- `file_ext`: 文件扩展名
- `file_type`: 文件分类
- `file_hash`: 文件哈希值（SHA256，用于去重）
- `storage_type`: 存储类型
- `width/height`: 图片尺寸（仅图片类型）
- `thumbnail_*`: 缩略图信息（仅图片类型）

## 获取文件列表

获取已上传文件的列表，支持搜索、筛选和分页。

**请求**：
```http
GET /api/admin/upload/index?page=1&limit=20&file_type=image&storage_type=local
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| original_name | str | 否 | 原始文件名（模糊搜索） |
| file_type | str | 否 | 文件类型筛选 |
| storage_type | str | 否 | 存储类型筛选 |
| sort | str | 否 | 排序规则，如 `-id` |
| created_at[start] | str | 否 | 创建时间开始 |
| created_at[end] | str | 否 | 创建时间结束 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "original_name": "example.jpg",
        "filename": "20240101/abc123.jpg",
        "file_path": "uploads/20240101/abc123.jpg",
        "url": "http://localhost:8000/uploads/20240101/abc123.jpg",
        "file_size": 102400,
        "mime_type": "image/jpeg",
        "file_ext": "jpg",
        "file_type": "image",
        "storage_type": "local",
        "width": 1920,
        "height": 1080,
        "created_at": "2024-01-01 00:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

## 删除文件

删除指定的文件。

**请求**：
```http
DELETE /api/admin/upload/destroy/{id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 文件 ID |

**响应**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**注意事项**：
- 本地存储的文件会从服务器磁盘删除
- 云存储的文件会从云服务商删除
- 缩略图也会一并删除

## 批量删除文件

批量删除多个文件。

**请求**：
```http
DELETE /api/admin/upload/destroy_all
Content-Type: application/json
```

**请求体**：
```json
{
  "id_array": [1, 2, 3, 4, 5]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": null
}
```

## 文件处理规则

### 图片处理

上传图片时，系统会自动进行以下处理：

1. **生成缩略图**：自动生成 200x200 的缩略图
2. **获取尺寸**：自动读取图片的宽度和高度
3. **计算哈希**：计算文件的 SHA256 哈希值，用于去重

### 文件命名规则

文件按以下规则命名：

```
{年月日}/{随机字符串}.{扩展名}
```

例如：`20240101/abc123def456.jpg`

### 文件去重

系统使用文件的 SHA256 哈希值进行去重：

1. 上传文件时计算哈希值
2. 检查数据库中是否已存在相同哈希的文件
3. 如果存在，返回已有文件信息，不重复存储

## 错误响应

### 文件类型不允许

```json
{
  "code": 422,
  "message": "不支持的文件类型",
  "data": {
    "file_type": ["必须是 image/document/video/audio/other 之一"]
  }
}
```

### 文件大小超限

```json
{
  "code": 422,
  "message": "文件大小超过限制",
  "data": {
    "file": ["文件大小不能超过 10485760 字节"]
  }
}
```

### 文件扩展名不允许

```json
{
  "code": 422,
  "message": "不支持的文件扩展名",
  "data": {
    "file": ["不允许上传 .exe 文件"]
  }
}
```

### 存储空间不足

```json
{
  "code": 500,
  "message": "存储空间不足",
  "data": null
}
```

## 注意事项

1. **文件大小限制**：默认最大 10MB，可在系统配置中调整
2. **文件类型限制**：根据 `file_type` 参数限制可上传的文件类型
3. **文件安全**：系统会检查文件扩展名和 MIME 类型
4. **云存储配置**：使用云存储前需要先配置相关参数
5. **URL 访问**：确保上传目录可以被 Web 服务器访问
6. **定期清理**：建议定期清理未使用的文件
7. **备份重要文件**：删除文件前请确认是否需要备份
