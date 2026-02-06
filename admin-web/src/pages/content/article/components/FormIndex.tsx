import { add, edit, update } from '@/services/content/article/api';
import { getTree as getCategoryTree } from '@/services/content/category/api';
import { getList as getTagList } from '@/services/content/tag/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { Button, Form, Input, message, Radio, Select, Spin, TreeSelect } from 'antd';
import React, { useRef, useState } from 'react';
import { DrawerForm } from '@ant-design/pro-components';
import ProFormTinyMCE from '@/components/common/ProFormTinyMCE';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
}

const FormIndex: React.FC<PorpsType> = (props) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(props.id ? false : true);
  const [categoryTreeData, setCategoryTreeData] = useState<any[]>([]);
  const [tagOptions, setTagOptions] = useState<{ label: string; value: number }[]>([]);
  const [categoryLoading, setCategoryLoading] = useState<boolean>(false);
  const [tagLoading, setTagLoading] = useState<boolean>(false);

  const formData: API.ContentArticleForm = {
    id: null,
    title: '',
    content: '',
    summary: '',
    cover_image_id: null,
    category_id: null,
    tag_ids: [],
    status: 0,
  };

  return (
    <DrawerForm<API.ContentArticleForm>
      layout="horizontal"
      labelCol={{ span: 3 }}
      wrapperCol={{ span: 21 }}
      formRef={restFormRef}
      initialValues={formData}
      title={props.id ? '编辑文章' : '添加文章'}
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
        width: 900,
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
        // 将 tag_ids 数组转换为逗号分隔的字符串
        const submitData = {
          ...values,
          tag_ids: values.tag_ids?.join(',') || '',
        };
        if (props.id) {
          res = await update(props.id, submitData);
        } else {
          res = await add(submitData);
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
          // 加载编辑数据
          if (props.id) {
            await setLoading(false);
            const res = await edit(props.id);
            if (res.code === 200) {
              await restFormRef.current?.setFieldsValue(res.data);
              await setLoading(true);
            }
          }

          // 加载分类树数据
          await setCategoryLoading(true);
          const categoryRes = await getCategoryTree({ status: 1 });
          if (categoryRes.code === 200 && categoryRes.data) {
            await setCategoryTreeData(categoryRes.data);
          }
          await setCategoryLoading(false);

          // 加载标签数据
          await setTagLoading(true);
          const tagRes = await getTagList({ page: 1, pageSize: 1000 });
          if (tagRes.code === 200 && tagRes.data?.items) {
            const options = tagRes.data.items
              .filter((item: API.ContentTagList) => item.status === 1)
              .map((item: API.ContentTagList) => ({
                label: item.name,
                value: item.id,
              }));
            await setTagOptions(options);
          }
          await setTagLoading(false);
        }
      }}
    >
      <Spin spinning={loading ? false : true}>
        {loading && (
          <div>
            <Form.Item
              label="文章标题"
              name="title"
              rules={[{ required: true, message: '请输入文章标题' }]}
            >
              <Input maxLength={200} allowClear placeholder="请输入文章标题" showCount />
            </Form.Item>

            <Form.Item
              label="文章分类"
              name="category_id"
              rules={[{ required: true, message: '请选择文章分类' }]}
            >
              <TreeSelect
                placeholder="请选择文章分类"
                allowClear
                showSearch
                treeData={categoryTreeData}
                loading={categoryLoading}
                treeDefaultExpandAll
                fieldNames={{ label: 'title', value: 'value', children: 'children' }}
                filterTreeNode={(input, treeNode) => {
                  return (treeNode.title as string)?.toLowerCase().includes(input.toLowerCase());
                }}
              />
            </Form.Item>

            <Form.Item
              label="文章标签"
              name="tag_ids"
            >
              <Select
                mode="multiple"
                placeholder="请选择文章标签（可多选）"
                allowClear
                options={tagOptions}
                loading={tagLoading}
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                maxTagCount={5}
              />
            </Form.Item>

            <Form.Item
              label="文章摘要"
              name="summary"
            >
              <Input.TextArea
                maxLength={500}
                allowClear
                placeholder="请输入文章摘要"
                showCount
                rows={3}
              />
            </Form.Item>

            <ProFormTinyMCE
              formRef={restFormRef}
              name="content"
              label="文章内容"
              placeholder="请输入文章内容..."
              rules={[{ required: true, message: '请输入文章内容' }]}
              required
              height={500}
            />

            <Form.Item
              name="status"
              label="状态"
              rules={[{ required: true, message: '请选择状态' }]}
            >
              <Radio.Group name="status">
                <Radio value={0}>草稿</Radio>
                <Radio value={1}>已发布</Radio>
                <Radio value={2}>审核中</Radio>
                <Radio value={3}>发布失败</Radio>
              </Radio.Group>
            </Form.Item>
          </div>
        )}
      </Spin>
    </DrawerForm>
  );
};

export default FormIndex;
