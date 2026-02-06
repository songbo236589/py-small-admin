# 前端页面开发

本文档介绍了前端页面的开发规范。

## 页面类型

### 1. 列表页面

展示数据列表，支持搜索、筛选、分页、排序等。

### 2. 表单页面

创建或编辑数据的表单页面。

### 3. 详情页面

查看单个资源的详细信息。

### 4. 仪表盘页面

展示统计数据和图表。

## 列表页面

### 基本结构

```typescript
import React from 'react';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { Button, Space } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';

export default function AdminList() {
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: '姓名',
      dataIndex: 'name',
    },
    {
      title: '操作',
      render: (_, record) => [
        <a key="edit">编辑</a>,
        <a key="delete">删除</a>,
      ],
    },
  ];

  return (
    <PageContainer>
      <ProTable
        columns={columns}
        request={async (params) => {
          const response = await getAdminList(params);
          return {
            data: response.data.items,
            success: true,
            total: response.data.total,
          };
        }}
        toolBarRender={() => [
          <Button key="add" type="primary">添加</Button>,
        ]}
      />
    </PageContainer>
  );
}
```

## 表单页面

### 基本结构

```typescript
import { PageContainer, ProForm, ProFormText } from '@ant-design/pro-components';

export default function AdminForm() {
  return (
    <PageContainer>
      <ProForm
        onFinish={async (values) => {
          await createAdmin(values);
        }}
      >
        <ProFormText name="name" label="姓名" />
        <ProFormText name="username" label="用户名" />
      </ProForm>
    </PageContainer>
  );
}
```

## 详情页面

### 基本结构

```typescript
import React, { useEffect, useState } from 'react';
import { PageContainer, ProDescriptions } from '@ant-design/pro-components';
import { Card, Button, Space } from 'antd';
import { history, useParams } from '@umijs/max';
import { getAdminDetail } from '@/services/api/admin';

export default function AdminDetail() {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Admin.AdminItem>();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await getAdminDetail({ id: Number(id) });
        setData(response.data);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  return (
    <PageContainer
      header={{
        title: '管理员详情',
        breadcrumb: {},
      }}
    >
      <Card>
        <ProDescriptions
          column={2}
          loading={loading}
          dataSource={data}
          columns={[
            {
              title: 'ID',
              dataIndex: 'id',
            },
            {
              title: '用户名',
              dataIndex: 'username',
            },
            {
              title: '姓名',
              dataIndex: 'name',
            },
            {
              title: '邮箱',
              dataIndex: 'email',
              span: 2,
            },
            {
              title: '手机号',
              dataIndex: 'mobile',
            },
            {
              title: '状态',
              dataIndex: 'status',
              valueEnum: {
                0: { text: '禁用', status: 'Error' },
                1: { text: '启用', status: 'Success' },
              },
            },
            {
              title: '创建时间',
              dataIndex: 'created_at',
              valueType: 'dateTime',
              span: 2,
            },
          ]}
        />
      </Card>
    </PageContainer>
  );
}
```

## 仪表盘页面

### 基本结构

```typescript
import React, { useEffect, useState } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Card, Row, Col, Statistic } from 'antd';
import { UserOutlined, ShoppingCartOutlined, DollarOutlined } from '@ant-design/icons';
import { getDashboardStats } from '@/services/api/dashboard';

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<Dashboard.Stats>();

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const response = await getDashboardStats();
        setStats(response.data);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <PageContainer>
      <Row gutter={16}>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="总用户数"
              value={stats?.totalUsers}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="总订单数"
              value={stats?.totalOrders}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="总收入"
              value={stats?.totalRevenue}
              prefix={<DollarOutlined />}
              precision={2}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>
    </PageContainer>
  );
}
```

## 列表页面（进阶）

### 搜索和筛选

