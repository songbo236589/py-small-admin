import { request } from '@/utils/request';

// 系统配置编辑页面数据
export async function edit(group_code: string) {
  return request({
    url: '/admin/sys_config/edit/' + group_code,
  });
}

// 系统配置编辑
export async function update(group_code: string, data: any) {
  return request({
    method: 'PUT',
    url: '/admin/sys_config/update/' + group_code,
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 发送测试邮件
export async function sendTestEmail(data: API.TestEmailForm) {
  data.to_emails = Array.isArray(data.to_emails) ? data.to_emails.join(',') : data.to_emails || '';
  return request({
    url: '/admin/email/send_batch',
    method: 'POST',
    data: data,
  });
}
