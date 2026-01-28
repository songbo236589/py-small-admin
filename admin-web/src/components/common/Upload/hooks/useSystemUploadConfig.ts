import { useModel } from '@umijs/max';
import type { FileType } from '../types';
import {
  getAudioUploadConfig,
  getDocumentUploadConfig,
  getImageUploadConfig,
  getVideoUploadConfig,
} from '../utils';

/**
 * 从系统配置中获取上传配置的 Hook
 * @param fileType 文件类型
 * @returns 上传配置对象 { maxSize, accept }
 */
export const useSystemUploadConfig = (fileType: FileType) => {
  const { initialState } = useModel('@@initialState');

  const configMap = {
    image: getImageUploadConfig,
    video: getVideoUploadConfig,
    document: getDocumentUploadConfig,
    audio: getAudioUploadConfig,
  };

  return configMap[fileType]?.(initialState?.systemConfig?.upload) || { maxSize: 0, accept: '' };
};
