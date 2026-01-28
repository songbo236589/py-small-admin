import { add, edit, update } from '@/services/admin/auth/admin/api';
import { get_group_list } from '@/services/admin/auth/group/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';

import { Button, Form, Input, message, Radio, Select, Spin } from 'antd';
import React, { useRef, useState } from 'react';

import { DrawerForm } from '@ant-design/pro-components';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
}
const FormIndex: React.FC<PorpsType> = (porps) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(porps.id ? false : true);
  const [groupList, setGroupList] = useState<any>([]);
  const [groupListLoading, setGroupListLoading] = useState<boolean>(false);

  const formData: API.AdminAdminForm = {
    id: null,
    username: '',
    name: '',
    phone: '',
    password: '',
    status: 1,
    group_id: null,
  };
  return (
    <DrawerForm<API.AdminAdminForm>
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

          await setGroupListLoading(true);
          const groupRes = await get_group_list();
          if (groupRes.code == 200) {
            await setGroupListLoading(false);
            await setGroupList(groupRes.data);
          }
        }
      }}
    >
      <Spin spinning={loading ? false : true}>
        {loading && (
          <div>
            <Form.Item
              label="所属角色"
              name="group_id"
              rules={[{ required: true, message: '请选择所属角色' }]}
            >
              <Select
                showSearch
                allowClear
                filterOption={(input, option: any) =>
                  (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
                }
                loading={groupListLoading}
                notFoundContent="暂无所属角色"
                placeholder="请选择所属角色"
              >
                {groupList.map((item: any) => (
                  <Select.Option key={item.id} value={item.id}>
                    {item.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              label="用户名"
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input maxLength={50} allowClear placeholder="请输入用户名" showCount />
            </Form.Item>
            <Form.Item
              label="真实姓名"
              name="name"
              rules={[{ required: true, message: '请输入真实姓名' }]}
            >
              <Input maxLength={50} allowClear placeholder="请输入真实姓名" showCount />
            </Form.Item>

            <Form.Item
              label="手机号"
              name="phone"
              rules={[{ required: true, message: '请输入机号' }]}
            >
              <Input maxLength={11} allowClear placeholder="请输入机号" showCount />
            </Form.Item>
            {!porps.id && (
              <Form.Item
                label="密码"
                name="password"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input maxLength={50} allowClear placeholder="请输入密码" showCount />
              </Form.Item>
            )}

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
