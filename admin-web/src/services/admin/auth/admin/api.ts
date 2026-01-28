import { request } from '@/utils/request';

// 获取管理员列表或搜索用户（统一接口）
export async function getList(data: API.ListQequest) {
  return request<API.AdminAdminList>({
    url: '/admin/admin/index',
    params: data,
  });
}

// 管理员添加
export async function add(data: API.AdminAdminForm) {
  return request({
    method: 'POST',
    url: '/admin/admin/add',
    data: data,
  });
}

// 管理员编辑页面数据
export async function edit(id: number) {
  return request<API.AdminAdminForm>({
    url: '/admin/admin/edit/' + id,
  });
}

// 管理员编辑
export async function update(id: number, data: API.AdminAdminForm) {
  return request({
    method: 'PUT',
    url: '/admin/admin/update/' + id,
    data: data,
  });
}

// 管理员状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/admin/admin/set_status/' + id,
    data: data,
  });
}

// 管理员删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/admin/admin/destroy/' + id,
  });
}
// 管理员删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/admin/admin/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 管理员初始化密码
export async function resetPwd(id: number) {
  return request({
    method: 'PUT',
    url: '/admin/admin/reset_pwd/' + id,
  });
}
