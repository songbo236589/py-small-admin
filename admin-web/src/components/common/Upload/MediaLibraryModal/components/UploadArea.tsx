import { file as fileUpload } from '@/services/admin/sys/upload/api';
import { InboxOutlined } from '@ant-design/icons';
import { Upload, message } from 'antd';
import React from 'react';
import { useFileValidation } from '../../hooks/useFileValidation';
import type { UploadAreaProps } from '../../types';

const { Dragger } = Upload;

/**
 * 上传区域组件
 */
const UploadArea: React.FC<UploadAreaProps> = ({
  fileType,
  maxSize,
  accept,
  onUploadSuccess,
  onUploadError,
  disabled = false,
}) => {
  const { beforeUpload, formatFileSize } = useFileValidation({
    maxSize,
    accept,
  });

  const acceptMap: Record<string, string> = {
    image: 'image/*',
    document: '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt',
    video: 'video/*',
    audio: 'audio/*',
  };

  /**
   * 自定义上传逻辑
   */
  const customRequest = async (options: any) => {
    const { file, onSuccess, onError } = options;
    try {
      const result = await fileUpload({
        file_type: fileType,
        file: file as File,
      });

      if (result?.data) {
        onSuccess(result.data, file);
        message.success('上传成功');
      }
    } catch (error) {
      onError(error as Error);
      message.error('上传失败');
    }
  };

  /**
   * 上传状态改变处理
   */
  const handleChange = (info: any) => {
    const { status } = info.file;

    if (status === 'done') {
      onUploadSuccess(info.file.response);
    } else if (status === 'error') {
      onUploadError(new Error('上传失败'));
    }
  };

  return (
    <div className="upload-area">
      <Dragger
        name="file"
        accept={accept || acceptMap[fileType]}
        beforeUpload={beforeUpload}
        customRequest={customRequest}
        onChange={handleChange}
        disabled={disabled}
        showUploadList={false}
        multiple
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
        <p className="ant-upload-hint">
          {maxSize && `文件大小不能超过 ${formatFileSize(maxSize)}`}
        </p>
      </Dragger>
    </div>
  );
};

export default UploadArea;
