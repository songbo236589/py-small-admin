import { request } from '@/utils/request';

// 获取行业管理或搜索用户（统一接口）
export async function getList(data: API.ListQequest) {
  return request({
    url: '/quant/industry/index',
    params: data,
  });
}

// 行业添加
export async function add(data: API.QuantIndustryForm) {
  return request({
    method: 'POST',
    url: '/quant/industry/add',
    data: data,
  });
}

// 行业编辑页面数据
export async function edit(id: number) {
  return request<API.QuantIndustryForm>({
    url: '/quant/industry/edit/' + id,
  });
}

// 行业编辑
export async function update(id: number, data: API.QuantIndustryForm) {
  return request({
    method: 'PUT',
    url: '/quant/industry/update/' + id,
    data: data,
  });
}

// 行业排序
export async function setSort(id: number, data: API.SortQequest) {
  return request({
    method: 'PUT',
    url: '/quant/industry/set_sort/' + id,
    data: data,
  });
}

// 行业状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/quant/industry/set_status/' + id,
    data: data,
  });
}

// 行业删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/quant/industry/destroy/' + id,
  });
}
// 行业删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/quant/industry/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 手动同步行业列表
export async function syncList() {
  return request({
    method: 'POST',
    url: '/quant/industry/sync_list',
  });
}

// 手动同步行业-股票关联关系
export async function syncRelation() {
  return request({
    method: 'POST',
    url: '/quant/industry/sync_relation',
  });
}

// 获取行业简单列表（不分页，只返回 id 和 name）
export async function simpleList(params?: { status?: number | null; sort?: string | null }) {
  return request({
    url: '/quant/industry/simple',
    params,
  });
}
