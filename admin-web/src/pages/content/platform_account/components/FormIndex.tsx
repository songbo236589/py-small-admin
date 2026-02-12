import { add, edit, update } from '@/services/content/platform_account/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { Button, Form, Input, message, Radio, Select, Spin } from 'antd';
import React, { useRef, useState } from 'react';
import { DrawerForm } from '@ant-design/pro-components';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
}

// 平台选项
const platformOptions: { label: string; value: string }[] = [
  { label: '知乎', value: 'zhihu' },
];

const FormIndex: React.FC<PorpsType> = (props) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(props.id ? false : true);

  const formData: API.ContentPlatformAccountForm = {
    id: null,
    platform: 'zhihu',
    account_name: '',
    cookies: '',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    status: 1,
  };

  return (
    <DrawerForm<API.ContentPlatformAccountForm>
      layout="horizontal"
      labelCol={{ span: 4 }}
      wrapperCol={{ span: 20 }}
      formRef={restFormRef}
      initialValues={formData}
      title={props.id ? '编辑' : '添加'}
      autoFocusFirstInput
      isKeyPressSubmit
      trigger={
        props.id ? (
          <Button type="primary" size="small">
            <FormOutlined />
            编辑
          </Button>
        ) : (
          <Button type="primary">
            <PlusOutlined />
            添加
          </Button>
        )
      }
      drawerProps={{
        forceRender: true,
        destroyOnClose: true,
      }}
      submitter={{
        render: (submitterProps, defaultDoms) => {
          return [
            ...defaultDoms,
            <Button
              loading={loading ? false : true}
              key="extra-reset"
              onClick={async () => {
                const id = submitterProps.form?.getFieldValue('id');
                if (id) {
                  await setLoading(false);
                  const res = await edit(id);
                  if (res.code === 200) {
                    restFormRef.current?.setFieldsValue(res.data);
                    await setLoading(true);
                  }
                } else {
                  submitterProps.reset();
                }
              }}
            >
              重置
            </Button>,
          ];
        },
      }}
      onFinish={async (values: any) => {
        // 验证cookies是否为有效的JSON
        try {
          if (values.cookies) {
            JSON.parse(values.cookies);
          }
        } catch (e) {
          message.error('Cookies必须是有效的JSON格式');
          return false;
        }

        let res: any = {};
        if (props.id) {
          res = await update(props.id, values);
        } else {
          res = await add(values);
        }
        if (res.code === 200) {
          message.success(res.message);
          props.onConfirm();
          return true;
        }
        return false;
      }}
      onOpenChange={async (visible) => {
        if (visible) {
          if (props.id) {
            await setLoading(false);
            const res = await edit(props.id);
            if (res.code === 200) {
              await restFormRef.current?.setFieldsValue(res.data);
              await setLoading(true);
            }
          }
        }
      }}
    >
      <Spin spinning={loading ? false : true}>
        {loading && (
          <div>
            <Form.Item
              label="发布平台"
              name="platform"
              rules={[{ required: true, message: '请选择发布平台' }]}
            >
              <Select placeholder="请选择发布平台" options={platformOptions} />
            </Form.Item>

            <Form.Item
              label="账号名称"
              name="account_name"
              rules={[{ required: true, message: '请输入账号名称' }]}
            >
              <Input maxLength={50} allowClear placeholder="请输入账号名称" showCount />
            </Form.Item>

            <Form.Item
              label="Cookies"
              name="cookies"
              rules={[
                { required: true, message: '请输入Cookies' },
              ]}
              extra="请输入JSON格式的Cookie信息"
            >
              <Input.TextArea
                allowClear
                placeholder='请输入Cookies，例如：{"session_id": "xxx", "token": "xxx"}'
                rows={6}
              />
            </Form.Item>

            <Form.Item
              label="浏览器UA"
              name="user_agent"
            >
              <Input
                allowClear
                placeholder="请输入浏览器User-Agent（可选）"
                showCount
                maxLength={500}
              />
            </Form.Item>

            <Form.Item
              name="status"
              label="状态"
              rules={[{ required: true, message: '请选择状态' }]}
            >
              <Radio.Group name="status">
                <Radio value={0}>失效</Radio>
                <Radio value={1}>有效</Radio>
                <Radio value={2}>过期</Radio>
              </Radio.Group>
            </Form.Item>
          </div>
        )}
      </Spin>
    </DrawerForm>
  );
};

export default FormIndex;
