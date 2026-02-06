# 上传组件指南

本文档介绍 Py Small Admin 前端的上传组件使用方法。

## 组件架构

```mermaid
graph TB
    A[Upload Components] --> B[ImageUpload]
    A --> C[VideoUpload]
    A --> D[AudioUpload]
    A --> E[DocumentUpload]

    A --> F[MediaLibraryModal]
    F --> G[FileList]
    F --> H[UploadArea]

    B --> I[useSystemUploadConfig]
    C --> I
    D --> I
    E --> I

    B --> J[useFileValidation]
    C --> J
    D --> J
    E --> J
```

## 目录结构

```
src/components/common/Upload/
├── index.ts                  # 导出入口
├── types.ts                  # 类型定义
├── utils.ts                  # 工具函数
├── hooks/
│   ├── useFileValidation.ts
│   ├── useMediaLibrary.ts
│   └── useSystemUploadConfig.ts
├── ImageUpload/
│   └── index.tsx             # 图片上传组件
├── VideoUpload/
│   └── index.tsx             # 视频上传组件
├── AudioUpload/
│   └── index.tsx             # 音频上传组件
├── DocumentUpload/
│   └── index.tsx             # 文档上传组件
└── MediaLibraryModal/
    ├── index.tsx             # 媒体库弹窗
    ├── components/
    │   ├── FileList.tsx      # 文件列表
    │   └── UploadArea.tsx    # 上传区域
    └── hooks/
        └── useMediaLibrary.ts
```

## 图片上传组件

### 1. 基础用法

```typescript
import { ImageUpload } from '@/components/common/Upload';

const MyForm = () => {
  const [imageUrl, setImageUrl] = useState();

  return (
    <Form>
      <Form.Item label="图片">
        <ImageUpload
          value={imageUrl}
          onChange={setImageUrl}
        />
      </Form.Item>
    </Form>
  );
};
```

### 2. 多图上传

```typescript
<ImageUpload
  multiple={true}
  maxCount={9}
  value={images}
  onChange={setImages}
/>
```

### 3. 图片配置

```typescript
interface ImageUploadProps {
  value?: AdminUploadList | AdminUploadList[];
  onChange?: (files?: AdminUploadList | AdminUploadList[]) => void;
  multiple?: boolean;           // 是否多选，默认 false
  maxCount?: number;            // 最大选择数量
  maxSize?: number;             // 文件大小限制（字节）
  showUploadList?: boolean;      // 是否显示上传列表，默认 true
  disabled?: boolean;           // 是否禁用
  maxWidth?: number;            // 图片宽度限制
  maxHeight?: number;           // 图片高度限制
  enableCrop?: boolean;         // 是否启用裁剪
  aspectRatio?: number;         // 裁剪比例
  enableCompress?: boolean;     // 是否启用压缩
  compressQuality?: number;     // 压缩质量（0-1）
  accept?: string;              // 接受的文件类型
}
```

### 4. 自定义渲染

```typescript
<ImageUpload
  value={imageUrl}
  onChange={setImageUrl}
  render={(selectedFiles, openModal) => (
    <div className="custom-upload">
      {selectedFiles.length > 0 ? (
        <img src={selectedFiles[0].url} alt="preview" />
      ) : (
        <Button onClick={openModal}>选择图片</Button>
      )}
    </div>
  )}
/>
```

## 视频上传组件

### 1. 基础用法

```typescript
import { VideoUpload } from '@/components/common/Upload';

const MyForm = () => {
  const [videoUrl, setVideoUrl] = useState();

  return (
    <Form>
      <Form.Item label="视频">
        <VideoUpload
          value={videoUrl}
          onChange={setVideoUrl}
        />
      </Form.Item>
    </Form>
  );
};
```

### 2. 视频配置

```typescript
interface VideoUploadProps {
  value?: AdminUploadList | AdminUploadList[];
  onChange?: (files?: AdminUploadList | AdminUploadList[]) => void;
  multiple?: boolean;
  maxCount?: number;
  maxSize?: number;
  accept?: string;              // 'video/*' | 'video/mp4,video/avi,video/mov'
  maxDuration?: number;        // 视频时长限制（秒）
  maxResolution?: number;      // 视频分辨率限制
  autoUploadCover?: boolean;   // 是否自动上传封面
  coverUpload?: ReactNode;     // 封面上传组件
}
```

