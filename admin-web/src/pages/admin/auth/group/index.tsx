import { CDel, CDelAll, ProTableWrapper } from '@/components';
import { destroy, destroyAll, getList, setStatus } from '@/services/admin/auth/group/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { message, Space, Switch } from 'antd';
import React, { useRef, useState } from 'react';
import AccessIndex from './components/AccessIndex';
import FormIndex from './components/FormIndex';
const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const { initialState } = useModel('@@initialState');
  let maps = {};

  const columns: ProColumns<API.AdminGroupList>[] = [
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
      title: '角色名称',
      dataIndex: 'name',
      align: 'center',
      width: 120,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '角色描述',
      dataIndex: 'content',
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
          disabled={record.id === 1}
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
      width: 210,
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
        <AccessIndex id={row.id} key={`AccessIndex-${row.id}`} disabled={row.id === 1} />,
        <CDel
          disabled={row.id === 1}
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
        getCheckboxProps: (record) => ({
          disabled: record.id === 1, // 禁止选择某行
        }),
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
          const stored = localStorage.getItem('admin_auth_group_table_columns');
          return stored ? JSON.parse(stored) : {};
        })(),
        onChange: (map: any) => {
          maps = map;
        },
        persistenceKey: 'admin_auth_group_table_columns',
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
        <FormIndex
          onConfirm={() => {
            return actionRef.current?.reload();
          }}
        />
      }
    />
  );
};

export default Index;
