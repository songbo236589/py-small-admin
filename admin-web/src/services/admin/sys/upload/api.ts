import { request } from '@/utils/request';

// 获取文件列表或搜索用户（统一接口）
export async function getList(data: any) {
  return request<API.AdminUploadList>({
    url: '/admin/upload/index',
    params: data,
  });
}

// 文件删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/admin/upload/destroy/' + id,
  });
}
// 批量文件删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/admin/upload/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}
// 上传文件接口
export async function file(data: API.AdminUploadFile) {
  return request({
    method: 'POST',
    url: '/admin/upload/file',
    data: data,
  });
}
