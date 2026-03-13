import { request } from '@/utils/request';

// 获取标签列表
export async function getList(data: API.ListQequest) {
  return request({
    url: '/content/tag/index',
    params: data,
  });
}

// 标签添加
export async function add(data: API.ContentTagForm) {
  return request({
    method: 'POST',
    url: '/content/tag/add',
    data: data,
  });
}

// 快速创建标签（用于前端输入标签时自动创建）
export async function quickAdd(name: string) {
  return request<{ id: number; name: string; slug: string }>({
    method: 'POST',
    url: '/content/tag/quick_add',
    data: { name },
  });
}

// 标签编辑页面数据
export async function edit(id: number) {
  return request<API.ContentTagForm>({
    url: '/content/tag/edit/' + id,
  });
}

// 标签编辑
export async function update(id: number, data: API.ContentTagForm) {
  return request({
    method: 'PUT',
    url: '/content/tag/update/' + id,
    data: data,
  });
}

// 标签状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/content/tag/set_status/' + id,
    data: data,
  });
}

// 标签排序
export async function setSort(id: number, data: { sort: number }) {
  return request({
    method: 'PUT',
    url: '/content/tag/set_sort/' + id,
    data: data,
  });
}

// 标签删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/content/tag/destroy/' + id,
  });
}

// 标签批量删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/content/tag/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 获取常用标签（用于文章编辑时选择）
export async function getPopularTags(params?: { limit?: number; status?: number }) {
  return request({
    url: '/content/tag/popular',
    params: params || { limit: 100, status: 1 },
  });
}

// 搜索标签（用于远程搜索）
export async function searchTags(params: { keyword: string; limit?: number; status?: number }) {
  return request({
    url: '/content/tag/search',
    params: params,
  });
}
