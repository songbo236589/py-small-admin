# 前端开发问题

本文档解答 Py Small Admin 前端开发的常见问题。

## 目录

- [开发环境](#开发环境)
- [组件开发](#组件开发)
- [状态管理](#状态管理)
- [样式开发](#样式开发)
- [常见问题](#常见问题)

## 开发环境

### Q: 如何搭建前端开发环境？

**A**:

1. **克隆项目**
   ```bash
   git clone https://github.com/songbo236589/py-small-admin.git
   cd py-small-admin/admin-web
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **配置环境变量**
   ```bash
   # 创建 .env.local
   UMI_APP_API_BASE_URL=http://localhost:8000/api
   UMI_APP_API_KEY=your-api-key
   ```

4. **启动开发服务器**
   ```bash
   npm start
   ```

### Q: 前端项目结构是怎样的？

**A**:

```
admin-web/
├── src/
│   ├── components/    # 公共组件
│   ├── pages/         # 页面组件
│   ├── services/      # API 服务
│   ├── hooks/         # 自定义 Hooks
│   ├── utils/         # 工具函数
│   ├── models/        # 数据模型
│   ├── styles/        # 全局样式
│   └── app.tsx        # 应用入口
├── config/            # 配置文件
├── mock/              # Mock 数据
└── package.json
```

### Q: 如何创建新的页面？

**A**:

使用 UmiJS 约定式路由：

```typescript
// src/pages/admin/users/index.tsx
import React from 'react';

const UserList: React.FC = () => {
  return <div>用户列表</div>;
};

export default UserList;
```

访问路径：`/admin/users`

### Q: 如何配置路由？

**A**:

```typescript
// config/routes.ts
export default [
  {
    path: '/admin',
    name: 'Admin',
    icon: 'SettingOutlined',
    routes: [
      {
        path: '/admin/users',
        name: 'Users',
        component: './admin/users',
      },
      {
        path: '/admin/roles',
        name: 'Roles',
        component: './admin/roles',
      },
    ],
  },
];
```

## 组件开发

### Q: 如何使用 ProComponents？

**A**:

```typescript
import { ProTable, ProColumns } from '@ant-design/pro-components';

const UserList: React.FC = () => {
  const columns: ProColumns<User>[] = [
    {
      title: '姓名',
      dataIndex: 'name',
    },
    {
      title: '操作',
      valueType: 'option',
      render: (_, record) => [
        <a key="edit" onClick={() => handleEdit(record)}>
          编辑
        </a>,
      ],
    },
  ];

  return (
    <ProTable<User>
      columns={columns}
      request={async (params) => {
        const res = await queryUsers(params);
        return {
          data: res.data.items,
          success: true,
          total: res.data.total,
        };
      }}
      rowKey="id"
      search={{
        labelWidth: 'auto',
      }}
      pagination={{
        pageSize: 10,
      }}
    />
  );
};
```

### Q: 如何使用 ModalForm？

**A**:

```typescript
import { ModalForm, ProFormText } from '@ant-design/pro-components';

const CreateUserModal: React.FC = () => {
  return (
    <ModalForm
      title="创建用户"
      trigger={<Button type="primary">新建</Button>}
      onFinish={async (values) => {
        await createUser(values);
        return true;
      }}
    >
      <ProFormText
        name="name"
        label="姓名"
        rules={[{ required: true }]}
      />
      <ProFormText
        name="email"
        label="邮箱"
        rules={[{ required: true, type: 'email' }]}
      />
    </ModalForm>
  );
};
```

### Q: 如何使用自定义 Hooks？

**A**:

```typescript
// src/hooks/useUser.ts
import { useState, useEffect } from 'react';
import { getUser } from '@/services/users';

export const useUser = (id: number) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUser(id).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [id]);

  return { user, loading };
};

// 使用
const UserProfile = ({ id }: { id: number }) => {
  const { user, loading } = useUser(id);

  if (loading) return <Spin />;
  return <div>{user?.name}</div>;
};
```

## 状态管理

### Q: 如何使用 UmiJS 内置状态管理？

**A**:

```typescript
// src/models/user.ts
import { useState } from 'umi';

export default () => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (username: string, password: string) => {
    const data = await loginApi(username, password);
    setUser(data);
    localStorage.setItem('token', data.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  return {
    user,
    login,
    logout,
  };
};

// 使用
const { user, login } = useModel('user');
```

### Q: 如何使用 React Query？

**A**:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 查询
const UserList = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  if (isLoading) return <Spin />;
  return <div>{data?.map(user => <div key={user.id}>{user.name}</div>)}</div>;
};

// 变更
const CreateUser = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      // 刷新列表
      queryClient.invalidateQueries(['users']);
    },
  });

  return <Button onClick={() => mutation.mutate(values)}>创建</Button>;
};
```

## 样式开发

### Q: 如何使用 Ant Design 主题？

**A**:

```typescript
// src/app.tsx
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

export function rootContainer(container: any) {
  return React.createElement(
    ConfigProvider,
    {
      locale: zhCN,
      theme: {
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 4,
        },
      },
    },
    container
  );
}
```

### Q: 如何使用 CSS Modules？

**A**:

```typescript
// src/pages/admin/users/index.module.less
.container {
  padding: 24px;

  .header {
    display: flex;
    justify-content: space-between;
  }
}

// 使用
import styles from './index.module.less';

const UserList = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>...</div>
    </div>
  );
};
```

### Q: 如何使用 Tailwind CSS？

**A**:

```tsx
// 直接使用 className
const UserCard = ({ user }: { user: User }) => {
  return (
    <div className="flex items-center p-4 bg-white rounded shadow">
      <img src={user.avatar} className="w-10 h-10 rounded-full" />
      <div className="ml-4">
        <h3 className="text-lg font-semibold">{user.name}</h3>
        <p className="text-gray-500">{user.email}</p>
      </div>
    </div>
  );
};
```

## 常见问题

### Q: 如何处理 API 错误？

**A**:

```typescript
// src/utils/request.ts
import { extend } from 'umi-request';

const request = extend({
  errorHandler: (error: any) => {
    const { response } = error;
    if (response) {
      const { status } = response;
      switch (status) {
        case 401:
          // 跳转登录
          window.location.href = '/login';
          break;
        case 403:
          message.error('没有权限');
          break;
        case 500:
          message.error('服务器错误');
          break;
        default:
          message.error(response.data?.message || '请求失败');
      }
    }
    throw error;
  },
});

// 请求拦截器
request.interceptors.request.use((url, options) => {
  const token = localStorage.getItem('token');
  if (token) {
    options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return { url, options };
});
```

### Q: 如何实现权限控制？

**A**:

```typescript
// src/access.ts
export default (initialState: { currentUser?: API.CurrentUser }) => {
  const { currentUser } = initialState || {};
  return {
    canAdmin: currentUser && currentUser.access === 'admin',
  };
};

// 使用
import { useAccess } from '@umijs/max';

const Page = () => {
  const access = useAccess();

  return (
    <div>
      {access.canAdmin && <Button>删除</Button>}
    </div>
  );
};
```

### Q: 如何实现国际化？

**A**:

```typescript
// src/locales/zh-CN.ts
export default {
  'pages.users.title': '用户管理',
  'pages.users.create': '新建用户',
};

// src/locales/en-US.ts
export default {
  'pages.users.title': 'User Management',
  'pages.users.create': 'Create User',
};

// 使用
import { useIntl } from '@umijs/max';

const Page = () => {
  const intl = useIntl();

  return (
    <div>
      {intl.formatMessage({ id: 'pages.users.title' })}
    </div>
  );
};
```

### Q: 如何实现文件上传？

**A**:

```typescript
import { Upload } from 'antd';

const FileUpload = () => {
  const handleChange = (info: any) => {
    if (info.file.status === 'done') {
      message.success('上传成功');
    }
    if (info.file.status === 'error') {
      message.error('上传失败');
    }
  };

  return (
    <Upload
      name="file"
      action="/api/upload"
      headers={{
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }}
      onChange={handleChange}
    >
      <Button icon={<UploadOutlined />}>点击上传</Button>
    </Upload>
  );
};
```

### Q: 如何优化首屏加载速度？

**A**:

1. **路由懒加载**
   ```typescript
   const Dashboard = React.lazy(() => import('./pages/Dashboard'));
   ```

2. **代码分割**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     build: {
       rollupOptions: {
         output: {
           manualChunks: {
             'antd': ['antd', '@ant-design/icons'],
           },
         },
       },
     },
   });
   ```

3. **使用 CDN**
   ```html
   <script src="https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js"></script>
   ```

### Q: 如何调试前端代码？

**A**:

1. **使用浏览器开发者工具**（F12）
2. **使用 React DevTools** 浏览器扩展
3. **使用 console.log 调试**
   ```typescript
   console.log('Debug info:', data);
   ```
4. **使用 debugger 断点**
   ```typescript
   debugger; // 设置断点
   ```

## 更多资源

- [API 文档](../../api/)
- [前端开发指南](../../guide/frontend/)
- [代码规范](../best-practices/code-style.md)
- [Ant Design 组件](https://ant.design/components/overview-cn/)
- [UmiJS 文档](https://umijs.org/)
