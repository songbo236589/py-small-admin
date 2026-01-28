# Upload 组件使用文档

## 📋 目录

- [一、组件概述](#一组件概述)
- [二、快速开始](#二快速开始)
- [三、组件使用](#三组件使用)
  - [3.1 ImageUpload 图片上传](#31-imageupload-图片上传)
  - [3.2 DocumentUpload 文档上传](#32-documentupload-文档上传)
  - [3.3 VideoUpload 视频上传](#33-videoupload-视频上传)
  - [3.4 AudioUpload 音频上传](#34-audioupload-音频上传)
- [四、API 文档](#四api-文档)
- [五、高级用法](#五高级用法)
- [六、常见问题](#六常见问题)

---

## 一、组件概述

Upload 组件会自动从系统配置中获取文件大小限制和允许的文件类型。使用时无需手动传入配置，组件会自动读取 `initialState.systemConfig.upload` 中的配置。

**注意：** 如果需要覆盖系统配置，可以通过 props 传入 `maxSize` 和 `accept`，props 的优先级高于系统配置。

### 核心特性

- ✅ **媒体库弹窗** - 统一的文件选择和上传界面
- ✅ **文件列表展示** - 网格/列表布局展示已上传的文件
- ✅ **文件上传** - 支持拖拽上传、点击上传
- ✅ **文件预览** - 支持图片、视频、音频预览
- ✅ **单选/多选** - 灵活的选择模式
- ✅ **文件验证** - 文件类型、大小、数量验证
- ✅ **受控组件** - 支持 value/onChange 模式
- ✅ **自动配置** - 自动从系统配置获取文件大小和类型限制

### 组件列表

| 组件名           | 功能说明     | 默认大小限制 |
| ---------------- | ------------ | ------------ |
| `ImageUpload`    | 图片上传组件 | 5MB          |
| `DocumentUpload` | 文档上传组件 | 10MB         |
| `VideoUpload`    | 视频上传组件 | 50MB         |
| `AudioUpload`    | 音频上传组件 | 20MB         |

---

## 二、快速开始

### 2.1 导入组件

```typescript
import { ImageUpload, DocumentUpload, VideoUpload, AudioUpload } from '@/components';
```

### 2.2 基础使用（自动获取系统配置）

```typescript
import { ImageUpload } from '@/components';

const MyComponent = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);

  return (
    <ImageUpload
      value={images}
      onChange={(files) => {
        if (!files) {
          setImages([]);
        } else if (Array.isArray(files)) {
          setImages(files);
        } else {
          setImages([files]);
        }
      }}
    />
  );
};
```

**说明：** 组件会自动从 `initialState.systemConfig.upload` 中获取配置，无需手动传入。

### 2.3 覆盖系统配置

如果需要使用自定义配置，可以通过 props 传入：

```typescript
import { ImageUpload } from '@/components';

const MyComponent = () => {
  return (
    <ImageUpload
      value={images}
      onChange={setImages}
      maxSize={20 * 1024 * 1024} // 自定义大小限制为 20MB
      accept=".jpg,.png" // 自定义文件类型
    />
  );
};
```

**说明：** props 传入的配置优先级高于系统配置。

---

## 三、组件使用

### 3.1 ImageUpload 图片上传

#### 基础用法

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [image, setImage] = useState<API.AdminUploadList>();

  return (
    <div>
      <h3>单图上传</h3>
      <ImageUpload value={image} onChange={setImage} />
    </div>
  );
};
```

#### 多图上传

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>多图上传（最多5张）</h3>
      <ImageUpload multiple maxCount={5} value={images} onChange={setImages} />
    </div>
  );
};
```

#### 自定义文件大小

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>限制文件大小为 10MB</h3>
      <ImageUpload
        multiple
        maxCount={10}
        maxSize={10 * 1024 * 1024} // 10MB
        value={images}
        onChange={setImages}
      />
    </div>
  );
};
```

#### 自定义渲染

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>自定义渲染</h3>
      <ImageUpload
        value={images}
        onChange={setImages}
        render={(selectedFiles, openModal) => (
          <div className="custom-image-uploader">
            <div className="image-grid">
              {selectedFiles.map((file) => (
                <div key={file.id} className="image-item">
                  <img src={file.file_path} alt={file.original_name} />
                  <div className="image-actions">
                    <span>{file.original_name}</span>
                  </div>
                </div>
              ))}
            </div>
            <button onClick={openModal} className="upload-btn">
              + 添加图片
            </button>
          </div>
        )}
      />
    </div>
  );
};
```

#### 禁用状态

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);
  const [disabled, setDisabled] = useState(false);

  return (
    <div>
      <h3>禁用上传</h3>
      <ImageUpload disabled={disabled} value={images} onChange={setImages} />
      <button onClick={() => setDisabled(!disabled)}>{disabled ? '启用' : '禁用'}</button>
    </div>
  );
};
```

---

### 3.2 DocumentUpload 文档上传

#### 基础用法

```typescript
import { DocumentUpload } from '@/components';

const Demo = () => {
  const [document, setDocument] = useState<API.AdminUploadList>();

  return (
    <div>
      <h3>单文档上传</h3>
      <DocumentUpload value={document} onChange={setDocument} />
    </div>
  );
};
```

#### 多文档上传

```typescript
import { DocumentUpload } from '@/components';

const Demo = () => {
  const [documents, setDocuments] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>多文档上传（最多10个）</h3>
      <DocumentUpload multiple maxCount={10} value={documents} onChange={setDocuments} />
    </div>
  );
};
```

#### 自定义文件大小

```typescript
import { DocumentUpload } from '@/components';

const Demo = () => {
  const [documents, setDocuments] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>限制文件大小为 20MB</h3>
      <DocumentUpload
        multiple
        maxSize={20 * 1024 * 1024} // 20MB
        value={documents}
        onChange={setDocuments}
      />
    </div>
  );
};
```

---

### 3.3 VideoUpload 视频上传

#### 基础用法

```typescript
import { VideoUpload } from '@/components';

const Demo = () => {
  const [video, setVideo] = useState<API.AdminUploadList>();

  return (
    <div>
      <h3>单视频上传</h3>
      <VideoUpload value={video} onChange={setVideo} />
    </div>
  );
};
```

#### 多视频上传

```typescript
import { VideoUpload } from '@/components';

const Demo = () => {
  const [videos, setVideos] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>多视频上传（最多3个）</h3>
      <VideoUpload multiple maxCount={3} value={videos} onChange={setVideos} />
    </div>
  );
};
```

#### 自定义文件大小

```typescript
import { VideoUpload } from '@/components';

const Demo = () => {
  const [videos, setVideos] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>限制文件大小为 100MB</h3>
      <VideoUpload
        multiple
        maxSize={100 * 1024 * 1024} // 100MB
        value={videos}
        onChange={setVideos}
      />
    </div>
  );
};
```

---

### 3.4 AudioUpload 音频上传

#### 基础用法

```typescript
import { AudioUpload } from '@/components';

const Demo = () => {
  const [audio, setAudio] = useState<API.AdminUploadList>();

  return (
    <div>
      <h3>单音频上传</h3>
      <AudioUpload value={audio} onChange={setAudio} />
    </div>
  );
};
```

#### 多音频上传

```typescript
import { AudioUpload } from '@/components';

const Demo = () => {
  const [audios, setAudios] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>多音频上传（最多5个）</h3>
      <AudioUpload multiple maxCount={5} value={audios} onChange={setAudios} />
    </div>
  );
};
```

#### 自定义文件大小

```typescript
import { AudioUpload } from '@/components';

