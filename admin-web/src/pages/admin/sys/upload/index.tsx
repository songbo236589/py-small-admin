import { CDel, CDelAll, ProTableWrapper } from '@/components';
import { destroy, destroyAll, getList } from '@/services/admin/sys/upload/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { message, Space } from 'antd';
import React, { useRef, useState } from 'react';
const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const { initialState } = useModel('@@initialState');
  let maps = {};

  const columns: ProColumns<API.AdminUploadList>[] = [
    {
      title: '编号',
      dataIndex: 'id',
      hideInSearch: true,
      align: 'center',
      width: 80,
      fixed: true,
      sorter: true,
    },

    {
      title: '原始文件名',
      dataIndex: 'original_name',
      align: 'center',
      width: 180,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '存储文件名',
      dataIndex: 'filename',
      align: 'center',
      width: 180,
      ellipsis: true,
      copyable: true,
      hideInSearch: true,
    },
    {
      title: '文件路径',
      dataIndex: 'file_path',
      align: 'center',
      width: 200,
      ellipsis: true,
      copyable: true,
      hideInSearch: true,
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      align: 'center',
      width: 100,
      hideInSearch: true,
      render: (_, record) => {
        const size = record.file_size;
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
        if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(2)} MB`;
        return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`;
      },
    },
    {
      title: 'MIME类型',
      dataIndex: 'mime_type',
      align: 'center',
      width: 120,
      ellipsis: true,
      hideInSearch: true,
    },
    {
      title: '文件扩展名',
      dataIndex: 'file_ext',
      align: 'center',
      width: 100,
      hideInSearch: true,
    },
    {
      title: '存储类型',
      dataIndex: 'storage_type',
      valueType: 'select',
      valueEnum: {
        local: { text: '本地存储', status: 'Default' },
        aliyun_oss: { text: '阿里云OSS', status: 'Processing' },
        tencent_oss: { text: '腾讯云OSS', status: 'Processing' },
        qiniu_oss: { text: '七牛云OSS', status: 'Processing' },
      },
      align: 'center',
      width: 120,
    },
    {
      title: '文件分类',
      dataIndex: 'file_type',
      valueType: 'select',
      valueEnum: {
        image: { text: '图片', status: 'Success' },
        document: { text: '文档', status: 'Processing' },
        video: { text: '视频', status: 'Warning' },
        audio: { text: '音频', status: 'Default' },
        other: { text: '其他', status: 'Default' },
      },
      align: 'center',
      width: 100,
    },

    {
      title: '上传者ID',
      dataIndex: 'admin_id',
      align: 'center',
      width: 100,
      hideInSearch: true,
    },
    {
      title: '图片尺寸',
      dataIndex: 'width',
      align: 'center',
      width: 120,
      hideInSearch: true,
      render: (_, record) => {
        if (record.width && record.height) {
          return `${record.width} x ${record.height}`;
        }
        return '-';
      },
    },
    {
      title: '时长',
      dataIndex: 'duration',
      align: 'center',
      width: 100,
      hideInSearch: true,
      render: (_, record) => {
        if (record.duration > 0) {
          const minutes = Math.floor(record.duration / 60);
          const seconds = record.duration % 60;
          return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        return '-';
      },
    },

    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      valueType: 'dateTime',
      sorter: true,
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '创建时间',
      key: 'created_at',
      dataIndex: 'created_at',
      valueType: 'dateTimeRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'created_at[start]': value[0],
            'created_at[end]': value[1],
          };
        },
      },
    },
    {
      title: '操作',
      key: 'option',
      width: 80,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        <CDel
          key={`CDel-${row.id}`}
          onCancel={async () => {
            const res = await destroy(row.id);
            if (res.code === 200) {
              message.success(res.message);
              actionRef.current?.reload();
            }
          }}
        />,
      ],
    },
  ];
  return (
    <ProTableWrapper
      loading={loading}
      actionRef={actionRef}
      rowKey="id"
      rowSelection={{
        fixed: true,
      }}
      columns={columns}
      request={async (params: API.ListQequest, sort) => {
        setLoading(true);
        const data = await getSort(params, sort);
        const res = await getList(data);
        setLoading(false);
        return await setLsetData(res);
      }}
      columnsState={{
        defaultValue: (() => {
          const stored = localStorage.getItem('admin_sys_upload_table_columns');
          return stored ? JSON.parse(stored) : {};
        })(),
        onChange: (map: any) => {
          maps = map;
        },
        persistenceKey: 'admin_sys_upload_table_columns',
        persistenceType: 'localStorage',
      }}
      tableAlertOptionRender={({ selectedRows, selectedRowKeys, onCleanSelected }) => {
        return (
          <Space size={16}>
            <CDelAll
              key={selectedRowKeys.length}
              count={selectedRowKeys.length}
              onCancel={async () => {
                const res = await destroyAll({ id_array: selectedRowKeys });
                if (res.code === 200) {
                  message.success(res.message);
                  actionRef.current?.reload();
                  onCleanSelected();
                }
              }}
            />
            <a
              onClick={() => {
                exportExcel({
                  breadcrumbData: initialState?.breadcrumbData || [],
                  columns,
                  columnsState: maps,
                  selectedRows,
                });
              }}
            >
              导出数据
            </a>
          </Space>
        );
      }}
    />
  );
};

export default Index;
