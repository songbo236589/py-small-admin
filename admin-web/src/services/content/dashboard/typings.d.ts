declare namespace API {
  /** Content Dashboard 统计数据 */
  interface ContentDashboardStatistics {
    article_count: number;
    category_count: number;
    tag_count: number;
    topic_count: number;
    platform_account_count: number;
    publish: {
      today: number;
      pending: number;
      total: number;
    };
  }
}
