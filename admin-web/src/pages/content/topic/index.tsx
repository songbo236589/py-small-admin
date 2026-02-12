import { CDel, CDelAll, ProTableWrapper } from '@/components';
import { destroy, destroyAll, getList, setStatus } from '@/services/content/topic/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import { ThunderboltOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { message, Space, Switch, Tooltip } from 'antd';
import { useRef, useState } from 'react';
import FetchModal from './components/FetchModal';
import TopicDrawer from './components/TopicDrawer';

const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const { initialState } = useModel('@@initialState');
  let maps = {};

  const columns: ProColumns<API.ContentTopic>[] = [
    {
      title: '编号',
      dataIndex: 'id',
      hideInSearch: true,
      align: 'center',
      width: 80,
      fixed: true,
    },
    {
      title: '问题标题',
      dataIndex: 'title',
      align: 'center',
      width: 300,
      ellipsis: true,
      copyable: true,
      render: (_, record) => (
        <a href={record.url} target="_blank" rel="noopener noreferrer">
          {record.title}
        </a>
      ),
    },
    {
      title: '平台',
      dataIndex: 'platform',
      valueType: 'select',
      width: 100,
      align: 'center',
      valueEnum: {
        zhihu: { text: '知乎', status: 'Default' },
      },
    },
    {
      title: '分类',
      dataIndex: 'category',
      width: 120,
      align: 'center',
      hideInTable: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      width: 100,
      align: 'center',
      hideInSearch: true,
      render: (_, record) => record.category || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        0: {
          text: '禁用',
          status: '0',
        },
        1: {
          text: '启用',
          status: '1',
        },
      },
      hideInTable: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      hideInSearch: true,
      width: 100,
      align: 'center',
      render: (text, record) => [
        <Switch
          key={record.id}
          checkedChildren="启用"
          unCheckedChildren="禁用"
          defaultChecked={record.status === 1 ? true : false}
          onChange={async (checked: boolean) => {
            const res = await setStatus(record.id, { status: checked ? 1 : 0 });
            if (res.code === 200) {
              message.success(res.message);
            } else {
              actionRef.current?.reload();
            }
          }}
        />,
      ],
    },
    {
      title: '热度',
      dataIndex: 'hot_score',
      hideInSearch: true,
      width: 100,
      align: 'center',
      sorter: true,
      render: (_, record) => (
        <Space>
          <ThunderboltOutlined twoToneColor="#ff4d4f" />
          {record.hot_score?.toLocaleString() || '-'}
        </Space>
      ),
    },
    {
      title: '浏览量',
      dataIndex: 'view_count',
      hideInSearch: true,
      width: 100,
      align: 'center',
      sorter: true,
      render: (text) => text?.toLocaleString() || '-',
    },
    {
      title: '回答数',
      dataIndex: 'answer_count',
      hideInSearch: true,
      width: 100,
      align: 'center',
      sorter: true,
      render: (text) => text?.toLocaleString() || '-',
    },
    {
      title: '关注者数',
      dataIndex: 'follower_count',
      hideInSearch: true,
      width: 100,
      align: 'center',
      sorter: true,
      render: (text) => text?.toLocaleString() || '-',
    },
    {
      title: '提问者',
      dataIndex: 'author_name',
      hideInSearch: true,
      width: 120,
      align: 'center',
      render: (_, record) => {
        if (record.author_name) {
          return (
            <Tooltip title={record.author_name}>
              <a
                href={record.author_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'inherit', textDecoration: 'none' }}
              >
                {record.author_name}
              </a>
            </Tooltip>
          );
        }
        return '-';
      },
    },
    {
      title: '问题描述',
      dataIndex: 'description',
      hideInSearch: true,
      width: 200,
      align: 'center',
      ellipsis: true,
      copyable: true,
    },
    {
      title: '抓取时间',
      dataIndex: 'fetched_at',
      valueType: 'dateTime',
      sorter: true,
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '操作',
      key: 'option',
      width: 150,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        <TopicDrawer
          id={row.id}
          key={`TopicDrawer-${row.id}`}
          onConfirm={() => {
            return actionRef.current?.reload();
          }}
        />,
        <CDel
          key="delete"
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
    <>
      <ProTableWrapper
        loading={loading}
        actionRef={actionRef}
        rowKey="id"
        rowSelection={{
          fixed: true,
        }}
        columns={columns}
        request={async (params: API.TopicRequest, sort) => {
          setLoading(true);
          const data = await getSort(params, sort);
          const res = await getList(data);
          setLoading(false);
          return await setLsetData(res);
        }}
        columnsState={{
          defaultValue: (() => {
            const stored = localStorage.getItem('content_topic_table_columns');
            return stored ? JSON.parse(stored) : {};
          })(),
          onChange: (map: any) => {
            maps = map;
          },
          persistenceKey: 'content_topic_table_columns',
          persistenceType: 'localStorage',
        }}
        tableAlertOptionRender={({ selectedRowKeys, selectedRows, onCleanSelected }) => (
          <Space size={16}>
            <CDelAll
              key={selectedRowKeys.length}
              count={selectedRowKeys.length}
              onCancel={async () => {
                const res = await destroyAll({ id_array: selectedRowKeys as number[] });
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
        )}
        headerTitle={
          <FetchModal
            onConfirm={() => {
              actionRef.current?.reload();
            }}
          />
        }
      />
    </>
  );
};

export default Index;
