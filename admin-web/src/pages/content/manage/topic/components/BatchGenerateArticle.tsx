import { generateArticle } from '@/services/content/ai/api';
import { getModels as getAIModels } from '@/services/content/ai/api';
import type { API } from '@/services/content/ai/typings';
import { FileTextOutlined } from '@ant-design/icons';
import { Button, Form, message, Modal, Progress, Radio, Select } from 'antd';
import { useEffect, useState } from 'react';

interface PropsType {
  selectedRowKeys: React.Key[];
  onConfirm: () => void;
}

type ArticleMode = 'title' | 'description' | 'full';

const BatchGenerateArticle: React.FC<PropsType> = (props) => {
  const [aiModels, setAiModels] = useState<API.AIModel[]>([]);
  const [defaultModel, setDefaultModel] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // Modal 状态
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedAiModel, setSelectedAiModel] = useState<string>('');
  const [articleMode, setArticleMode] = useState<ArticleMode>('title');

  // 进度 Modal 状态
  const [progressInfo, setProgressInfo] = useState({ current: 0, total: 0, percent: 0 });
  const [progressModalVisible, setProgressModalVisible] = useState(false);
  const [currentTopicTitle, setCurrentTopicTitle] = useState<string>('');

  // 获取 AI 模型列表
  const fetchAIModels = async () => {
    const res = await getAIModels();
    if (res.code === 200 && res.data) {
      setAiModels(res.data.models || []);
      setDefaultModel(res.data.default_model || '');
      setSelectedAiModel(res.data.default_model || '');
    }
  };

  // 页面加载时获取数据
  useEffect(() => {
    fetchAIModels();
  }, []);

  // 获取模式文本
  const getModeText = (mode: ArticleMode): string => {
    switch (mode) {
      case 'title':
        return '精简模式 (800-1500字)';
      case 'description':
        return '标准模式 (1000-2000字)';
      case 'full':
        return '详细模式 (1500-3000字)';
      default:
        return '精简模式';
    }
  };

  // 打开 Modal
  const openModal = () => {
    if (props.selectedRowKeys.length === 0) {
      message.warning('请先选择要生成文章的话题');
      return;
    }
    setModalVisible(true);
  };

  // 执行 AI 批量生成文章
  const handleGenerate = async () => {
    if (!selectedAiModel) {
      message.warning('请选择 AI 模型');
      return;
    }

    const topicIds = props.selectedRowKeys as number[];
    const total = topicIds.length;

    setModalVisible(false);
    setProgressModalVisible(true);
    setProgressInfo({ current: 0, total, percent: 0 });
    setLoading(true);

    let successCount = 0;
    let failCount = 0;
    const failedTopics: { id: number; title: string; error: string }[] = [];

    // 顺序执行 AI 生成
    for (let i = 0; i < topicIds.length; i++) {
      try {
        // 更新当前处理的话题标题
        setCurrentTopicTitle(`话题 ${i + 1}/${total}`);

        const res = await generateArticle({
          id: topicIds[i],
          mode: articleMode,
          model: selectedAiModel,
          variant_index: 0, // 批量生成使用默认变体
        });

        if (res.code === 200) {
          successCount++;
        } else {
          failCount++;
          failedTopics.push({
            id: topicIds[i],
            title: `话题 ${topicIds[i]}`,
            error: res.message || '未知错误',
          });
        }
      } catch (error: any) {
        failCount++;
        failedTopics.push({
          id: topicIds[i],
          title: `话题 ${topicIds[i]}`,
          error: error.message || '网络错误',
        });
      }

      // 更新进度
      const percent = Math.round(((i + 1) / total) * 100);
      setProgressInfo({ current: i + 1, total, percent });
    }

    setLoading(false);
    setProgressModalVisible(false);
    setCurrentTopicTitle('');

    // 显示结果
    if (failCount === 0) {
      message.success(`文章生成完成！成功 ${successCount} 篇，已保存到文章管理`);
    } else {
      Modal.warning({
        title: '文章生成完成（部分失败）',
        width: 500,
        content: (
          <div>
            <p>成功：{successCount} 篇</p>
            <p>失败：{failCount} 篇</p>
            {failedTopics.length > 0 && failedTopics.length <= 5 && (
              <div style={{ marginTop: 12 }}>
                <p style={{ fontWeight: 'bold' }}>失败详情：</p>
                {failedTopics.map((t) => (
                  <p key={t.id} style={{ fontSize: 12, color: '#666' }}>
                    {t.title}: {t.error}
                  </p>
                ))}
              </div>
            )}
            {failedTopics.length > 5 && (
              <div style={{ marginTop: 12 }}>
                <p style={{ fontSize: 12, color: '#666' }}>
                  失败话题过多，请检查网络或稍后重试
                </p>
              </div>
            )}
          </div>
        ),
      });
    }

    props.onConfirm();
  };

  return (
    <>
      <a
        style={{ color: 'inherit' }}
        onClick={() => {
          openModal();
        }}
      >
        <FileTextOutlined style={{ marginRight: 4 }} />
        批量生成文章
      </a>

      {/* AI 生成文章 Modal */}
      <Modal
        title="批量生成文章"
        open={modalVisible}
        onOk={handleGenerate}
        onCancel={() => setModalVisible(false)}
        confirmLoading={loading}
        width={500}
      >
        <Form layout="vertical">
          <Form.Item label="已选择话题数量">
            <span>{props.selectedRowKeys.length} 个</span>
          </Form.Item>

          <Form.Item label="生成模式" required>
            <Radio.Group
              value={articleMode}
              onChange={(e) => setArticleMode(e.target.value)}
            >
              <Radio value="title">精简模式</Radio>
              <Radio value="description">标准模式</Radio>
              <Radio value="full">详细模式</Radio>
            </Radio.Group>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              当前：{getModeText(articleMode)}
            </div>
          </Form.Item>

          <Form.Item label="AI 模型" required>
            <Select
              showSearch
              style={{ width: '100%' }}
              placeholder="请选择 AI 模型"
              value={selectedAiModel}
              onChange={(value) => setSelectedAiModel(value)}
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={aiModels.map((model) => ({
                label: `${model.label || model.name} - ${model.description || '默认模型'}`,
                value: model.name,
              }))}
            />
          </Form.Item>

          <div style={{ padding: '12px 0', color: '#666', fontSize: 12 }}>
            <p>• AI 将根据话题内容自动生成完整文章</p>
            <p>• 预计耗时：约 {props.selectedRowKeys.length * 8} 秒</p>
            <p>• 生成后的文章会自动保存到文章管理</p>
            <p>• 请确保网络连接稳定，生成过程中请勿关闭页面</p>
          </div>
        </Form>
      </Modal>

      {/* 生成进度 Modal */}
      <Modal
        title="AI 正在生成文章"
        open={progressModalVisible}
        footer={null}
        closable={false}
        width={450}
      >
        <div style={{ marginTop: 16 }}>
          <Progress
            percent={progressInfo.percent}
            status="active"
            format={() => `${progressInfo.current} / ${progressInfo.total}`}
          />
          <p style={{ marginTop: 16, color: '#666', textAlign: 'center', fontSize: 13 }}>
            正在处理：{currentTopicTitle || '准备中...'}
          </p>
          <p style={{ marginTop: 8, color: '#999', textAlign: 'center', fontSize: 12 }}>
            生成步骤：标题 → 内容 → 摘要 → 标签
          </p>
        </div>
      </Modal>
    </>
  );
};

export default BatchGenerateArticle;
