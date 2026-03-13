import { fetchZhihuContent } from '@/services/content/manage/topic/api';
import { CloudDownloadOutlined } from '@ant-design/icons';
import { message, Modal, Progress } from 'antd';
import { useState } from 'react';

interface PropsType {
  selectedRowKeys: React.Key[];
  onConfirm: () => void;
}

const MAX_BATCH_SIZE = 50; // 单次最多处理数量

const BatchFetchZhihuContent: React.FC<PropsType> = (props) => {
  const [loading, setLoading] = useState(false);
  const [confirmModalVisible, setConfirmModalVisible] = useState(false);

  // 进度 Modal 状态
  const [progressInfo, setProgressInfo] = useState({ current: 0, total: 0, percent: 0 });
  const [progressModalVisible, setProgressModalVisible] = useState(false);

  // 打开确认 Modal
  const openConfirmModal = () => {
    if (props.selectedRowKeys.length === 0) {
      message.warning('请先选择要获取内容的话题');
      return;
    }

    if (props.selectedRowKeys.length > MAX_BATCH_SIZE) {
      message.warning(`单次最多支持 ${MAX_BATCH_SIZE} 个话题，请减少选择数量`);
      return;
    }

    setConfirmModalVisible(true);
  };

  // 执行批量获取
  const handleFetch = async () => {
    const topicIds = props.selectedRowKeys as number[];
    const total = topicIds.length;

    setConfirmModalVisible(false);
    setProgressModalVisible(true);
    setProgressInfo({ current: 0, total, percent: 0 });
    setLoading(true);

    let successCount = 0;
    let failCount = 0;
    const failedTopics: { id: number; error: string }[] = [];

    // 顺序执行获取
    for (let i = 0; i < topicIds.length; i++) {
      try {
        const res = await fetchZhihuContent(topicIds[i]);
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
      message.success(`内容获取完成！成功 ${successCount} 个`);
    } else {
      Modal.warning({
        title: '内容获取完成（部分失败）',
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
            {failedTopics.length > 5 && (
              <div style={{ marginTop: 8 }}>
                <p style={{ fontSize: 12, color: '#666' }}>
                  失败话题过多，请检查网络或话题链接有效性
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
          openConfirmModal();
        }}
      >
        <CloudDownloadOutlined style={{ marginRight: 4 }} />
        批量获取内容
      </a>

      {/* 确认 Modal */}
      <Modal
        title="批量获取知乎内容"
        open={confirmModalVisible}
        onOk={handleFetch}
        onCancel={() => setConfirmModalVisible(false)}
        confirmLoading={loading}
        width={450}
      >
        <div style={{ padding: '12px 0' }}>
          <p>已选择话题数量：<strong>{props.selectedRowKeys.length}</strong> 个</p>
          <p style={{ marginTop: 16, color: '#666', fontSize: 13 }}>
            • 将从知乎获取话题的详细内容（问题描述、回答数、浏览量等）
          </p>
          <p style={{ color: '#666', fontSize: 13 }}>
            • 预计耗时：约 {props.selectedRowKeys.length * 3} 秒
          </p>
          <p style={{ color: '#ff4d4f', fontSize: 13 }}>
            • 请确保网络连接稳定
          </p>
        </div>
      </Modal>

      {/* 进度 Modal */}
      <Modal
        title="正在获取内容"
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

export default BatchFetchZhihuContent;
