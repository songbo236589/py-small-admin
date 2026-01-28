import { request } from '@/utils/request';

// 获取概念管理或搜索用户（统一接口）
export async function getList(data: API.ListQequest) {
  return request({
    url: '/quant/concept/index',
    params: data,
  });
}

// 概念添加
export async function add(data: API.QuantConceptForm) {
  return request({
    method: 'POST',
    url: '/quant/concept/add',
    data: data,
  });
}

// 概念编辑页面数据
export async function edit(id: number) {
  return request<API.QuantConceptForm>({
    url: '/quant/concept/edit/' + id,
  });
}

// 概念编辑
export async function update(id: number, data: API.QuantConceptForm) {
  return request({
    method: 'PUT',
    url: '/quant/concept/update/' + id,
    data: data,
  });
}

// 概念排序
export async function setSort(id: number, data: API.SortQequest) {
  return request({
    method: 'PUT',
    url: '/quant/concept/set_sort/' + id,
    data: data,
  });
}

// 概念状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/quant/concept/set_status/' + id,
    data: data,
  });
}

// 概念删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/quant/concept/destroy/' + id,
  });
}
// 概念删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/quant/concept/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 手动同步概念列表
export async function syncList() {
  return request({
    method: 'POST',
    url: '/quant/concept/sync_list',
  });
}

// 手动同步概念-概念关联关系
export async function syncRelation() {
  return request({
    method: 'POST',
    url: '/quant/concept/sync_relation',
  });
}

// 获取概念简单列表（不分页，只返回 id 和 name）
export async function simpleList(params?: { status?: number | null; sort?: string | null }) {
  return request({
    url: '/quant/concept/simple',
    params,
  });
}
