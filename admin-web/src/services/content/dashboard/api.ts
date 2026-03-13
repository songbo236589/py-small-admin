import { request } from '@/utils/request';

// 获取内容统计数据
export async function getStatistics() {
  return request<API.ContentDashboardStatistics>({
    url: '/content/dashboard/statistics',
  });
}
