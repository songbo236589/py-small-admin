import { request } from '@/utils/request';

// 获取话题列表
export async function getList(data: API.TopicRequest) {
  return request({
    url: '/content/topics/index',
    params: data,
  });
}

// 获取话题详情
export async function getDetail(id: number) {
  return request({
    url: '/content/topics/detail/' + id,
  });
}

// 抓取新话题（同步执行，预计耗时 10-30 秒）
export async function fetchTopics(data: {
  platform: string;
  platform_account_id: number;
  limit?: number;
}) {
  return request({
    method: 'POST',
    url: '/content/topics/fetch',
    data: data,
  });
}

// 话题状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/content/topics/set_status/' + id,
    data: data,
  });
}

// 删除话题
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/content/topics/destroy/' + id,
  });
}

// 批量删除话题
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/content/topics/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
