import { request } from '@/utils/request';

// 获取发布记录列表
export async function getLogs(data: API.ListQequest) {
  return request({
    url: '/content/publish/logs',
    params: data,
  });
}

// 发布文章
export async function publishArticle(data: API.PublishArticleRequest) {
  return request({
    method: 'POST',
    url: '/content/publish/article/' + data.article_id,
    data: data,
  });
}

// 批量发布文章
export async function publishBatch(data: API.PublishBatchRequest) {
  return request({
    method: 'POST',
    url: '/content/publish/batch',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 获取发布记录详情
export async function getLogDetail(id: number) {
  return request<API.ContentPublishLogList>({
    url: '/content/publish/logs/' + id,
  });
}

// 重试发布
export async function retry(id: number) {
  return request({
    method: 'PUT',
    url: '/content/publish/retry/' + id,
  });
}
