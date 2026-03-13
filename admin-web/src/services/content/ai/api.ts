import { request } from '@/utils/request';

// 获取可用 AI 模型列表
export async function getModels() {
  return request({
    url: '/content/ai/models',
  });
}

// AI 生成文章
export async function generateArticle(data: {
  id: number;
  mode: string;
  model?: string;
  variant_index?: number;
}) {
  return request({
    method: 'POST',
    url: '/content/ai/generate_article',
    data: data,
  });
}
