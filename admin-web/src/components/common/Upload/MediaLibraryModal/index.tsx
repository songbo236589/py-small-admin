import { Button, Col, message, Modal, Row } from 'antd';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useMediaLibrary } from '../hooks/useMediaLibrary';
import type { MediaLibraryModalProps } from '../types';
import FileList from './components/FileList';
import UploadArea from './components/UploadArea';
import './index.less';

/**
 * 媒体库弹窗组件
 */
const MediaLibraryModal: React.FC<MediaLibraryModalProps> = ({
  visible,
  onCancel,
  onConfirm,
  fileType,
  multiple = false,
  maxCount,
  defaultSelectedIds = [],
  maxSize,
  accept,
}) => {
  const { fileList, loading, pagination, keyword, loadFileList, handleSearch, handlePageChange } =
    useMediaLibrary({ fileType });

  const [selectedIds, setSelectedIds] = useState<number[]>(defaultSelectedIds);
  const prevKeywordRef = useRef('');
  const prevPaginationRef = useRef(pagination);

  /**
   * 当弹窗打开时重新加载文件列表
   */
  useEffect(() => {
    if (visible) {
      loadFileList();
    }
  }, [loadFileList, visible]);

  /**
   * 当搜索关键词变化时重新加载文件列表
   */
  useEffect(() => {
    if (visible && keyword !== prevKeywordRef.current) {
      prevKeywordRef.current = keyword;
      loadFileList();
    }
  }, [visible, keyword, loadFileList]);

  /**
   * 当分页变化时重新加载文件列表
   */
  useEffect(() => {
    if (
      visible &&
      (pagination.current !== prevPaginationRef.current.current ||
        pagination.pageSize !== prevPaginationRef.current.pageSize)
    ) {
      prevPaginationRef.current = pagination;
      loadFileList();
    }
  }, [visible, pagination, loadFileList]);
  /**
   * 当 defaultSelectedIds 变化时更新选中的 ID
   */
  useEffect(() => {
    setSelectedIds(defaultSelectedIds);
  }, [defaultSelectedIds]);

  /**
   * 计算已选择的文件数量
   */
  const selectedCount = useMemo(() => selectedIds.length, [selectedIds]);

  /**
   * 计算是否可以确认
   */
  const canConfirm = useMemo(() => {
    if (!multiple) {
      return selectedCount === 1;
    }
    if (maxCount) {
      return selectedCount > 0 && selectedCount <= maxCount;
    }
    return selectedCount > 0;
  }, [multiple, maxCount, selectedCount]);

  /**
   * 选择文件
   */
  const handleSelect = (id: number) => {
    if (!multiple) {
      setSelectedIds([id]);
      return;
    }

    if (maxCount && selectedIds.length >= maxCount) {
      message.warning(`最多只能选择 ${maxCount} 个文件`);
      return;
    }

    setSelectedIds((prev) => [...prev, id]);
  };

  /**
   * 取消选择文件
   */
  const handleDeselect = (id: number) => {
    setSelectedIds((prev) => prev.filter((selectedId) => selectedId !== id));
  };

  /**
   * 全选
   */
  const handleSelectAll = () => {
    if (maxCount && fileList.length > maxCount) {
      message.warning(`最多只能选择 ${maxCount} 个文件`);
      return;
    }
    setSelectedIds(fileList.map((file) => file.id));
  };

  /**
   * 取消全选
   */
  const handleDeselectAll = () => {
    setSelectedIds([]);
  };

  /**
   * 上传成功处理
   */
  const handleUploadSuccess = (file: any) => {
    // 刷新文件列表
    loadFileList();
    // 自动选中新上传的文件
    if (!multiple) {
      setSelectedIds([file.id]);
    } else if (!maxCount || selectedIds.length < maxCount) {
      setSelectedIds((prev) => [...prev, file.id]);
    }
  };

  /**
   * 上传失败处理
   */
  const handleUploadError = (error: Error) => {
    console.error('上传失败:', error);
  };

  /**
   * 确认选择
   */
  const handleConfirm = () => {
    const selectedFiles = fileList.filter((file) => selectedIds.includes(file.id));
    onConfirm(selectedFiles);
  };

  /**
   * 关闭弹窗
   */
  const handleCancel = () => {
    setSelectedIds([]);
    onCancel();
  };

  return (
    <Modal
      title={`媒体库 - ${
        fileType === 'image'
          ? '图片'
          : fileType === 'document'
          ? '文档'
          : fileType === 'video'
          ? '视频'
          : '音频'
      }选择`}
      open={visible}
      onCancel={handleCancel}
      width={1200}
      footer={null}
      destroyOnHidden
      zIndex={1500}
    >
      <Row gutter={16} style={{ height: 600 }}>
        <Col span={16} style={{ height: '100%', borderRight: '1px solid #f0f0f0' }}>
          <FileList
            fileList={fileList}
            loading={loading}
            selectedIds={selectedIds}
            multiple={multiple}
            fileType={fileType}
            onSelect={handleSelect}
            onDeselect={handleDeselect}
            onSelectAll={handleSelectAll}
            onDeselectAll={handleDeselectAll}
            pagination={pagination}
            onPageChange={handlePageChange}
            keyword={keyword}
            onSearch={handleSearch}
          />
        </Col>

        <Col span={8} style={{ height: '100%', padding: '16px' }}>
          <UploadArea
            fileType={fileType}
            maxSize={maxSize}
            accept={accept}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </Col>
      </Row>

      <div className="media-library-modal-footer">
        <div className="selected-info">
          已选择 {selectedCount}
          {maxCount && `/${maxCount}`} 个文件
        </div>
        <div className="footer-actions">
          <Button onClick={handleCancel}>取消</Button>
          <Button type="primary" onClick={handleConfirm} disabled={!canConfirm}>
            确定
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default MediaLibraryModal;