const Demo = () => {
  const [audios, setAudios] = useState<API.AdminUploadList[]>([]);

  return (
    <div>
      <h3>限制文件大小为 50MB</h3>
      <AudioUpload
        multiple
        maxSize={50 * 1024 * 1024} // 50MB
        value={audios}
        onChange={setAudios}
      />
    </div>
  );
};
```

---

## 四、API 文档

### 4.1 BaseUploadProps（基础属性）

所有上传组件都支持以下基础属性：

| 属性名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `value` | `AdminUploadList \| AdminUploadList[]` | - | 已选文件 |
| `onChange` | `(files?: AdminUploadList \| AdminUploadList[]) => void` | - | 值变化回调 |
| `multiple` | `boolean` | `false` | 是否多选 |
| `maxCount` | `number` | - | 最大选择数量 |
| `maxSize` | `number` | 系统配置或默认值 | 文件大小限制（字节） |
| `accept` | `string` | 系统配置或默认值 | 文件类型限制 |
| `showUploadList` | `boolean` | `true` | 是否显示上传列表 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `render` | `(selectedFiles: AdminUploadList[], openModal: () => void) => ReactNode` | - | 自定义渲染 |

### 4.2 ImageUpload

图片上传组件，继承自 `BaseUploadProps`。

| 属性名    | 类型     | 默认值            | 说明                     |
| --------- | -------- | ----------------- | ------------------------ |
| `maxSize` | `number` | `5 * 1024 * 1024` | 文件大小限制（默认 5MB） |
| `accept`  | `string` | `'image/*'`       | 文件类型限制             |

**示例：**

```typescript
<ImageUpload multiple maxCount={5} maxSize={10 * 1024 * 1024} value={images} onChange={setImages} />
```

### 4.3 DocumentUpload

文档上传组件，继承自 `BaseUploadProps`。

| 属性名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `maxSize` | `number` | `10 * 1024 * 1024` | 文件大小限制（默认 10MB） |
| `accept` | `string` | `'.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt'` | 文件类型限制 |

**示例：**

```typescript
<DocumentUpload
  multiple
  maxCount={10}
  maxSize={20 * 1024 * 1024}
  value={documents}
  onChange={setDocuments}
