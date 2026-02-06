import { getList as getAccountList } from '@/services/content/platform_account/api';
import { publishArticle } from '@/services/content/publish/api';
import { SendOutlined } from '@ant-design/icons';
import { Button, Form, message, Modal, Select, Spin } from 'antd';
import React, { useEffect, useState } from 'react';

interface PorpsType {
  articleId?: number;
  articleIds?: number[];
  onConfirm: () => void;
}

// 平台选项映射
const platformMap: Record<string, string> = {
  zhihu: '知乎',
};

const PublishModal: React.FC<PorpsType> = (props) => {
  const [form] = Form.useForm();
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [platform, setPlatform] = useState<string>('zhihu');
  const [accountOptions, setAccountOptions] = useState<{ label: string; value: number }[]>([]);

  // 加载平台账号
  useEffect(() => {
    if (visible && platform) {
      const loadAccounts = async () => {
        setLoading(true);
        const res = await getAccountList({
          page: 1,
          limit: 1000,
          platform: platform,
          status: 1, // 只显示有效的账号
        });
        if (res.code === 200 && res.data?.items) {
          const options = res.data.items.map((item: API.ContentPlatformAccountList) => ({
            label: `${item.account_name} (${platformMap[item.platform] || item.platform})`,
            value: item.id,
          }));
          setAccountOptions(options);
        } else {
          setAccountOptions([]);
        }
        setLoading(false);
      };
      loadAccounts();
    }
  }, [visible, platform]);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      setConfirmLoading(true);

      let res: any;
      if (props.articleIds && props.articleIds.length > 1) {
        // 批量发布
        res = await publishArticle({
          article_ids: props.articleIds,
          platform: values.platform,
          platform_account_id: values.platform_account_id,
        } as any);
      } else {
        // 单篇发布
        res = await publishArticle({
          article_id: props.articleId || props.articleIds?.[0] || 0,
          platform: values.platform,
          platform_account_id: values.platform_account_id,
        });
      }

      if (res.code === 200) {
        message.success(res.message || '发布任务已创建');
        setVisible(false);
        form.resetFields();
        props.onConfirm();
      }
      setConfirmLoading(false);
    } catch (e) {
      setConfirmLoading(false);
    }
  };

  const handleCancel = () => {
    setVisible(false);
    form.resetFields();
  };

  return (
    <>
      {props.articleIds && props.articleIds.length > 1 ? (
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={() => setVisible(true)}
          disabled={props.articleIds.length === 0}
        >
          批量发布 ({props.articleIds.length})
        </Button>
      ) : (
        <Button
          type="link"
          icon={<SendOutlined />}
          onClick={() => setVisible(true)}
        >
          发布
        </Button>
      )}

      <Modal
        title={props.articleIds && props.articleIds.length > 1 ? '批量发布文章' : '发布文章'}
        open={visible}
        onOk={handleOk}
        onCancel={handleCancel}
        confirmLoading={confirmLoading}
        width={500}
        okText="创建发布任务"
        cancelText="取消"
      >
        <Spin spinning={loading}>
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              platform: 'zhihu',
              platform_account_id: undefined,
            }}
          >
            <Form.Item
              label="发布平台"
              name="platform"
              rules={[{ required: true, message: '请选择发布平台' }]}
            >
              <Select
                placeholder="请选择发布平台"
                options={[
                  { label: '知乎', value: 'zhihu' },
                ]}
                onChange={(value) => {
                  setPlatform(value);
                  form.setFieldValue('platform_account_id', undefined);
                }}
              />
            </Form.Item>

            <Form.Item
              label="平台账号"
              name="platform_account_id"
              rules={[{ required: true, message: '请选择平台账号' }]}
            >
              <Select
                placeholder={accountOptions.length > 0 ? '请选择平台账号' : '该平台暂无有效账号'}
                allowClear
                options={accountOptions}
                disabled={accountOptions.length === 0}
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
              />
            </Form.Item>

            {accountOptions.length === 0 && platform && (
              <div style={{ color: '#ff4d4f', marginTop: '-16px', marginBottom: '16px' }}>
                该平台暂无有效账号，请先在"平台账号"中添加账号
              </div>
            )}
          </Form>
        </Spin>
      </Modal>
    </>
  );
};

export default PublishModal;
