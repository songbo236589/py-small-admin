import type { ProFormInstance } from '@ant-design/pro-components';

import { add, edit, getList, update } from '@/services/admin/auth/rule/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import { DrawerForm } from '@ant-design/pro-components';
import { Button, Col, Form, Input, InputNumber, message, Radio, Row, Spin, TreeSelect } from 'antd';
import React, { useRef, useState } from 'react';
interface PorpsType {
  onConfirm: () => void;
  id?: number;
  pid?: number;
  disabled?: boolean;
}
const FormIndex: React.FC<PorpsType> = (porps) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(porps.id ? false : true);
  const [pidList, setPidList] = useState<any>([]);
  const [pidListLoading, setPidListLoading] = useState<boolean>(false);

  const formData: API.AdminRuleForm = {
    id: null,
    path: '',
    redirect: '',
    icon: '',
    name: '',
    type: 1,
    status: 1,
    pid: 0,
    sort: 1,
    component: '',
    target: '_self',
  };
  return (
    <DrawerForm<API.AdminRuleForm>
      layout="horizontal"
      labelCol={{ span: 4 }}
      wrapperCol={{ span: 20 }}
      formRef={restFormRef}
      initialValues={formData}
      title={porps.id ? '编辑' : '添加'}
      autoFocusFirstInput
      isKeyPressSubmit
      trigger={
        porps.id ? (
          <Button type="primary" disabled={porps.disabled ? true : false} size="small">
            <FormOutlined />
            编辑
          </Button>
        ) : porps.pid ? (
          <Button type="primary" size="small">
            <PlusOutlined />
            添加子菜单
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
                if (porps.pid) {
                  await restFormRef.current?.setFieldsValue({ pid: porps.pid });
                }
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
          if (porps.pid) {
            await restFormRef.current?.setFieldsValue({ pid: porps.pid });
          }
          if (porps.id) {
            await setLoading(false);
            const res = await edit(porps.id);
            if (res.code === 200) {
              await restFormRef.current?.setFieldsValue(res.data);
              await setLoading(true);
            }
          }
          await setPidListLoading(true);
          const pidRes = await getList();
          if (pidRes.code == 200) {
            await setPidListLoading(false);
            pidRes.data.unshift({
              value: 0,
              title: '默认顶级菜单',
            });
            await setPidList(pidRes.data);
          }
        }
      }}
    >
      <Spin spinning={loading ? false : true}>
        {loading && (
          <>
            <Form.Item
              label="父级菜单"
              name="pid"
              rules={[{ required: true, message: '请选择父级菜单' }]}
            >
              <TreeSelect
                treeData={pidList}
                allowClear
                showSearch
                placeholder="请选择父级菜单"
                loading={pidListLoading}
              />
            </Form.Item>
            <Form.Item
              label="菜单名称"
              name="name"
              rules={[{ required: true, message: '请输入菜单名称' }]}
            >
              <Input maxLength={100} allowClear placeholder="请输入菜单名称" showCount />
            </Form.Item>

            <Form.Item label="路由路径" name="path">
              <Input maxLength={100} allowClear placeholder="请输入路由路径" showCount />
            </Form.Item>
            <Form.Item label="组件路径" name="component">
              <Input maxLength={100} allowClear placeholder="请输入组件路径" showCount />
            </Form.Item>
            <Form.Item label="重定向路径" name="redirect">
              <Input maxLength={100} allowClear placeholder="请输入重定向路径" showCount />
            </Form.Item>
            <Row>
              <Col span={16}>
                <Form.Item
                  labelCol={{ span: 6 }}
                  wrapperCol={{ span: 18 }}
                  label="图标"
                  name="icon"
                >
                  <Input maxLength={100} allowClear placeholder="请输入图标" showCount />
                </Form.Item>
              </Col>
              <Col span={8}>
                <a
                  href="https://ant.design/components/icon-cn/"
                  target="_blank"
                  style={{ paddingLeft: '10px', lineHeight: '32px' }}
                  rel="noreferrer"
                >
                  去选择图标
                </a>
              </Col>
            </Row>
            <Form.Item
              name="target"
              label="链接打开方式"
              rules={[{ required: true, message: '请选择链接打开方式' }]}
            >
              <Radio.Group name="target">
                <Radio value="_self">当前窗口</Radio>
                <Radio value="_blank">新窗口</Radio>
              </Radio.Group>
            </Form.Item>
            <Row>
              <Col span={12}>
                <Form.Item
                  labelCol={{ span: 8 }}
                  wrapperCol={{ span: 16 }}
                  name="status"
                  label="状态"
                  rules={[{ required: true, message: '请选择状态' }]}
                >
                  <Radio.Group name="status">
                    <Radio value={0}>隐藏</Radio>
                    <Radio value={1}>显示</Radio>
                  </Radio.Group>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  labelCol={{ span: 6 }}
                  wrapperCol={{ span: 18 }}
                  name="type"
                  label="菜单类型"
                  rules={[{ required: true, message: '请选择菜单类型' }]}
                >
                  <Radio.Group name="type">
                    <Radio value={1}>模块</Radio>
                    <Radio value={2}>目录</Radio>
                    <Radio value={3}>菜单</Radio>
                  </Radio.Group>
                </Form.Item>
              </Col>
            </Row>
            <Form.Item label="排序" name="sort" rules={[{ required: true, message: '请输入排序' }]}>
              <InputNumber
                maxLength={11}
                placeholder="请输入排序"
                min={0}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </>
        )}
      </Spin>
    </DrawerForm>
  );
};
export default FormIndex;
