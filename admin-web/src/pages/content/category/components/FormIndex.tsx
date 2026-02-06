import { add, edit, getTree, update } from '@/services/content/category/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { Button, Form, Input, InputNumber, message, Radio, Spin, TreeSelect } from 'antd';
import React, { useRef, useState } from 'react';
import { DrawerForm } from '@ant-design/pro-components';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
  parentId?: number;
  disabled?: boolean;
}

const FormIndex: React.FC<PorpsType> = (props) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(props.id ? false : true);
  const [pidList, setPidList] = useState<any>([]);
  const [pidListLoading, setPidListLoading] = useState<boolean>(false);

  const formData: API.ContentCategoryForm = {
    id: null,
    name: '',
    slug: '',
    parent_id: props.parentId || 0,
    sort: 0,
    status: 1,
    description: '',
  };

  return (
    <DrawerForm<API.ContentCategoryForm>
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
          <Button type="primary" disabled={props.disabled ? true : false} size="small">
            <FormOutlined />
            编辑
          </Button>
        ) : props.parentId ? (
          <Button type="primary" size="small">
            <PlusOutlined />
            添加子分类
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
                if (props.parentId) {
                  await restFormRef.current?.setFieldsValue({ parent_id: props.parentId });
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
          if (props.parentId) {
            await restFormRef.current?.setFieldsValue({ parent_id: props.parentId });
          }
          if (props.id) {
            await setLoading(false);
            const res = await edit(props.id);
            if (res.code === 200) {
              await restFormRef.current?.setFieldsValue(res.data);
              await setLoading(true);
            }
          }
          await setPidListLoading(true);
          const pidRes = await getTree();
          if (pidRes.code == 200) {
            await setPidListLoading(false);
            pidRes.data.unshift({
              value: 0,
              title: '默认顶级分类',
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
              label="父分类"
              name="parent_id"
              rules={[{ required: true, message: '请选择父分类' }]}
            >
              <TreeSelect
                treeData={pidList}
                allowClear
                showSearch
                placeholder="请选择父分类"
                loading={pidListLoading}
                fieldNames={{ label: 'title', value: 'value', children: 'children' }}
              />
            </Form.Item>
            <Form.Item
              label="分类名称"
              name="name"
              rules={[{ required: true, message: '请输入分类名称' }]}
            >
              <Input maxLength={50} allowClear placeholder="请输入分类名称" showCount />
            </Form.Item>

            <Form.Item
              label="分类别名"
              name="slug"
              rules={[
                { required: true, message: '请输入分类别名' },
                { pattern: /^[a-z0-9-]+$/, message: '只能包含小写字母、数字和横线' },
              ]}
            >
              <Input maxLength={50} allowClear placeholder="请输入分类别名（如：tech）" />
            </Form.Item>

            <Form.Item label="排序" name="sort" rules={[{ required: true, message: '请输入排序' }]}>
              <InputNumber
                maxLength={11}
                placeholder="请输入排序"
                min={0}
                style={{ width: '100%' }}
              />
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

            <Form.Item label="分类描述" name="description">
              <Input.TextArea
                maxLength={200}
                allowClear
                placeholder="请输入分类描述"
                showCount
                rows={3}
              />
            </Form.Item>
          </>
        )}
      </Spin>
    </DrawerForm>
  );
};

export default FormIndex;
