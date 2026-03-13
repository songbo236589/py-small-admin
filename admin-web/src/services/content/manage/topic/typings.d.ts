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
    category_id?: number;
    category?: {
      id: number;
      name: string;
      slug: string;
    };
    category_name?: string;
    category_slug?: string;
    hot_score?: number;
    author_name?: string;
    author_url?: string;
    status: TopicStatus;
    fetched_at: string;
    article_count: number;
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
    category_id?: number | string;
    category?: string;
    has_description?: 'all' | 'has' | 'none';
    sort?: string;
  };

  // 话题使用请求
  type TopicUseRequest = {
    topic_id: number;
    article_id?: number;
  };

  // 生成描述请求
  type GenerateDescriptionRequest = {
    model?: string;
  };

  // 更新描述请求
  type UpdateDescriptionRequest = {
    description: string;
  };

  // 批量更新分类请求
  type BatchUpdateCategoryRequest = {
    id_array: number[];
    category_id: number | null;
  };

  // 批量更新分类响应
  type BatchUpdateCategoryResponse = {
    updated_count: number;
    category_id: number | null;
    message: string;
  };

  // 生成描述响应
  type GenerateDescriptionResponse = {
    id: number;
    title: string;
    description: string;
    model?: string;
    message: string;
  };

  // 生成分类响应
  type GenerateCategoryResponse = {
    id: number;
    category_id: number;
    category_name: string;
    category_slug: string;
    parent_name?: string;   // 父分类名称
    is_new?: boolean;       // 是否是新创建的分类
    model?: string;
    message: string;
  };

  // 抓取知乎内容响应
  type FetchZhihuContentResponse = {
    id: number;
    title: string;
    description?: string;
    url?: string;
    answers: Array<{
      author: string;
      content: string;
    }>;
    answer_count: number;
    updated_at?: string;
    message: string;
  };

  // 知乎内容详情（用于 Modal 显示）
  type ZhihuContentDetail = {
    title: string;
    description?: string;
    url?: string;
    answers: Array<{
      author: string;
      content: string;
    }>;
    answer_count: number;
    updated_at?: string;
  };

  // 话题详情（包含知乎内容）
  type ContentTopicDetail = {
    id: number;
    platform: string;
    platform_question_id: string;
    title: string;
    description?: string;
    url?: string;
    view_count: number;
    answer_count: number;
    follower_count: number;
    category_id?: number;
    category?: {
      id: number;
      name: string;
      slug: string;
    };
    category_name?: string;
    category_slug?: string;
    hot_score?: number;
    author_name?: string;
    author_url?: string;
    status: TopicStatus;
    fetched_at: string;
    zhihu_content?: string;              // 知乎内容 JSON 字符串
    zhihu_content_updated_at?: string;  // 知乎内容更新时间
    created_at?: string;
  };
}