/>
```

### 4.4 VideoUpload

视频上传组件，继承自 `BaseUploadProps`。

| 属性名    | 类型     | 默认值             | 说明                      |
| --------- | -------- | ------------------ | ------------------------- |
| `maxSize` | `number` | `50 * 1024 * 1024` | 文件大小限制（默认 50MB） |
| `accept`  | `string` | `'video/*'`        | 文件类型限制              |

**示例：**

```typescript
<VideoUpload
  multiple
  maxCount={3}
  maxSize={100 * 1024 * 1024}
  value={videos}
  onChange={setVideos}
/>
```

### 4.5 AudioUpload

音频上传组件，继承自 `BaseUploadProps`。

| 属性名    | 类型     | 默认值             | 说明                      |
| --------- | -------- | ------------------ | ------------------------- |
| `maxSize` | `number` | `20 * 1024 * 1024` | 文件大小限制（默认 20MB） |
| `accept`  | `string` | `'audio/*'`        | 文件类型限制              |

**示例：**

```typescript
<AudioUpload multiple maxCount={5} maxSize={50 * 1024 * 1024} value={audios} onChange={setAudios} />
```

---

## 五、高级用法

### 5.1 表单集成

```typescript
import { Form } from 'antd';
import { ImageUpload, DocumentUpload, VideoUpload, AudioUpload } from '@/components';

