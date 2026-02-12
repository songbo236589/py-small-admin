import { add, edit, update } from '@/services/content/tag/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { DrawerForm } from '@ant-design/pro-components';
import { Button, ColorPicker, Form, Input, InputNumber, message, Radio, Spin } from 'antd';
import React, { useRef, useState } from 'react';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
}

const FormIndex: React.FC<PorpsType> = (props) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(props.id ? false : true);

  const formData: API.ContentTagForm = {
    id: null,
    name: '',
    slug: '',
    color: null,
    sort: 0,
    status: 1,
  };

  return (
    <DrawerForm<API.ContentTagForm>
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
        let res: any = {};
        // 处理颜色值
        if (values.color && typeof values.color === 'object') {
          values.color = values.color.toHexString();
        }
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
              label="标签名称"
              name="name"
              rules={[{ required: true, message: '请输入标签名称' }]}
            >
              <Input maxLength={30} allowClear placeholder="请输入标签名称" showCount />
            </Form.Item>

            <Form.Item
              label="标签别名"
              name="slug"
              rules={[
                { required: true, message: '请输入标签别名' },
                { pattern: /^[a-z0-9-]+$/, message: '只能包含小写字母、数字和横线' },
              ]}
            >
              <Input maxLength={30} allowClear placeholder="请输入标签别名（如：python）" />
            </Form.Item>

            <Form.Item label="标签颜色" name="color">
              <ColorPicker showText format="hex" style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item label="排序" name="sort">
              <InputNumber min={0} placeholder="数字越小越靠前" style={{ width: '100%' }} />
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
