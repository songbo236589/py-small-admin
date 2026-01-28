import { simpleList as industrySimpleList } from '@/services/quant/data/industry/api';
import { add, edit, update } from '@/services/quant/data/stock/api';
import {
  exchangeSelectOptions,
  listStatusSelectOptions,
  marketSelectOptions,
  stockTypeSelectOptions,
  tradeStatusSelectOptions,
} from '@/services/quant/data/stock/options';
import { FormOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';

import {
  DrawerForm,
  ProFormDatePicker,
  ProFormDigit,
  ProFormRadio,
  ProFormSelect,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { Button, Divider, Form, message, Select, Spin } from 'antd';
import React, { useRef, useState } from 'react';

interface PorpsType {
  onConfirm: () => void;
  id?: number;
}

const FormIndex: React.FC<PorpsType> = (porps) => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(porps.id ? false : true);
  const [industryList, setIndustryList] = useState<any>([]);
  const [industryListLoading, setIndustryListLoading] = useState<boolean>(false);

  const formData: API.StockForm = {
    id: null,
    stock_code: '',
    stock_name: '',
    market: null,
    exchange: null,
    list_status: 1,
    trade_status: 1,
    is_st: 0,
    stock_type: null,
    total_market_cap: null,
    circulating_market_cap: null,
    pe_ratio: null,
    pb_ratio: null,
    total_shares: null,
    circulating_shares: null,
    latest_price: null,
    open_price: null,
    close_price: null,
    high_price: null,
    low_price: null,
    change_percent: null,
    change_amount: null,
    change_speed: null,
    volume: null,
    amount: null,
    volume_ratio: null,
    turnover_rate: null,
    amplitude: null,
    change_5min: null,
    change_60day: null,
    change_ytd: null,
    list_date: null,
    delist_date: null,
    ipo_price: null,
    ipo_shares: null,
    description: '',
    website: '',
    logo_url: '',
    status: 1,
    industry_id: null,
  };

  return (
    <DrawerForm<API.StockForm>
      layout="horizontal"
      labelCol={{ span: 4 }}
      wrapperCol={{ span: 20 }}
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

          await setIndustryListLoading(true);
          const industryRes = await industrySimpleList({ status: 1, sort: '{"sort":"asc"}' });
          if (industryRes.code == 200) {
            await setIndustryListLoading(false);
            await setIndustryList(industryRes.data);
          }
        }
      }}
    >
      <Spin spinning={loading ? false : true}>
        {loading && (
          <div>
            {/* 基础信息 */}
            <Divider orientation="left">基础信息</Divider>
            <ProFormText
              label="股票代码"
              name="stock_code"
              rules={[{ required: true, message: '请输入股票代码' }]}
              fieldProps={{
                maxLength: 20,
                allowClear: true,
                placeholder: '请输入股票代码（如：600000.SH、000001.SZ）',
                showCount: true,
              }}
            />

            <ProFormText
              label="股票名称"
              name="stock_name"
              rules={[{ required: true, message: '请输入股票名称' }]}
              fieldProps={{
                maxLength: 100,
                allowClear: true,
                placeholder: '请输入股票名称',
                showCount: true,
              }}
            />

            <ProFormTextArea
              label="股票描述"
              name="description"
              fieldProps={{
                maxLength: 1000,
                allowClear: true,
                placeholder: '请输入股票描述/简介',
                showCount: true,
                rows: 4,
              }}
            />

            {/* 市场信息 */}
            <Divider orientation="left">市场信息</Divider>
            <ProFormSelect
              label="市场类型"
              name="market"
              rules={[{ required: true, message: '请选择市场类型' }]}
              options={marketSelectOptions}
              placeholder="请选择市场类型"
            />

            <ProFormSelect
              label="交易所"
              name="exchange"
              options={exchangeSelectOptions}
              placeholder="请选择交易所"
            />

            <ProFormSelect
              label="股票类型"
              name="stock_type"
              options={stockTypeSelectOptions}
              placeholder="请选择股票类型"
            />

            <Form.Item label="所属行业" name="industry_id">
              <Select
                showSearch
                allowClear
                filterOption={(input, option: any) =>
                  (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
                }
                loading={industryListLoading}
                notFoundContent="暂无所属行业"
                placeholder="请选择所属行业"
              >
                {industryList.map((item: any) => (
                  <Select.Option key={item.id} value={item.id}>
                    {item.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {/* 财务数据 */}
            <Divider orientation="left">财务数据</Divider>
            <ProFormDigit
              label="总市值"
              name="total_market_cap"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入总市值（单位：亿元）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="流通市值"
              name="circulating_market_cap"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入流通市值（单位：亿元）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="市盈率"
              name="pe_ratio"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入市盈率（动态）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="市净率"
              name="pb_ratio"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入市净率',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="总股本"
              name="total_shares"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入总股本（万股）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="流通股本"
              name="circulating_shares"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入流通股本（万股）',
                style: { width: '100%' },
              }}
            />

            {/* 实时交易数据 */}
            <Divider orientation="left">实时交易数据</Divider>
            <ProFormDigit
              label="最新价"
              name="latest_price"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入最新价',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="今开"
              name="open_price"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入今开',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="昨收"
              name="close_price"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入昨收',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="最高"
              name="high_price"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入最高',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="最低"
              name="low_price"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入最低',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="涨跌幅(%)"
              name="change_percent"
              fieldProps={{
                precision: 4,
                placeholder: '请输入涨跌幅（%）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="涨跌额"
              name="change_amount"
              fieldProps={{
                precision: 2,
                placeholder: '请输入涨跌额',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="涨速"
              name="change_speed"
              fieldProps={{
                precision: 4,
                placeholder: '请输入涨速',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="成交量"
              name="volume"
              fieldProps={{
                min: 0,
                precision: 0,
                placeholder: '请输入成交量',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="成交额"
              name="amount"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入成交额',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="量比"
              name="volume_ratio"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入量比',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="换手率(%)"
              name="turnover_rate"
              fieldProps={{
                min: 0,
                precision: 4,
                placeholder: '请输入换手率（%）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="振幅(%)"
              name="amplitude"
              fieldProps={{
                min: 0,
                precision: 4,
                placeholder: '请输入振幅（%）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="5分钟涨跌(%)"
              name="change_5min"
              fieldProps={{
                precision: 4,
                placeholder: '请输入5分钟涨跌（%）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="60日涨跌幅(%)"
              name="change_60day"
              fieldProps={{
                precision: 4,
                placeholder: '请输入60日涨跌幅（%）',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="年初至今涨跌幅(%)"
              name="change_ytd"
              fieldProps={{
                precision: 4,
                placeholder: '请输入年初至今涨跌幅（%）',
                style: { width: '100%' },
              }}
            />

            {/* IPO信息 */}
            <Divider orientation="left">IPO信息</Divider>
            <ProFormDatePicker
              label="上市日期"
              name="list_date"
              fieldProps={{
                style: { width: '100%' },
                placeholder: '请选择上市日期',
              }}
            />

            <ProFormDatePicker
              label="退市日期"
              name="delist_date"
              fieldProps={{
                style: { width: '100%' },
                placeholder: '请选择退市日期',
              }}
            />

            <ProFormDigit
              label="发行价格"
              name="ipo_price"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入发行价格',
                style: { width: '100%' },
              }}
            />

            <ProFormDigit
              label="发行数量"
              name="ipo_shares"
              fieldProps={{
                min: 0,
                precision: 2,
                placeholder: '请输入发行数量（万股）',
                style: { width: '100%' },
              }}
            />

            {/* 状态信息 */}
            <Divider orientation="left">状态信息</Divider>
            <ProFormSelect
              label="上市状态"
              name="list_status"
              rules={[{ required: true, message: '请选择上市状态' }]}
              options={listStatusSelectOptions}
              placeholder="请选择上市状态"
            />

            <ProFormSelect
              label="交易状态"
              name="trade_status"
              rules={[{ required: true, message: '请选择交易状态' }]}
              options={tradeStatusSelectOptions}
              placeholder="请选择交易状态"
            />

            <ProFormRadio.Group
              label="是否ST股"
              name="is_st"
              options={[
                { label: '否', value: 0 },
                { label: '是', value: 1 },
              ]}
            />

            <ProFormText
              label="官方网站"
              name="website"
              fieldProps={{
                maxLength: 200,
                allowClear: true,
                placeholder: '请输入官方网站',
                showCount: true,
              }}
            />

            <ProFormText
              label="Logo URL"
              name="logo_url"
              fieldProps={{
                maxLength: 500,
                allowClear: true,
                placeholder: '请输入公司Logo URL',
                showCount: true,
              }}
            />

            <ProFormRadio.Group
              label="记录状态"
              name="status"
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
