import { request } from '@/utils/request';

// 获取分类树形结构
export async function getTree(params?: { status?: number | null }) {
  return request<API.ContentCategoryTree>({
    url: '/content/category/tree',
    params,
  });
}

// 获取分类列表
export async function getList(data: API.ListQequest) {
  return request({
    url: '/content/category/index',
    params: data,
  });
}

// 分类添加
export async function add(data: API.ContentCategoryForm) {
  return request({
    method: 'POST',
    url: '/content/category/add',
    data: data,
  });
}

// 分类编辑页面数据
export async function edit(id: number) {
  return request<API.ContentCategoryForm>({
    url: '/content/category/edit/' + id,
  });
}

// 分类编辑
export async function update(id: number, data: API.ContentCategoryForm) {
  return request({
    method: 'PUT',
    url: '/content/category/update/' + id,
    data: data,
  });
}

// 分类状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/content/category/set_status/' + id,
    data: data,
  });
}

// 分类排序
export async function setSort(id: number, data: { sort: number }) {
  return request({
    method: 'PUT',
    url: '/content/category/set_sort/' + id,
    data: data,
  });
}

// 分类删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/content/category/destroy/' + id,
  });
}

// 分类批量删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/content/category/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
