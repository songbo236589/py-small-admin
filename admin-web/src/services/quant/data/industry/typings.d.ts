declare namespace API {
  // 列表参数
  type QuantIndustryList = {
    id: number;
    name: string;
    code: string;
    sort: number;
    latest_price: number;
    change_amount: number;
    change_percent: number;
    total_market_cap: number;
    turnover_rate: number;
    up_count: number;
    down_count: number;
    leading_stock: string;
    leading_stock_change: number;
    description: string | null;
    status: 0 | 1;
    created_at: string; // datetime
    updated_at: string | null; // datetime
  };

  type QuantIndustryForm = {
    id: number | null;
    name: string;
    code: string;
    sort: number;
    latest_price: number;
    change_amount: number;
    change_percent: number;
    total_market_cap: number;
    turnover_rate: number;
    up_count: number;
    down_count: number;
    leading_stock: string;
    leading_stock_change: number;
    description: string;
    status: 0 | 1;
  };
}
