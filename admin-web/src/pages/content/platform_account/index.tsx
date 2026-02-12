import { CDel, CDelAll, ProTableWrapper } from '@/components';
import { destroy, destroyAll, getList, verify } from '@/services/content/platform_account/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import { CheckCircleOutlined, CloudDownloadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Alert, Badge, Button, message, Space } from 'antd';
import React, { useRef, useState } from 'react';
import FormIndex from './components/FormIndex';

// 平台选项映射
const platformMap: Record<string, string> = {
  zhihu: '知乎',
};

// 状态映射
const statusMap = {
  0: { text: '失效', color: 'error' },
  1: { text: '有效', color: 'success' },
  2: { text: '过期', color: 'warning' },
};

const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const { initialState } = useModel('@@initialState');
  let maps = {};

  const columns: ProColumns<API.ContentPlatformAccountList>[] = [
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
      render: (_, record) => platformMap[record.platform] || record.platform,
      align: 'center',
      width: 120,
    },
    {
      title: '账号名称',
      dataIndex: 'account_name',
      align: 'center',
      width: 150,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        0: { text: '失效', status: '0' },
        1: { text: '有效', status: '1' },
        2: { text: '过期', status: '2' },
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
      title: '最后验证',
      dataIndex: 'last_verified',
      hideInSearch: true,
      width: 180,
      align: 'center',
      valueType: 'dateTime',
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
      title: '更新时间',
      key: 'updated_at',
      dataIndex: 'updated_at',
      valueType: 'dateTime',
      sorter: true,
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '更新时间',
      key: 'updated_at',
      dataIndex: 'updated_at',
      valueType: 'dateTimeRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'updated_at[start]': value[0],
            'updated_at[end]': value[1],
          };
        },
      },
    },
    {
      title: '操作',
      key: 'option',
      width: 200,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        <Button
          key="verify"
          size="small"
          type="default"
          icon={<CheckCircleOutlined />}
          onClick={async () => {
            const res = await verify(row.id);
            if (res.code === 200) {
              message.success(res.message);
              actionRef.current?.reload();
            }
          }}
        >
          验证
        </Button>,
        <FormIndex
          id={row.id}
          key={`FormIndex-${row.id}`}
          onConfirm={() => {
            return actionRef.current?.reload();
          }}
        />,
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
    <>
      <Alert
        message="浏览器登录助手"
        description={
          <Space direction="vertical" size={0}>
            <span>使用浏览器扩展可以一键获取各平台的登录信息，无需手动复制 Cookies。</span>
            <Space>
              <Button
                type="link"
                icon={<CloudDownloadOutlined />}
                onClick={() => {
                  window.open('/downloads/py-small-admin-extension.zip', '_blank');
                }}
                style={{ padding: 0, height: 'auto' }}
              >
                下载浏览器扩展
              </Button>
              <span style={{ color: '#999' }}>安装后在已登录的平台网站点击扩展图标即可</span>
            </Space>
          </Space>
        }
        type="info"
        icon={<InfoCircleOutlined />}
        closable
        style={{ marginBottom: 16 }}
      />
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
            const stored = localStorage.getItem('content_platform_account_table_columns');
            return stored ? JSON.parse(stored) : {};
          })(),
          onChange: (map: any) => {
            maps = map;
          },
          persistenceKey: 'content_platform_account_table_columns',
          persistenceType: 'localStorage',
        }}
        tableAlertOptionRender={({ selectedRowKeys, selectedRows, onCleanSelected }) => {
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
        headerTitle={
          <FormIndex
            onConfirm={() => {
              return actionRef.current?.reload();
            }}
          />
        }
      />
    </>
  );
};

export default Index;
