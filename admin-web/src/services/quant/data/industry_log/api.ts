import { request } from '@/utils/request';

// 获取行业日志列表
export async function getList(data: API.ListQequest) {
  return request({
    url: '/quant/industry_log/index',
    params: data,
  });
}

// 批量删除行业日志
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/quant/industry_log/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
