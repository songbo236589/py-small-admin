# 前端服务封装

本文档介绍了前端 API 服务的封装和使用。

## 简介

前端服务层是对后端 API 的封装，提供了类型安全的 API 调用方法。

## 服务目录结构

```
src/services/
├── admin/
│   ├── auth/
│   │   ├── admin.ts       # 管理员 API
│   │   ├── group.ts       # 角色组 API
│   │   └── rule.ts        # 菜单规则 API
│   ├── common/
│   │   ├── upload.ts      # 上传 API
│   │   └── captcha.ts     # 验证码 API
│   └── sys/
│       ├── config.ts      # 系统配置 API
│       └── email.ts       # 邮件 API
└── quant/
    └── data/
        ├── stock.ts       # 股票 API
        ├── industry.ts    # 行业 API
        └── concept.ts      # 概念 API
```

## 类型定义

### 基础类型

```typescript
// typings/api.d.ts
declare namespace API {
  // 当前用户信息
  interface CurrentUser {
    id: number;
    username: string;
    name: string;
    phone?: string;
    group_id?: number;
    group_name?: string;
  }

  // 分页请求参数
  interface PaginationParams {
    page?: number;
    limit?: number;
    sort?: string;
    [key: string]: any;
  }

  // 分页响应
  interface PaginationResponse<T> {
    items: T[];
    total: number;
    page: number;
    limit: number;
  }

  // 统一响应格式
  interface BaseResponse<T> {
    code: number;
    message: string;
    data: T;
  }
}
```

### Admin 模块类型

```typescript
declare namespace API {
  // 管理员
  interface Admin {
    id: number;
    username: string;
    name: string;
    phone?: string;
    group_id?: number;
    group_name?: string;
    status: number;
    created_at: string;
    updated_at: string;
  }

  // 角色组
  interface Group {
    id: number;
    name: string;
    content?: string;
    rules?: string;
    status: number;
  }

  // 菜单规则
  interface Rule {
    id: number;
    pid: number;
    name: string;
    path: string;
    component?: string;
    type: number;
    icon?: string;
    sort: number;
  }
}
```

## 服务函数定义

### 基本结构

```typescript
// services/admin/auth/admin.ts
import { request } from '@/utils/request';
import type { BaseResponse, PaginationResponse } from '@/typings';

export interface Admin {
  id: number;
  username: string;
  name: string;
}

/**
 * 获取管理员列表
 */
export async function getAdminList(params?: API.PaginationParams): Promise<BaseResponse<PaginationResponse<Admin>>> {
  return request('/admin/admin/index', {
    method: 'GET',
    params,
  });
}

/**
 * 创建管理员
 */
export async function createAdmin(data: Partial<Admin>): Promise<BaseResponse<Admin>> {
  return request('/admin/admin/add', {
    method: 'POST',
    data,
  });
}

/**
 * 更新管理员
 */
export async function updateAdmin(id: number, data: Partial<Admin>): Promise<BaseResponse<Admin>> {
  return request(`/admin/admin/update/${id}`, {
    method: 'PUT',
    data,
  });
}

/**
 * 删除管理员
 */
export async function deleteAdmin(id: number): Promise<BaseResponse<null>> {
  return request(`/admin/admin/destroy/${id}`, {
    method: 'DELETE',
  });
}

/**
 * 批量删除管理员
 */
export async function deleteAdmins(ids: number[]): Promise<BaseResponse<null>> {
  return request('/admin/admin/destroy_all', {
    method: 'DELETE',
    data: { id_array: ids },
  });
}
```

## 请求拦截器

### 添加认证令牌

```typescript
// utils/request.ts
import { extend } from 'umi-request';

const request = extend({
  requestInterceptors: [
    (url, options) => {
      // 从 localStorage 获取 token
      const token = localStorage.getItem('access_token');
      if (token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token}`,
        };
      }
      return { url, options };
    },
  ],
});
```

## 响应拦截器

### 统一响应处理

```typescript
// utils/request.ts
const request = extend({
  responseInterceptors: [
    async (response) => {
      const res = await response.clone().json();

      // 处理业务错误
      if (res.code !== 200) {
        throw new Error(res.message);
      }

      // 处理 Token 过期
      if (res.code === 401) {
        // 跳转登录
        window.location.href = '/login';
      }

      return res;
    },
  ],
});
```

## 服务使用示例

### 在组件中使用

```typescript
import React, { useEffect, useState } from 'react';
import { getAdminList, deleteAdmin } from '@/services/admin/auth/admin';
import type { Admin } from '@/typings';

export default function AdminList() {
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<Admin[]>([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await getAdminList({ page: 1, limit: 20 });
      setDataSource(res.data.items);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    await deleteAdmin(id);
    fetchData();
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    // ...
  );
}
```

### 使用 Hooks 封装

```typescript
// hooks/useAdminList.ts
import { useState, useEffect } from 'react';
import { getAdminList } from '@/services/admin/auth/admin';
import type { Admin } from '@/typings';

export function useAdminList(params?: API.PaginationParams) {
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<Admin[]>([]);
  const [total, setTotal] = useState(0);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await getAdminList(params);
      setDataSource(res.data.items);
      setTotal(res.data.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [params]);

  return { loading, dataSource, total, fetchData };
}
```

## 错误处理

### 统一错误处理

```typescript
// utils/request.ts
import { message } from 'antd';

const request = extend({
  errorHandler: (error) => {
    const { response } = error;

    if (response) {
      switch (response.status) {
        case 401:
          message.error('请先登录');
          window.location.href = '/login';
          break;
        case 403:
          message.error('没有权限');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error('服务器错误');
          break;
        default:
          message.error('请求失败');
      }
    } else {
      message.error('网络错误，请检查网络连接');
    }

    throw error;
  },
});
```

## 服务模块化

### 按功能模块划分

```
services/
├── admin/           # Admin 模块 API
├── quant/           # Quant 模块 API
├── common/          # 公共 API
└── types.ts         # 类型定义
```

### 按业务划分

```
services/
├── auth/            # 认证相关
├── user/            # 用户相关
├── content/         # 内容相关
└── system/          # 系统相关
```

## 最佳实践

### 1. 使用 TypeScript 类型

为所有 API 定义类型：

```typescript
export interface User {
  id: number;
  username: string;
}

export async function getUser(id: number): Promise<BaseResponse<User>> {
  return request(`/api/user/${id}`);
}
```

### 2. 统一命名规范

- 获取列表：`get{Resource}List`
- 创建：`create{Resource}`
- 更新：`update{Resource}`
- 删除：`delete{Resource}`

### 3. 使用枚举

```typescript
// typings/enums.d.ts
export enum UserStatus {
  Disabled = 0,
  Enabled = 1,
}

// 在 API 中使用
export async function getUsersByStatus(status: UserStatus) {
  return request('/api/user', {
    params: { status },
  });
}
```

### 4. 缓存策略

```typescript
// hooks/useCache.ts
const cache = new Map();

export function useCachedRequest<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl = 60000
) {
  const [data, setData] = useState<T | null>(null);

  useEffect(() => {
    const cached = cache.get(key);
    if (cached) {
      setData(cached);
      return;
    }

    fetcher().then((result) => {
      setData(result);
      cache.set(key, result);
      setTimeout(() => cache.delete(key), ttl);
    });
  }, [key, fetcher, ttl]);

  return data;
}
```

## 相关文档

- [请求服务](./request.md)
- [API 列表](./api-list.md)
- [类型定义](../../typings.d.ts)
