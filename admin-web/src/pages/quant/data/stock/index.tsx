import { CDel, CDelAll, ProTableWrapper } from '@/components';
import { simpleList } from '@/services/quant/data/concept/api';
import { simpleList as industrySimpleList } from '@/services/quant/data/industry/api';
import { syncKline1d, syncSingleKline1d } from '@/services/quant/data/kline/api';
import { destroy, destroyAll, getList, setStatus } from '@/services/quant/data/stock/api';
import {
  exchangeOptions,
  listStatusOptions,
  marketOptions,
  stockTypeOptions,
  tradeStatusOptions,
} from '@/services/quant/data/stock/options';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import { SyncOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Button, message, Space, Switch, Tag } from 'antd';
import React, { useEffect, useRef, useState } from 'react';

import FormIndex from './components/FormIndex';
import SyncStockList from './components/SyncStockList';

const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const [syncKline1dLoading, setSyncKline1dLoading] = useState(false);
  const [syncSingleLoading, setSyncSingleLoading] = useState<Record<number, boolean>>({});
  const { initialState } = useModel('@@initialState');
  const [conceptList, setConceptList] = useState<any>([]);
  const [industryList, setIndustryList] = useState<any>([]);
  let maps = {};

  // 从 URL 中获取 concept_id 参数
  const urlParams = new URLSearchParams(window.location.search);
  const conceptIdFromUrl = urlParams.get('concept_id');
  const industryIdFromUrl = urlParams.get('industry_id');
  // 获取概念数据
  const fetchConceptList = async () => {
    const res = await simpleList({ status: 1, sort: '{"sort":"asc"}' });
    if (res.code === 200) {
      const conceptListData: Record<string, { text: string; status: number }> = {};
      for (let i = 0; i < res.data.length; i++) {
        conceptListData[res.data[i].id + '-'] = {
          text: res.data[i].name,
          status: res.data[i].id,
        };
      }
      if (conceptListData.length) await setConceptList({ ...conceptListData });
    }
  };

  // 获取行业数据
  const fetchIndustryList = async () => {
    const res = await industrySimpleList({ status: 1, sort: '{"sort":"asc"}' });
    if (res.code === 200) {
      const industryListData: Record<string, { text: string; status: number }> = {};
      for (let i = 0; i < res.data.length; i++) {
        industryListData[res.data[i].id + '-'] = {
          text: res.data[i].name,
          status: res.data[i].id,
        };
      }
      if (industryListData.length) await setIndustryList({ ...industryListData });
    }
  };

  // 页面加载时获取概念数据和行业数据
  useEffect(() => {
    fetchConceptList();
    fetchIndustryList();
  }, []);

  const handleSyncKline1d = async () => {
    setSyncKline1dLoading(true);
    try {
      const res = await syncKline1d();
      if (res.code === 200) {
        message.success(res.message || '同步日K线成功');
        actionRef.current?.reload();
      }
    } finally {
      setSyncKline1dLoading(false);
    }
  };

  const handleSyncSingleKline1d = async (row: API.StockList) => {
    setSyncSingleLoading((prev) => ({ ...prev, [row.id]: true }));
    try {
      const res = await syncSingleKline1d({
        id: row.id,
      });
      if (res.code === 200) {
        message.success(res.message || `同步${row.stock_name}日K线成功`);
        actionRef.current?.reload();
      }
    } finally {
      setSyncSingleLoading((prev) => ({ ...prev, [row.id]: false }));
    }
  };

  const columns: ProColumns<API.StockList>[] = [
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      align: 'center',
      width: 120,
      ellipsis: true,
      copyable: true,
      fixed: true,
    },
    {
      title: '股票名称',
      dataIndex: 'stock_name',
      align: 'center',
      width: 200,
      ellipsis: true,
      copyable: true,
      fixed: true,
    },
    {
      title: '市场',
      dataIndex: 'market',
      valueType: 'select',
      valueEnum: marketOptions,
      align: 'center',
      width: 100,
    },
    {
      title: '交易所',
      dataIndex: 'exchange',
      valueType: 'select',
      valueEnum: exchangeOptions,
      align: 'center',
      width: 200,
    },
    {
      title: '行业',
      dataIndex: 'industry',
      align: 'center',
      width: 100,
      ellipsis: true,
      copyable: true,
      render: (text, record) => [<span key={record.id}>{record.industry?.name}</span>],
    },
    {
      title: '行业',
      dataIndex: 'industry_id',
      valueType: 'select',
      fieldProps: {
        showSearch: true,
      },
      valueEnum: industryList,
      hideInTable: true,
      initialValue: industryIdFromUrl,
    },
    {
      title: '概念',
      dataIndex: 'concepts',
      align: 'center',
      width: 300,
      hideInSearch: true,
      render: (_, record) => {
        if (!record.concepts || record.concepts.length === 0) {
          return '-';
        }
        return (
          <Space size={[4, 4]} wrap>
            {record.concepts.map((concept: any) => (
              <Tag key={concept.id} color="blue">
                {concept.name}
              </Tag>
            ))}
          </Space>
        );
      },
    },
    {
      title: '概念',
      dataIndex: 'concept_id',
      valueType: 'select',
      fieldProps: {
        showSearch: true,
      },
      valueEnum: conceptList,
      hideInTable: true,
      initialValue: conceptIdFromUrl,
    },
    {
      title: '上市状态',
      dataIndex: 'list_status',
      valueType: 'select',
      valueEnum: listStatusOptions,
      align: 'center',
      width: 100,
    },
    {
      title: '交易状态',
      dataIndex: 'trade_status',
      valueType: 'select',
      valueEnum: tradeStatusOptions,
      align: 'center',
      width: 100,
    },
    {
      title: '是否ST',
      dataIndex: 'is_st',
      valueType: 'select',
      valueEnum: {
        0: { text: '否', status: 'Default' },
        1: { text: '是', status: 'Error' },
      },
      align: 'center',
      width: 80,
    },
    {
      title: '股票类型',
      dataIndex: 'stock_type',
      valueType: 'select',
      valueEnum: stockTypeOptions,
      align: 'center',
      width: 100,
    },
    {
      title: '总市值(亿)',
      dataIndex: 'total_market_cap',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '总市值(亿)',
      dataIndex: 'total_market_cap',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'total_market_cap[start]': value[0],
            'total_market_cap[end]': value[1],
          };
        },
      },
    },
    {
      title: '流通市值(亿)',
      dataIndex: 'circulating_market_cap',
      align: 'center',
      width: 120,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '流通市值(亿)',
      dataIndex: 'circulating_market_cap',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'circulating_market_cap[start]': value[0],
            'circulating_market_cap[end]': value[1],
          };
        },
      },
    },
    {
      title: '市盈率',
      dataIndex: 'pe_ratio',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '市盈率',
      dataIndex: 'pe_ratio',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'pe_ratio[start]': value[0],
            'pe_ratio[end]': value[1],
          };
        },
      },
    },
    {
      title: '市净率',
      dataIndex: 'pb_ratio',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '市净率',
      dataIndex: 'pb_ratio',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'pb_ratio[start]': value[0],
            'pb_ratio[end]': value[1],
          };
        },
      },
    },
    {
      title: '总股本(万股)',
      dataIndex: 'total_shares',
      align: 'center',
      width: 120,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '总股本(万股)',
      dataIndex: 'total_shares',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'total_shares[start]': value[0],
            'total_shares[end]': value[1],
          };
        },
      },
    },
    {
      title: '流通股本(万股)',
      dataIndex: 'circulating_shares',
      align: 'center',
      width: 140,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '流通股本',
      dataIndex: 'circulating_shares',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'circulating_shares[start]': value[0],
            'circulating_shares[end]': value[1],
          };
        },
      },
    },
    {
      title: '最新价',
      dataIndex: 'latest_price',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '最新价',
      dataIndex: 'latest_price',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'latest_price[start]': value[0],
            'latest_price[end]': value[1],
          };
        },
      },
    },
    {
      title: '今开',
      dataIndex: 'open_price',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '今开',
      dataIndex: 'open_price',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'open_price[start]': value[0],
            'open_price[end]': value[1],
          };
        },
      },
    },
    {
      title: '昨收',
      dataIndex: 'close_price',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '昨收',
      dataIndex: 'close_price',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'close_price[start]': value[0],
            'close_price[end]': value[1],
          };
        },
      },
    },
    {
      title: '最高',
      dataIndex: 'high_price',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '最高',
      dataIndex: 'high_price',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'high_price[start]': value[0],
            'high_price[end]': value[1],
          };
        },
      },
    },
    {
      title: '最低',
      dataIndex: 'low_price',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '最低',
      dataIndex: 'low_price',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'low_price[start]': value[0],
            'low_price[end]': value[1],
          };
        },
      },
    },
    {
      title: '涨跌幅(%)',
      dataIndex: 'change_percent',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,

      render: (text: any, record) => [
        <span style={{ color: text > 0 ? '#ff4d4f' : '#000000' }} key={record.id}>
          {text}
        </span>,
      ],
    },
    {
      title: '涨跌幅(%)',
      dataIndex: 'change_percent',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_percent[start]': value[0],
            'change_percent[end]': value[1],
          };
        },
      },
    },
    {
      title: '涨跌额',
      dataIndex: 'change_amount',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text: any, record) => [
        <span style={{ color: text > 0 ? '#ff4d4f' : '#000000' }} key={record.id}>
          {text}
        </span>,
      ],
    },
    {
      title: '涨跌额',
      dataIndex: 'change_amount',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_amount[start]': value[0],
            'change_amount[end]': value[1],
          };
        },
      },
    },
    {
      title: '涨速',
      dataIndex: 'change_speed',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '涨速',
      dataIndex: 'change_speed',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_speed[start]': value[0],
            'change_speed[end]': value[1],
          };
        },
      },
    },
    {
      title: '成交量(亿)',
      dataIndex: 'volume',
      align: 'center',
      width: 120,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '成交量(亿)',
      dataIndex: 'volume',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'volume[start]': value[0],
            'volume[end]': value[1],
          };
        },
      },
    },
    {
      title: '成交额(亿)',
      dataIndex: 'amount',
      align: 'center',
      width: 120,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '成交额(亿)',
      dataIndex: 'amount',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'amount[start]': value[0],
            'amount[end]': value[1],
          };
        },
      },
    },
    {
      title: '量比',
      dataIndex: 'volume_ratio',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '量比',
      dataIndex: 'volume_ratio',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'volume_ratio[start]': value[0],
            'volume_ratio[end]': value[1],
          };
        },
      },
    },
    {
      title: '换手率(%)',
      dataIndex: 'turnover_rate',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '换手率(%)',
      dataIndex: 'turnover_rate',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'turnover_rate[start]': value[0],
            'turnover_rate[end]': value[1],
          };
        },
      },
    },
    {
      title: '振幅(%)',
      dataIndex: 'amplitude',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '振幅(%)',
      dataIndex: 'amplitude',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'amplitude[start]': value[0],
            'amplitude[end]': value[1],
          };
        },
      },
    },
    {
      title: '5分钟涨跌(%)',
      dataIndex: 'change_5min',
      align: 'center',
      width: 120,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '5分钟涨跌(%)',
      dataIndex: 'change_5min',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_5min[start]': value[0],
            'change_5min[end]': value[1],
          };
        },
      },
    },
    {
      title: '60日涨跌幅(%)',
      dataIndex: 'change_60day',
      align: 'center',
      width: 140,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '60日涨跌幅(%)',
      dataIndex: 'change_60day',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_60day[start]': value[0],
            'change_60day[end]': value[1],
          };
        },
      },
    },
    {
      title: '年初至今涨跌幅(%)',
      dataIndex: 'change_ytd',
      align: 'center',
      width: 160,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '年初至今涨跌幅(%)',
      dataIndex: 'change_ytd',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'change_ytd[start]': value[0],
            'change_ytd[end]': value[1],
          };
        },
      },
    },
    {
      title: '上市日期',
      dataIndex: 'list_date',
      valueType: 'date',
      align: 'center',
      width: 120,
      hideInSearch: true,
      sorter: true,
    },
    {
      title: '上市日期',
      dataIndex: 'list_date',
      valueType: 'dateRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'list_date[start]': value[0],
            'list_date[end]': value[1],
          };
        },
      },
    },
    {
      title: '退市日期',
      dataIndex: 'delist_date',
      valueType: 'date',
      align: 'center',
      width: 120,
      hideInSearch: true,
      sorter: true,
    },
    {
      title: '退市日期',
      dataIndex: 'delist_date',
      valueType: 'dateRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'delist_date[start]': value[0],
            'delist_date[end]': value[1],
          };
        },
      },
    },
    {
      title: '发行价格',
      dataIndex: 'ipo_price',
      align: 'center',
      width: 100,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '发行价格',
      dataIndex: 'ipo_price',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'ipo_price[start]': value[0],
            'ipo_price[end]': value[1],
          };
        },
      },
    },
    {
      title: '发行数(万股)',
      dataIndex: 'ipo_shares',
      align: 'center',
      width: 140,
      hideInSearch: true,
      sorter: true,
      render: (text, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '发行数量(万股)',
      dataIndex: 'ipo_shares',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'ipo_shares[start]': value[0],
            'ipo_shares[end]': value[1],
          };
        },
      },
    },
    {
      title: '股票描述',
      dataIndex: 'description',
      align: 'center',
      width: 200,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '官方网站',
      dataIndex: 'website',
      align: 'center',
      width: 150,
      ellipsis: true,
      render: (_, record) =>
        record.website ? (
          <a href={record.website} target="_blank" rel="noopener noreferrer">
            {record.website}
          </a>
        ) : (
          '-'
        ),
    },
    {
      title: 'Logo',
      dataIndex: 'logo_url',
      align: 'center',
      width: 100,
      hideInSearch: true,
      render: (_, record) =>
        record.logo_url ? (
          <img
            src={record.logo_url}
            alt="logo"
            style={{ width: 40, height: 40, objectFit: 'cover' }}
          />
        ) : (
          '-'
        ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        0: { text: '禁用', status: '0' },
        1: { text: '启用', status: '1' },
      },
      hideInTable: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      hideInSearch: true,
      width: 100,
      align: 'center',
      render: (text, record) => [
        <Switch
          key={record.id}
          checkedChildren="启用"
          unCheckedChildren="禁用"
          defaultChecked={record.status === 1 ? true : false}
          onChange={async (checked: boolean) => {
            const res = await setStatus(record.id, { status: checked ? 1 : 0 });
            if (res.code === 200) {
              message.success(res.message);
            } else {
              actionRef.current?.reload();
            }
          }}
        />,
      ],
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      valueType: 'dateTime',
      sorter: true,
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '创建时间',
      key: 'created_at',
      dataIndex: 'created_at',
      valueType: 'dateTimeRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'created_at[start]': value[0],
            'created_at[end]': value[1],
          };
        },
      },
    },
    {
      title: '更新时间',
      key: 'updated_at',
      dataIndex: 'updated_at',
      valueType: 'dateTime',
      sorter: true,
      hideInSearch: true,
      width: 180,
      align: 'center',
    },
    {
      title: '更新时间',
      key: 'updated_at',
      dataIndex: 'updated_at',
      valueType: 'dateTimeRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'updated_at[start]': value[0],
            'updated_at[end]': value[1],
          };
        },
      },
    },
    {
      title: '操作',
      key: 'option',
      width: 260,
      valueType: 'option',
      align: 'center',
      fixed: 'right',
      render: (_, row) => [
        <FormIndex
          id={row.id}
          key={`FormIndex-${row.id}`}
          onConfirm={() => {
            return actionRef.current?.reload();
          }}
        />,
        <Button
          key={`sync-${row.id}`}
          type="primary"
          size="small"
          icon={<SyncOutlined />}
          loading={syncSingleLoading[row.id]}
          onClick={() => handleSyncSingleKline1d(row)}
        >
          同步K线
        </Button>,
        <CDel
          key={`CDel-${row.id}`}
          onCancel={async () => {
            const res = await destroy(row.id);
            if (res.code === 200) {
              message.success(res.message);
              actionRef.current?.reload();
            }
          }}
        />,
      ],
    },
  ];

  return (
    <ProTableWrapper
      loading={loading}
      actionRef={actionRef}
      rowKey="id"
      rowSelection={{
        fixed: true,
      }}
      columns={columns}
      request={async (params: any, sort) => {
        setLoading(true);
        if (params.concept_id) {
          params.concept_id = params.concept_id.slice(0, -1);
        }
        if (params.industry_id) {
          params.industry_id = params.industry_id.slice(0, -1);
        }
        const data = await getSort(params, sort);
        const res = await getList(data);
        setLoading(false);
        return await setLsetData(res);
      }}
      columnsState={{
        defaultValue: (() => {
          const stored = localStorage.getItem('quant_data_stock_table_columns');
          return stored ? JSON.parse(stored) : {};
        })(),
        onChange: (map: any) => {
          maps = map;
        },
        persistenceKey: 'quant_data_stock_table_columns',
        persistenceType: 'localStorage',
      }}
      tableAlertOptionRender={({ selectedRows, selectedRowKeys, onCleanSelected }) => {
        return (
          <Space size={16}>
            <CDelAll
              key={selectedRowKeys.length}
              count={selectedRowKeys.length}
              onCancel={async () => {
                const res = await destroyAll({ id_array: selectedRowKeys });
                if (res.code === 200) {
                  message.success(res.message);
                  actionRef.current?.reload();
                  onCleanSelected();
                }
              }}
            />
            <a
              onClick={() => {
                exportExcel({
                  breadcrumbData: initialState?.breadcrumbData || [],
                  columns,
                  columnsState: maps,
                  selectedRows,
                });
              }}
            >
              导出数据
            </a>
          </Space>
        );
      }}
      headerTitle={
        <Space>
          <FormIndex
            onConfirm={() => {
              return actionRef.current?.reload();
            }}
          />
          <SyncStockList
            onConfirm={() => {
              return actionRef.current?.reload();
            }}
          />
          <Button
            type="default"
            icon={<SyncOutlined />}
            loading={syncKline1dLoading}
            onClick={handleSyncKline1d}
          >
            同步日K线
          </Button>
        </Space>
      }
    />
  );
};

export default Index;