```typescript
import React from 'react';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { Button, Space, Tag } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

export default function AdminList() {
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
      sorter: true,
    },
    {
      title: '用户名',
      dataIndex: 'username',
    },
    {
      title: '姓名',
      dataIndex: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        0: { text: '禁用', status: 'Error' },
        1: { text: '启用', status: 'Success' },
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      valueType: 'dateTime',
      sorter: true,
      hideInSearch: true,
    },
    {
      title: '操作',
      valueType: 'option',
      render: (_, record) => [
        <a key="edit" onClick={() => handleEdit(record)}>编辑</a>,
        <a key="delete" onClick={() => handleDelete(record)}>删除</a>,
      ],
    },
  ];

  return (
    <PageContainer>
      <ProTable
        columns={columns}
        request={async (params) => {
          const { current, pageSize, username, status, sort } = params;
          const response = await getAdminList({
            page: current,
            page_size: pageSize,
            username,
            status,
            sort,
          });
          return {
            data: response.data.items,
            success: true,
            total: response.data.total,
          };
        }}
        rowKey="id"
        search={{
          labelWidth: 'auto',
        }}
        pagination={{
          defaultPageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
        }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />}>
            添加
          </Button>,
        ]}
      />
    </PageContainer>
  );
}
```

### 分页配置

```typescript
<ProTable
  pagination={{
    // 当前页
    current: 1,
    // 每页条数
    pageSize: 10,
    // 每页条数选项
    showSizeChanger: true,
    pageSizeOptions: ['10', '20', '50', '100'],
    // 快速跳转
    showQuickJumper: true,
    // 总数显示
    showTotal: (total) => `共 ${total} 条`,
    // 简单模式
    simple: false,
  }}
/>
```

### 删除操作实现

```typescript
import { Modal } from 'antd';
import { deleteAdmin } from '@/services/api/admin';

const handleDelete = async (record: Admin.AdminItem) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除管理员 "${record.name}" 吗？`,
    onOk: async () => {
      try {
        await deleteAdmin({ id: record.id });
        message.success('删除成功');
        actionRef.current?.reload();
      } catch (error) {
        message.error('删除失败');
      }
    },
  });
};

// 在 columns 中使用
{
  title: '操作',
  render: (_, record) => [
    <a key="edit" onClick={() => handleEdit(record)}>编辑</a>,
    <a key="delete" onClick={() => handleDelete(record)}>删除</a>,
  ],
}
```

## 权限控制

### 按钮级权限控制

```typescript
import { useAccess } from '@umijs/max';

export default function AdminList() {
  const access = useAccess();

  return (
    <ProTable
      toolBarRender={() => [
        access.canCreateAdmin && (
          <Button key="add" type="primary">添加</Button>
        ),
      ]}
      columns={[
        // ...
        {
          title: '操作',
          render: (_, record) => [
            <a key="edit">编辑</a>,
            access.canDeleteAdmin && (
              <a key="delete">删除</a>,
            ),
          ],
        },
      ]}
    />
  );
}
```

### 菜单权限配置

在 `config/access.ts` 中配置权限：

```typescript
export default (initialState: { currentUser?: API.CurrentUser }) => {
  const { currentUser } = initialState || {};
  return {
    canCreateAdmin: currentUser?.permissions?.includes('admin.create'),
    canEditAdmin: currentUser?.permissions?.includes('admin.edit'),
    canDeleteAdmin: currentUser?.permissions?.includes('admin.delete'),
  };
};
```

### 路由权限控制

在路由配置中添加权限：

```typescript
{
  path: '/admin',
  component: './admin',
  access: 'canAdmin',
  routes: [
    {
      path: '/admin/list',
      component: './admin/list',
      name: '管理员列表',
    },
  ],
}
```

## 表单页面（进阶）

### 编辑/新建共用表单

```typescript
import React, { useEffect, useState } from 'react';
import { PageContainer, ProForm, ProFormText, ProFormSelect } from '@ant-design/pro-components';
import { history, useParams } from '@umijs/max';
import { getAdminDetail, createAdmin, updateAdmin } from '@/services/api/admin';

