import type { ReactNode } from 'react';

/**
 * 上传配置类型
 */
export interface UploadConfig {
  /** 存储类型 */
  upload_storage_type: 'local' | 'aliyun_oss' | 'tencent_oss' | 'qiniu_oss';
  /** 图片最大大小（MB） */
  upload_image_max_size: number;
  /** 图片允许的文件类型 */
  upload_image_allowed_types: string[];
  /** 视频最大大小（MB） */
  upload_video_max_size: number;
  /** 视频允许的文件类型 */
  upload_video_allowed_types: string[];
  /** 文档最大大小（MB） */
  upload_document_max_size: number;
  /** 文档允许的文件类型 */
  upload_document_allowed_types: string[];
  /** 音频最大大小（MB） */
  upload_audio_max_size: number;
  /** 音频允许的文件类型 */
  upload_audio_allowed_types: string[];
}

/**
 * 文件列表项类型
 */
export interface AdminUploadList {
  id: number;
  url: string;
  thumbnail_url: string;
  original_name: string;
  filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  file_ext: string;
  file_hash: string | null;
  storage_type: 'local' | 'aliyun_oss' | 'tencent_oss' | 'qiniu_oss';
  file_type: 'image' | 'document' | 'video' | 'audio' | 'other';
  admin_id: number | null;
  width: number;
  height: number;
  duration: number;
  thumbnail_filename: string | null;
  thumbnail_path: string | null;
  extra_info: string | null;
  created_at: string;
}

/**
 * 上传文件参数类型
 */
export interface AdminUploadFile {
  file_type: 'image' | 'document' | 'video' | 'audio' | 'other';
  file: File;
}

/**
 * 列表请求参数类型
 */
export interface ListRequest {
  page?: number;
  limit?: number;
  file_type?: 'image' | 'document' | 'video' | 'audio' | 'other';
  keyword?: string;
}

/**
 * 文件类型枚举
 */
export type FileType = 'image' | 'document' | 'video' | 'audio';

/**
 * 基础上传组件 Props
 */
export interface BaseUploadProps {
  /** 已选文件 */
  value?: AdminUploadList | AdminUploadList[];
  /** 值变化回调 */
  onChange?: (files?: AdminUploadList | AdminUploadList[]) => void;
  /** 是否多选（默认 false） */
  multiple?: boolean;
  /** 最大选择数量 */
  maxCount?: number;
  /** 文件大小限制（字节） */
  maxSize?: number;
  /** 是否显示上传列表（默认 true） */
  showUploadList?: boolean;
  /** 是否禁用（默认 false） */
  disabled?: boolean;
  /** 自定义渲染 */
  render?: (selectedFiles: AdminUploadList[], openModal: () => void) => ReactNode;
}

/**
 * 图片上传组件 Props
 */
export interface ImageUploadProps extends BaseUploadProps {
  /** 图片宽度限制 */
  maxWidth?: number;
  /** 图片高度限制 */
  maxHeight?: number;
  /** 是否启用裁剪 */
  enableCrop?: boolean;
  /** 裁剪比例 */
  aspectRatio?: number;
  /** 是否启用压缩 */
  enableCompress?: boolean;
  /** 压缩质量（0-1） */
  compressQuality?: number;
  /** 支持的图片格式 */
  accept?: 'image/*' | 'image/jpeg,image/png,image/gif';
  /** 文件大小限制（字节）默认 5MB */
  maxSize?: number;
}

/**
 * 文档上传组件 Props
 */
export interface DocumentUploadProps extends BaseUploadProps {
  /** 支持的文档格式 */
  accept?: string;
  /** 是否显示文件图标 */
  showIcon?: boolean;
  /** 自定义图标映射 */
  iconMap?: Record<string, string>;
  /** 文件大小限制（字节）默认 10MB */
  maxSize?: number;
}

/**
 * 视频上传组件 Props
 */
export interface VideoUploadProps extends BaseUploadProps {
  /** 支持的视频格式 */
  accept?: 'video/*' | 'video/mp4,video/avi,video/mov';
  /** 视频时长限制（秒） */
  maxDuration?: number;
  /** 视频分辨率限制 */
  maxResolution?: number;
  /** 是否自动上传封面 */
  autoUploadCover?: boolean;
  /** 封面上传组件 */
  coverUpload?: ReactNode;
  /** 文件大小限制（字节）默认 50MB */
  maxSize?: number;
}

/**
 * 音频上传组件 Props
 */
export interface AudioUploadProps extends BaseUploadProps {
  /** 支持的音频格式 */
  accept?: 'audio/*' | 'audio/mp3,audio/wav,audio/m4a';
  /** 音频时长限制（秒） */
  maxDuration?: number;
  /** 是否显示波形 */
  showWaveform?: boolean;
  /** 是否自动播放 */
  autoPlay?: boolean;
  /** 文件大小限制（字节）默认 20MB */
  maxSize?: number;
}

/**
 * 媒体库弹窗 Props
 */
export interface MediaLibraryModalProps {
  /** 弹窗显示状态 */
  visible: boolean;
  /** 关闭弹窗回调 */
  onCancel: () => void;
  /** 确认选择回调 */
  onConfirm: (selectedFiles: AdminUploadList[]) => void;
  /** 文件类型 */
  fileType: FileType;
  /** 是否多选（默认 false） */
  multiple?: boolean;
  /** 最大选择数量 */
  maxCount?: number;
  /** 默认选中的文件ID */
  defaultSelectedIds?: number[];
  /** 文件大小限制 */
  maxSize?: number;
  /** 接受的文件类型 */
  accept?: string;
}

/**
 * 文件列表组件 Props
 */
export interface FileListProps {
  /** 文件列表 */
  fileList: AdminUploadList[];
  /** 加载状态 */
  loading: boolean;
  /** 选中的文件ID */
  selectedIds: number[];
  /** 是否多选 */
  multiple: boolean;
  /** 文件类型 */
  fileType: FileType;
  /** 选择文件回调 */
  onSelect: (id: number) => void;
  /** 取消选择回调 */
  onDeselect: (id: number) => void;
  /** 全选回调 */
  onSelectAll: () => void;
  /** 取消全选回调 */
  onDeselectAll: () => void;
  /** 分页信息 */
  pagination: {
    current: number;
    pageSize: number;
    total: number;
  };
  /** 分页改变回调 */
  onPageChange: (page: number, pageSize: number) => void;
  /** 搜索关键词 */
  keyword: string;
  /** 搜索回调 */
  onSearch: (keyword: string) => void;
}

/**
 * 上传区域组件 Props
 */
export interface UploadAreaProps {
  /** 文件类型 */
  fileType: FileType;
  /** 文件大小限制 */
  maxSize?: number;
  /** 接受的文件类型 */
  accept?: string;
  /** 上传成功回调 */
  onUploadSuccess: (file: AdminUploadList) => void;
  /** 上传失败回调 */
  onUploadError: (error: Error) => void;
  /** 是否禁用 */
  disabled?: boolean;
}
