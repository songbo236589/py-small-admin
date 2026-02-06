import { CDel, NumberInput } from '@/components';
import { destroy, getTree, setSort, setStatus } from '@/services/content/category/api';
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

  const columns: ProColumns<API.ContentCategoryList>[] = [
    {
      title: '分类名称',
      dataIndex: 'name',
      hideInSearch: true,
      width: 200,
      fixed: true,
    },
    {
      title: '分类别名',
      dataIndex: 'slug',
      align: 'center',
      hideInSearch: true,
      width: 150,
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
      title: '分类描述',
      dataIndex: 'description',
      hideInSearch: true,
      width: 200,
      ellipsis: true,
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
          parentId={row.id}
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
        const res = await getTree();
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
