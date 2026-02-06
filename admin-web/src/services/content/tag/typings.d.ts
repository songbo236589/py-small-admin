declare namespace API {
  // 标签列表
  type ContentTagList = {
    id: number;
    name: string;
    slug: string;
    color: string | null;
    sort: number;
    status: 0 | 1;
    created_at: string;
    updated_at: string;
  };

  // 标签表单
  type ContentTagForm = {
    id: number | null;
    name: string;
    slug: string;
    color: string | null;
    sort: number;
    status: 0 | 1;
  };
}