const Demo = () => {
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('表单值:', values);
  };

  return (
    <Form form={form} onFinish={onFinish}>
      {/* 图片上传 */}
      <Form.Item name="avatar" label="头像" rules={[{ required: true, message: '请选择头像' }]}>
        <ImageUpload maxCount={1} />
      </Form.Item>

      {/* 产品图片 */}
      <Form.Item
        name="images"
        label="产品图片"
        rules={[{ required: true, message: '请选择产品图片' }]}
      >
        <ImageUpload multiple maxCount={5} />
      </Form.Item>

      {/* 附件文档 */}
      <Form.Item name="documents" label="附件文档">
        <DocumentUpload multiple maxCount={10} />
      </Form.Item>

      {/* 产品视频 */}
      <Form.Item name="video" label="产品视频">
        <VideoUpload maxCount={1} />
      </Form.Item>

      {/* 背景音乐 */}
      <Form.Item name="audio" label="背景音乐">
        <AudioUpload maxCount={1} />
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

### 5.2 动态设置 maxCount

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);
  const [maxCount, setMaxCount] = useState(5);

  return (
    <div>
      <h3>动态设置最大数量</h3>
      <Space>
        <span>最大数量:</span>
        <InputNumber
          min={1}
          max={10}
          value={maxCount}
          onChange={(value) => setMaxCount(value || 5)}
        />
      </Space>
      <ImageUpload multiple maxCount={maxCount} value={images} onChange={setImages} />
    </div>
  );
};
```

### 5.3 条件禁用

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);
  const [isReadOnly, setIsReadOnly] = useState(false);

  return (
    <div>
      <h3>条件禁用</h3>
      <Switch
        checked={isReadOnly}
        onChange={setIsReadOnly}
        checkedChildren="只读"
        unCheckedChildren="编辑"
      />
      <ImageUpload disabled={isReadOnly} value={images} onChange={setImages} />
    </div>
  );
};
```

### 5.4 获取文件信息

```typescript
import { ImageUpload } from '@/components';

const Demo = () => {
  const [images, setImages] = useState<API.AdminUploadList[]>([]);

  const handleChange = (files?: API.AdminUploadList | API.AdminUploadList[]) => {
    console.log('选中的文件:', files);

    // 如果是数组（多选）
    if (Array.isArray(files)) {
      files.forEach((file) => {
        console.log('文件名:', file.original_name);
        console.log('文件大小:', (file.file_size / 1024).toFixed(2), 'KB');
        console.log('文件路径:', file.file_path);
        console.log('文件类型:', file.file_ext);
      });
    }

    setImages(files as API.AdminUploadList[]);
  };

  return (
    <div>
      <h3>获取文件信息</h3>
      <ImageUpload multiple value={images} onChange={handleChange} />
    </div>
  );
};
```

### 5.5 完整示例 - 产品管理

```typescript
import { Form, Button, Space, message } from 'antd';
import { ImageUpload, DocumentUpload, VideoUpload } from '@/components';

interface ProductFormValues {
  name: string;
  coverImage: API.AdminUploadList;
  detailImages: API.AdminUploadList[];
  manual: API.AdminUploadList;
  video: API.AdminUploadList;
}

const ProductForm = () => {
  const [form] = Form.useForm<ProductFormValues>();

  const onFinish = async (values: ProductFormValues) => {
    try {
      // 提交数据到后端
      console.log('提交的数据:', values);
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  return (
    <Form form={form} layout="vertical" onFinish={onFinish}>
      <Form.Item
        name="name"
        label="产品名称"
        rules={[{ required: true, message: '请输入产品名称' }]}
      >
        <Input placeholder="请输入产品名称" />
      </Form.Item>

      {/* 封面图 - 单图 */}
      <Form.Item
        name="coverImage"
        label="封面图"
        rules={[{ required: true, message: '请选择封面图' }]}
      >
        <ImageUpload maxCount={1} />
      </Form.Item>

      {/* 详情图 - 多图 */}
      <Form.Item
        name="detailImages"
        label="详情图"
        rules={[{ required: true, message: '请至少选择一张详情图' }]}
      >
        <ImageUpload multiple maxCount={9} />
      </Form.Item>

      {/* 产品说明书 - 单文档 */}
      <Form.Item name="manual" label="产品说明书">
        <DocumentUpload maxCount={1} />
      </Form.Item>

      {/* 产品视频 - 单视频 */}
      <Form.Item name="video" label="产品视频">
        <VideoUpload maxCount={1} />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit">
            保存
          </Button>
          <Button onClick={() => form.resetFields()}>重置</Button>
        </Space>
      </Form.Item>
    </Form>
  );
};
```

---

## 六、常见问题

### Q1: 如何获取上传文件的 URL？

A: 通过 `file.file_path` 获取文件 URL：

