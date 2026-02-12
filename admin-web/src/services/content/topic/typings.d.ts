declare namespace API {
  type TopicStatus = 0 | 1 | 2; // 0=未使用, 1=已使用, 2=已收藏

  // 话题列表项
  type ContentTopic = {
    id: number;
    platform: string;
    platform_question_id: string;
    title: string;
    description?: string;
    url?: string;
    view_count: number;
    answer_count: number;
    follower_count: number;
    category?: string;
    hot_score?: number;
    author_name?: string;
    author_url?: string;
    status: TopicStatus;
    fetched_at: string;
    created_at: string;
  };

  // 话题列表请求参数
  type TopicRequest = {
    page?: number;
    limit?: number;
    current?: number;
    pageSize?: number;
    platform?: string;
    status?: TopicStatus;
    category?: string;
    sort?: string;
  };

  // 话题使用请求
  type TopicUseRequest = {
    topic_id: number;
    article_id?: number;
  };
}
