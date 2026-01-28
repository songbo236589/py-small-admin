import { request } from '@/utils/request';

// 获取股票列表
export async function getList(data: API.ListQequest) {
  return request({
    url: '/quant/stock/index',
    params: data,
  });
}

// 股票添加
export async function add(data: API.StockForm) {
  return request({
    method: 'POST',
    url: '/quant/stock/add',
    data: data,
  });
}

// 股票编辑页面数据
export async function edit(id: number) {
  return request<API.StockForm>({
    url: '/quant/stock/edit/' + id,
  });
}

// 股票编辑
export async function update(id: number, data: API.StockForm) {
  return request({
    method: 'PUT',
    url: '/quant/stock/update/' + id,
    data: data,
  });
}

// 股票状态
export async function setStatus(id: number, data: API.StatusQequest) {
  return request({
    method: 'PUT',
    url: '/quant/stock/set_status/' + id,
    data: data,
  });
}

// 股票删除
export async function destroy(id: number) {
  return request({
    method: 'DELETE',
    url: '/quant/stock/destroy/' + id,
  });
}

// 股票批量删除
export async function destroyAll(data: API.IdArrayQequest) {
  return request({
    method: 'DELETE',
    url: '/quant/stock/destroy_all',
    data: data,
    config: {
      customHeaders: { 'Content-Type': 'application/json' },
    },
  });
}

// 同步股票列表
export async function syncStockList(market: number = 1) {
  return request({
    method: 'POST',
    url: '/quant/stock/sync_stock_list',
    data: { market: market },
  });
}
