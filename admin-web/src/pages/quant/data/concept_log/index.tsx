import { CDelAll, ProTableWrapper } from '@/components';

import { simpleList } from '@/services/quant/data/concept/api';
import { destroyAll, getList } from '@/services/quant/data/concept_log/api';
import { exportExcel } from '@/utils/exportExcel';
import { getSort, setLsetData } from '@/utils/utils';
import type { Chart } from '@ant-design/charts';
import { Line } from '@ant-design/charts';

import { DownloadOutlined, FullscreenExitOutlined, FullscreenOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Button, Card, message, Space, Tooltip } from 'antd';
import React, { useEffect, useRef, useState } from 'react';

const Index: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [loading, setLoading] = useState(true);
  const [conceptList, setConceptList] = useState<any>([]);
  const [chartData, setChartData] = useState<API.QuantConceptLogList[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { initialState } = useModel('@@initialState');
  const chartRef = useRef<any>(null);
  let maps = {};

  // 从 URL 中获取 concept_id 参数
  const urlParams = new URLSearchParams(window.location.search);
  const conceptIdFromUrl = urlParams.get('concept_id');

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
      if (Object.keys(conceptListData).length) await setConceptList({ ...conceptListData });
    }
  };

  // 页面加载时获取概念数据
  useEffect(() => {
    fetchConceptList();
  }, []);

  const columns: ProColumns<API.QuantConceptLogList>[] = [
    {
      title: '排名',
      dataIndex: 'sort',
      hideInSearch: true,
      width: 80,
      align: 'center',
      sorter: true,
    },
    {
      title: '概念名称',
      dataIndex: 'name',
      align: 'center',
      width: 120,
      ellipsis: true,
      copyable: true,
      hideInSearch: true,
    },
    {
      title: '概念名称',
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
      title: '记录日期',
      dataIndex: 'record_date',
      valueType: 'date',
      align: 'center',
      width: 120,
      sorter: true,
      hideInSearch: true,
    },
    {
      title: '记录日期',
      dataIndex: 'record_date',
      valueType: 'dateRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'record_date[start]': value[0],
            'record_date[end]': value[1],
          };
        },
      },
    },
    {
      title: '最新价',
      dataIndex: 'latest_price',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
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
      title: '涨跌额',
      dataIndex: 'change_amount',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
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
      title: '涨跌幅(%)',
      dataIndex: 'change_percent',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
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
      title: '总市值(亿)',
      dataIndex: 'total_market_cap',
      align: 'center',
      width: 120,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
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
      title: '换手率(%)',
      dataIndex: 'turnover_rate',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
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
      title: '上涨家数',
      dataIndex: 'up_count',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '上涨家数',
      dataIndex: 'up_count',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'up_count[start]': value[0],
            'up_count[end]': value[1],
          };
        },
      },
    },
    {
      title: '下跌家数',
      dataIndex: 'down_count',
      align: 'center',
      width: 100,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [<span key={record.id}>{text}</span>],
    },
    {
      title: '下跌家数',
      dataIndex: 'down_count',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'down_count[start]': value[0],
            'down_count[end]': value[1],
          };
        },
      },
    },
    {
      title: '领涨股票',
      dataIndex: 'leading_stock',
      align: 'center',
      width: 120,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '领涨涨跌幅(%)',
      dataIndex: 'leading_stock_change',
      align: 'center',
      width: 140,
      sorter: true,
      hideInSearch: true,
      render: (text: any, record) => [
        <span style={{ color: text > 0 ? '#ff4d4f' : '#000000' }} key={record.id}>
          {text}
        </span>,
      ],
    },
    {
      title: '领涨涨跌幅(%)',
      dataIndex: 'leading_stock_change',
      valueType: 'digitRange',
      hideInTable: true,
      search: {
        transform: (value) => {
          return {
            'leading_stock_change[start]': value[0],
            'leading_stock_change[end]': value[1],
          };
        },
      },
    },
    {
      title: '概念描述',
      dataIndex: 'description',
      align: 'center',
      width: 200,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      width: 100,
      align: 'center',
      valueEnum: {
        0: {
          text: '禁用',
          status: '0',
        },
        1: {
          text: '启用',
          status: '1',
        },
      },
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
  ];

  // 进入全屏
  const handleFullscreen = () => {
    const element = document.getElementById('chart-card') as any;
    if (element) {
      if (element.requestFullscreen) {
        element.requestFullscreen();
      } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
      } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
      }
    }
  };

  // 退出全屏
  const handleExitFullscreen = () => {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if ((document as any).webkitExitFullscreen) {
      (document as any).webkitExitFullscreen();
    } else if ((document as any).msExitFullscreen) {
      (document as any).msExitFullscreen();
    }
  };

  // 监听全屏状态变化
  useEffect(() => {
    const handleFullscreenChange = () => {
      const fullscreenActive = !!(
        document.fullscreenElement ||
        (document as any).webkitFullscreenElement ||
        (document as any).msFullscreenElement
      );
      setIsFullscreen(fullscreenActive);
      // 全屏状态变化时，触发图表重新计算尺寸
      if (chartRef.current && chartRef.current.forceFit) {
        setTimeout(() => {
          chartRef.current.forceFit();
        }, 100);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('msfullscreenchange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('msfullscreenchange', handleFullscreenChange);
    };
  }, []);

  // 转换数据为图表格式（长格式，支持多系列）
  const transformChartData = (data: API.QuantConceptLogList[]) => {
    if (!data || data.length === 0) return [];

    // 按日期升序排序
    const sortedData = [...data].sort((a, b) => {
      return new Date(a.record_date).getTime() - new Date(b.record_date).getTime();
    });

    // 定义指标映射
    const metrics = [
      { key: 'latest_price', name: '最新价格' },
      { key: 'change_percent', name: '涨跌幅' },
      { key: 'total_market_cap', name: '总市值' },
      { key: 'turnover_rate', name: '换手率' },
      { key: 'up_count', name: '上涨家数' },
      { key: 'down_count', name: '下跌家数' },
    ];

    // 转换为长格式数据
    const result: any[] = [];
    sortedData.forEach((item) => {
      metrics.forEach((metric) => {
        result.push({
          date: item.record_date,
          value: Number((item as any)[metric.key]),
          name: metric.name,
        });
      });
    });
    return result;
  };

  // 多系列折线图配置
  const multiLineChartConfig = {
    title: {
      align: 'center', // 图表标题的对齐方式
      size: 28, // 图表标题的高度，默认为 36
      // 标题
      title: '概念指标趋势图', // 图表标题的文本
      titleFontSize: 28, // 图表主标题的字体大小
      titleFontFamily: 'sans-serif', // 图表主标题的字体
      titleFontWeight: 600, // 图表主标题的字体粗细
    },
    // 设置数据
    data: transformChartData(chartData),
    height: isFullscreen ? 800 : 400,
    // 设置x轴字段
    xField: 'date',
    // 设置y轴字段
    yField: 'value',
    // 多折线图区分字段
    seriesField: 'name',
    colorField: 'name',
    tooltip: (
      d: any, // 每一个数据项
    ) => {
      let unit = '';
      if (d.name === '涨跌幅') unit = '%';
      if (d.name === '换手率') unit = '%';
      if (d.name === '总市值') unit = ' 亿';
      if (d.name === '最新价格') unit = '元';
      return {
        name: d.name,
        value: `${d.value}${unit}`,
      };
    },
  };

  return (
    <div>
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
          const data = await getSort(params, sort);
          const res = await getList(data);
          setLoading(false);

          // 当搜索了概念名称时，保存数据用于图表展示
          if (params.concept_id && res.code === 200 && res.data.items) {
            setChartData(res.data.items);
          } else {
            setChartData([]);
          }

          return await setLsetData(res);
        }}
        columnsState={{
          defaultValue: (() => {
            const stored = localStorage.getItem('quant_data_concept_log_table_columns');
            return stored ? JSON.parse(stored) : {};
          })(),
          onChange: (map: any) => {
            maps = map;
          },
          persistenceKey: 'quant_data_concept_log_table_columns',
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
      />
      {chartData.length > 0 && (
        <Card id="chart-card" style={{ marginBottom: 16, padding: '24px', position: 'relative' }}>
          <Tooltip title={isFullscreen ? '退出全屏' : '全屏'} placement="bottom">
            <Button
              icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
              onClick={isFullscreen ? handleExitFullscreen : handleFullscreen}
              type="text"
              style={{ position: 'absolute', right: '64px', top: '24px', zIndex: 1 }}
            />
          </Tooltip>
          <Tooltip title="下载图表" placement="bottom">
            <Button
              icon={<DownloadOutlined />}
              onClick={() => {
                chartRef.current.downloadImage('概念指标趋势图', 'image/png', 1);
              }}
              type="text"
              style={{ position: 'absolute', right: '24px', top: '24px', zIndex: 1 }}
            />
          </Tooltip>
          <Line
            {...multiLineChartConfig}
            onReady={(chart: Chart) => {
              chartRef.current = chart;
            }}
          />
        </Card>
      )}
    </div>
  );
};

export default Index;
