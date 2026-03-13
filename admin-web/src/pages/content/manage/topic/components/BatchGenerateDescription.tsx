import { generateDescription } from '@/services/content/manage/topic/api';
import { getModels as getAIModels } from '@/services/content/ai/api';
import type { API } from '@/services/content/ai/typings';
import { FileTextOutlined, RobotOutlined } from '@ant-design/icons';
import { Button, Form, message, Modal, Progress, Select } from 'antd';
import { useEffect, useState } from 'react';

interface PropsType {
  selectedRowKeys: React.Key[];
  onConfirm: () => void;
}

const BatchGenerateDescription: React.FC<PropsType> = (props) => {
  const [aiModels, setAiModels] = useState<API.AIModel[]>([]);
  const [defaultModel, setDefaultModel] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // Modal 状态
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedAiModel, setSelectedAiModel] = useState<string>('');

  // 进度 Modal 状态
  const [progressInfo, setProgressInfo] = useState({ current: 0, total: 0, percent: 0 });
  const [progressModalVisible, setProgressModalVisible] = useState(false);

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

  // 打开 Modal
  const openModal = () => {
    setModalVisible(true);
  };

  // 执行 AI 批量生成描述
  const handleGenerate = async () => {
    if (props.selectedRowKeys.length === 0) {
      message.warning('请先选择要生成描述的话题');
      return;
    }

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
    const failedTopics: { id: number; error: string }[] = [];

    // 顺序执行 AI 生成
    for (let i = 0; i < topicIds.length; i++) {
      try {
        const res = await generateDescription(topicIds[i], { model: selectedAiModel });
        if (res.code === 200) {
          successCount++;
        } else {
          failCount++;
          failedTopics.push({ id: topicIds[i], error: res.message || '未知错误' });
        }
      } catch (error: any) {
        failCount++;
        failedTopics.push({ id: topicIds[i], error: error.message || '网络错误' });
      }

      // 更新进度
      const percent = Math.round(((i + 1) / total) * 100);
      setProgressInfo({ current: i + 1, total, percent });
    }

    setLoading(false);
    setProgressModalVisible(false);

    // 显示结果
    if (failCount === 0) {
      message.success(`AI 描述生成完成！成功 ${successCount} 个`);
    } else {
      Modal.warning({
        title: 'AI 描述生成完成（部分失败）',
        content: (
          <div>
            <p>成功：{successCount} 个</p>
            <p>失败：{failCount} 个</p>
            {failedTopics.length > 0 && failedTopics.length <= 5 && (
              <div style={{ marginTop: 8 }}>
                <p style={{ fontWeight: 'bold' }}>失败详情：</p>
                {failedTopics.map((t) => (
                  <p key={t.id} style={{ fontSize: 12, color: '#666' }}>
                    ID {t.id}: {t.error}
                  </p>
                ))}
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
        批量生成描述
      </a>

      {/* AI 生成描述 Modal */}
      <Modal
        title="AI 批量生成描述"
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
          <Form.Item label="选择 AI 模型" required>
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
            <p>• AI 将根据话题标题自动生成问题描述</p>
            <p>• 预计耗时：约 {props.selectedRowKeys.length * 3} 秒</p>
            <p>• 生成后的描述会覆盖原有描述</p>
          </div>
        </Form>
      </Modal>

      {/* AI 生成进度 Modal */}
      <Modal
        title="AI 正在生成描述"
        open={progressModalVisible}
        footer={null}
        closable={false}
        width={400}
      >
        <div style={{ marginTop: 16 }}>
          <Progress
            percent={progressInfo.percent}
            status="active"
            format={() => `${progressInfo.current} / ${progressInfo.total}`}
          />
          <p style={{ marginTop: 16, color: '#666', textAlign: 'center' }}>
            正在处理，请稍候...
          </p>
        </div>
      </Modal>
    </>
  );
};

export default BatchGenerateDescription;
