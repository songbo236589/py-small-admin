declare namespace API {
  // 概念日志列表数据
  type QuantConceptLogList = {
    id: number;
    concept_id: number; // 关联的概念ID
    name: string;
    record_date: string; // 记录日期（年月日）
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
}
