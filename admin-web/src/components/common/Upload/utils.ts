import type { UploadConfig } from './types';

/**
 * 将文件扩展名数组转换为 accept 字符串
 * @param extensions 文件扩展名数组，如 ['jpg', 'png', 'gif']
 * @returns accept 字符串，如 '.jpg,.png,.gif'
 */
export const extensionsToAccept = (extensions: string[]): string => {
  return extensions.map((ext) => `.${ext}`).join(',');
};

/**
 * 将文件大小从 MB 转换为字节
 * @param sizeMB 大小（MB）
 * @returns 大小（字节）
 */
export const mbToBytes = (sizeMB: number): number => {
  return sizeMB * 1024 * 1024;
};

/**
 * 从系统配置中获取图片上传配置
 * @param config 系统配置
 * @returns 图片上传配置对象
 */
export const getImageUploadConfig = (config?: API.AdminUploadConfigForm | UploadConfig) => {
  if (!config) {
    return {
      maxSize: 5 * 1024 * 1024, // 默认 5MB
      accept: 'image/*',
    };
  }

  return {
    maxSize: mbToBytes(config.upload_image_max_size),
    accept: extensionsToAccept(config.upload_image_allowed_types),
  };
};

/**
 * 从系统配置中获取视频上传配置
 * @param config 系统配置
 * @returns 视频上传配置对象
 */
export const getVideoUploadConfig = (config?: API.AdminUploadConfigForm | UploadConfig) => {
  if (!config) {
    return {
      maxSize: 50 * 1024 * 1024, // 默认 50MB
      accept: 'video/*',
    };
  }

  return {
    maxSize: mbToBytes(config.upload_video_max_size),
    accept: extensionsToAccept(config.upload_video_allowed_types),
  };
};

/**
 * 从系统配置中获取文档上传配置
 * @param config 系统配置
 * @returns 文档上传配置对象
 */
export const getDocumentUploadConfig = (config?: API.AdminUploadConfigForm | UploadConfig) => {
  if (!config) {
    return {
      maxSize: 10 * 1024 * 1024, // 默认 10MB
      accept: '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt',
    };
  }

  return {
    maxSize: mbToBytes(config.upload_document_max_size),
    accept: extensionsToAccept(config.upload_document_allowed_types),
  };
};

/**
 * 从系统配置中获取音频上传配置
 * @param config 系统配置
 * @returns 音频上传配置对象
 */
export const getAudioUploadConfig = (config?: API.AdminUploadConfigForm | UploadConfig) => {
  if (!config) {
    return {
      maxSize: 20 * 1024 * 1024, // 默认 20MB
      accept: 'audio/*',
    };
  }

  return {
    maxSize: mbToBytes(config.upload_audio_max_size),
    accept: extensionsToAccept(config.upload_audio_allowed_types),
  };
};