```typescript
<ImageUpload
  value={images}
  onChange={(files) => {
    if (Array.isArray(files)) {
      files.forEach((file) => {
        console.log('文件 URL:', file.file_path);
      });
    }
  }}
/>
```

### Q2: 如何限制文件类型？

A: 组件内部已经根据文件类型进行了限制：

- `ImageUpload` - 只允许图片类型
- `DocumentUpload` - 只允许文档类型
- `VideoUpload` - 只允许视频类型
- `AudioUpload` - 只允许音频类型

### Q3: 如何自定义文件大小限制？

A: 通过 `maxSize` 属性设置（单位：字节）：

```typescript
// 限制为 10MB
<ImageUpload maxSize={10 * 1024 * 1024} />
```

### Q4: 如何禁用上传组件？

A: 通过 `disabled` 属性设置：

```typescript
<ImageUpload disabled={true} />
```

### Q5: 如何在表单中使用？

A: 配合 Ant Design Form 组件使用：

```typescript
<Form.Item name="image" label="图片">
  <ImageUpload />
</Form.Item>
```

### Q6: 如何实现单选？

A: 不设置 `multiple` 属性或设置为 `false`：

```typescript
<ImageUpload multiple={false} />
```

### Q7: 如何限制选择数量？

A: 通过 `maxCount` 属性设置：

```typescript
<ImageUpload multiple maxCount={5} />
```

### Q8: 如何隐藏上传列表？

A: 通过 `showUploadList` 属性设置：

```typescript
<ImageUpload showUploadList={false} />
```

### Q9: 如何自定义渲染？

A: 通过 `render` 属性自定义渲染逻辑：

```typescript
<ImageUpload
  render={(selectedFiles, openModal) => (
    <div>
      {selectedFiles.map((file) => (
        <img key={file.id} src={file.file_path} />
      ))}
      <button onClick={openModal}>选择图片</button>
    </div>
  )}
/>
```

### Q10: 如何获取文件的其他信息？

A: `AdminUploadList` 类型包含以下信息：

```typescript
interface AdminUploadList {
  id: number; // 文件 ID
  original_name: string; // 原始文件名
  filename: string; // 存储文件名
  file_path: string; // 文件路径
  file_size: number; // 文件大小（字节）
  mime_type: string; // MIME 类型
  file_ext: string; // 文件扩展名
  file_hash: string | null; // 文件哈希值
  storage_type: string; // 存储类型
  file_type: string; // 文件类型
  width: number; // 宽度（图片/视频）
  height: number; // 高度（图片/视频）
  duration: number; // 时长（视频/音频，秒）
  thumbnail_path: string | null; // 缩略图路径
  created_at: string; // 创建时间
}
```

### Q11: 组件如何自动获取系统配置？

A: 组件会自动从 `initialState.systemConfig.upload` 中读取配置，包括：

- `upload_image_max_size` - 图片最大大小（MB）
- `upload_image_allowed_types` - 图片允许的文件类型
- `upload_video_max_size` - 视频最大大小（MB）
- `upload_video_allowed_types` - 视频允许的文件类型
- `upload_document_max_size` - 文档最大大小（MB）
- `upload_document_allowed_types` - 文档允许的文件类型
- `upload_audio_max_size` - 音频最大大小（MB）
- `upload_audio_allowed_types` - 音频允许的文件类型

### Q12: 如何覆盖系统配置？

A: 通过 props 传入 `maxSize` 和 `accept`，props 的优先级高于系统配置：

```typescript
<ImageUpload
  maxSize={20 * 1024 * 1024} // 覆盖系统配置
  accept=".jpg,.png" // 覆盖系统配置
/>
```

---

## 更新日志

| 版本  | 日期       | 说明                                     |
| ----- | ---------- | ---------------------------------------- |
| 1.0.0 | 2025-12-31 | 初始版本，支持四种文件类型上传           |
| 1.1.0 | 2025-12-31 | 更新使用文档，添加详细使用示例           |
| 1.2.0 | 2025-12-31 | 支持自动从系统配置获取文件大小和类型限制 |

---

## 技术支持

如有问题，请联系开发团队或提交 Issue。
