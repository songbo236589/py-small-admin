import { request } from '@/utils/request';

// 同步日K线数据
export async function syncKline1d() {
  return request({
    method: 'POST',
    url: '/quant/kline/sync_kline_1d',
  });
}

// 同步单个股票日K线数据
export async function syncSingleKline1d(data: { id: number }) {
  return request({
    method: 'POST',
    url: '/quant/kline/sync_single_kline_1d',
    data: data,
  });
}
