import { request } from '@/utils/request';

// 获取概念日志列表
export async function getList(data: API.ListQequest) {
  return request({
    url: '/quant/concept_log/index',
    params: data,
  });
}

// 批量删除概念日志
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/quant/concept_log/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
