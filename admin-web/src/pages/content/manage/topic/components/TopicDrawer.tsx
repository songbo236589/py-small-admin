import ProFormTinyMCE from '@/components/common/ProFormTinyMCE';
import { generateArticle, getModels } from '@/services/content/ai/api';
import { add, update } from '@/services/content/manage/article/api';
import { getTree as getCategoryTree } from '@/services/content/manage/category/api';
import {
  getPopularTags,
  quickAdd as quickAddTag,
  searchTags,
} from '@/services/content/manage/tag/api';
import {
  fetchZhihuContent,
  generateCategory,
  generateDescription,
  getDetail,
  updateCategory,
} from '@/services/content/manage/topic/api';
import {
  CheckOutlined,
  CloseOutlined,
  DeleteOutlined,
  EditOutlined,
  LoadingOutlined,
  PlusOutlined,
  ReloadOutlined,
  RobotOutlined,
  SaveOutlined,
  StopOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { DrawerForm, ModalForm, ProFormText, ProFormTextArea } from '@ant-design/pro-components';
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
  topic_id?: number;
  tag_ids?: number[];
  tags?: { id: number; name: string; color?: string }[];
}

type GenerateModeType = 'title' | 'description' | 'full';

// 生成任务状态
type GenerateTaskStatus = 'pending' | 'generating' | 'success' | 'failed';

interface GenerateTask {
  id: string;
  status: GenerateTaskStatus;
  index: number;
  error?: string;
  article?: GeneratedArticle;
}

const GenerateMode: Record<string, GenerateModeType> = {
  TITLE: 'title',
  DESCRIPTION: 'description',
  FULL: 'full',
};