### 3. 带封面的视频上传

```typescript
const [cover, setCover] = useState();
const [video, setVideo] = useState();

<VideoUpload
  value={video}
  onChange={setVideo}
  coverUpload={
    <ImageUpload
      value={cover}
      onChange={setCover}
    />
  }
/>
```

## 音频上传组件

### 1. 基础用法

```typescript
import { AudioUpload } from '@/components/common/Upload';

const MyForm = () => {
  const [audioUrl, setAudioUrl] = useState();

  return (
    <Form>
      <Form.Item label="音频">
        <AudioUpload
          value={audioUrl}
          onChange={setAudioUrl}
        />
      </Form.Item>
    </Form>
  );
};
```

### 2. 音频配置

```typescript
interface AudioUploadProps {
  value?: AdminUploadList | AdminUploadList[];
  onChange?: (files?: AdminUploadList | AdminUploadList[]) => void;
  multiple?: boolean;
  maxCount?: number;
  maxSize?: number;
  accept?: string;              // 'audio/*' | 'audio/mp3,audio/wav,audio/m4a'
  maxDuration?: number;        // 音频时长限制（秒）
  showWaveform?: boolean;      // 是否显示波形
  autoPlay?: boolean;          // 是否自动播放
}
```

## 文档上传组件

### 1. 基础用法

```typescript
import { DocumentUpload } from '@/components/common/Upload';

const MyForm = () => {
  const [file, setFile] = useState();

  return (
    <Form>
      <Form.Item label="文档">
        <DocumentUpload
          value={file}
          onChange={setFile}
        />
      </Form.Item>
    </Form>
  );
};
```

### 2. 文档配置

```typescript
interface DocumentUploadProps {
  value?: AdminUploadList | AdminUploadList[];
  onChange?: (files?: AdminUploadList | AdminUploadList[]) => void;
  multiple?: boolean;
  maxCount?: number;
  maxSize?: number;
  accept?: string;              // 支持的文档格式
  showIcon?: boolean;          // 是否显示文件图标
  iconMap?: Record<string, string>;  // 自定义图标映射
}
```

### 3. 多文件上传

```typescript
<DocumentUpload
  multiple={true}
  maxCount={5}
  value={files}
  onChange={setFiles}
  accept=".pdf,.doc,.docx,.xls,.xlsx"
/>
```

## 媒体库弹窗

### 1. 基础用法

```typescript
import { MediaLibraryModal } from '@/components/common/Upload';

const MyPage = () => {
  const [visible, setVisible] = useState(false);

  return (
    <>
      <Button onClick={() => setVisible(true)}>打开媒体库</Button>

      <MediaLibraryModal
        visible={visible}
        onCancel={() => setVisible(false)}
        onConfirm={(files) => {
          console.log('选中的文件:', files);
          setVisible(false);
        }}
        fileType="image"
      />
    </>
  );
};
```

### 2. 媒体库配置

```typescript
interface MediaLibraryModalProps {
  visible: boolean;
  onCancel: () => void;
  onConfirm: (selectedFiles: AdminUploadList[]) => void;
  fileType: FileType;         // 'image' | 'document' | 'video' | 'audio'
  multiple?: boolean;         // 是否多选
  maxCount?: number;          // 最大选择数量
  defaultSelectedIds?: number[];
  maxSize?: number;
  accept?: string;
}
```

## 系统上传配置

### 1. 获取系统配置

```typescript
import { useSystemUploadConfig } from '@/components/common/Upload';

const MyComponent = () => {
  // 获取图片上传配置
  const imageConfig = useSystemUploadConfig('image');
  // 返回: { maxSize: number, accept: string }

  // 获取视频上传配置
  const videoConfig = useSystemUploadConfig('video');

  // 获取音频上传配置
  const audioConfig = useSystemUploadConfig('audio');

  // 获取文档上传配置
  const documentConfig = useSystemUploadConfig('document');

  return (
    <div>
      <p>图片最大大小: {imageConfig.maxSize / 1024 / 1024} MB</p>
      <p>支持的格式: {imageConfig.accept}</p>
    </div>
  );
};
```

