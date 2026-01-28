import { edit, update } from '@/services/admin/sys/sys_config/api';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm, ProFormText } from '@ant-design/pro-components';
import { Button, message, Spin } from 'antd';
import React, { useRef, useState } from 'react';
import TestEmailDrawer from './TestEmailDrawer';

const EmailConfigForm: React.FC = () => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(true);
  const formData: API.AdminEmailConfigForm = {
    smtp_host: '',
    smtp_port: '',
    smtp_username: '',
    smtp_password: '',
    mail_from_address: '',
    mail_from_name: '',
  };

  return (
    <ProForm<API.AdminEmailConfigForm>
      layout="horizontal"
      labelCol={{ span: 8 }}
      wrapperCol={{ span: 10 }}
      formRef={restFormRef}
      initialValues={formData}
      onInit={async () => {
        await setLoading(true);
        const res = await edit('email');
        if (res.code === 200) {
          restFormRef.current?.setFieldsValue(res.data);
        }
        await setLoading(false);
      }}
      onFinish={async (values) => {
        const res = await update('email', values);
        if (res.code === 200) {
          message.success(res.message);
        }
      }}
      submitter={{
        searchConfig: {
          submitText: '保存配置',
        },
        render: (props, defaultDoms) => {
          return (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
              <Button
                loading={loading}
                disabled={loading}
                key="extra-reset"
                onClick={async () => {
                  await setLoading(true);
                  const res = await edit('email');
                  if (res.code === 200) {
                    restFormRef.current?.setFieldsValue(res.data);
                  } else {
                    props.reset();
                  }
                  await setLoading(false);
                }}
              >
                重置
              </Button>
              <TestEmailDrawer />
              {defaultDoms[1]}
            </div>
          );
        },
      }}
    >
      <Spin spinning={loading}>
        <ProFormText
          name="smtp_host"
          label="SMTP服务器"
          placeholder="例如: smtp.example.com"
          fieldProps={{
            maxLength: 100,
            showCount: true,
          }}
          rules={[{ required: true, message: '请输入SMTP服务器' }]}
        />

        <ProFormText
          name="smtp_port"
          label="SMTP端口"
          placeholder="例如: 587"
          fieldProps={{
            maxLength: 10,
            showCount: true,
          }}
          rules={[{ required: true, message: '请输入SMTP端口' }]}
        />

        <ProFormText
          name="smtp_username"
          label="SMTP用户名"
          placeholder="请输入邮箱地址"
          fieldProps={{
            maxLength: 100,
            showCount: true,
          }}
          rules={[{ required: true, message: '请输入SMTP用户名' }]}
        />

        <ProFormText.Password
          name="smtp_password"
          label="SMTP密码"
          placeholder="请输入邮箱密码或授权码"
          fieldProps={{
            maxLength: 100,
          }}
          rules={[{ required: true, message: '请输入SMTP密码' }]}
        />

        <ProFormText
          name="mail_from_address"
          label="发件人地址"
          placeholder="请输入发件人地址"
          fieldProps={{
            maxLength: 100,
            showCount: true,
          }}
          rules={[{ required: true, message: '请输入发件人地址' }]}
        />

        <ProFormText
          name="mail_from_name"
          label="发件人名称"
          placeholder="请输入发件人名称"
          fieldProps={{
            maxLength: 100,
            showCount: true,
          }}
          rules={[{ required: true, message: '请输入发件人名称' }]}
        />
      </Spin>
    </ProForm>
  );
};

export default EmailConfigForm;
