import ProFormTinyMCE from '@/components/common/ProFormTinyMCE';
import { add, edit, update } from '@/services/content/manage/article/api';
import { getTree as getCategoryTree } from '@/services/content/manage/category/api';
import {
  getPopularTags,
  quickAdd as quickAddTag,
  searchTags,
} from '@/services/content/manage/tag/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { DrawerForm } from '@ant-design/pro-components';
import { Button, Form, Input, message, Radio, Select, Spin, TreeSelect } from 'antd';
import React, { useCallback, useRef, useState } from 'react';

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
  const [tagSearching, setTagSearching] = useState<boolean>(false);
  const [creatingTag, setCreatingTag] = useState<boolean>(false);

  // 处理标签选择：自定义标签按回车时创建并返回 ID
  const handleTagChange = useCallback(
    async (values: (string | number)[]) => {
      console.log('[handleTagChange] 输入值:', values);

      // 获取已存在标签的所有 value
      const existingValues = new Set(tagOptions.map((opt) => opt.value));
      console.log('[handleTagChange] 已存在的标签值:', Array.from(existingValues));

      // 区分已存在的标签和需要创建的自定义标签
      // 检查值是否在已存在标签中
      const existingTagIds = values.filter((v) => existingValues.has(v as number));
      const customTags = values
        .filter((v) => !existingValues.has(v as number))
        .map((v) => String(v).trim())
        .filter((name) => name.length > 0);

      console.log('[handleTagChange] 已存在标签 ID:', existingTagIds);
      console.log('[handleTagChange] 需要创建的自定义标签:', customTags);

      // 如果没有自定义标签，直接更新表单值
      if (customTags.length === 0) {
        const tagIds = values
          .map((v) => (typeof v === 'number' ? v : parseInt(v as string)))
          .filter((id) => !isNaN(id));
        console.log('[handleTagChange] 设置表单值 tag_ids (仅已存在标签):', tagIds);
        restFormRef.current?.setFieldsValue({ tag_ids: tagIds });
        return;
      }

      // 有自定义标签需要创建
      setCreatingTag(true);
      try {
        // 并发创建所有自定义标签
        const createPromises = customTags.map((tagName) => quickAddTag(tagName));
        const results = await Promise.all(createPromises);

        console.log('[handleTagChange] 创建标签结果:', results);

        const newTagIds = results.filter((res) => res.code === 200).map((res) => res.data!.id);
        console.log('[handleTagChange] 新创建的标签 ID:', newTagIds);

        // 更新选项列表
        const newOptions = results
          .filter((res) => res.code === 200)
          .map((res) => ({ label: String(res.data!.name), value: res.data!.id }));
        if (newOptions.length > 0) {
          setTagOptions((prev) => [...prev, ...newOptions]);
          console.log('[handleTagChange] 更新后的选项列表:', newOptions);
        }

        // 合并所有标签 ID：已存在标签 + 新创建的标签 ID
        const allTagIds = [...existingTagIds, ...newTagIds];
        console.log('[handleTagChange] 最终所有标签 ID:', allTagIds);

        // 更新表单值为纯 ID 数组
        restFormRef.current?.setFieldsValue({ tag_ids: allTagIds });
      } catch (error) {
        console.error('[handleTagChange] 创建标签失败:', error);
        message.error('创建标签失败');
      } finally {
        setCreatingTag(false);
      }
    },
    [tagOptions],
  );

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
        // 将 tag_ids 数组转换为逗号分隔的字符串
        const submitData = {
          ...values,
          tag_ids: Array.isArray(values.tag_ids) ? values.tag_ids.join(',') : values.tag_ids || '',
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

          // 加载常用标签数据
          await setTagLoading(true);
          const tagRes = await getPopularTags({ limit: 100, status: 1 });
          if (tagRes.code === 200 && tagRes.data?.items) {
            const options = tagRes.data.items.map((item: any) => ({
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
              tooltip="输入标签名称后按回车添加，支持自定义标签"
            >
              <Select
                mode="tags"
                placeholder="输入标签名称后按回车添加（可自定义）"
                allowClear
                options={tagOptions}
                loading={tagLoading || tagSearching || creatingTag}
                showSearch
                tokenSeparators={[',', ' ']}
                filterOption={false}
                maxTagCount={10}
                onSearch={async (value: string) => {
                  if (value && value.trim().length > 0) {
                    setTagSearching(true);
                    try {
                      const res = await searchTags({ keyword: value.trim(), limit: 50, status: 1 });
                      if (res.code === 200 && res.data?.items) {
                        // 获取当前已选中的标签 ID
                        const currentValues = restFormRef.current?.getFieldValue('tag_ids') || [];
                        const currentIds = Array.isArray(currentValues) ? currentValues : [];

                        // 搜索结果选项
                        const searchOptions = res.data.items.map((item: any) => ({
                          label: item.name,
                          value: item.id,
                        }));

                        // 保留已选标签的选项（从现有 options 中查找）
                        const selectedOptions = tagOptions.filter((opt) =>
                          currentIds.includes(opt.value),
                        );

                        // 合并选项：已选标签 + 搜索结果，并去重
                        const allOptions = [
                          ...selectedOptions,
                          ...searchOptions.filter(
                            (opt: { value: number }) =>
                              !selectedOptions.some((selected) => selected.value === opt.value),
                          ),
                        ];

                        setTagOptions(allOptions);
                      }
                    } finally {
                      setTagSearching(false);
                    }
                  } else if (value === '') {
                    // 清空搜索时重新加载常用标签
                    setTagLoading(true);
                    try {
                      const res = await getPopularTags({ limit: 100, status: 1 });
                      if (res.code === 200 && res.data?.items) {
                        const options = res.data.items.map((item: any) => ({
                          label: item.name,
                          value: item.id,
                        }));
                        setTagOptions(options);
                      }
                    } finally {
                      setTagLoading(false);
                    }
                  }
                }}
                onChange={handleTagChange}
              />
            </Form.Item>

            <Form.Item label="文章摘要" name="summary">
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
