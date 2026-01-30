# 前端服务封装

本文档介绍了 API 服务的封装。

## 服务目录结构

```
src/services/
├── admin/
│   ├── auth/admin/
│   ├── auth/group/
│   ├── auth/rule/
│   ├── common/
│   └── sys/
└── quant/
    └── data/
        ├── stock/
        ├── industry/
        └── concept/
```

## 服务定义

### 类型定义

```typescript
// typings.d.ts
declare namespace API {
  interface CurrentUser {
    id: number;
    name: string;
    username: string;
  }

  interface Admin {
    id: number;
    name: string;
    username: string;
  }

  interface PaginationResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
  }

  interface BaseResponse<T> {
    code: number;
    message: string;
    data: T;
  }
}
```

### 服务函数

```typescript
// services/admin/auth/admin/api.ts
import { request } from '@/utils/request';
import type { BaseResponse, PaginationResponse } from '@/typings';

export interface Admin {
  id: number;
  name: string;
  username: string;
}

export async function getAdminList(params?: any): Promise<BaseResponse<PaginationResponse<Admin>>> {
  return request('/admin/admin/index', {
    method: 'GET',
    params,
  });
}

export async function createAdmin(data: Partial<Admin>): Promise<BaseResponse<Admin>> {
  return request('/admin/admin/add', {
    method: 'POST',
    data,
  });
}
```

## 最佳实践

1. 使用 TypeScript 类型
2. 统一错误处理
3. 统一响应格式
4. 使用缓存优化