export default function AdminForm() {
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;
  const [initialValues, setInitialValues] = useState<Admin.AdminItem>();

  useEffect(() => {
    if (isEdit) {
      getAdminDetail({ id: Number(id) }).then((res) => {
        setInitialValues(res.data);
      });
    }
  }, [id, isEdit]);

  return (
    <PageContainer>
      <ProForm
        title={isEdit ? '编辑管理员' : '新建管理员'}
        initialValues={initialValues}
        onFinish={async (values) => {
          try {
            if (isEdit) {
              await updateAdmin({ id: Number(id), ...values });
            } else {
              await createAdmin(values);
            }
            message.success(isEdit ? '更新成功' : '创建成功');
            history.back();
          } catch (error) {
            message.error('操作失败');
          }
        }}
      >
        <ProFormText
          name="username"
          label="用户名"
          rules={[
            { required: true, message: '请输入用户名' },
            { pattern: /^[a-zA-Z0-9_]{4,20}$/, message: '用户名只能包含字母、数字和下划线，长度4-20位' },
          ]}
          disabled={isEdit}
        />
        <ProFormText
          name="name"
          label="姓名"
          rules={[{ required: true, message: '请输入姓名' }]}
        />
        <ProFormText.Password
          name="password"
          label="密码"
          rules={isEdit ? [] : [{ required: true, message: '请输入密码' }]}
          placeholder={isEdit ? '不填则不修改密码' : undefined}
        />
        <ProFormText
          name="email"
          label="邮箱"
          rules={[{ type: 'email', message: '请输入有效的邮箱地址' }]}
        />
        <ProFormSelect
          name="status"
          label="状态"
          options={[
            { label: '启用', value: 1 },
            { label: '禁用', value: 0 },
          ]}
          rules={[{ required: true, message: '请选择状态' }]}
        />
      </ProForm>
    </PageContainer>
  );
}
```

## 最佳实践

### 1. 使用 ProTable

使用 ProTable 提高开发效率，内置分页、搜索、筛选等功能。

### 2. 使用 ProForm

使用 ProForm 简化表单开发，支持布局、验证、联动等功能。

### 3. 统一错误处理

使用统一的错误处理方式，配合 `request` 配置自动处理错误响应。

```typescript
// app.tsx
export const request: RequestConfig = {
  errorConfig: {
    adaptor: (resData) => {
      return {
        success: resData.code === 200,
        errorMessage: resData.message,
        data: resData.data,
      };
    },
  },
};
```

### 4. 使用 TypeScript 类型定义

为 API 响应定义类型，提高代码可维护性。

```typescript
// typings/api.d.ts
declare namespace API {
  namespace Admin {
    interface AdminItem {
      id: number;
      username: string;
      name: string;
      email?: string;
      mobile?: string;
      status: number;
      created_at: string;
    }

    interface ListParams {
      page?: number;
      page_size?: number;
      username?: string;
      status?: number;
    }

    interface ListResponse {
      items: AdminItem[];
      total: number;
    }
  }
}
```

### 5. 使用自定义 Hooks

将可复用的逻辑提取为自定义 Hook。

```typescript
// hooks/useAdminList.ts
export const useAdminList = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<API.Admin.AdminItem[]>([]);
  const [total, setTotal] = useState(0);

  const fetch = async (params: API.Admin.ListParams) => {
    setLoading(true);
    try {
      const res = await getAdminList(params);
      setData(res.data.items);
      setTotal(res.data.total);
    } finally {
      setLoading(false);
    }
  };

  return { loading, data, total, fetch };
};
```

### 6. 表单验证规则

为常见字段提供验证规则模板。

```typescript
// utils/rules.ts
export const rules = {
  username: [
    { required: true, message: '请输入用户名' },
    { pattern: /^[a-zA-Z0-9_]{4,20}$/, message: '用户名只能包含字母、数字和下划线，长度4-20位' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少6位' },
  ],
  email: [
    { type: 'email' as const, message: '请输入有效的邮箱地址' },
  ],
  mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' },
  ],
};
```