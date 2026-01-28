import { add, edit, update } from '@/services/quant/data/industry/api';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';

import {
  DrawerForm,
  ProFormDigit,
  ProFormRadio,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { Button, message, Spin } from 'antd';
import React, { useRef, useState } from 'react';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
}
const FormIndex: React.FC<PorpsType> = (porps) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(porps.id ? false : true);

  const formData: API.QuantIndustryForm = {
    id: null,
    name: '',
    code: '',
    sort: 1,
    latest_price: 0,
    change_amount: 0,
    change_percent: 0,
    total_market_cap: 0,
    turnover_rate: 0,
    up_count: 0,
    down_count: 0,
    leading_stock: '',
    leading_stock_change: 0,
    description: '',
    status: 1,
  };
  return (
    <DrawerForm<API.QuantIndustryForm>
      layout="horizontal"
      labelCol={{ span: 3 }}
      wrapperCol={{ span: 21 }}
      formRef={restFormRef}
      initialValues={formData}
      title={porps.id ? '编辑' : '添加'}
      autoFocusFirstInput
      isKeyPressSubmit
      trigger={
        porps.id ? (
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
      }}
      submitter={{
        render: (props, defaultDoms) => {
          return [
            ...defaultDoms,
            <Button
              loading={loading ? false : true}
              key="extra-reset"
              onClick={async () => {
                const id = props.form?.getFieldValue('id');
                if (id) {
                  await setLoading(false);
                  const res = await edit(id);
                  if (res.code === 200) {
                    restFormRef.current?.setFieldsValue(res.data);

                    await setLoading(true);
                  }
                } else {
                  props.reset();
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
        if (porps.id) {
          res = await update(porps.id, values);
        } else {
          res = await add(values);
        }
        if (res.code === 200) {
          message.success(res.message);
          porps.onConfirm();
          return true;
        }
        return false;
      }}
      onOpenChange={async (visible) => {
        if (visible) {
          if (porps.id) {
            await setLoading(false);
            const res = await edit(porps.id);
            if (res.code === 200) {
              await restFormRef.current?.setFieldsValue(res.data);

              await setLoading(true);
            }
          }
        }
      }}
    >
      <Spin spinning={loading ? false : true}>
        {loading && (
          <div>
            <ProFormText
              label="行业名称"
              name="name"
              rules={[{ required: true, message: '请输入行业名称' }]}
              fieldProps={{
                maxLength: 50,
                allowClear: true,
                placeholder: '请输入行业名称（如：电子化学品、银行、房地产）',
                showCount: true,
              }}
            />

            <ProFormText
              label="行业代码"
              name="code"
              rules={[{ required: true, message: '请输入行业代码' }]}
              fieldProps={{
                maxLength: 20,
                allowClear: true,
                placeholder: '请输入行业代码（如：BK0433、BK0001）',
                showCount: true,
              }}
            />

            <ProFormDigit
              label="最新价"
              name="latest_price"
              fieldProps={{
                placeholder: '请输入最新价',
                min: 0,
                precision: 2,
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="涨跌额"
              name="change_amount"
              fieldProps={{
                placeholder: '请输入涨跌额',
                precision: 2,
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="涨跌幅"
              name="change_percent"
              fieldProps={{
                placeholder: '请输入涨跌幅（%）',
                min: -100,
                max: 100,
                precision: 2,
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="总市值"
              name="total_market_cap"
              fieldProps={{
                placeholder: '请输入总市值',
                min: 0,
                precision: 2,
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="换手率"
              name="turnover_rate"
              fieldProps={{
                placeholder: '请输入换手率（%）',
                min: 0,
                max: 100,
                precision: 2,
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="上涨家数"
              name="up_count"
              fieldProps={{
                placeholder: '请输入上涨家数',
                min: 0,
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="下跌家数"
              name="down_count"
              fieldProps={{
                placeholder: '请输入下跌家数',
                min: 0,
                style: { width: '100%' },
              }}
            />

            <ProFormText
              label="领涨股票"
              name="leading_stock"
              fieldProps={{
                maxLength: 50,
                allowClear: true,
                placeholder: '请输入领涨股票',
                showCount: true,
              }}
            />

            <ProFormDigit
              label="领涨涨跌幅"
              name="leading_stock_change"
              fieldProps={{
                placeholder: '请输入领涨涨跌幅（%）',
                min: -100,
                max: 100,
                precision: 2,
                style: { width: '100%' },
              }}
            />

            <ProFormTextArea
              label="行业描述"
              name="description"
              fieldProps={{
                maxLength: 500,
                allowClear: true,
                placeholder: '请输入行业描述',
                showCount: true,
                rows: 4,
              }}
            />

            <ProFormDigit
              label="排序"
              name="sort"
              rules={[{ required: true, message: '请输入排序' }]}
              fieldProps={{
                placeholder: '请输入排序',
                min: 0,
                style: { width: '100%' },
              }}
            />

            <ProFormRadio.Group
              name="status"
              label="状态"
              rules={[{ required: true, message: '请选择状态' }]}
              options={[
                { label: '禁用', value: 0 },
                { label: '启用', value: 1 },
              ]}
            />
          </div>
        )}
      </Spin>
    </DrawerForm>
  );
};
export default FormIndex;
