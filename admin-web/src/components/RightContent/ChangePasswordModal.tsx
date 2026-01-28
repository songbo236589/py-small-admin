import { changePassword } from '@/services/admin/common/api';
import { LockOutlined } from '@ant-design/icons';
import { ModalForm, ProFormText } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { message } from 'antd';
import React from 'react';

type ChangePasswordModalProps = {
  open: boolean;
  onCancel: () => void;
};

const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({ open, onCancel }) => {
  const { initialState } = useModel('@@initialState');
  const { currentUser } = initialState || {};

  const handleSubmit = async (values: API.AdminChangePasswordParams) => {
    try {
      const response = await changePassword(values);
      if (response.code === 200) {
        message.success('密码修改成功');
        return true;
      } else {
        message.error(response.message || '密码修改失败');
        return false;
      }
    } catch (error: any) {
      message.error(error.message || '密码修改失败，请稍后重试');
      return false;
    }
  };

  return (
    <ModalForm<API.AdminChangePasswordParams>
      title="修改密码"
      width={600}
      open={open}
      onOpenChange={(visible) => {
        if (!visible) {
          onCancel();
        }
      }}
      onFinish={async (values) => {
        const success = await handleSubmit(values);
        if (success) {
          onCancel();
        }
        return success;
      }}
      modalProps={{
        destroyOnHidden: true,
      }}
      submitTimeout={2000}
      layout="horizontal"
      labelCol={{ span: 4 }}
      wrapperCol={{ span: 20 }}
    >
      <ProFormText
        name="username"
        label="用户名"
        placeholder="用户名"
        initialValue={currentUser?.username}
        disabled
        fieldProps={{
          autoComplete: 'username',
        }}
      />

      <ProFormText.Password
        name="old_password"
        label="原密码"
        placeholder="请输入原密码"
        fieldProps={{
          prefix: <LockOutlined />,
          autoComplete: 'current-password',
        }}
        rules={[
          {
            required: true,
            message: '请输入原密码',
          },
        ]}
      />

      <ProFormText.Password
        name="new_password"
        label="新密码"
        placeholder="请输入新密码"
        fieldProps={{
          prefix: <LockOutlined />,
          autoComplete: 'new-password',
        }}
        rules={[
          {
            required: true,
            message: '请输入新密码',
          },
          {
            min: 6,
            message: '密码长度至少6位',
          },
        ]}
      />

      <ProFormText.Password
        name="confirm_password"
        label="确认新密码"
        placeholder="请再次输入新密码"
        fieldProps={{
          prefix: <LockOutlined />,
          autoComplete: 'new-password',
        }}
        dependencies={['new_password']}
        rules={[
          {
            required: true,
            message: '请确认新密码',
          },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue('new_password') === value) {
                return Promise.resolve();
              }
              return Promise.reject(new Error('两次输入的密码不一致'));
            },
          }),
        ]}
      />
    </ModalForm>
  );
};

export default ChangePasswordModal;
