import { ProFormTinyMCE } from '@/components';
import { sendTestEmail } from '@/services/admin/sys/sys_config/api';
import { MailOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import {
  DrawerForm,
  ProFormRadio,
  ProFormSelect,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { Button, message } from 'antd';
import React, { useRef, useState } from 'react';

interface TestEmailDrawerProps {
  onConfirm?: () => void;
}

const TestEmailDrawer: React.FC<TestEmailDrawerProps> = ({ onConfirm }) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [contentType, setContentType] = useState<string>('html');
  const formData: API.TestEmailForm = {
    to_emails: null,
    subject: '',
    content: '',
    content_type: 'html',
    attachments: '',
  };
  return (
    <DrawerForm<API.TestEmailForm>
      title="发送测试邮件"
      layout="horizontal"
      labelCol={{ span: 3 }}
      wrapperCol={{ span: 21 }}
      formRef={restFormRef}
      initialValues={formData}
      autoFocusFirstInput
      isKeyPressSubmit
      onValuesChange={(changedValues) => {
        if (changedValues.content_type !== undefined) {
          setContentType(changedValues.content_type);
          restFormRef.current?.setFieldsValue({ content: '' });
        }
      }}
      trigger={
        <button
          type="button"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 15px',
            fontSize: '14px',
            lineHeight: '1.5715',
            background: '#ffffff',
            border: '1px solid #d9d9d9',
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'all 0.3s',
            color: '#000000d9',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#4096ff';
            e.currentTarget.style.color = '#4096ff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#d9d9d9';
            e.currentTarget.style.color = '#000000d9';
          }}
        >
          <MailOutlined />
          测试邮件
        </button>
      }
      drawerProps={{
        forceRender: true,
        destroyOnClose: true,
      }}
      submitter={{
        render: (props, defaultDoms) => {
          return [
            ...defaultDoms,
            <Button
              key="extra-reset"
              onClick={() => {
                props.reset();
              }}
            >
              重置
            </Button>,
          ];
        },
      }}
      onFinish={async (values) => {
        const res = await sendTestEmail(values);
        if (res.code === 200) {
          message.success(res.message);
          onConfirm?.();
          return true;
        }
        return false;
      }}
    >
      <ProFormSelect
        name="to_emails"
        label="收件人邮箱"
        mode="tags"
        placeholder="请输入收件人邮箱，按回车添加"
        fieldProps={{
          showSearch: true,
          tokenSeparators: [',', ' '],
          maxTagCount: 'responsive',
        }}
        rules={[
          { required: true, message: '请输入收件人邮箱' },
          {
            validator: (_, value) => {
              if (!value || value.length === 0) {
                return Promise.resolve();
              }
              const emailRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
              const invalidEmails = value.filter((email: string) => !emailRegex.test(email));
              if (invalidEmails.length > 0) {
                return Promise.reject(new Error(`以下邮箱格式不正确：${invalidEmails.join(', ')}`));
              }
              return Promise.resolve();
            },
          },
        ]}
      />

      <ProFormText
        name="subject"
        label="邮件主题"
        placeholder="请输入邮件主题"
        rules={[{ required: true, message: '请输入邮件主题' }]}
        fieldProps={{
          maxLength: 200,
          showCount: true,
        }}
      />
      <ProFormRadio.Group
        name="content_type"
        label="内容类型"
        rules={[{ required: true, message: '请选择内容类型' }]}
        options={[
          { label: 'HTML', value: 'html' },
          { label: '纯文本', value: 'plain' },
        ]}
      />
      {contentType === 'plain' ? (
        <ProFormTextArea
          name="content"
          label="邮件内容"
          placeholder="请输入邮件内容（纯文本）"
          rules={[{ required: true, message: '请输入邮件内容' }]}
          fieldProps={{
            maxLength: 5000,
            showCount: true,
            autoSize: { minRows: 8, maxRows: 16 },
          }}
        />
      ) : (
        <ProFormTinyMCE
          name="content"
          label="邮件内容"
          placeholder="请输入邮件内容（支持HTML）"
          rules={[{ required: true, message: '请输入邮件内容' }]}
          formRef={restFormRef}
          height={1000}
        />
      )}

      <ProFormTextArea
        name="attachments"
        label="附件路径"
        placeholder="请输入附件路径，多个路径用逗号分隔（可选）"
        fieldProps={{
          maxLength: 1000,
          showCount: true,
          autoSize: { minRows: 2, maxRows: 4 },
        }}
      />
    </DrawerForm>
  );
};

export default TestEmailDrawer;
