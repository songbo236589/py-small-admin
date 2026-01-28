// 导出类型
export type {
  AdminUploadFile,
  AdminUploadList,
  AudioUploadProps,
  BaseUploadProps,
  DocumentUploadProps,
  FileListProps,
  FileType,
  ImageUploadProps,
  ListRequest,
  MediaLibraryModalProps,
  UploadAreaProps,
  UploadConfig,
  VideoUploadProps,
} from './types';

// 导出 Hooks
export { useFileValidation } from './hooks/useFileValidation';
export { useMediaLibrary } from './hooks/useMediaLibrary';
export { useSystemUploadConfig } from './hooks/useSystemUploadConfig';

// 导出工具函数
export {
  extensionsToAccept,
  getAudioUploadConfig,
  getDocumentUploadConfig,
  getImageUploadConfig,
  getVideoUploadConfig,
  mbToBytes,
} from './utils';

// 导出组件
export { default as AudiosUpload } from './AudiosUpload';
export { default as DocumentUpload } from './DocumentUpload';
export { default as ImageUpload } from './ImageUpload';
export { default as MediaLibraryModal } from './MediaLibraryModal';
export { default as VideoUpload } from './VideoUpload';
