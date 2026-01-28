// 市场类型枚举
export const marketOptions = {
  1: { text: '上海(SH)', status: 'Default' },
  2: { text: '深圳(SZ)', status: 'Default' },
  3: { text: '北京(BJ)', status: 'Default' },
  4: { text: '港股(HK)', status: 'Default' },
  5: { text: '美股(US)', status: 'Default' },
};

// 市场类型下拉选项
export const marketSelectOptions = [
  { label: '上海(SH)', value: 1 },
  { label: '深圳(SZ)', value: 2 },
  { label: '北京(BJ)', value: 3 },
  { label: '港股(HK)', value: 4 },
  { label: '美股(US)', value: 5 },
];

// 市场类型下拉选项（拉取数据选项）
export const marketSelectSyncStockListOptions = [
  { label: '上海(SH)、深圳(SZ)、北京(BJ)', value: 1 },
  { label: '港股(HK)', value: 4 },
  { label: '美股(US)', value: 5 },
];

// 交易所枚举
export const exchangeOptions = {
  1: { text: '上海证券交易所(SSE)', status: 'Default' },
  2: { text: '深圳证券交易所(SZSE)', status: 'Default' },
  3: { text: '北京证券交易所(BSE)', status: 'Default' },
  4: { text: '香港交易所(HKEX)', status: 'Default' },
  5: { text: '纳斯达克(NASDAQ)', status: 'Default' },
  6: { text: '纽约证券交易所(NYSE)', status: 'Default' },
  7: { text: '美国证券交易所(AMEX)', status: 'Default' },
};

// 交易所下拉选项
export const exchangeSelectOptions = [
  { label: '上海证券交易所(SSE)', value: 1 },
  { label: '深圳证券交易所(SZSE)', value: 2 },
  { label: '北京证券交易所(BSE)', value: 3 },
  { label: '香港交易所(HKEX)', value: 4 },
  { label: '纳斯达克(NASDAQ)', value: 5 },
  { label: '纽约证券交易所(NYSE)', value: 6 },
  { label: '美国证券交易所(AMEX)', value: 7 },
];

// 上市状态枚举
export const listStatusOptions = {
  0: { text: '未上市', status: 'Default' },
  1: { text: '已上市', status: 'Success' },
  2: { text: '退市', status: 'Error' },
  3: { text: '暂停上市', status: 'Warning' },
};

// 上市状态下拉选项
export const listStatusSelectOptions = [
  { label: '未上市', value: 0 },
  { label: '已上市', value: 1 },
  { label: '退市', value: 2 },
  { label: '暂停上市', value: 3 },
];

// 交易状态枚举
export const tradeStatusOptions = {
  0: { text: '停牌', status: 'Error' },
  1: { text: '正常交易', status: 'Success' },
  2: { text: '特别处理', status: 'Warning' },
};

// 交易状态下拉选项
export const tradeStatusSelectOptions = [
  { label: '停牌', value: 0 },
  { label: '正常交易', value: 1 },
  { label: '特别处理', value: 2 },
];

// 股票类型枚举
export const stockTypeOptions = {
  1: { text: '主板', status: 'Default' },
  2: { text: '创业板', status: 'Default' },
  3: { text: '科创板', status: 'Default' },
  4: { text: '北交所', status: 'Default' },
};

// 股票类型下拉选项
export const stockTypeSelectOptions = [
  { label: '主板', value: 1 },
  { label: '创业板', value: 2 },
  { label: '科创板', value: 3 },
  { label: '北交所', value: 4 },
];
