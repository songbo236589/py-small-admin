declare namespace API {
  // 分类列表
  type ContentCategoryList = {
    id: number;
    name: string;
    slug: string;
    parent_id: number | null;
    sort: number;
    status: 0 | 1;
    description: string | null;
    created_at: string;
    updated_at: string;
    children?: ContentCategoryList[];
  };

  // 分类树形结构
  type ContentCategoryTree = {
    id: number;
    name: string;
    slug: string;
    parent_id: number | null;
    sort: number;
    status: 0 | 1;
    description: string | null;
    created_at: string;
    updated_at: string;
    value: number;
    key: number;
    title: string;
    children?: ContentCategoryTree[];
  }[];

  // 分类表单
  type ContentCategoryForm = {
    id: number | null;
    name: string;
    slug: string;
    parent_id: number | null;
    sort: number;
    status: 0 | 1;
    description: string | null;
  };
}
