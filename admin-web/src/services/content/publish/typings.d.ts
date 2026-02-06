declare namespace API {
  // 发布记录列表
  type ContentPublishLogList = {
    id: number;
    article_id: number;
    article_title?: string;
    platform: string;
    platform_name: string;
    platform_article_id: string | null;
    platform_url: string | null;
    status: 0 | 1 | 2 | 3;
    error_message: string | null;
    retry_count: number;
    task_id: string | null;
    created_at: string;
  };

  // 发布状态
  type PublishStatus = 0 | 1 | 2 | 3; // 0=待发布, 1=发布中, 2=成功, 3=失败

  // 发布文章请求
  type PublishArticleRequest = {
    article_id: number;
    platform: string;
    platform_account_id: number;
  };

  // 批量发布请求
  type PublishBatchRequest = {
    article_ids: number[];
    platform: string;
    platform_account_id: number;
  };
}
