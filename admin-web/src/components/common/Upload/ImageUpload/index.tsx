import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Image, Tag } from 'antd';
import React, { useState } from 'react';
import { useSystemUploadConfig } from '../hooks/useSystemUploadConfig';
import MediaLibraryModal from '../MediaLibraryModal';
import type { ImageUploadProps } from '../types';
import './index.less';

/**
 * 图片上传组件
 */
const ImageUpload: React.FC<ImageUploadProps> = ({
  value,
  onChange,
  multiple = false,
  maxCount,
  maxSize,
  accept,
  showUploadList = true,
  disabled = false,
  render,
}) => {
  const [modalVisible, setModalVisible] = useState(false);

  // 从系统配置获取默认配置
  const systemConfig = useSystemUploadConfig('image');

  // props 优先级高于系统配置
  const finalMaxSize = maxSize ?? systemConfig.maxSize;
  const finalAccept = accept ?? systemConfig.accept;

  /**
   * 将 value 转换为数组
   */
  const selectedFiles = Array.isArray(value) ? value : value ? [value] : [];

  /**
   * 打开媒体库弹窗
   */
  const handleOpenModal = () => {
    if (!disabled) {
      setModalVisible(true);
    }
  };

  /**
   * 关闭媒体库弹窗
   */
  const handleCloseModal = () => {
    setModalVisible(false);
  };

  /**
   * 确认选择
   */
  const handleConfirm = (files: any[]) => {
    if (multiple) {
      onChange?.(files);
    } else {
      onChange?.(files[0] || null);
    }
    handleCloseModal();
  };

  /**
   * 删除文件
   */
  const handleDelete = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (disabled) return;

    if (multiple) {
      const newFiles = [...selectedFiles];
      newFiles.splice(index, 1);
      onChange?.(newFiles);
    } else {
      onChange?.(undefined);
    }
  };

  /**
   * 默认渲染
   */
  const defaultRender = () => {
    if (selectedFiles.length === 0) {
      return (
        <Button
          icon={<PlusOutlined />}
          onClick={handleOpenModal}
          disabled={disabled}
          style={{ display: 'flex', flexDirection: 'column' }}
          className="image-upload-add-btn"
        >
          添加图片
        </Button>
      );
    }

    return (
      <div className="image-upload-list">
        {selectedFiles.map((file, index) => (
          <div key={file.id} className="image-upload-item">
            <Image
              src={file.url}
              alt={file.original_name}
              width={104}
              height={104}
              preview={true}
            />
            {!disabled && (
              <div className="image-upload-item-actions">
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={(e) => handleDelete(index, e)}
                />
              </div>
            )}
            <div className="image-upload-item-info">
              <Tag color="blue">{file.original_name}</Tag>
            </div>
          </div>
        ))}

        {multiple && (!maxCount || selectedFiles.length < maxCount) && (
          <Button
            icon={<PlusOutlined />}
            onClick={handleOpenModal}
            disabled={disabled}
            className="image-upload-add-btn"
            style={{ display: 'flex', flexDirection: 'column' }}
          >
            添加图片
          </Button>
        )}
      </div>
    );
  };

  return (
    <>
      {render ? (
        render(selectedFiles, handleOpenModal)
      ) : (
        <div className="image-upload">{showUploadList && defaultRender()}</div>
      )}

      <MediaLibraryModal
        visible={modalVisible}
        onCancel={handleCloseModal}
        onConfirm={handleConfirm}
        fileType="image"
        multiple={multiple}
        maxCount={maxCount}
        defaultSelectedIds={selectedFiles.map((file) => file.id)}
        maxSize={finalMaxSize}
        accept={finalAccept}
      />
    </>
  );
};

export default ImageUpload;
