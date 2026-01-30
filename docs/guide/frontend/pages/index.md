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

## 最佳实践

### 1. 使用 ProTable

使用 ProTable 提高开发效率。

### 2. 使用 ProForm

使用 ProForm 简化表单开发。

### 3. 统一错误处理

使用统一的错误处理方式。