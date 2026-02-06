# 请求服务

本文档介绍了前端的 HTTP 请求封装。

## 简介

项目基于 `umi-request` 封装了统一的请求服务，提供了请求拦截、响应拦截、错误处理等功能。

## 基础使用

### 导入请求实例

```typescript
import request from '@/services/request';

// GET 请求
const data = await request('/api/user/info');

// POST 请求
const result = await request('/api/user/create', {
  method: 'POST',
  data: { name: 'John', age: 30 },
});
```

## 请求配置

### 基础配置

```typescript
import { extend } from 'umi-request';

const request = extend({
  timeout: 10000,           // 请求超时时间
  prefix: '/api',           // URL 前缀
  headers: {                // 默认请求头
    'Content-Type': 'application/json',
  },
  errorHandler: (error) => { // 错误处理
    console.error(error);
  },
});
```

### 请求参数

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| method | 请求方法 | string | GET |
| url | 请求地址 | string | - |
| data | 请求数据 | any | - |
| params | URL 参数 | object | - |
| headers | 请求头 | object | - |
| timeout | 超时时间 | number | 10000 |
| prefix | URL 前缀 | string | /api |

## 请求拦截器

### 添加请求头

```typescript
import { extend } from 'umi-request';

const request = extend({
  requestInterceptors: [
    (url, options) => {
      // 添加认证令牌
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

### 请求日志

```typescript
requestInterceptors: [
  (url, options) => {
    console.log(`[Request] ${options.method} ${url}`, options.data);
    return { url, options };
  },
]
```

## 响应拦截器

### 统一响应处理

```typescript
import { extend } from 'umi-request';

const request = extend({
  responseInterceptors: [
    (response) => {
      return response.clone().then(async (res) => {
        const data = await res.json();

        // 处理业务错误
        if (data.code !== 200) {
          throw new Error(data.message);
        }

        return data;
      });
    },
  ],
});
```

### 响应日志

```typescript
responseInterceptors: [
  (response) => {
    console.log(`[Response] ${response.status} ${response.url}`);
    return response;
  },
]
```

## 错误处理

### 统一错误处理

```typescript
import { extend } from 'umi-request';

const request = extend({
  errorHandler: (error) => {
    const { response } = error;

    if (response) {
      const { status } = response;
      switch (status) {
        case 401:
          // 未授权，跳转登录
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

### 自定义错误处理

```typescript
try {
  const data = await request('/api/user/info');
} catch (error) {
  if (error.name === 'BizError') {
    message.error(error.message);
  } else {
    message.error('请求失败');
  }
}
```

## Token 管理

### 自动刷新 Token

```typescript
let isRefreshing = false;
let subscribers: ((token: string) => void)[] = [];

function subscribeTokenRefresh(cb: (token: string) => void) {
  subscribers.push(cb);
}

function onTokenRefreshed(token: string) {
  subscribers.forEach((cb) => cb(token));
  subscribers = [];
}

const request = extend({
  responseInterceptors: [
    async (response) => {
      // Token 过期
      if (response.status === 401) {
        if (!isRefreshing) {
          isRefreshing = true;
          try {
            // 刷新 Token
            const res = await refreshToken();
            const newToken = res.access_token;
            localStorage.setItem('access_token', newToken);
            onTokenRefreshed(newToken);
          } finally {
            isRefreshing = false;
          }
        }

        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            // 重试原请求
            const originalRequest = response.clone();
            originalRequest.headers.set('Authorization', `Bearer ${token}`);
            resolve(request(originalRequest.url, originalRequest));
          });
        });
      }
      return response;
    },
  ],
});
```

## 上传文件

### 基础上传

```typescript
import request from '@/services/request';

async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  return request('/api/upload', {
    method: 'POST',
    data: formData,
  });
}
```

### 上传进度

```typescript
import request from '@/services/request';

async function uploadFileWithProgress(
  file: File,
  onProgress: (percent: number) => void
) {
  const formData = new FormData();
  formData.append('file', file);

  return request('/api/upload', {
    method: 'POST',
    data: formData,
    requestType: 'form',
    onUploadProgress: (e) => {
      const percent = (e.loaded / e.total) * 100;
      onProgress(percent);
    },
  });
}
```

## 下载文件

### 下载文件

```typescript
import request from '@/services/request';

async function downloadFile(id: string) {
  return request(`/api/files/${id}/download`, {
    method: 'GET',
    responseType: 'blob',
  }).then((blob) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'filename.ext';
    a.click();
    window.URL.revokeObjectURL(url);
  });
}
```

## 请求取消

### 使用 AbortController

```typescript
import request from '@/services/request';

const controller = new AbortController();

// 发送请求
const promise = request('/api/long-request', {
  signal: controller.signal,
});

// 取消请求
controller.abort();
```

## 完整示例

```typescript
import { extend } from 'umi-request';
import { message } from 'antd';

// 创建请求实例
const request = extend({
  timeout: 10000,
  prefix: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  // 请求拦截器
  requestInterceptors: [
    (url, options) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        options.headers.Authorization = `Bearer ${token}`;
      }
      return { url, options };
    },
  ],
  // 响应拦截器
  responseInterceptors: [
    async (response) => {
      const res = await response.clone().json();
      if (res.code !== 200) {
        throw new Error(res.message);
      }
      return res;
    },
  ],
  // 错误处理
  errorHandler: (error) => {
    const { response } = error;
    if (response) {
      switch (response.status) {
        case 401:
          message.error('请先登录');
          break;
        case 403:
          message.error('没有权限');
          break;
        case 500:
          message.error('服务器错误');
          break;
        default:
          message.error('请求失败');
      }
    } else {
      message.error('网络错误');
    }
    throw error;
  },
});

export default request;
```

## 最佳实践

### 1. API 服务模块化

```typescript
// services/api/user.ts
import request from '@/services/request';

export async function getUserInfo(id: number) {
  return request(`/api/user/${id}`);
}

export async function updateUser(id: number, data: any) {
  return request(`/api/user/${id}`, {
    method: 'PUT',
    data,
  });
}
```

### 2. 类型定义

```typescript
// types/api/user.d.ts
export interface UserInfo {
  id: number;
  username: string;
  email: string;
}

export interface UserListResponse {
  items: UserInfo[];
  total: number;
}
```

### 3. 错误重试

```typescript
import { retry } from '@/utils/request';

const data = await retry(
  () => request('/api/unstable-endpoint'),
  { times: 3, delay: 1000 }
);
```
