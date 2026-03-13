import { request } from '@/utils/request';

// 获取发布记录列表
export async function getLogs(data: API.ListQequest) {
  return request({
    url: '/content/publish/logs',
    params: data,
  });
}

// 发布文章 (article_id 从 URL 路径获取，data 只包含 platform 和 platform_account_id)
export async function publishArticle(articleId: number, data: API.PublishArticleRequest) {
  return request({
    method: 'POST',
    url: '/content/publish/article/' + articleId,
    data: data,
  });
}

// 批量发布文章 (article_ids 是逗号分隔的字符串)
export async function publishBatch(data: API.PublishBatchRequest) {
  return request({
    method: 'POST',
    url: '/content/publish/batch',
    data: data,
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

// 删除发布记录
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/content/publish/destroy/' + id,
  });
}

// 批量删除发布记录
export async function destroyAll(data: { id_array: number[] }) {
  return request({
    method: 'DELETE',
    url: '/content/publish/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
