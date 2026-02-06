import { request } from '@/utils/request';

// 获取文章列表
export async function getList(data: API.ListQequest) {
  return request({
    url: '/content/article/index',
    params: data,
  });
}

// 文章添加
export async function add(data: API.ContentArticleForm) {
  return request({
    method: 'POST',
    url: '/content/article/add',
    data: data,
  });
}

// 文章编辑页面数据
export async function edit(id: number) {
  return request<API.ContentArticleForm>({
    url: '/content/article/edit/' + id,
  });
}

// 文章编辑
export async function update(id: number, data: API.ContentArticleForm) {
  return request({
    method: 'PUT',
    url: '/content/article/update/' + id,
    data: data,
  });
}

// 文章状态
export async function setStatus(id: number, data: { status: number }) {
  return request({
    method: 'PUT',
    url: '/content/article/set_status/' + id,
    data: data,
  });
}

// 文章删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/content/article/destroy/' + id,
  });
}

// 文章批量删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/content/article/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
