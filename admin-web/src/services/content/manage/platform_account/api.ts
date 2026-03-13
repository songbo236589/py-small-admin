import { request } from '@/utils/request';

// 获取平台账号列表
export async function getList(data: any) {
  return request({
    url: '/content/platform_account/index',
    params: data,
  });
}

// 平台账号添加
export async function add(data: API.ContentPlatformAccountForm) {
  return request({
    method: 'POST',
    url: '/content/platform_account/add',
    data: data,
  });
}

// 平台账号编辑页面数据
export async function edit(id: number) {
  return request<API.ContentPlatformAccountForm>({
    url: '/content/platform_account/edit/' + id,
  });
}

// 平台账号编辑
export async function update(id: number, data: API.ContentPlatformAccountForm) {
  return request({
    method: 'PUT',
    url: '/content/platform_account/update/' + id,
    data: data,
  });
}

// 平台账号状态
export async function setStatus(id: number, data: { status: number }) {
  return request({
    method: 'PUT',
    url: '/content/platform_account/set_status/' + id,
    data: data,
  });
}

// 验证Cookie
export async function verify(id: number) {
  return request({
    method: 'POST',
    url: '/content/platform_account/verify/' + id,
  });
}

// 平台账号删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/content/platform_account/destroy/' + id,
  });
}

// 平台账号批量删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/content/platform_account/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