### 2. 配置数据结构

```typescript
interface UploadConfig {
  // 存储类型
  upload_storage_type: 'local' | 'aliyun_oss' | 'tencent_oss' | 'qiniu_oss';

  // 图片配置
  upload_image_max_size: number;        // MB
  upload_image_allowed_types: string[];

  // 视频配置
  upload_video_max_size: number;        // MB
  upload_video_allowed_types: string[];

  // 文档配置
  upload_document_max_size: number;     // MB
  upload_document_allowed_types: string[];

  // 音频配置
  upload_audio_max_size: number;        // MB
  upload_audio_allowed_types: string[];
}
```

## 文件验证

### 1. 使用验证 Hook

```typescript
import { useFileValidation } from '@/components/common/Upload';

const MyUpload = () => {
  const { validateFile, getErrorMessage } = useFileValidation({
    maxSize: 5 * 1024 * 1024,  // 5MB
    accept: 'image/jpeg,image/png',
  });

  const handleFileChange = (file: File) => {
    const valid = validateFile(file);
    if (!valid) {
      message.error(getErrorMessage());
      return false;
    }
    return true;
  };

  return (
    <Upload beforeUpload={handleFileChange}>
      <Button>上传文件</Button>
    </Upload>
  );
};
```

### 2. 自定义验证规则

```typescript
const { validateFile } = useFileValidation({
  maxSize: 10 * 1024 * 1024,
  accept: 'image/*',
  customRules: [
    {
      validate: (file) => {
        return file.size > 0;
      },
      message: '文件大小不能为 0',
    },
    {
      validate: (file) => {
        const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
        return validTypes.includes(file.type);
      },
      message: '只支持 JPEG、PNG、GIF 格式',
    },
  ],
});
```

## 完整示例

### 1. 文章编辑表单

```typescript
import { Form, Input, Button } from 'antd';
import { ImageUpload, VideoUpload, DocumentUpload } from '@/components/common/Upload';

const ArticleForm = () => {
  const [form] = Form.useForm();

  const handleSubmit = async (values) => {
    console.log('表单数据:', values);
    // 提交逻辑
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
    >
      <Form.Item
        label="封面图片"
        name="cover_image"
        rules={[{ required: true, message: '请上传封面图片' }]}
      >
        <ImageUpload />
      </Form.Item>

      <Form.Item
        label="文章图集"
        name="images"
      >
        <ImageUpload
          multiple={true}
          maxCount={9}
        />
      </Form.Item>

      <Form.Item
        label="视频"
        name="video"
      >
        <VideoUpload />
      </Form.Item>

      <Form.Item
        label="附件"
        name="attachments"
      >
        <DocumentUpload
          multiple={true}
          maxCount={5}
        />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">
          提交
        </Button>
      </Form.Item>
    </Form>
  );
};
```

### 2. 产品编辑表单

```typescript
import { Form, Input, Select, Button } from 'antd';
import { ImageUpload } from '@/components/common/Upload';

const ProductForm = ({ isEdit, initialValues }) => {
  const [form] = Form.useForm();

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
    >
      <Form.Item
        label="产品名称"
        name="name"
        rules={[{ required: true }]}
      >
        <Input placeholder="请输入产品名称" />
      </Form.Item>

      <Form.Item
        label="主图"
        name="main_image"
        rules={[{ required: true, message: '请上传产品主图' }]}
      >
        <ImageUpload
          aspectRatio={1}
          enableCompress={true}
          compressQuality={0.8}
        />
      </Form.Item>

      <Form.Item
        label="产品图集"
        name="gallery"
        rules={[{ required: true, message: '请上传至少一张产品图片' }]}
      >
        <ImageUpload
          multiple={true}
          maxCount={5}
          aspectRatio={1}
          enableCompress={true}
        />
      </Form.Item>

      <Form.Item
        label="产品详情图"
        name="detail_images"
      >
        <ImageUpload
          multiple={true}
          maxCount={10}
        />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">
          保存产品
        </Button>
      </Form.Item>
    </Form>
  );
};
```

