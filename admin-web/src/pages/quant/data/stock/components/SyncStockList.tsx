import { syncStockList } from '@/services/quant/data/stock/api';
import { marketSelectSyncStockListOptions } from '@/services/quant/data/stock/options';
import { SyncOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ModalForm, ProFormSelect } from '@ant-design/pro-components';
import { Button, message, Spin } from 'antd';
import React, { useRef, useState } from 'react';

interface PropsType {
  onConfirm?: () => void;
}

const SyncStockList: React.FC<PropsType> = (props) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(false);

  const formData = {
    market: 1,
  };

  return (
    <ModalForm
      width={600}
      layout="horizontal"
      labelCol={{ span: 4 }}
      wrapperCol={{ span: 20 }}
      formRef={restFormRef}
      initialValues={formData}
      title="同步股票列表"
      autoFocusFirstInput
      isKeyPressSubmit
      trigger={
        <Button type="primary">
          <SyncOutlined />
          同步股票列表
        </Button>
      }
      modalProps={{
        forceRender: true,
        destroyOnClose: true,
      }}
      submitter={{
        render: (formProps, defaultDoms) => {
          return [
            ...defaultDoms,
            <Button
              key="extra-reset"
              onClick={async () => {
                formProps.reset();
              }}
            >
              重置
            </Button>,
          ];
        },
      }}
      onFinish={async (values: any) => {
        setLoading(true);
        try {
          const res = await syncStockList(values.market);
          if (res.code === 200) {
            message.success(res.message || '同步成功');
            props.onConfirm?.();
            return true;
          } else {
            message.error(res.message || '同步失败');
            return false;
          }
        } catch (error) {
          message.error('同步失败，请稍后重试');
          return false;
        } finally {
          setLoading(false);
        }
      }}
    >
      <Spin spinning={loading}>
        <ProFormSelect
          label="市场类型"
          name="market"
          rules={[{ required: true, message: '请选择市场类型' }]}
          options={marketSelectSyncStockListOptions}
          placeholder="请选择市场类型"
          fieldProps={{
            disabled: loading,
          }}
        />
        <div style={{ color: '#999', fontSize: 12, marginTop: 16 }}>
          注意：同步操作可能需要较长时间，请耐心等待。
        </div>
      </Spin>
    </ModalForm>
  );
};

export default SyncStockList;
