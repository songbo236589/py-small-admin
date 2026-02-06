import { CDel, CDelAll, ProTableWrapper } from '@/components';
import { destroy, destroyAll, getList, setStatus } from '@/services/content/article/api';
import { getTree as getCategoryTree } from '@/services/content/category/api';
import { getList as getTagList } from '@/services/content/tag/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Badge, message, Space, Tag } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import FormIndex from './components/FormIndex';
import PublishModal from '../publish/components/PublishModal';

const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [categoryTreeData, setCategoryTreeData] = useState<any[]>([]);
  const [tagOptions, setTagOptions] = useState<{ label: string; value: number }[]>([]);
  const { initialState } = useModel('@@initialState');
  let maps = {};

  // 获取分类树数据
  const fetchCategoryTree = async () => {
    const res = await getCategoryTree({ status: 1 });
    if (res.code === 200 && res.data) {
      setCategoryTreeData(res.data);
    }
  };

  // 获取标签列表数据
  const fetchTagOptions = async () => {
    const res = await getTagList({ page: 1, pageSize: 1000, status: 1 });
    if (res.code === 200 && res.data?.items) {
      const options = res.data.items.map((item: API.ContentTagList) => ({
        label: item.name,
        value: item.id,
      }));
      setTagOptions(options);
    }
  };

  // 页面加载时获取分类树和标签数据
  useEffect(() => {
    fetchCategoryTree();
    fetchTagOptions();
  }, []);

  const columns: ProColumns<API.ContentArticleList>[] = [
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
      title: '文章标题',
      dataIndex: 'title',
      align: 'center',
      width: 250,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '文章分类',
      dataIndex: 'category_id',
      valueType: 'treeSelect',
      width: 120,
      align: 'center',
      render: (_, record) => {
        return record.category_name || '-';
      },
      fieldProps: {
        treeDefaultExpandAll: true,
        treeData:categoryTreeData,
        showSearch: true,
        fieldNames: { label: 'title', value: 'value', children: 'children' },
        filterTreeNode:(input: string, treeNode: { title: string; }) => {
          return (treeNode.title as string)?.toLowerCase().includes(input.toLowerCase());
        }
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        0: {
          text: '草稿',
          status: 'Default',
        },
        1: {
          text: '已发布',
          status: 'Success',
        },
        2: {
          text: '审核中',
          status: 'Processing',
        },
        3: {
          text: '发布失败',
          status: 'Error',
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
      render: (_, record) => {
        const statusMap = {
          0: { text: '草稿', color: 'default' },
          1: { text: '已发布', color: 'success' },
          2: { text: '审核中', color: 'processing' },
          3: { text: '发布失败', color: 'error' },
        };
        const status = statusMap[record.status as keyof typeof statusMap];
        return <Badge status={status.color as any} text={status.text} />;
      },
    },
    {
      title: '浏览次数',
      dataIndex: 'view_count',
      hideInSearch: true,
      width: 100,
      align: 'center',
    },
    {
      title: '标签',
      dataIndex: 'tag_id',
      valueType: 'select',
      width: 150,
      align: 'center',
      hideInTable: true,
      fieldProps: {
        options: tagOptions,
        showSearch: true,
      },
    },
    {
      title: '标签',
      dataIndex: 'tags',
      hideInSearch: true,
      width: 150,
      align: 'center',
      render: (_, record) => {
        if (record.tags && record.tags.length > 0) {
          return (
            <Space size={4} wrap>
              {record.tags.map((tag: API.ContentTagList) => (
                <Tag key={tag.id} color={tag.color || 'default'}>
                  {tag.name}
                </Tag>
              ))}
            </Space>
          );
        }
        return '-';
      },
    },
    {
      title: '发布时间',
      dataIndex: 'published_at',
      key: 'published_at',
      valueType: 'dateTime',
      sorter: true,
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '发布时间',
      key: 'published_at',
      dataIndex: 'published_at',
      valueType: 'dateTimeRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'published_at[start]': value[0],
            'published_at[end]': value[1],
          };
        },
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
      width: 250,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        <PublishModal
          key={`Publish-${row.id}`}
          articleId={row.id}
          onConfirm={() => {
            return actionRef.current?.reload();
          }}
        />,
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
    <ProTableWrapper
      loading={loading}
      actionRef={actionRef}
      rowKey="id"
      rowSelection={{
        fixed: true,
        selectedRowKeys,
        onChange: (selectedRowKeys) => {
          setSelectedRowKeys(selectedRowKeys);
        },
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
          const stored = localStorage.getItem('content_article_table_columns');
          return stored ? JSON.parse(stored) : {};
        })(),
        onChange: (map: any) => {
          maps = map;
        },
        persistenceKey: 'content_article_table_columns',
        persistenceType: 'localStorage',
      }}
      tableAlertOptionRender={({ selectedRowKeys, onCleanSelected }) => {
        return (
          <Space size={16}>
            <PublishModal
              key="batchPublish"
              articleIds={selectedRowKeys}
              onConfirm={() => {
                actionRef.current?.reload();
                onCleanSelected();
              }}
            />
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
                  selectedRows: [],
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
