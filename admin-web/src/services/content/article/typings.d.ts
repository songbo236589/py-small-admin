declare namespace API {
  // 文章列表
  type ContentArticleList = {
    id: number;
    title: string;
    summary: string | null;
    cover_image_id: number | null;
    status: 0 | 1 | 2 | 3;
    author_id: number;
    category_id: number | null;
    category_name?: string;
    tags?: ContentTagList[];
    view_count: number;
    published_at: string | null;
    created_at: string;
    updated_at: string;
  };

  // 文章表单
  type ContentArticleForm = {
    id: number | null;
    title: string;
    content: string;
    summary: string | null;
    cover_image_id: number | null;
    category_id: number | null;
    tag_ids: number[];
    status: 0 | 1 | 2 | 3;
  };

  // 文章状态
  type ArticleStatus = 0 | 1 | 2 | 3; // 0=草稿, 1=已发布, 2=审核中, 3=发布失败
}
