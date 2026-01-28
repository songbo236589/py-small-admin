import { request } from '@/utils/request';

// 获取角色列表
export async function get_group_list(data: any = {}) {
  return request<API.ResponseCommonList>({
    url: '/admin/group/get_group_list',
    params: data,
  });
}

// 获取角色列表或搜索用户（统一接口）
export async function getList(data: API.ListQequest) {
  return request<API.AdminGroupList>({
    url: '/admin/group/index',
    params: data,
  });
}

// 角色添加
export async function add(data: API.AdminGroupForm) {
  return request({
    method: 'POST',
    url: '/admin/group/add',
    data: data,
  });
}

// 角色编辑页面数据
export async function edit(id: number) {
  return request<API.AdminGroupForm>({
    url: '/admin/group/edit/' + id,
  });
}

// 角色编辑
export async function update(id: number, data: API.AdminGroupForm) {
  return request({
    method: 'PUT',
    url: '/admin/group/update/' + id,
    data: data,
  });
}

// 角色状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/admin/group/set_status/' + id,
    data: data,
  });
}

// 角色删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/admin/group/destroy/' + id,
  });
}
// 角色删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/admin/group/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 配置权限规则页面数据
export async function getAccess(id: number) {
  return request<API.AdminGroupForm>({
    url: '/admin/group/get_access/' + id,
  });
}

// 配置权限规则
export async function accessUpdate(id: number, data: { rules: number[] }) {
  return request({
    method: 'PUT',
    url: '/admin/group/access_update/' + id,
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