const TopicDrawer: React.FC<PropsType> = (props) => {
  const modalFormRef = useRef<ProFormInstance>(null);

  // Drawer 状态
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generatingDesc, setGeneratingDesc] = useState(false);
  const [generatingCategory, setGeneratingCategory] = useState(false);
  const [topicData, setTopicData] = useState<API.ContentTopic | null>(null);
  const [models, setModels] = useState<{ label: string; value: string }[]>([]);
  const [selectedModel, setSelectedModel] = useState<string | undefined>();
  const [mode, setMode] = useState<GenerateModeType>(GenerateMode.DESCRIPTION);
  const [generatedArticles, setGeneratedArticles] = useState<GeneratedArticle[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [categoryTreeData, setCategoryTreeData] = useState<any[]>([]);
  const [tagOptions, setTagOptions] = useState<{ label: string; value: number }[]>([]);
  const [saving, setSaving] = useState(false);
  const [tagSearching, setTagSearching] = useState(false);
  const [creatingTag, setCreatingTag] = useState(false);

  // 批量生成状态
  const [generateCount, setGenerateCount] = useState<number>(1);
  const [generateTasks, setGenerateTasks] = useState<GenerateTask[]>([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState<number>(0);
  const [cancelled, setCancelled] = useState<boolean>(false);

  // 知乎内容状态
  const [fetchingZhihu, setFetchingZhihu] = useState(false);
  const [zhihuContent, setZhihuContent] = useState<{
    title: string;
    answer_count: number;
    updated_at: string;
  } | null>(null);
  const [zhihuDetailModalVisible, setZhihuDetailModalVisible] = useState(false);
  const [zhihuDetail, setZhihuDetail] = useState<API.ZhihuContentDetail | null>(null);

  // 编辑模态框状态
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingArticle, setEditingArticle] = useState<GeneratedArticle | null>(null);
  const [editFormReady, setEditFormReady] = useState(false);

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
        modalFormRef.current?.setFieldsValue({ tag_ids: tagIds });
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
        modalFormRef.current?.setFieldsValue({ tag_ids: allTagIds });
      } catch (error) {
        console.error('[handleTagChange] 创建标签失败:', error);
        message.error('创建标签失败');
      } finally {
        setCreatingTag(false);
      }
    },
    [tagOptions],
  );

  // 并行加载数据
  const loadDrawerData = useCallback(async () => {
    setDrawerLoading(true);
    try {
      const [modelsRes, topicRes, categoryRes, tagRes] = await Promise.all([
        getModels(),
        getDetail(props.id),
        getCategoryTree({ status: 1 }),
        getPopularTags({ limit: 100, status: 1 }),
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
        // 检查是否有知乎内容
        if (topicRes.data.zhihu_content_updated_at && topicRes.data.zhihu_content) {
          try {
            const zhihuData = JSON.parse(topicRes.data.zhihu_content);
            // 设置状态显示
            setZhihuContent({
              title: zhihuData.title,
              answer_count: zhihuData.answer_count,
              updated_at: topicRes.data.zhihu_content_updated_at,
            });
            // 同时设置详情（用于 Modal 显示）
            setZhihuDetail({
              title: zhihuData.title,
              description: zhihuData.description,
              url: zhihuData.url,
              answers: zhihuData.answers,
              answer_count: zhihuData.answer_count,
              updated_at: topicRes.data.zhihu_content_updated_at,
            });
          } catch {
            // 解析失败，zhihuContent 和 zhihuDetail 保持 null
          }
        }
      }

      // 处理分类树
      if (categoryRes.code === 200 && categoryRes.data) {
        setCategoryTreeData(categoryRes.data);
      }

      // 处理标签列表（用于编辑文章时选择标签）
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

  // 抓取知乎问题内容
  const handleFetchZhihu = useCallback(async () => {
    if (!topicData) return;

    setFetchingZhihu(true);
    try {
      const res = await fetchZhihuContent(topicData.id);
      if (res.code === 200) {
        // 更新状态
        setZhihuContent({
          title: res.data.title,
          answer_count: res.data.answer_count,
          updated_at: res.data.updated_at || '',
        });
        // 存储完整的知乎内容详情（用于 Modal 显示）
        setZhihuDetail({
          title: res.data.title,
          description: res.data.description,
          url: res.data.url,
          answers: res.data.answers,
          answer_count: res.data.answer_count,
          updated_at: res.data.updated_at,
        });
        message.success(`成功获取：${res.data.title}（${res.data.answer_count} 个回答）`);
        // 刷新话题数据
        const topicRes = await getDetail(props.id);
        if (topicRes.code === 200) {
          setTopicData(topicRes.data);
        }
      } else {
        message.error(res.message || '获取失败');
      }
    } catch (error) {
      message.error('网络错误，请稍后重试');
    } finally {
      setFetchingZhihu(false);
    }
  }, [topicData, props.id]);

  // 生成文章（支持批量串行生成）
  const handleGenerate = useCallback(async () => {
    if (!topicData) {
      message.warning('请先等待话题信息加载');
      return;
    }

    if (!selectedModel) {
      message.warning('请选择 AI 模型');
      return;
    }

    // 重置状态
    setCancelled(false);
    setGenerating(true);

    // 创建任务列表
    const tasks: GenerateTask[] = Array.from({ length: generateCount }, (_, i) => ({
      id: `task_${Date.now()}_${i}`,
      status: 'pending',
      index: i + 1,
    }));
    setGenerateTasks(tasks);
    setCurrentTaskIndex(0);

    // 串行执行任务
    let successCount = 0;
    let failedCount = 0;

    for (let i = 0; i < tasks.length; i++) {
      // 检查是否取消
      if (cancelled) {
        setGenerateTasks((prev) =>
          prev.map((task, idx) =>
            idx > i - 1 ? { ...task, status: 'failed' as const, error: '已取消' } : task,
          ),
        );
        break;
      }

      const task = tasks[i];
      setCurrentTaskIndex(i);

      // 更新任务状态为生成中
      setGenerateTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: 'generating' } : t)),
      );

      try {
        console.log(`[handleGenerate] 开始生成第 ${i + 1} 篇文章, variant_index: ${i}`);
        const res = await generateArticle({
          id: props.id,
          mode: mode,
          model: selectedModel,
          variant_index: i,
        });

        console.log(`[handleGenerate] 第 ${i + 1} 篇文章生成响应:`, res);

        if (res.code === 200) {
          console.log('[handleGenerate] AI 生成的标签 ID:', res.data?.tag_ids);
          console.log('[handleGenerate] AI 生成的标签对象:', res.data?.tags);
          console.log('[handleGenerate] 后端返回的文章 ID:', res.data?.article_id);

          const generatedTags = res.data?.tags || [];
          // 将 AI 生成的新标签添加到 tagOptions（去重）
          if (generatedTags.length > 0) {
            setTagOptions((prev) => {
              const existingIds = new Set(prev.map((opt) => opt.value));
              const newOptions = generatedTags
                .filter((tag: { id: number }) => !existingIds.has(tag.id))
                .map((tag: { id: number; name: string }) => ({
                  label: tag.name,
                  value: tag.id,
                }));
              console.log('[handleGenerate] 添加到 tagOptions 的新标签:', newOptions);
              return [...prev, ...newOptions];
            });
          }

          // 后端已自动保存，直接使用返回的 article_id
          const articleId = res.data?.article_id;
          const newArticle: GeneratedArticle = {
            id: `gen_${Date.now()}_${i}`,
            title: res.data?.title || topicData.title,
            content: res.data?.content || '',
            summary: res.data?.summary,
            status: articleId ? 'saved' : 'draft', // 有 article_id 则已保存
            savedId: articleId, // 保存后端返回的文章 ID
            category_id: topicData.category_id,
            topic_id: props.id,
            tag_ids: res.data?.tag_ids || [], // AI 生成的标签 ID 列表
            tags: generatedTags, // 保存完整的标签对象
          };
          console.log('[handleGenerate] 创建的文章对象:', newArticle);

          // 更新任务状态为成功
          setGenerateTasks((prev) =>
            prev.map((t) =>
              t.id === task.id ? { ...t, status: 'success', article: newArticle } : t,
            ),
          );

          // 立即添加到已生成列表（新文章放前面）
          setGeneratedArticles((prev) => [newArticle, ...prev]);
          successCount++;
        } else {
          // 更新任务状态为失败
          setGenerateTasks((prev) =>
            prev.map((t) =>
              t.id === task.id ? { ...t, status: 'failed', error: res.message || '生成失败' } : t,
            ),
          );
          failedCount++;
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : '网络错误';
        setGenerateTasks((prev) =>
          prev.map((t) => (t.id === task.id ? { ...t, status: 'failed', error: errorMessage } : t)),
        );
        failedCount++;
      }
    }

    setGenerating(false);
    setCurrentTaskIndex(tasks.length);

    // 显示结果提示
    if (successCount > 0 && failedCount === 0) {
      message.success(`成功生成 ${successCount} 篇文章，已自动保存到文章管理`);
    } else if (successCount > 0 && failedCount > 0) {
      message.warning(`生成完成：成功 ${successCount} 篇（已保存），失败 ${failedCount} 篇`);
    } else if (successCount === 0 && failedCount > 0) {
      message.error(`生成失败 ${failedCount} 篇，请稍后重试`);
    }

    // 延迟清空任务列表
    setTimeout(() => {
      setGenerateTasks([]);
    }, 3000);
  }, [topicData, selectedModel, mode, props.id, generateCount, cancelled]);

  // 取消批量生成
  const handleCancelGenerate = useCallback(() => {
    Modal.confirm({
      title: '确认取消',
      content: '确定要取消剩余的生成任务吗？已生成的文章将保留。',
      okText: '确认取消',
      okButtonProps: { danger: true },
      cancelText: '继续生成',
      onOk: () => {
        setCancelled(true);
        message.info('正在取消剩余任务...');
      },
    });
  }, []);

  // 生成描述
  const handleGenerateDescription = useCallback(async () => {
    if (!topicData) {
      message.warning('请先等待话题信息加载');
      return;
    }

    if (!selectedModel) {
      message.warning('请选择 AI 模型');
      return;
    }

    setGeneratingDesc(true);
    try {
      const res = await generateDescription(props.id, { model: selectedModel });

      if (res.code === 200) {
        const newDescription = res.data?.description;
        if (newDescription) {
          // 更新 topicData
          setTopicData((prev) => (prev ? { ...prev, description: newDescription } : null));
          message.success('描述生成并保存成功');
        }
      } else {
        message.error(res.message || '描述生成失败');
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '网络错误';
      message.error(`描述生成失败: ${errorMessage}`);
    } finally {
      setGeneratingDesc(false);
    }
  }, [topicData, selectedModel, props.id]);

  // 更新话题分类
  const handleUpdateCategory = useCallback(
    async (value: number | undefined) => {
      if (!topicData) return;

      try {
        const res = await updateCategory(props.id, { category_id: value ?? null });
        if (res.code === 200) {
          message.success(res.message || '分类更新成功');
          // 更新本地 topicData
          setTopicData((prev) => {
            if (!prev) return null;
            const updated: API.ContentTopic = {
              ...prev,
              category_id: value,
              category: value
                ? {
                    id: value,
                    name: categoryTreeData.find((c) => c.value === value)?.title,
                    slug: categoryTreeData.find((c) => c.value === value)?.slug,
                  }
                : undefined,
            };
            return updated;
          });
        } else {
          message.error(res.message || '分类更新失败');
          // 失败时恢复原值
          setTopicData((prev) => prev);
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : '网络错误';
        message.error(`分类更新失败: ${errorMessage}`);
        // 失败时恢复原值
        setTopicData((prev) => prev);
      }
    },
    [topicData, props.id, categoryTreeData],
  );

  // AI 生成话题分类
  const handleGenerateCategory = useCallback(async () => {
    if (!topicData) return;

    setGeneratingCategory(true);
    try {
      const res = await generateCategory(props.id, { model: selectedModel });
      if (res.code === 200) {
        const { category_id, category_name, parent_name, is_new } = res.data || {};
        if (category_id) {
          // 如果创建了新分类，重新加载分类树数据
          if (is_new) {
            const treeRes = await getCategoryTree({ status: 1 });
            if (treeRes.code === 200 && treeRes.data) {
              setCategoryTreeData(treeRes.data);
            }
          }

          // 更新本地 topicData
          setTopicData((prev) => {
            if (!prev) return null;
            const updated: API.ContentTopic = {
              ...prev,
              category_id,
              category: {
                id: category_id,
                name: category_name || categoryTreeData.find((c) => c.value === category_id)?.title,
                slug: categoryTreeData.find((c) => c.value === category_id)?.slug,
              },
            };
            return updated;
          });

          // 显示成功消息（包含父分类信息）
          const displayText = parent_name ? `${parent_name} > ${category_name}` : category_name;
          const newTag = is_new ? '（新创建）' : '';
          message.success(`${res.message || '分类生成成功'}：${displayText}${newTag}`);
        }
      } else {
        message.error(res.message || '分类生成失败');
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '网络错误';
      message.error(`分类生成失败: ${errorMessage}`);
    } finally {
      setGeneratingCategory(false);
    }
  }, [topicData, selectedModel, props.id, categoryTreeData]);

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
        modalFormRef.current.setFieldsValue({
          title: editingArticle.title,
          summary: editingArticle.summary || '',
          content: editingArticle.content,
          category_id: editingArticle.category_id ?? topicData?.category_id ?? null,
          tag_ids: editingArticle.tag_ids || [],
          status: 0,
        });
        // 再标记表单准备好，渲染内容
        setTimeout(() => {
          setEditFormReady(true);
        }, 50);
      }
    },
    [editingArticle, topicData],
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
  const handleSelectAll = useCallback(
    (checked: boolean) => {
      if (checked) {
        setSelectedIds(new Set(generatedArticles.map((a) => a.id)));
      } else {
        setSelectedIds(new Set());
      }
    },
    [generatedArticles],
  );

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

    console.log('[handleSaveSelected] 开始保存文章, 数量:', articlesToSave.length);
    console.log('[handleSaveSelected] 待保存文章:', articlesToSave);

    setSaving(true);
    let successCount = 0;
    let addCount = 0;
    let updateCount = 0;
    const failedArticles: { title: string; reason: string }[] = [];

    for (const article of articlesToSave) {
      try {
        console.log('[handleSaveSelected] 处理文章:', article.title);
        console.log('[handleSaveSelected] AI 生成的标签 ID:', article.tag_ids);

        const submitData = {
          id: null as number | null,
          title: article.title,
          content: article.content,
          summary: article.summary || '',
          cover_image_id: null as number | null,
          status: 0 as const,
          category_id: article.category_id ?? topicData?.category_id ?? null,
          topic_id: article.topic_id ?? props.id,
          // 将 tag_ids 数组转换为逗号分隔的字符串
          tag_ids: Array.isArray(article.tag_ids)
            ? article.tag_ids.join(',')
            : article.tag_ids || '',
        };

        console.log('[handleSaveSelected] 提交的数据:', submitData);

        let res;
        if (article.savedId) {
          // 已保存的文章，调用 update
          console.log('[handleSaveSelected] 调用更新接口, ID:', article.savedId);
          res = await update(article.savedId, submitData);
        } else {
          // 新文章，调用 add
          console.log('[handleSaveSelected] 调用新增接口');
          res = await add(submitData);
        }

        console.log('[handleSaveSelected] 保存响应:', res);

        if (res.code === 200) {
          console.log('[handleSaveSelected] 保存成功, 文章 ID:', res.data?.id);
          successCount++;
          if (article.savedId) {
            updateCount++;
          } else {
            addCount++;
          }
          setGeneratedArticles((prev) =>
            prev.map((a) =>
              a.id === article.id
                ? { ...a, status: 'saved' as const, savedId: article.savedId || res.data?.id }
                : a,
            ),
          );
        } else {
          console.error('[handleSaveSelected] 保存失败:', res.message);
          failedArticles.push({ title: article.title, reason: res.message || '未知错误' });
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : '网络错误';
        console.error('[handleSaveSelected] 保存异常:', errorMessage, error);
        failedArticles.push({ title: article.title, reason: errorMessage });
      }
    }

    setSaving(false);

    if (successCount > 0) {
      let messageText = '';
      if (addCount > 0 && updateCount > 0) {
        messageText = `新增 ${addCount} 篇，更新 ${updateCount} 篇`;
      } else if (addCount > 0) {
        messageText = `新增 ${addCount} 篇`;
      } else if (updateCount > 0) {
        messageText = `更新 ${updateCount} 篇`;
      }
      if (failedArticles.length > 0) {
        messageText += `，失败 ${failedArticles.length} 篇`;
      }
      message.success(messageText);
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
  }, [generatedArticles, selectedIds, topicData, props]);

  // 编辑模态框提交
  const handleEditSubmit = useCallback(
    async (values: any) => {
      if (!editingArticle) return false;

      const submitData = {
        ...values,
        topic_id: values.topic_id ?? editingArticle.topic_id ?? props.id,
        // 将 tag_ids 数组转换为逗号分隔的字符串
        tag_ids: Array.isArray(values.tag_ids) ? values.tag_ids.join(',') : values.tag_ids || '',
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
                  title: values.title,
                  content: values.content,
                  summary: values.summary,
                  category_id: values.category_id,
                  tag_ids: values.tag_ids,
                  status: 'saved' as const,
                  savedId: editingArticle.savedId || res.data?.id,
                }
              : a,
          ),
        );
        setEditModalOpen(false);
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
            setGenerateCount(1);
            setGenerateTasks([]);
            setCurrentTaskIndex(0);
            setCancelled(false);
            setZhihuContent(null);
            // 并行加载数据
            await loadDrawerData();
          }
        }}
      >
        <Spin spinning={drawerLoading}>
          {!drawerLoading && topicData && (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 话题信息 */}
              <Descriptions
                title="话题信息"
                bordered
                size="small"
                column={1}
                labelStyle={{ width: 120, minWidth: 120 }}
              >
                <Descriptions.Item label="问题标题">{topicData.title}</Descriptions.Item>
                <Descriptions.Item label="问题描述">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {topicData.description ? (
                      <Paragraph style={{ marginBottom: 0 }}>{topicData.description}</Paragraph>
                    ) : (
                      <Text type="secondary">暂无描述</Text>
                    )}
                    <Button
                      type="primary"
                      size="small"
                      icon={<ThunderboltOutlined />}
                      onClick={handleGenerateDescription}
                      loading={generatingDesc}
                      disabled={!selectedModel || generating || generatingDesc}
                    >
                      {topicData.description ? '重新生成描述' : 'AI 生成描述'}
                    </Button>
                  </Space>
                </Descriptions.Item>
                <Descriptions.Item label="分类">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <TreeSelect
                      value={topicData.category_id}
                      onChange={handleUpdateCategory}
                      treeData={categoryTreeData}
                      placeholder="请选择分类"
                      allowClear
                      showSearch
                      style={{ width: '100%' }}
                      fieldNames={{ label: 'title', value: 'value', children: 'children' }}
                      treeDefaultExpandAll
                      filterTreeNode={(input, treeNode) => {
                        return (treeNode.title as string)
                          ?.toLowerCase()
                          .includes(input.toLowerCase());
                      }}
                    />
                    <Button
                      type="primary"
                      ghost
                      size="small"
                      icon={<RobotOutlined />}
                      onClick={handleGenerateCategory}
                      loading={generatingCategory}
                      disabled={!selectedModel || generating || generatingCategory}
                      block
                    >
                      {topicData.category_id ? 'AI 重新推荐分类' : 'AI 智能推荐分类'}
                    </Button>
                  </Space>
                </Descriptions.Item>
                <Descriptions.Item label="知乎内容">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {zhihuContent ? (
                      <>
                        <Space>
                          <Text type="success">✓ 已获取（{zhihuContent.answer_count} 个回答）</Text>
                          <Button
                            size="small"
                            type="link"
                            onClick={() => setZhihuDetailModalVisible(true)}
                          >
                            查看详情
                          </Button>
                        </Space>
                        {zhihuContent.updated_at && (
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            更新于 {zhihuContent.updated_at}
                          </Text>
                        )}
                        <Button
                          size="small"
                          onClick={handleFetchZhihu}
                          loading={fetchingZhihu}
                          disabled={fetchingZhihu}
                        >
                          刷新内容
                        </Button>
                      </>
                    ) : (
                      <Button
                        type="primary"
                        size="small"
                        icon={<ReloadOutlined />}
                        onClick={handleFetchZhihu}
                        loading={fetchingZhihu}
                        disabled={fetchingZhihu || !topicData?.url?.includes('zhihu.com')}
                      >
                        获取问题详情
                      </Button>
                    )}
                  </Space>
                </Descriptions.Item>
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
                      disabled={generating || generatingDesc || generatingCategory}
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
                        <Radio value={GenerateMode.DESCRIPTION}>根据标题和描述生成（标准）</Radio>
                        <Radio value={GenerateMode.FULL}>完整深度生成（详细）</Radio>
                      </Space>
                    </Radio.Group>
                  </div>

                  <div>
                    <Text strong>生成数量：</Text>
                    <Select
                      style={{ marginTop: 8, width: '100%' }}
                      value={generateCount}
                      onChange={(value) => setGenerateCount(value)}
                      options={[
                        { label: '1 篇', value: 1 },
                        { label: '2 篇', value: 2 },
                        { label: '3 篇', value: 3 },
                        { label: '5 篇', value: 5 },
                      ]}
                      disabled={generating}
                    />
                  </div>

                  <Button
                    type="primary"
                    icon={<RobotOutlined />}
                    onClick={handleGenerate}
                    loading={generating}
                    disabled={!selectedModel || generating}
                    block
                  >
                    {generating
                      ? `AI 正在生成 (${currentTaskIndex + 1}/${generateCount})...`
                      : generateCount > 1
                      ? `开始生成 ${generateCount} 篇`
                      : '开始生成'}
                  </Button>

                  {/* 生成进度显示 */}
                  {generateTasks.length > 0 && (
                    <Card size="small" style={{ background: '#f5f5f5' }}>
                      <Space direction="vertical" style={{ width: '100%' }} size="small">
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <Text strong>
                            生成进度 ({currentTaskIndex}/{generateCount})
                          </Text>
                          {generating && (
                            <Button
                              size="small"
                              danger
                              icon={<StopOutlined />}
                              onClick={handleCancelGenerate}
                            >
                              取消
                            </Button>
                          )}
                        </div>

                        {/* 任务列表 */}
                        {generateTasks.map((task) => (
                          <div
                            key={task.id}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              padding: '4px 0',
                            }}
                          >
                            {task.status === 'pending' && (
                              <Tag style={{ margin: 0, width: 70 }}>等待中</Tag>
                            )}
                            {task.status === 'generating' && (
                              <Tag
                                icon={<LoadingOutlined />}
                                color="processing"
                                style={{ margin: 0, width: 70 }}
                              >
                                生成中
                              </Tag>
                            )}
                            {task.status === 'success' && (
                              <Tag
                                icon={<CheckOutlined />}
                                color="success"
                                style={{ margin: 0, width: 70 }}
                              >
                                完成
                              </Tag>
                            )}
                            {task.status === 'failed' && (
                              <Tag
                                icon={<CloseOutlined />}
                                color="error"
                                style={{ margin: 0, width: 70 }}
                              >
                                失败
                              </Tag>
                            )}
                            <Text style={{ marginLeft: 8 }}>
                              第 {task.index} 篇{task.error && `: ${task.error}`}
                            </Text>
                          </div>
                        ))}
                      </Space>
                    </Card>
                  )}
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
                        {/* 显示 AI 生成的标签 */}
                        {article.tag_ids && article.tag_ids.length > 0 && (
                          <div style={{ marginTop: 4 }}>
                            <Space size={4} wrap>
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                AI 标签:
                              </Text>
                              {article.tag_ids.map((tagId) => {
                                const tag = tagOptions.find((opt) => opt.value === tagId);
                                return tag ? (
                                  <Tag key={tagId} color="blue" style={{ fontSize: 11, margin: 0 }}>
                                    {tag.label}
                                  </Tag>
                                ) : null;
                              })}
                            </Space>
                          </div>
                        )}
                      </Space>
                    </Card>
                  ))}

                  <Button
                    icon={<PlusOutlined />}
                    onClick={handleGenerate}
                    loading={generating}
                    disabled={!selectedModel || generating}
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
                    return (treeNode.title as string)?.toLowerCase().includes(input.toLowerCase());
                  }}
                />
              </Form.Item>

              <Form.Item
                name="tag_ids"
                label="文章标签"
                tooltip="输入标签名称后按回车添加，支持自定义标签"
              >
                <Select
                  mode="tags"
                  style={{ width: '100%' }}
                  placeholder="输入标签名称后按回车添加（可自定义）"
                  options={tagOptions}
                  tokenSeparators={[',', ' ']}
                  maxTagCount={10}
                  showSearch
                  allowClear
                  loading={creatingTag || tagSearching}
                  filterOption={false}
                  onSearch={async (value: string) => {
                    if (value && value.trim().length > 0) {
                      setTagSearching(true);
                      try {
                        const res = await searchTags({
                          keyword: value.trim(),
                          limit: 50,
                          status: 1,
                        });
                        if (res.code === 200 && res.data?.items) {
                          // 获取当前已选中的标签 ID
                          const currentValues =
                            modalFormRef.current?.getFieldValue('tag_ids') || [];
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
                      const res = await getPopularTags({ limit: 100, status: 1 });
                      if (res.code === 200 && res.data?.items) {
                        const options = res.data.items.map((item: any) => ({
                          label: item.name,
                          value: item.id,
                        }));
                        setTagOptions(options);
                      }
                    }
                  }}
                  onChange={handleTagChange}
                />
              </Form.Item>

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

      {/* 知乎内容详情 Modal */}
      <Modal
        title="知乎问题详情"
        open={zhihuDetailModalVisible}
        onCancel={() => setZhihuDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setZhihuDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {zhihuDetail && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <Text strong style={{ fontSize: 16 }}>
                问题标题
              </Text>
              <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>{zhihuDetail.title}</Paragraph>
            </div>

            {zhihuDetail.description && (
              <div>
                <Text strong>问题描述</Text>
                <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
                  {zhihuDetail.description}
                </Paragraph>
              </div>
            )}

            <div>
              <Text strong>高赞回答（{zhihuDetail.answer_count} 个）</Text>
              <Space direction="vertical" style={{ width: '100%', marginTop: 8 }} size="middle">
                {zhihuDetail.answers.map((answer, index) => (
                  <Card
                    // eslint-disable-next-line react/no-array-index-key
                    key={index}
                    size="small"
                    title={`回答 ${index + 1}（作者：${answer.author}）`}
                    style={{ backgroundColor: '#fafafa' }}
                  >
                    <Paragraph
                      style={{
                        marginBottom: 0,
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {answer.content.length > 500
                        ? answer.content.substring(0, 500) + '...'
                        : answer.content}
                    </Paragraph>
                  </Card>
                ))}
              </Space>
            </div>

            {zhihuDetail.updated_at && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                更新于 {zhihuDetail.updated_at}
              </Text>
            )}
          </Space>
        )}
      </Modal>
    </>
  );
};

export default TopicDrawer;
