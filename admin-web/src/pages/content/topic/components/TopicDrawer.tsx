import ProFormTinyMCE from '@/components/common/ProFormTinyMCE';
import { generateArticle, getModels } from '@/services/content/ai/api';
import { add, update } from '@/services/content/article/api';
import { getTree as getCategoryTree } from '@/services/content/category/api';
import { getList as getTagList } from '@/services/content/tag/api';
import { getDetail } from '@/services/content/topic/api';
import {
  CheckOutlined,
  CloseOutlined,
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  RobotOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import {
  DrawerForm,
  ModalForm,
  ProFormSelect,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import {
  Button,
  Card,
  Checkbox,
  Descriptions,
  Form,
  message,
  Modal,
  Radio,
  Select,
  Space,
  Spin,
  Tag,
  TreeSelect,
  Typography,
} from 'antd';
import { useCallback, useRef, useState } from 'react';

const { Paragraph, Text } = Typography;

interface PropsType {
  onConfirm: () => void;
  id: number;
}

interface GeneratedArticle {
  id: string;
  title: string;
  content: string;
  summary?: string;
  status: 'draft' | 'saved';
  savedId?: number;
  category_id?: number;
  tag_ids?: number[];
}

type GenerateModeType = 'title' | 'description' | 'full';

const GenerateMode: Record<string, GenerateModeType> = {
  TITLE: 'title',
  DESCRIPTION: 'description',
  FULL: 'full',
};

// 工具函数：将 tag_ids 转换为逗号分隔的字符串
const formatTagIds = (tagIds: number[] | undefined, defaultTagIds: number[]): string => {
  const value = tagIds ?? defaultTagIds;
  if (Array.isArray(value) && value.length > 0) {
    return value.join(',');
  }
  return '';
};

const TopicDrawer: React.FC<PropsType> = (props) => {
  const modalFormRef = useRef<ProFormInstance>(null);

  // Drawer 状态
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [topicData, setTopicData] = useState<API.ContentTopic | null>(null);
  const [models, setModels] = useState<{ label: string; value: string }[]>([]);
  const [selectedModel, setSelectedModel] = useState<string | undefined>();
  const [mode, setMode] = useState<GenerateModeType>(GenerateMode.DESCRIPTION);
  const [generatedArticles, setGeneratedArticles] = useState<GeneratedArticle[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [categoryTreeData, setCategoryTreeData] = useState<any[]>([]);
  const [tagOptions, setTagOptions] = useState<{ label: string; value: number }[]>([]);
  const [defaultCategoryId, setDefaultCategoryId] = useState<number | undefined>();
  const [defaultTagIds, setDefaultTagIds] = useState<number[]>([]);
  const [saving, setSaving] = useState(false);

  // 编辑模态框状态
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingArticle, setEditingArticle] = useState<GeneratedArticle | null>(null);
  const [editFormReady, setEditFormReady] = useState(false);

  // 并行加载数据
  const loadDrawerData = useCallback(async () => {
    setDrawerLoading(true);
    try {
      const [modelsRes, topicRes, categoryRes, tagRes] = await Promise.all([
        getModels(),
        getDetail(props.id),
        getCategoryTree({ status: 1 }),
        getTagList({ page: 1, pageSize: 1000 }),
      ]);

      // 处理模型列表
      if (modelsRes.code === 200 && modelsRes.data?.models) {
        const options = modelsRes.data.models.map((model: API.OllamaModel) => ({
          label: model.name,
          value: model.name,
        }));
        setModels(options);
        if (options.length > 0) {
          setSelectedModel(options[0].value);
        }
      }

      // 处理话题详情
      if (topicRes.code === 200) {
        setTopicData(topicRes.data);
      }

      // 处理分类树
      if (categoryRes.code === 200 && categoryRes.data) {
        setCategoryTreeData(categoryRes.data);
      }

      // 处理标签列表
      if (tagRes.code === 200 && tagRes.data?.items) {
        const options = tagRes.data.items
          .filter((item: API.ContentTagList) => item.status === 1)
          .map((item: API.ContentTagList) => ({
            label: item.name,
            value: item.id,
          }));
        setTagOptions(options);
      }
    } finally {
      setDrawerLoading(false);
    }
  }, [props.id]);

  // 生成文章
  const handleGenerate = useCallback(async () => {
    if (!topicData) {
      message.warning('请先等待话题信息加载');
      return;
    }

    if (!selectedModel) {
      message.warning('请选择 AI 模型');
      return;
    }

    setGenerating(true);
    try {
      const res = await generateArticle({
        id: props.id,
        mode: mode,
        title: topicData.title,
        description: topicData.description || '',
        model: selectedModel,
      });

      if (res.code === 200) {
        const newArticle: GeneratedArticle = {
          id: `gen_${Date.now()}`,
          title: res.data?.title || topicData.title,
          content: res.data?.content || '',
          summary: res.data?.summary,
          status: 'draft',
          category_id: defaultCategoryId,
          tag_ids: defaultTagIds.length > 0 ? [...defaultTagIds] : undefined,
        };
        setGeneratedArticles((prev) => [...prev, newArticle]);
        message.success('文章生成成功');
      }
    } finally {
      setGenerating(false);
    }
  }, [topicData, selectedModel, mode, props.id, defaultCategoryId, defaultTagIds]);

  // 编辑文章
  const handleEdit = useCallback((article: GeneratedArticle) => {
    setEditingArticle(article);
    setEditFormReady(false);
    setEditModalOpen(true);
  }, []);

  // 关闭编辑模态框
  const handleEditModalClose = useCallback((open: boolean) => {
    if (!open) {
      setEditModalOpen(false);
      setEditingArticle(null);
      setEditFormReady(false);
    }
  }, []);

  // 编辑模态框打开后设置表单值
  const handleEditModalAfterOpenChange = useCallback(
    (open: boolean) => {
      if (open && editingArticle && modalFormRef.current) {
        // 先设置表单值
        modalFormRef.current.setFieldsValue({
          title: editingArticle.title,
          summary: editingArticle.summary || '',
          content: editingArticle.content,
          category_id: editingArticle.category_id ?? defaultCategoryId,
          tag_ids: editingArticle.tag_ids ?? defaultTagIds,
          status: 0,
        });
        // 再标记表单准备好，渲染内容
        setTimeout(() => {
          setEditFormReady(true);
        }, 50);
      }
    },
    [editingArticle, defaultCategoryId, defaultTagIds],
  );

  // 删除文章（带确认）
  const handleDelete = useCallback((article: GeneratedArticle) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文章「${article.title}」吗？`,
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: () => {
        setGeneratedArticles((prev) => prev.filter((a) => a.id !== article.id));
        setSelectedIds((prev) => {
          const newSet = new Set(prev);
          newSet.delete(article.id);
          return newSet;
        });
        message.success('已删除');
      },
    });
  }, []);

  // 全选/取消全选
  const handleSelectAll = useCallback((checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(generatedArticles.map((a) => a.id)));
    } else {
      setSelectedIds(new Set());
    }
  }, [generatedArticles]);

  // 选中/取消选中单个
  const handleSelectOne = useCallback((id: string, checked: boolean) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (checked) {
        newSet.add(id);
      } else {
        newSet.delete(id);
      }
      return newSet;
    });
  }, []);

  // 批量保存选中的文章
  const handleSaveSelected = useCallback(async () => {
    // 选择所有未保存的文章，或者已保存但需要更新的文章
    const articlesToSave = generatedArticles.filter((a) => selectedIds.has(a.id));
    if (articlesToSave.length === 0) {
      message.warning('请选择要保存的文章');
      return;
    }

    setSaving(true);
    let successCount = 0;
    const failedArticles: { title: string; reason: string }[] = [];

    for (const article of articlesToSave) {
      try {
        const submitData = {
          id: null as number | null,
          title: article.title,
          content: article.content,
          summary: article.summary || '',
          cover_image_id: null as number | null,
          status: 0 as const,
          category_id: article.category_id ?? defaultCategoryId ?? null,
          tag_ids: formatTagIds(article.tag_ids, defaultTagIds),
        };

        let res;
        if (article.savedId) {
          // 已保存的文章，调用 update
          res = await update(article.savedId, submitData);
        } else {
          // 新文章，调用 add
          res = await add(submitData);
        }

        if (res.code === 200) {
          successCount++;
          setGeneratedArticles((prev) =>
            prev.map((a) =>
              a.id === article.id
                ? { ...a, status: 'saved' as const, savedId: article.savedId || res.data?.id }
                : a,
            ),
          );
        } else {
          failedArticles.push({ title: article.title, reason: res.message || '未知错误' });
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : '网络错误';
        failedArticles.push({ title: article.title, reason: errorMessage });
      }
    }

    setSaving(false);

    if (successCount > 0) {
      message.success(
        `成功保存 ${successCount} 篇文章${failedArticles.length > 0 ? `，失败 ${failedArticles.length} 篇` : ''}`,
      );
      props.onConfirm();
    }

    if (failedArticles.length > 0) {
      // 使用 Modal 显示失败详情，而不是控制台
      Modal.error({
        title: '部分文章保存失败',
        content: (
          <div>
            {failedArticles.map((a) => (
              <div key={a.title} style={{ marginBottom: 8 }}>
                <Text strong>{a.title}</Text>
                <br />
                <Text type="secondary">{a.reason}</Text>
              </div>
            ))}
          </div>
        ),
      });
    }

    setSelectedIds(new Set());
  }, [generatedArticles, selectedIds, defaultCategoryId, defaultTagIds, props]);

  // 编辑模态框提交
  const handleEditSubmit = useCallback(
    async (values: any) => {
      if (!editingArticle) return false;

      const submitData = {
        ...values,
        tag_ids: values.tag_ids?.join(',') || '',
      };

      let res;
      if (editingArticle.savedId) {
        res = await update(editingArticle.savedId, submitData);
      } else {
        res = await add(submitData);
      }

      if (res.code === 200) {
        message.success('保存成功');
        setGeneratedArticles((prev) =>
          prev.map((a) =>
            a.id === editingArticle.id
              ? {
                  ...a,
                  ...values,
                  status: 'saved' as const,
                  savedId: editingArticle.savedId || res.data?.id,
                  category_id: values.category_id,
                  tag_ids: values.tag_ids,
                }
              : a,
          ),
        );
        setEditModalOpen(false);
        props.onConfirm();
        return true;
      }
      return false;
    },
    [editingArticle, props],
  );

  return (
    <>
      <DrawerForm<Record<string, any>>
        title="AI 批量生成文章"
        width={800}
        trigger={
          <Button type="primary" size="small">
            <RobotOutlined />
            使用
          </Button>
        }
        drawerProps={{
          destroyOnClose: true,
        }}
        submitter={false}
        onOpenChange={async (visible) => {
          if (visible) {
            // 重置状态
            setGeneratedArticles([]);
            setSelectedIds(new Set());
            setMode(GenerateMode.DESCRIPTION);
            setDefaultCategoryId(undefined);
            setDefaultTagIds([]);
            // 并行加载数据
            await loadDrawerData();
          }
        }}
      >
        <Spin spinning={drawerLoading}>
          {!drawerLoading && topicData && (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 话题信息 */}
              <Descriptions title="话题信息" bordered size="small" column={1}>
                <Descriptions.Item label="问题标题">{topicData.title}</Descriptions.Item>
                {topicData.description && (
                  <Descriptions.Item label="问题描述">{topicData.description}</Descriptions.Item>
                )}
                <Descriptions.Item label="分类">{topicData.category || '-'}</Descriptions.Item>
                <Descriptions.Item label="热度">
                  {topicData.hot_score?.toLocaleString() || '-'}
                </Descriptions.Item>
              </Descriptions>

              {/* AI 配置区域 */}
              <Card size="small" title="AI 生成配置">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>AI 模型：</Text>
                    <Select
                      style={{ marginTop: 8, width: '100%' }}
                      placeholder="选择 AI 模型"
                      value={selectedModel}
                      onChange={setSelectedModel}
                      options={models}
                      loading={drawerLoading}
                      showSearch
                    />
                  </div>

                  <div>
                    <Text strong>生成模式：</Text>
                    <Radio.Group
                      value={mode}
                      onChange={(e) => setMode(e.target.value)}
                      style={{ marginTop: 8, display: 'block' }}
                    >
                      <Space direction="vertical">
                        <Radio value={GenerateMode.TITLE}>仅根据标题生成（快速）</Radio>
                        <Radio value={GenerateMode.DESCRIPTION}>
                          根据标题和描述生成（标准）
                        </Radio>
                        <Radio value={GenerateMode.FULL}>完整深度生成（详细）</Radio>
                      </Space>
                    </Radio.Group>
                  </div>

                  <div>
                    <Text strong>默认文章分类：</Text>
                    <TreeSelect
                      style={{ marginTop: 8, width: '100%' }}
                      placeholder="请选择默认文章分类（可选）"
                      value={defaultCategoryId}
                      onChange={setDefaultCategoryId}
                      treeData={categoryTreeData}
                      allowClear
                      showSearch
                      fieldNames={{ label: 'title', value: 'value', children: 'children' }}
                      treeDefaultExpandAll
                      filterTreeNode={(input, treeNode) => {
                        return (treeNode.title as string)
                          ?.toLowerCase()
                          .includes(input.toLowerCase());
                      }}
                    />
                  </div>

                  <div>
                    <Text strong>默认文章标签：</Text>
                    <Select
                      style={{ marginTop: 8, width: '100%' }}
                      mode="multiple"
                      placeholder="请选择默认文章标签（可选）"
                      value={defaultTagIds}
                      onChange={setDefaultTagIds}
                      options={tagOptions}
                      allowClear
                      showSearch
                      maxTagCount={5}
                    />
                  </div>

                  <Button
                    type="primary"
                    icon={<RobotOutlined />}
                    onClick={handleGenerate}
                    loading={generating}
                    disabled={!selectedModel}
                    block
                  >
                    {generating ? 'AI 正在生成...' : '开始生成'}
                  </Button>
                </Space>
              </Card>

              {/* 已生成文章列表 */}
              {generatedArticles.length > 0 && (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Text strong>已生成文章 ({generatedArticles.length} 篇)</Text>
                    <Space>
                      <Checkbox
                        checked={
                          selectedIds.size === generatedArticles.length &&
                          generatedArticles.length > 0
                        }
                        indeterminate={
                          selectedIds.size > 0 && selectedIds.size < generatedArticles.length
                        }
                        onChange={(e) => handleSelectAll(e.target.checked)}
                      >
                        全选
                      </Checkbox>
                      <Button
                        type="primary"
                        icon={<SaveOutlined />}
                        onClick={handleSaveSelected}
                        disabled={selectedIds.size === 0 || saving}
                        loading={saving}
                      >
                        保存选中 ({selectedIds.size})
                      </Button>
                    </Space>
                  </div>

                  {generatedArticles.map((article) => (
                    <Card
                      key={article.id}
                      size="small"
                      style={{
                        border: selectedIds.has(article.id)
                          ? '2px solid #1890ff'
                          : '1px solid #d9d9d9',
                      }}
                    >
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'flex-start',
                          }}
                        >
                          <Space>
                            <Checkbox
                              checked={selectedIds.has(article.id)}
                              onChange={(e) => handleSelectOne(article.id, e.target.checked)}
                            />
                            <Text strong ellipsis style={{ maxWidth: 400 }}>
                              {article.title}
                            </Text>
                            {article.status === 'saved' ? (
                              <Tag icon={<CheckOutlined />} color="success">
                                已保存
                              </Tag>
                            ) : (
                              <Tag icon={<CloseOutlined />} color="default">
                                草稿
                              </Tag>
                            )}
                          </Space>
                          <Space>
                            <Button
                              size="small"
                              icon={<EditOutlined />}
                              onClick={() => handleEdit(article)}
                            >
                              编辑
                            </Button>
                            <Button
                              size="small"
                              danger
                              icon={<DeleteOutlined />}
                              onClick={() => handleDelete(article)}
                            >
                              删除
                            </Button>
                          </Space>
                        </div>
                        <Paragraph
                          ellipsis={{ rows: 2 }}
                          style={{ margin: 0, fontSize: 12, color: '#666' }}
                        >
                          {article.summary ||
                            article.content
                              .replace(/[#*`\n]/g, ' ')
                              .replace(/\s+/g, ' ')
                              .trim()}
                        </Paragraph>
                      </Space>
                    </Card>
                  ))}

                  <Button
                    icon={<PlusOutlined />}
                    onClick={handleGenerate}
                    loading={generating}
                    disabled={!selectedModel}
                    block
                  >
                    再生成一篇
                  </Button>
                </Space>
              )}
            </Space>
          )}
        </Spin>
      </DrawerForm>

      {/* 文章编辑模态框 */}
      <ModalForm
        title="编辑文章"
        open={editModalOpen}
        onOpenChange={handleEditModalClose}
        modalProps={{
          destroyOnClose: true,
          afterOpenChange: handleEditModalAfterOpenChange,
        }}
        formRef={modalFormRef}
        width={900}
        layout="horizontal"
        labelCol={{ span: 3 }}
        wrapperCol={{ span: 21 }}
        onFinish={handleEditSubmit}
      >
        {/* 使用 editFormReady 控制内容渲染，确保表单值先设置 */}
        <Spin spinning={!editFormReady}>
          {editFormReady && (
            <>
              <ProFormText
                name="title"
                label="文章标题"
                placeholder="请输入文章标题"
                rules={[{ required: true, message: '请输入文章标题' }]}
                fieldProps={{ maxLength: 200, showCount: true }}
              />

              <Form.Item
                name="category_id"
                label="文章分类"
                rules={[{ required: true, message: '请选择文章分类' }]}
              >
                <TreeSelect
                  placeholder="请选择文章分类"
                  allowClear
                  showSearch
                  treeData={categoryTreeData}
                  fieldNames={{ label: 'title', value: 'value', children: 'children' }}
                  treeDefaultExpandAll
                  filterTreeNode={(input, treeNode) => {
                    return (treeNode.title as string)
                      ?.toLowerCase()
                      .includes(input.toLowerCase());
                  }}
                />
              </Form.Item>

              <ProFormSelect
                name="tag_ids"
                label="文章标签"
                placeholder="请选择文章标签（可多选）"
                mode="multiple"
                options={tagOptions}
                fieldProps={{ showSearch: true, maxTagCount: 5 }}
              />

              <ProFormTextArea
                name="summary"
                label="文章摘要"
                placeholder="请输入文章摘要"
                fieldProps={{ rows: 3, maxLength: 500, showCount: true }}
              />

              <ProFormTinyMCE
                formRef={modalFormRef}
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
                <Radio.Group>
                  <Radio value={0}>草稿</Radio>
                  <Radio value={1}>已发布</Radio>
                  <Radio value={2}>审核中</Radio>
                  <Radio value={3}>发布失败</Radio>
                </Radio.Group>
              </Form.Item>
            </>
          )}
        </Spin>
      </ModalForm>
    </>
  );
};

export default TopicDrawer;
