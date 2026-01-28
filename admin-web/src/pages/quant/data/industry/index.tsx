import { CDel, CDelAll, NumberInput, ProTableWrapper } from '@/components';
import {
  destroy,
  destroyAll,
  getList,
  setSort,
  setStatus,
  syncList,
  syncRelation,
} from '@/services/quant/data/industry/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import { EyeOutlined, FileTextOutlined, LinkOutlined, SyncOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Button, message, Space, Switch } from 'antd';
import React, { useRef, useState } from 'react';

import FormIndex from './components/FormIndex';
const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncRelationLoading, setSyncRelationLoading] = useState(false);
  const { initialState } = useModel('@@initialState');
  let maps = {};

  const columns: ProColumns<API.QuantIndustryList>[] = [
    {
      title: '排名',
      dataIndex: 'sort',
      hideInSearch: true,
      width: 100,
      align: 'center',
      sorter: true,
      fixed: true,
      render: (text, record) => [
        <NumberInput
          value={record.sort}
          key={`NumberInput-${record.id}`}
          onBlur={async (value: number) => {
            const res = await setSort(record.id, { sort: value });
            if (res.code === 200) {
              message.success(res.message);
              actionRef.current?.reload();
            } else {
              actionRef.current?.reload();
            }
          }}
        />,
      ],
    },
    {
      title: '行业名称',
      dataIndex: 'name',
      align: 'center',
      width: 120,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '行业代码',
      dataIndex: 'code',
      align: 'center',
      width: 100,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '最新价',
      dataIndex: 'latest_price',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '最新价',
      dataIndex: 'latest_price',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'latest_price[start]': value[0],
            'latest_price[end]': value[1],
          };
        },
      },
    },
    {
      title: '涨跌额',
      dataIndex: 'change_amount',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [
        <span style={{ color: text > 0 ? '#ff4d4f' : '#000000' }} key={record.id}>
          {text}
        </span>,
      ],
    },
    {
      title: '涨跌额',
      dataIndex: 'change_amount',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_amount[start]': value[0],
            'change_amount[end]': value[1],
          };
        },
      },
    },
    {
      title: '涨跌幅(%)',
      dataIndex: 'change_percent',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [
        <span style={{ color: text > 0 ? '#ff4d4f' : '#000000' }} key={record.id}>
          {text}
        </span>,
      ],
    },
    {
      title: '涨跌幅(%)',
      dataIndex: 'change_percent',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_percent[start]': value[0],
            'change_percent[end]': value[1],
          };
        },
      },
    },
    {
      title: '总市值(亿)',
      dataIndex: 'total_market_cap',
      align: 'center',
      width: 120,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '总市值(亿)',
      dataIndex: 'total_market_cap',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'total_market_cap[start]': value[0],
            'total_market_cap[end]': value[1],
          };
        },
      },
    },
    {
      title: '换手率(%)',
      dataIndex: 'turnover_rate',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '换手率(%)',
      dataIndex: 'turnover_rate',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'turnover_rate[start]': value[0],
            'turnover_rate[end]': value[1],
          };
        },
      },
    },
    {
      title: '上涨家数',
      dataIndex: 'up_count',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '上涨家数',
      dataIndex: 'up_count',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'up_count[start]': value[0],
            'up_count[end]': value[1],
          };
        },
      },
    },
    {
      title: '下跌家数',
      dataIndex: 'down_count',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '下跌家数',
      dataIndex: 'down_count',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'down_count[start]': value[0],
            'down_count[end]': value[1],
          };
        },
      },
    },
    {
      title: '领涨股票',
      dataIndex: 'leading_stock',
      align: 'center',
      width: 120,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '领涨涨跌幅(%)',
      dataIndex: 'leading_stock_change',
      align: 'center',
      width: 140,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [
        <span style={{ color: text > 0 ? '#ff4d4f' : '#000000' }} key={record.id}>
          {text}
        </span>,
      ],
    },
    {
      title: '领涨涨跌幅(%)',
      dataIndex: 'leading_stock_change',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'leading_stock_change[start]': value[0],
            'leading_stock_change[end]': value[1],
          };
        },
      },
    },
    {
      title: '行业描述',
      dataIndex: 'description',
      align: 'center',
      width: 200,
      ellipsis: true,
      copyable: true,
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
      width: 300,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        <FormIndex
          id={row.id}
          key={`FormIndex-${row.id}`}
          onConfirm={() => {
            return actionRef.current?.reload();
          }}
        />,
        <Button
          key={`Logs-${row.id}`}
          type="default"
          size="small"
          icon={<FileTextOutlined />}
          onClick={() => {
            window.open(`/quant/data/industry_log?industry_id=${row.id}`, '_blank');
          }}
        >
          日志
        </Button>,
        <Button
          key={`Detail-${row.id}`}
          type="primary"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => {
            window.open(`/quant/data/stock?industry_id=${row.id}`, '_blank');
          }}
        >
          详情
        </Button>,
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
  const handleSyncList = async () => {
    setSyncLoading(true);
    try {
      const res = await syncList();
      if (res.code === 200) {
        message.success(res.message || '同步成功');
        actionRef.current?.reload();
      } else {
        message.error(res.message || '同步失败');
      }
    } finally {
      setSyncLoading(false);
    }
  };

  const handleSyncRelation = async () => {
    setSyncRelationLoading(true);
    try {
      const res = await syncRelation();
      if (res.code === 200) {
        message.success(res.message || '同步关联关系成功');
        actionRef.current?.reload();
      } else {
        message.error(res.message || '同步关联关系失败');
      }
    } finally {
      setSyncRelationLoading(false);
    }
  };

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
          const stored = localStorage.getItem('quant_data_industry_table_columns');
          return stored ? JSON.parse(stored) : {};
        })(),
        onChange: (map: any) => {
          maps = map;
        },
        persistenceKey: 'quant_data_industry_table_columns',
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
      headerTitle={
        <Space>
          <FormIndex
            onConfirm={() => {
              return actionRef.current?.reload();
            }}
          />
          <Button
            type="primary"
            icon={<SyncOutlined />}
            loading={syncLoading}
            onClick={handleSyncList}
          >
            同步行业列表
          </Button>
          <Button
            type="default"
            icon={<LinkOutlined />}
            loading={syncRelationLoading}
            onClick={handleSyncRelation}
          >
            同步关联关系
          </Button>
        </Space>
      }
    />
  );
};

export default Index;
