import { API_CONFIG, TOKEN_KEYS } from '@/config/config';
import { clearTokens, refreshAccessToken, saveTokens } from '@/services/admin/common/api';
import storage from '@/utils/storage';
import type { RequestOptions } from '@@/plugin-request/request';
import { request as umiRequest } from '@umijs/max';
import { message } from 'antd';
// 请求配置接口
export interface RequestConfig extends Omit<RequestOptions, 'headers'> {
  skipAuth?: boolean; // 是否跳过认证
  skipApiKey?: boolean; // 是否跳过API Key
  customHeaders?: Record<string, string>; // 自定义请求头
}

// 响应数据接口
export interface ResponseData<T = any> {
  code: number;
  message: string;
  data: T | any;
}

// 请求参数接口
export interface RequestParams {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'DOWNLOAD'; // 请求方法，默认GET
  url: string; // 请求地址
  data?: any; // 请求数据
  params?: any; // 请求参数
  config?: RequestConfig; // 额外配置
}

/**
 * 创建统一请求配置
 * @param config 请求配置
 * @returns 处理后的请求配置
 */
const createRequestConfig = (config: RequestConfig, method?: string): RequestOptions => {
  const { skipAuth = false, skipApiKey = false, customHeaders = {}, ...options } = config;

  // 基础请求头 - 根据请求方法设置不同的Content-Type
  const headers: Record<string, string> = {
    ...(method === 'GET' ? {} : { 'Content-Type': 'multipart/form-data' }),
    ...customHeaders,
  };

  // 添加API Key（除非明确跳过）
  if (!skipApiKey && API_CONFIG.API_KEY) {
    headers['X-API-Key'] = API_CONFIG.API_KEY;
  }

  // 添加认证Token（除非明确跳过）
  if (!skipAuth) {
    const accessToken = storage.get(TOKEN_KEYS.ACCESS_TOKEN);
    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    }
  }

  return {
    ...options,
    headers,
  };
};

/**
 * 处理请求URL，添加API前缀
 * @param url 原始URL
 * @returns 处理后的URL
 */
const processUrl = (url: string): string => {
  // 如果URL已经包含完整域名或已经是绝对路径，则不添加前缀
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/api')) {
    return url;
  }

  // 添加API前缀
  return `${API_CONFIG.BASE_URL}${url}`;
};

/**
 * 基础请求方法
 * @param config 请求配置
 * @returns Promise
 */
const customRequest = <T = any>(
  config: RequestConfig,
  method?: string,
): Promise<ResponseData<T>> => {
  const requestConfig = createRequestConfig(config, method);
  const processedUrl = processUrl(config.url || '');
  return umiRequest<ResponseData<T>>(processedUrl, requestConfig)
    .then((response) => {
      // 处理可能的undefined情况
      if (!response) {
        return {
          code: 500,
          message: '网络错误',
          data: null as T,
        };
      }
      return response;
    })
    .catch(async (error) => {
      // 检查是否是令牌相关的错误码
      const tokenErrorCodes = [477];
      const errorCode = error.response?.data?.code;

      if (tokenErrorCodes.includes(errorCode)) {
        try {
          // 获取刷新令牌
          const refreshTokenValue = storage.get(TOKEN_KEYS.REFRESH_TOKEN) as string;

          if (!refreshTokenValue) {
            // 没有刷新令牌，清除所有令牌并跳转到登录页
            clearTokens();
            window.location.href = '/login';
            return Promise.reject(error);
          }

          // 尝试刷新令牌
          const refreshResult = await refreshAccessToken(refreshTokenValue);
          if (refreshResult.code === 200) {
            // 保存新的令牌
            saveTokens(refreshResult.data);
            // return customRequest(config, method);
            // 重新发起原始请求
            const newRequestConfig = createRequestConfig(config, method);
            const retryUrl = processUrl(config.url || '');
            return umiRequest<ResponseData<T>>(retryUrl, newRequestConfig)
              .then((response) => {
                if (!response) {
                  return {
                    code: 500,
                    message: '网络错误',
                    data: null as T,
                  };
                }
                return response;
              })
              .catch(async (errorV) => {
                // 非令牌相关错误，显示错误消息
                message.error(errorV.response?.data?.message || '请求失败');
                return errorV.response?.data || { code: 500, message: '请求失败', data: null };
              });
          } else {
            // 刷新失败，清除令牌并跳转登录页
            clearTokens();
            window.location.href = '/login';
            return Promise.reject(error);
          }
        } catch (refreshError) {
          // 刷新令牌过程中出错，清除令牌并跳转登录页
          clearTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // 非令牌相关错误，显示错误消息
        message.error(error.response?.data?.message || '请求失败');
        return error.response?.data || { code: 500, message: '请求失败', data: null };
      }
    });
};

/**
 * 统一请求方法 - 封装所有HTTP方法到一个函数中
 * @param params 请求参数对象
 * @returns Promise
 */
export const request = <T = any>(params: RequestParams): Promise<ResponseData<T>> => {
  const { method = 'GET', url, data, params: queryParams, config = {} } = params;

  // 处理特殊请求类型
  if (method === 'DOWNLOAD') {
    const processedUrl = processUrl(url);
    const requestConfig = createRequestConfig(
      {
        url: processedUrl,
        method: 'GET',
        params: queryParams,
        responseType: 'blob' as any,
        ...config,
      },
      'GET',
    );

    return umiRequest<Blob>(processedUrl, requestConfig).then((response) => {
      const blob = response instanceof Blob ? response : new Blob([response as any]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = data || 'download'; // 使用data参数作为文件名
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      return {} as ResponseData<T>; // 返回空对象以满足类型要求
    });
  }

  // 处理标准HTTP方法
  return customRequest<T>(
    {
      url,
      method,
      data: method !== 'GET' ? data : undefined,
      params: method === 'GET' ? queryParams : undefined,
      ...config,
    },
    method,
  );
};

// 导出默认请求对象
export default {
  request,
};
