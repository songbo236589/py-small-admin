import { add, edit, update } from '@/services/admin/auth/group/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';

import { Button, Form, Input, message, Radio, Spin } from 'antd';
import React, { useRef, useState } from 'react';

import { DrawerForm } from '@ant-design/pro-components';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
}
const FormIndex: React.FC<PorpsType> = (porps) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(porps.id ? false : true);

  const formData: API.AdminGroupForm = {
    id: null,
    name: '',
    content: '',
    status: 1,
  };
  return (
    <DrawerForm<API.AdminGroupForm>
      layout="horizontal"
      labelCol={{ span: 3 }}
      wrapperCol={{ span: 21 }}
      formRef={restFormRef}
      initialValues={formData}
      title={porps.id ? '编辑' : '添加'}
      autoFocusFirstInput
      isKeyPressSubmit
      trigger={
        porps.id ? (
          <Button type="primary" size="small" disabled={porps.id === 1}>
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
        render: (props, defaultDoms) => {
          return [
            ...defaultDoms,
            <Button
              loading={loading ? false : true}
              key="extra-reset"
              onClick={async () => {
                const id = props.form?.getFieldValue('id');
                if (id) {
                  await setLoading(false);
                  const res = await edit(id);
                  if (res.code === 200) {
                    restFormRef.current?.setFieldsValue(res.data);

                    await setLoading(true);
                  }
                } else {
                  props.reset();
                }
              }}
            >
              重置
            </Button>,
          ];
        },
      }}
      onFinish={async (values: any) => {
        let res: any = {};
        if (porps.id) {
          res = await update(porps.id, values);
        } else {
          res = await add(values);
        }
        if (res.code === 200) {
          message.success(res.message);
          porps.onConfirm();
          return true;
        }
        return false;
      }}
      onOpenChange={async (visible) => {
        if (visible) {
          if (porps.id) {
            await setLoading(false);
            const res = await edit(porps.id);
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
              label="角色名称"
              name="name"
              rules={[{ required: true, message: '请输入角色名称' }]}
            >
              <Input maxLength={30} allowClear placeholder="请输入角色名称" showCount />
            </Form.Item>

            <Form.Item
              label="角色描述"
              name="content"
              rules={[{ required: true, message: '请输入角色描述' }]}
            >
              <Input maxLength={50} allowClear placeholder="请输入角色描述" showCount />
            </Form.Item>

            <Form.Item
              name="status"
              label="状态"
              rules={[{ required: true, message: '请选择状态' }]}
            >
              <Radio.Group name="status">
                <Radio value={0}>禁用</Radio>
                <Radio value={1}>启用</Radio>
              </Radio.Group>
            </Form.Item>
          </div>
        )}
      </Spin>
    </DrawerForm>
  );
};
export default FormIndex;
