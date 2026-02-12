import { getList as getAccountList } from '@/services/content/platform_account/api';
import { fetchTopics } from '@/services/content/topic/api';
import { ThunderboltOutlined } from '@ant-design/icons';
import { ModalForm, ProFormSelect } from '@ant-design/pro-components';
import { Button, message } from 'antd';
import { useState } from 'react';

interface PropsType {
  onConfirm: () => void;
}

const FetchModal: React.FC<PropsType> = (props) => {
  const [accountOptions, setAccountOptions] = useState<{ label: string; value: number }[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchAccountOptions = async () => {
    const res = await getAccountList({ page: 1, limit: 100, platform: 'zhihu', status: 1 });
    if (res.code === 200 && res.data?.items) {
      const options = res.data.items.map((item: API.ContentPlatformAccountList) => ({
        label: `${item.account_name} (${item.status === 1 ? '有效' : '失效'})`,
        value: item.id,
      }));
      setAccountOptions(options);
    }
  };

  return (
    <ModalForm
      layout="horizontal"
      labelCol={{ span: 4 }}
      wrapperCol={{ span: 20 }}
      title="抓取知乎推荐话题"
      trigger={
        <Button type="primary" icon={<ThunderboltOutlined />}>
          抓取话题
        </Button>
      }
      autoFocusFirstInput
      isKeyPressSubmit
      onOpenChange={async (visible) => {
        if (visible) {
          fetchAccountOptions();
        }
      }}
      modalProps={{
        forceRender: true,
        destroyOnClose: true,
      }}
      onFinish={async (values) => {
        setLoading(true);
        try {
          const res = await fetchTopics({
            platform: 'zhihu',
            platform_account_id: values.platform_account_id,
            limit: values.limit || 20,
          });
          setLoading(false);
          if (res.code === 200) {
            message.success(res.message);
            props.onConfirm();
            return true;
          }
          return false;
        } catch (error) {
          setLoading(false);
          message.error('抓取失败，请稍后重试');
          return false;
        }
      }}
      submitter={{
        searchConfig: {
          submitText: '开始抓取',
          resetText: '取消',
        },
        submitButtonProps: {
          loading,
          disabled: loading,
        },
      }}
    >
      <ProFormSelect
        name="platform_account_id"
        label="知乎账号"
        placeholder="请选择要使用的知乎账号"
        options={accountOptions}
        rules={[{ required: true, message: '请选择知乎账号' }]}
        fieldProps={{
          showSearch: true,
          filterOption: (input, option) =>
            (option?.label ?? '').toLowerCase().includes(input.toLowerCase()),
        }}
      />
      <ProFormSelect
        name="limit"
        label="抓取数量"
        placeholder="请选择抓取数量"
        options={[
          { label: '10个', value: 10 },
          { label: '20个', value: 20 },
          { label: '50个', value: 50 },
        ]}
        initialValue={20}
        rules={[{ required: true, message: '请选择抓取数量' }]}
      />
    </ModalForm>
  );
};

export default FetchModal;
