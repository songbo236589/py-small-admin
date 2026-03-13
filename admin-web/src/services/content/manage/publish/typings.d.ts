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

  // 发布文章请求（article_id 从 URL 路径获取，不在 body 中）
  type PublishArticleRequest = {
    platform: string;
    platform_account_id: number;
  };

  // 批量发布请求（article_ids 是逗号分隔的字符串，由 Form 数据传递）
  type PublishBatchRequest = {
    article_ids: string; // 逗号分隔的文章ID字符串，如 "1,2,3"
    platform: string;
    platform_account_id: number;
  };
}
