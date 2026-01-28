import { getList } from '@/services/admin/sys/upload/api';
import { useCallback, useEffect, useRef, useState } from 'react';
import type { AdminUploadList, ListRequest } from '../types';

interface UseMediaLibraryOptions {
  fileType: 'image' | 'document' | 'video' | 'audio';
  defaultPageSize?: number;
}

interface UseMediaLibraryReturn {
  fileList: AdminUploadList[];
  loading: boolean;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
  };
  keyword: string;
  loadFileList: (params?: Partial<ListRequest>) => Promise<void>;
  handleSearch: (keyword: string) => void;
  handlePageChange: (page: number, pageSize: number) => void;
}

/**
 * 媒体库逻辑 Hook
 * 用于管理文件列表的加载、搜索、分页等逻辑
 */
export const useMediaLibrary = (options: UseMediaLibraryOptions): UseMediaLibraryReturn => {
  const { fileType, defaultPageSize = 20 } = options;

  const [fileList, setFileList] = useState<AdminUploadList[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: defaultPageSize,
    total: 0,
  });
  const [keyword, setKeyword] = useState('');

  // 使用 ref 存储 pagination 和 keyword 的最新值，避免依赖循环
  const paginationRef = useRef(pagination);
  const keywordRef = useRef(keyword);

  // 保持 ref 与 state 同步
  useEffect(() => {
    paginationRef.current = pagination;
  }, [pagination]);

  useEffect(() => {
    keywordRef.current = keyword;
  }, [keyword]);

  /**
   * 加载文件列表
   */
  const loadFileList = useCallback(
    async (params?: Partial<ListRequest>) => {
      setLoading(true);
      const response = await getList({
        page: paginationRef.current.current,
        limit: paginationRef.current.pageSize,
        file_type: fileType,
        original_name: keywordRef.current || undefined,
        ...params,
      });

      if (response.code === 200) {
        setFileList(response.data.items || []);
        setPagination({
          current: response.data.page || 1,
          pageSize: response.data.size || defaultPageSize,
          total: response.data.total || 0,
        });
      }
      setLoading(false);
    },
    [fileType, defaultPageSize],
  );

  /**
   * 搜索处理
   */
  const handleSearch = useCallback((searchKeyword: string) => {
    setKeyword(searchKeyword);
    setPagination((prev) => ({ ...prev, current: 1 }));
  }, []);

  /**
   * 分页改变处理
   */
  const handlePageChange = useCallback((page: number, pageSize: number) => {
    setPagination((prev) => ({ ...prev, current: page, pageSize }));
  }, []);

  return {
    fileList,
    loading,
    pagination,
    keyword,
    loadFileList,
    handleSearch,
    handlePageChange,
  };
};
