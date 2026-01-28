import { AudioOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, List, Tag } from 'antd';
import React, { useState } from 'react';
import { useSystemUploadConfig } from '../hooks/useSystemUploadConfig';
import MediaLibraryModal from '../MediaLibraryModal';
import type { AudioUploadProps } from '../types';
import './index.less';

/**
 * 音频上传组件
 */
const AudiosUpload: React.FC<AudioUploadProps> = ({
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
  const systemConfig = useSystemUploadConfig('audio');

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
      onChange?.(files[0] || undefined);
    }
    handleCloseModal();
  };

  /**
   * 删除文件
   */
  const handleDelete = (index: number) => {
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
   * 格式化时长
   */
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * 默认渲染
   */
  const defaultRender = () => {
    if (selectedFiles.length === 0) {
      return (
        <Button icon={<PlusOutlined />} onClick={handleOpenModal} disabled={disabled}>
          选择音频
        </Button>
      );
    }

    return (
      <div className="audio-upload-list">
        <List
          dataSource={selectedFiles}
          renderItem={(file, index) => (
            <List.Item
              actions={
                !disabled
                  ? [
                      <Button
                        key="delete"
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleDelete(index)}
                      />,
                    ]
                  : undefined
              }
            >
              <List.Item.Meta
                avatar={<AudioOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                title={
                  <a href={file.file_path} target="_blank" rel="noopener noreferrer">
                    {file.original_name}
                  </a>
                }
                description={
                  <div className="audio-meta">
                    <Tag color="blue">{file.file_ext}</Tag>
                    {file.duration > 0 && <Tag color="green">{formatDuration(file.duration)}</Tag>}
                    <span className="file-size">{(file.file_size / 1024).toFixed(2)} KB</span>
                  </div>
                }
              />
            </List.Item>
          )}
        />

        {multiple && (!maxCount || selectedFiles.length < maxCount) && (
          <Button icon={<PlusOutlined />} onClick={handleOpenModal} disabled={disabled} block>
            添加音频
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
        <div className="audio-upload">{showUploadList && defaultRender()}</div>
      )}

      <MediaLibraryModal
        visible={modalVisible}
        onCancel={handleCloseModal}
        onConfirm={handleConfirm}
        fileType="audio"
        multiple={multiple}
        maxCount={maxCount}
        defaultSelectedIds={selectedFiles.map((file) => file.id)}
        maxSize={finalMaxSize}
        accept={finalAccept}
      />
    </>
  );
};

export default AudiosUpload;
