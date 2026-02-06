# 文件上传

本文档介绍了项目的文件上传功能。

## 简介

项目支持多种文件上传方式，包括本地存储和云存储（七牛云、阿里云 OSS、腾讯云 COS）。

## 基础使用

### 上传接口

```python
from fastapi import UploadFile, File

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    from Modules.common.libs.upload.upload_lib import upload_handler

    result = await upload_handler.upload(file)
    return {
        "code": 200,
        "message": "上传成功",
        "data": result
    }
```

### 上传响应

```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "https://cdn.example.com/uploads/image.jpg",
    "path": "uploads/2024/01/01/abc123.jpg",
    "filename": "image.jpg",
    "size": 102400,
    "mime_type": "image/jpeg"
  }
}
```

## 上传配置

### 环境变量配置

```env
# 上传驱动：local, qiniu, aliyun, tencent
UPLOAD_DRIVER=local

# 本地存储配置
UPLOAD_PATH=./uploads
UPLOAD_URL_PREFIX=/uploads

# 文件大小限制（字节）
UPLOAD_MAX_SIZE=10485760

# 允许的文件类型
UPLOAD_ALLOWED_TYPES=jpg,jpeg,png,gif,pdf,doc,docx
```

### 七牛云配置

```env
UPLOAD_DRIVER=qiniu
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET=your_bucket
QINIU_DOMAIN=https://cdn.example.com
```

### 阿里云 OSS 配置

```env
UPLOAD_DRIVER=aliyun
ALIYUN_OSS_ACCESS_KEY_ID=your_access_key_id
ALIYUN_OSS_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_OSS_BUCKET=your_bucket
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_DOMAIN=https://cdn.example.com
```

### 腾讯云 COS 配置

```env
UPLOAD_DRIVER=tencent
TENCENT_COS_SECRET_ID=your_secret_id
TENCENT_COS_SECRET_KEY=your_secret_key
TENCENT_COS_BUCKET=your_bucket-1234567890
TENCENT_COS_REGION=ap-guangzhou
TENCENT_COS_DOMAIN=https://cdn.example.com
```

## 上传处理器

### 基础使用

```python
from Modules.common.libs.upload.upload_lib import upload_handler

# 上传文件
result = await upload_handler.upload(file)

# 获取存储类型
storage_type = upload_handler.get_storage_type()  # local/qiniu/aliyun/tencent
```

### 图片处理

```python
from Modules.common.libs.upload.image_processor import ImageProcessor

# 创建图片处理器
processor = ImageProcessor()

# 生成缩略图
thumbnail = await processor.create_thumbnail(file, size=(200, 200))

# 添加水印
watermarked = await processor.add_watermark(file, text="© 2024")

# 压缩图片
compressed = await processor.compress(file, quality=85)
```

### 文件验证

```python
from Modules.common.libs.upload.validator import FileValidator

# 创建验证器
validator = FileValidator()

# 验证文件类型
is_valid = validator.validate_type(file, allowed_types=["jpg", "png", "gif"])

# 验证文件大小
is_valid = validator.validate_size(file, max_size=10 * 1024 * 1024)  # 10MB

# 验证图片尺寸
width, height = validator.get_image_dimensions(file)
```

## 前端上传

### 基础上传

```typescript
import { upload } from '@/services/upload';

async function handleUpload(file: File) {
  const result = await upload(file);
  console.log(result.url);
}
```

### 使用 Ant Design Upload

```tsx
import { Upload } from 'antd';
import type { UploadProps } from 'antd';

const props: UploadProps = {
  name: 'file',
  action: '/api/upload',
  headers: {
    authorization: `Bearer ${token}`,
  },
  onChange(info) {
    if (info.file.status === 'done') {
      console.log(info.file.response.data.url);
    }
  },
};

<Upload {...props}>
  <Button>上传文件</Button>
</Upload>
```

### 自定义上传组件

```tsx
import { Upload, message } from 'antd';

function ImageUpload({ value, onChange }) {
  const handleUpload = async (file) => {
    try {
      const result = await upload(file);
      onChange(result.url);
      return false;
    } catch (error) {
      message.error('上传失败');
      return false;
    }
  };

  return (
    <Upload
      listType="picture-card"
      beforeUpload={handleUpload}
      showUploadList={false}
    >
      {value ? <img src={value} alt="" /> : <div>上传图片</div>}
    </Upload>
  );
}
```

## 上传安全

### 文件类型验证

```python
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}

def validate_file_type(filename: str) -> bool:
    """验证文件扩展名"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
```

### MIME 类型验证

```python
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/pdf",
}

def validate_mime_type(file: UploadFile) -> bool:
    """验证 MIME 类型"""
    return file.content_type in ALLOWED_MIME_TYPES
```

### 文件名处理

```python
import uuid
from pathlib import Path

def generate_filename(original_filename: str) -> str:
    """生成安全的文件名"""
    # 获取扩展名
    ext = Path(original_filename).suffix

    # 生成唯一文件名
    filename = f"{uuid.uuid4().hex}{ext}"

    # 添加日期路径
    date_path = datetime.now().strftime("%Y/%m/%d")

    return f"{date_path}/{filename}"
```

## 上传最佳实践

### 1. 使用异步上传

```python
# 使用 Celery 异步处理上传
@celery_app().task
def process_upload(file_path: str):
    """异步处理上传文件"""
    # 图片压缩、水印等
    pass
```

### 2. 分片上传

```python
# 大文件分片上传
CHUNK_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/api/upload/chunk")
async def upload_chunk(
    chunk: UploadFile,
    chunk_index: int,
    file_id: str
):
    """上传文件分片"""
    # 保存分片
    save_chunk(chunk, file_id, chunk_index)
```

### 3. 进度反馈

```python
async def upload_with_progress(file: UploadFile):
    """带进度的上传"""
    total_size = file.size
    uploaded = 0

    with open(file_path, "wb") as f:
        while content := await file.read(1024 * 1024):
            f.write(content)
            uploaded += len(content)
            progress = uploaded / total_size * 100
            # 发送进度
            await send_progress(progress)
```

## 相关文档

- [前端上传组件](../../frontend/components/upload-comps.md)
- [配置指南](../config/index.md)
