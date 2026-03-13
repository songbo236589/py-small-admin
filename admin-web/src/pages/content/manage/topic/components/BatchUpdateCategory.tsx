import { batchUpdateCategory, generateCategory } from '@/services/content/manage/topic/api';
import { getTree as getCategoryTree } from '@/services/content/manage/category/api';
import { getModels as getAIModels } from '@/services/content/ai/api';
import type { API } from '@/services/content/ai/typings';
import { FolderOutlined, RobotOutlined } from '@ant-design/icons';
import { Button, Form, message, Modal, Progress, Select, TreeSelect } from 'antd';
import { Dropdown, Space } from 'antd';
import type { MenuProps } from 'antd';
import { useEffect, useState } from 'react';

interface PropsType {
  selectedRowKeys: React.Key[];
  onConfirm: () => void;
}

const BatchUpdateCategory: React.FC<PropsType> = (props) => {
  const [categoryTreeData, setCategoryTreeData] = useState<any[]>([]);
  const [aiModels, setAiModels] = useState<API.AIModel[]>([]);
  const [defaultModel, setDefaultModel] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // 手动设置 Modal 状态
  const [manualModalVisible, setManualModalVisible] = useState(false);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);

  // AI 设置 Modal 状态
  const [aiModalVisible, setAiModalVisible] = useState(false);
  const [selectedAiModel, setSelectedAiModel] = useState<string>('');

  // 进度 Modal 状态
  const [aiProgress, setAiProgress] = useState({ current: 0, total: 0 });
  const [progressModalVisible, setProgressModalVisible] = useState(false);
  const [progressInfo, setProgressInfo] = useState({ current: 0, total: 0, percent: 0 });

  // 获取分类树数据
  const fetchCategoryTree = async () => {
    const res = await getCategoryTree({ status: 1 });
    if (res.code === 200 && res.data) {
      setCategoryTreeData(res.data);
    }
  };

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
    fetchCategoryTree();
    fetchAIModels();
  }, []);

  // 打开手动设置 Modal
  const openManualModal = () => {
    setSelectedCategoryId(null);
    setManualModalVisible(true);
  };

  // 打开 AI 设置 Modal
  const openAIModal = () => {
    setAiModalVisible(true);
  };

  // 执行手动批量更新
  const handleManualUpdate = async () => {
    if (props.selectedRowKeys.length === 0) {
      message.warning('请先选择要更新的话题');
      return;
    }

    setLoading(true);
    try {
      const res = await batchUpdateCategory({
        id_array: props.selectedRowKeys as number[],
        category_id: selectedCategoryId,
      });
      setLoading(false);
      if (res.code === 200) {
        message.success(res.message);
        setManualModalVisible(false);
        props.onConfirm();
      }
    } catch (error) {
      setLoading(false);
      message.error('更新失败，请稍后重试');
    }
  };

  // 执行 AI 批量生成
  const handleAIUpdate = async () => {
    if (!selectedAiModel) {
      message.warning('请选择 AI 模型');
      return;
    }

    const topicIds = props.selectedRowKeys as number[];
    const total = topicIds.length;

    setAiModalVisible(false);
    setProgressModalVisible(true);
    setProgressInfo({ current: 0, total, percent: 0 });
    setLoading(true);

    let successCount = 0;
    let failCount = 0;
    const failedTopics: { id: number; error: string }[] = [];

    // 顺序执行 AI 生成
    for (let i = 0; i < topicIds.length; i++) {
      try {
        const res = await generateCategory(topicIds[i], { model: selectedAiModel });
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
      message.success(`AI 分类完成！成功 ${successCount} 个`);
    } else {
      Modal.warning({
        title: 'AI 分类完成（部分失败）',
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

  // 下拉菜单项
  const menuItems: MenuProps['items'] = [
    {
      key: 'manual',
      label: (
        <span>
          <FolderOutlined style={{ marginRight: 8 }} />
          手动设置分类
        </span>
      ),
      onClick: openManualModal,
    },
    {
      key: 'divider',
      type: 'divider',
    },
    {
      key: 'ai',
      label: (
        <span>
          <RobotOutlined style={{ marginRight: 8 }} />
          AI 智能分类
        </span>
      ),
      onClick: openAIModal,
    },
  ];

  return (
    <>
      <Dropdown menu={{ items: menuItems }} trigger={['click']}>
        <a style={{ color: 'inherit' }}>
          <FolderOutlined style={{ marginRight: 4 }} />
          批量设置分类
        </a>
      </Dropdown>

      {/* 手动设置分类 Modal */}
      <Modal
        title="手动设置分类"
        open={manualModalVisible}
        onOk={handleManualUpdate}
        onCancel={() => setManualModalVisible(false)}
        confirmLoading={loading}
        width={500}
      >
        <Form layout="vertical">
          <Form.Item label="已选择话题数量">
            <span>{props.selectedRowKeys.length} 个</span>
          </Form.Item>
          <Form.Item label="选择分类">
            <TreeSelect
              showSearch
              allowClear
              treeDefaultExpandAll
              style={{ width: '100%' }}
              dropdownStyle={{ maxHeight: 400, overflow: 'auto' }}
              placeholder="请选择分类（留空则清除分类）"
              treeData={categoryTreeData}
              fieldNames={{ label: 'title', value: 'value', children: 'children' }}
              onChange={(value) => setSelectedCategoryId(value as number | null)}
              filterTreeNode={(input, treeNode) => {
                return (treeNode.title as string)?.toLowerCase().includes(input.toLowerCase());
              }}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* AI 智能分类 Modal */}
      <Modal
        title="AI 智能分类"
        open={aiModalVisible}
        onOk={handleAIUpdate}
        onCancel={() => setAiModalVisible(false)}
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
            <p>• AI 将根据话题标题自动分配到合适的分类</p>
            <p>• 预计耗时：约 {props.selectedRowKeys.length * 3} 秒</p>
            <p>• 不同话题可能会被分配到不同的分类</p>
          </div>
        </Form>
      </Modal>

      {/* AI 生成进度 Modal */}
      <Modal
        title="AI 正在生成分类"
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

export default BatchUpdateCategory;
