import { AudioOutlined, FileTextOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { Checkbox, Empty, Image, Input, Pagination, Spin, Tag } from 'antd';
import React, { useMemo } from 'react';
import type { FileListProps } from '../../types';
import './index.less';

const { Search } = Input;

/**
 * 文件列表组件
 */
const FileList: React.FC<FileListProps> = ({
  fileList,
  loading,
  selectedIds,
  multiple,
  fileType,
  onSelect,
  onDeselect,
  onSelectAll,
  onDeselectAll,
  pagination,
  onPageChange,
  keyword,
  onSearch,
}) => {
  /**
   * 计算是否全选
   */
  const isAllSelected = useMemo(() => {
    return fileList.length > 0 && fileList.every((file) => selectedIds.includes(file.id));
  }, [fileList, selectedIds]);

  /**
   * 计算是否部分选中
   */
  const isIndeterminate = useMemo(() => {
    return !isAllSelected && fileList.some((file) => selectedIds.includes(file.id));
  }, [fileList, selectedIds, isAllSelected]);

  /**
   * 全选/取消全选
   */
  const handleSelectAllChange = (checked: boolean) => {
    if (checked) {
      onSelectAll();
    } else {
      onDeselectAll();
    }
  };

  /**
   * 选择/取消选择文件
   */
  const handleFileSelect = (fileId: number, checked: boolean) => {
    if (checked) {
      onSelect(fileId);
    } else {
      onDeselect(fileId);
    }
  };

  /**
   * 渲染文件项
   */
  const renderFileItem = (file: any) => {
    const isSelected = selectedIds.includes(file.id);

    return (
      <div
        key={file.id}
        className={`file-item ${isSelected ? 'selected' : ''}`}
        onClick={() => {
          if (!multiple) {
            handleFileSelect(file.id, !isSelected);
          }
        }}
      >
        <div className="file-item-content">
          {multiple && (
            <Checkbox
              checked={isSelected}
              onChange={(e) => handleFileSelect(file.id, e.target.checked)}
              onClick={(e) => e.stopPropagation()}
            />
          )}

          <div className="file-preview">
            {fileType === 'image' && (
              <Image
                src={file.url}
                alt={file.original_name}
                preview={{
                  src: file.url,
                }}
              />
            )}

            {fileType === 'video' && (
              <div className="video-preview">
                {file.thumbnail_url ? (
                  <img src={file.thumbnail_url} alt={file.original_name} />
                ) : (
                  <PlayCircleOutlined className="video-icon" />
                )}
              </div>
            )}

            {fileType === 'audio' && (
              <div className="audio-preview">
                <AudioOutlined className="audio-icon" />
              </div>
            )}

            {fileType === 'document' && (
              <div className="document-preview">
                <FileTextOutlined className="document-icon" />
              </div>
            )}
          </div>

          <div className="file-info">
            <div className="file-name" title={file.original_name}>
              {file.original_name}
            </div>
            <div className="file-meta">
              <Tag color="blue">{file.file_ext}</Tag>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="file-list">
      <div className="file-list-header">
        <div className="file-list-actions">
          {multiple && (
            <Checkbox
              checked={isAllSelected}
              indeterminate={isIndeterminate}
              onChange={(e) => handleSelectAllChange(e.target.checked)}
            >
              全选
            </Checkbox>
          )}

          <Search
            placeholder="搜索文件"
            defaultValue={keyword}
            onSearch={(value) => {
              onSearch(value);
            }}
            style={{ width: 200 }}
            allowClear
          />
        </div>

        <div className="file-list-count">共 {pagination.total} 个文件</div>
      </div>

      <Spin spinning={loading}>
        <div className="file-list-content" style={{ height: '420px' }}>
          {fileList.length === 0 && !loading ? (
            <Empty description="暂无文件" />
          ) : (
            <div className="file-grid">{fileList.map(renderFileItem)}</div>
          )}
        </div>
      </Spin>

      {pagination.total > 0 && (
        <div className="file-list-pagination">
          <Pagination
            current={pagination.current}
            pageSize={pagination.pageSize}
            total={pagination.total}
            onChange={onPageChange}
            showSizeChanger
            showQuickJumper
            showTotal={(total) => `共 ${total} 个文件`}
          />
        </div>
      )}
    </div>
  );
};

export default FileList;
