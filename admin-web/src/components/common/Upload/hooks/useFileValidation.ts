import { message } from 'antd';

interface UseFileValidationOptions {
  maxSize?: number;
  accept?: string;
}

/**
 * 文件验证 Hook
 * 用于验证文件类型和大小
 */
export const useFileValidation = (options: UseFileValidationOptions = {}) => {
  const { maxSize, accept } = options;

  /**
   * 格式化文件大小
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  /**
   * 验证文件类型
   */
  const isValidFileType = (file: File, acceptTypes?: string): boolean => {
    if (!acceptTypes) return true;

    const acceptedTypes = acceptTypes.split(',').map((type) => type.trim());
    const fileType = file.type;
    const fileName = file.name.toLowerCase();

    return acceptedTypes.some((acceptedType) => {
      if (acceptedType.startsWith('.')) {
        // 扩展名匹配
        return fileName.endsWith(acceptedType.toLowerCase());
      } else if (acceptedType.includes('/*')) {
        // MIME 类型通配符匹配
        const mimeType = acceptedType.split('/*')[0];
        return fileType.startsWith(mimeType);
      } else {
        // 精确 MIME 类型匹配
        return fileType === acceptedType;
      }
    });
  };

  /**
   * 上传前验证
   */
  const beforeUpload = (file: File): boolean => {
    // 验证文件大小
    if (maxSize && file.size > maxSize) {
      message.error(`文件大小不能超过 ${formatFileSize(maxSize)}`);
      return false;
    }

    // 验证文件类型
    if (!isValidFileType(file, accept)) {
      message.error(`不支持的文件类型`);
      return false;
    }

    return true;
  };

  return {
    beforeUpload,
    formatFileSize,
    isValidFileType,
  };
};
