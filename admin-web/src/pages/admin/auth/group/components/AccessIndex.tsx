import { accessUpdate, getAccess } from '@/services/admin/auth/group/api';
import { LockOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { DrawerForm } from '@ant-design/pro-components';
import { Button, Form, message, Spin, Tree } from 'antd';
import React, { useRef, useState } from 'react';
interface PorpsType {
  id: number;
  disabled?: boolean;
}
const AccessIndex: React.FC<PorpsType> = (porps) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [editStatus, setEditStatus] = useState<boolean>(false);
  const [accessList, setAccessList] = useState<any>([]);
  const [accessRules, setAccessRules] = useState<number[]>([]);
  const formData: API.AdminGroupAccess = {
    id: null,
    rules: [],
  };
  return (
    <DrawerForm<API.AdminGroupAccess>
      layout="horizontal"
      labelCol={{ span: 3 }}
      wrapperCol={{ span: 20 }}
      formRef={restFormRef}
      initialValues={formData}
      title={'配置规则'}
      autoFocusFirstInput
      isKeyPressSubmit
      trigger={
        <Button type="primary" disabled={porps.disabled ? true : false} size="small">
          <LockOutlined />
          配置规则
        </Button>
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
                await setLoading(false);
                const res = await getAccess(porps.id);
                if (res.code === 200) {
                  await setAccessList(res.data.list);
                  await setAccessRules(res.data.rules);
                  await setLoading(true);
                  await setEditStatus(false);
                }
              }}
            >
              重置
            </Button>,
          ];
        },
      }}
      onFinish={async () => {
        if (editStatus === false) return true;
        const res = await accessUpdate(porps.id, { rules: accessRules });
        if (res.code === 200) {
          message.success(res.message);
          return true;
        }
        return false;
      }}
      onOpenChange={async (visible) => {
        if (visible) {
          await setLoading(false);
          const res = await getAccess(porps.id);
          if (res.code === 200) {
            await setAccessList(res.data.list);
            await setAccessRules(res.data.rules);

            await setLoading(true);
            await setEditStatus(false);
          }
        }
      }}
    >
      <Spin spinning={loading ? false : true}>
        {loading && (
          <>
            <Form.Item
              label="选择菜单"
              name="rules"
              rules={[
                () => ({
                  validator() {
                    if (accessRules.length) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('请选择菜单'));
                  },
                }),
              ]}
            >
              <Tree
                checkable
                onCheck={async (checked: any, info: any) => {
                  await setAccessRules([...checked, ...info.halfCheckedKeys]);
                  await setEditStatus(true);
                }}
                defaultCheckedKeys={accessRules}
                defaultExpandAll
                showLine={true}
                treeData={accessList}
              />
            </Form.Item>
          </>
        )}
      </Spin>
    </DrawerForm>
  );
};
export default AccessIndex;
