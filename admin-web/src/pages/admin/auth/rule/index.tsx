import { CDel, NumberInput } from '@/components';

import { destroy, getList, setSort, setStatus } from '@/services/admin/auth/rule/api';

import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { message, Switch } from 'antd';
import React, { useRef, useState } from 'react';
import FormIndex from './components/FormIndex';
const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  // 存储所有id的数组（用于默认展开）
  const [allIds, setAllIds] = useState<number[]>([]);

  // 核心：递归提取所有层级的id
  const getAllIds = (data: any[]): number[] => {
    let ids: number[] = [];
    data.forEach((item) => {
      // 收集当前节点的id
      ids.push(item.id);
      // 如果有children，递归收集子节点的id并合并
      if (item.children && Array.isArray(item.children) && item.children.length > 0) {
        ids = [...ids, ...getAllIds(item.children)];
      }
    });
    return ids;
  };

  const columns: ProColumns<API.AdminRuleList>[] = [
    {
      title: '菜单名称',
      dataIndex: 'name',
      hideInSearch: true,
      width: 200,
      fixed: true,
    },

    {
      title: '路由文件',
      dataIndex: 'path',
      align: 'center',
      hideInSearch: true,
      width: 200,
    },
    {
      title: '组件路径',
      dataIndex: 'component',
      align: 'center',
      hideInSearch: true,
      width: 200,
    },
    {
      title: '重定向路径',
      dataIndex: 'redirect',
      align: 'center',
      hideInSearch: true,
      width: 200,
    },
    {
      title: '链接打开方式',
      dataIndex: 'target',
      align: 'center',
      hideInSearch: true,
      width: 100,
      valueType: 'select',
      valueEnum: {
        _self: { text: '当前窗口', status: '_self' },
        _blank: { text: '新窗口', status: '_blank' },
      },
    },
    {
      title: '菜单类型',
      dataIndex: 'type',
      align: 'center',
      hideInSearch: true,
      width: 100,
      valueType: 'select',
      valueEnum: {
        1: { text: '模块', status: '1' },
        2: { text: '目录', status: '2' },
        3: { text: '菜单', status: '3' },
      },
    },
    {
      title: '排序',
      dataIndex: 'sort',
      hideInSearch: true,
      width: 100,
      align: 'center',
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
      title: '状态',
      dataIndex: 'status',
      hideInSearch: true,
      width: 100,
      align: 'center',
      render: (text, record) => [
        <Switch
          key={record.id + record.status}
          checkedChildren="显示"
          unCheckedChildren="隐藏"
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
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '更新时间',
      key: 'updated_at',
      dataIndex: 'updated_at',
      valueType: 'dateTime',
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '操作',
      key: 'option',
      width: 270,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        <FormIndex
          pid={row.id}
          key={`FormIndex-${row.id}`}
          onConfirm={() => {
            return actionRef.current?.reload();
          }}
        />,
        <FormIndex
          id={row.id}
          key={`FormIndex1-${row.id}`}
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
    <ProTable
      loading={loading}
      scroll={{ x: 1300, y: 'calc(100vh - 400px)' }}
      actionRef={actionRef}
      rowKey="id"
      options={{ fullScreen: true }}
      columns={columns}
      search={false}
      pagination={false}
      expandable={{
        defaultExpandAllRows: true,
        // expandRowByClick: true,
        expandedRowKeys: allIds,
        onExpand: (expanded, record) => {
          if (expanded) {
            // 展开时：添加当前行id到数组
            setAllIds((prev) => [...prev, record.id]);
          } else {
            // 收起时：从数组中移除当前行id
            setAllIds((prev) => prev.filter((id) => id !== record.id));
          }
        },
      }}
      request={async () => {
        setLoading(true);
        const res = await getList();
        // 获取数据后，提取所有id并更新状态
        const allIdsData = getAllIds(res.data);
        setAllIds(allIdsData);
        setLoading(false);
        return { success: true, data: res.data };
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
