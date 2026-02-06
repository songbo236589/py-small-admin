import { ProTableWrapper } from '@/components';
import { getLogs, retry } from '@/services/content/publish/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Badge, Button, message, Space, Tag } from 'antd';
import { RedoOutlined } from '@ant-design/icons';
import React, { useRef, useState } from 'react';

// 平台选项映射
const platformMap: Record<string, string> = {
  zhihu: '知乎',
  juejin: '掘金',
  csdn: 'CSDN',
  jianshu: '简书',
  segmentfault: '思否',
};

// 状态映射
const statusMap = {
  0: { text: '待发布', color: 'default' },
  1: { text: '发布中', color: 'processing' },
  2: { text: '成功', color: 'success' },
  3: { text: '失败', color: 'error' },
};

const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const { initialState } = useModel('@@initialState');
  let maps = {};

  const columns: ProColumns<API.ContentPublishLogList>[] = [
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
      title: '文章ID',
      dataIndex: 'article_id',
      hideInSearch: true,
      width: 100,
      align: 'center',
    },
    {
      title: '文章标题',
      dataIndex: 'article_title',
      hideInSearch: true,
      width: 250,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '发布平台',
      dataIndex: 'platform',
      valueType: 'select',
      valueEnum: {
        zhihu: { text: '知乎', status: 'zhihu' },
        juejin: { text: '掘金', status: 'juejin' },
        csdn: { text: 'CSDN', status: 'csdn' },
        jianshu: { text: '简书', status: 'jianshu' },
        segmentfault: { text: '思否', status: 'segmentfault' },
      },
      render: (_, record) => {
        const platformName = platformMap[record.platform] || record.platform;
        return <Tag color="blue">{platformName}</Tag>;
      },
      align: 'center',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        0: { text: '待发布', status: '0' },
        1: { text: '发布中', status: '1' },
        2: { text: '成功', status: '2' },
        3: { text: '失败', status: '3' },
      },
      hideInTable: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      hideInSearch: true,
      width: 100,
      align: 'center',
      render: (_, record) => {
        const status = statusMap[record.status as keyof typeof statusMap];
        return <Badge status={status.color as any} text={status.text} />;
      },
    },
    {
      title: '平台文章ID',
      dataIndex: 'platform_article_id',
      hideInSearch: true,
      width: 120,
      align: 'center',
      ellipsis: true,
      render: (_, record) => record.platform_article_id || '-',
    },
    {
      title: '平台文章链接',
      dataIndex: 'platform_url',
      hideInSearch: true,
      width: 200,
      ellipsis: true,
      render: (_, record) => {
        if (record.platform_url) {
          return (
            <a href={record.platform_url} target="_blank" rel="noreferrer">
              {record.platform_url}
            </a>
          );
        }
        return '-';
      },
    },
    {
      title: '错误信息',
      dataIndex: 'error_message',
      hideInSearch: true,
      width: 200,
      ellipsis: true,
      render: (_, record) => {
        if (record.error_message) {
          return <span style={{ color: '#ff4d4f' }}>{record.error_message}</span>;
        }
        return '-';
      },
    },
    {
      title: '重试次数',
      dataIndex: 'retry_count',
      hideInSearch: true,
      width: 100,
      align: 'center',
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
      width: 120,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        row.status === 3 && (
          <Button
            key="retry"
            size="small"
            type="primary"
            ghost
            icon={<RedoOutlined />}
            onClick={async () => {
              const res = await retry(row.id);
              if (res.code === 200) {
                message.success(res.message || '已重新创建发布任务');
                actionRef.current?.reload();
              }
            }}
          >
            重试
          </Button>
        ),
      ],
    },
  ];

  return (
    <ProTableWrapper
      loading={loading}
      actionRef={actionRef}
      rowKey="id"
      columns={columns}
      request={async (params: API.ListQequest, sort) => {
        setLoading(true);
        const data = await getSort(params, sort);
        const res = await getLogs(data);
        setLoading(false);
        return await setLsetData(res);
      }}
      columnsState={{
        defaultValue: (() => {
          const stored = localStorage.getItem('content_publish_table_columns');
          return stored ? JSON.parse(stored) : {};
        })(),
        onChange: (map: any) => {
          maps = map;
        },
        persistenceKey: 'content_publish_table_columns',
        persistenceType: 'localStorage',
      }}
      tableAlertOptionRender={({ selectedRowKeys }) => {
        return (
          <Space size={16}>
            <a
              onClick={() => {
                exportExcel({
                  breadcrumbData: initialState?.breadcrumbData || [],
                  columns,
                  columnsState: maps,
                  selectedRows: [],
                });
              }}
            >
              导出数据
            </a>
          </Space>
        );
      }}
      search={{
        labelWidth: 'auto',
      }}
    />
  );
};

export default Index;