### 3. 自定义上传组件

```typescript
import { Button, Space } from 'antd';
import { ImageUpload } from '@/components/common/Upload';

const CustomImageUpload = () => {
  const [images, setImages] = useState([]);

  const handleUploadSuccess = (files) => {
    setImages(files);
  };

  return (
    <Space direction="vertical" size="middle">
      <ImageUpload
        value={images}
        onChange={handleUploadSuccess}
        multiple={true}
        maxCount={3}
        render={(selectedFiles, openModal) => (
          <div className="custom-upload-area">
            {selectedFiles.length === 0 ? (
              <div className="upload-placeholder" onClick={openModal}>
                <PlusOutlined />
                <p>点击上传图片</p>
                <p className="hint">最多上传 3 张图片，支持 JPG、PNG 格式</p>
              </div>
            ) : (
              <div className="uploaded-files">
                {selectedFiles.map((file, index) => (
                  <div key={file.id} className="file-item">
                    <img src={file.url} alt={file.original_name} />
                    <div className="file-actions">
                      <Button
                        type="link"
                        onClick={() => {
                          const newFiles = [...selectedFiles];
                          newFiles.splice(index, 1);
                          setImages(newFiles);
                        }}
                      >
                        删除
                      </Button>
                    </div>
                  </div>
                ))}
                {selectedFiles.length < 3 && (
                  <div className="add-more" onClick={openModal}>
                    <PlusOutlined />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      />
    </Space>
  );
};
```

## 类型定义

### 文件数据类型

```typescript
interface AdminUploadList {
  id: number;
  url: string;                    // 文件访问地址
  thumbnail_url: string;          // 缩略图地址
  original_name: string;          // 原始文件名
  filename: string;               // 存储文件名
  file_path: string;              // 文件路径
  file_size: number;              // 文件大小（字节）
  mime_type: string;              // MIME 类型
  file_ext: string;               // 文件扩展名
  file_hash: string;              // 文件哈希
  storage_type: string;           // 存储类型
  file_type: string;              // 文件类型
  admin_id: number;               // 上传管理员 ID
  width: number;                  // 图片/视频宽度
  height: number;                 // 图片/视频高度
  duration: number;               // 音频/视频时长
  thumbnail_filename: string;     // 缩略图文件名
  thumbnail_path: string;          // 缩略图路径
  extra_info: string;             // 额外信息
  created_at: string;             // 创建时间
}
```

## 最佳实践

### 1. 预加载配置

```typescript
// 在应用启动时获取上传配置
const App = () => {
  const [uploadConfig, setUploadConfig] = useState<UploadConfig>();

  useEffect(() => {
    const fetchConfig = async () => {
      const config = await getSystemConfig();
      setUploadConfig(config.data.upload_config);
    };
    fetchConfig();
  }, []);

  return (
    <UploadConfigContext.Provider value={uploadConfig}>
      {/* 应用内容 */}
    </UploadConfigContext.Provider>
  );
};
```

### 2. 统一错误处理

```typescript
const handleUploadError = (error: Error) => {
  if (error.message.includes('file too large')) {
    message.error('文件太大，请上传小于 5MB 的文件');
  } else if (error.message.includes('invalid type')) {
    message.error('文件格式不支持');
  } else {
    message.error('上传失败，请重试');
  }
};
```

### 3. 上传进度显示

```typescript
const [uploadProgress, setUploadProgress] = useState(0);

<Upload
  beforeUpload={(file) => {
    const formData = new FormData();
    formData.append('file', file);

    uploadFile(formData, {
      onUploadProgress: (progress) => {
        setUploadProgress(progress);
      },
    });
    return false;
  }}
>
  <Button>上传</Button>
</Upload>

<Progress percent={uploadProgress} />
```

### 4. 图片压缩配置

```typescript
<ImageUpload
  enableCompress={true}
  compressQuality={0.8}
  maxWidth={1920}
  maxHeight={1080}
  value={image}
  onChange={setImage}
/>
```
