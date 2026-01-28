import { request } from '@/utils/request';

// 获取菜单列表或搜索用户（统一接口）
export async function getList() {
  return request<API.AdminRuleList>({
    url: '/admin/rule/index',
  });
}

// 菜单状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/admin/rule/set_status/' + id,
    data: data,
  });
}
// 菜单排序
export async function setSort(id: number, data: API.SortQequest) {
  return request({
    method: 'PUT',
    url: '/admin/rule/set_sort/' + id,
    data: data,
  });
}

// 菜单添加
export async function add(data: API.AdminRuleForm) {
  return request({
    method: 'POST',
    url: '/admin/rule/add',
    data: data,
  });
}

// 菜单编辑页面数据
export async function edit(id: number) {
  return request<API.AdminRuleForm>({
    url: '/admin/rule/edit/' + id,
  });
}

// 菜单编辑
export async function update(id: number, data: API.AdminRuleForm) {
  return request({
    method: 'PUT',
    url: '/admin/rule/update/' + id,
    data: data,
  });
}
// 菜单删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/admin/rule/destroy/' + id,
  });
}
