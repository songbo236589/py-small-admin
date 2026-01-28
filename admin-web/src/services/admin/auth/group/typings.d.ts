declare namespace API {
  // 列表参数
  type AdminGroupList = {
    id: number;
    name: string;
    content: string;
    status: 0 | 1;
    created_at: string; // datetime
    updated_at: string; // datetime
  };

  type AdminGroupForm = {
    id: number | null;
    name: string;
    content: string;
    status: 0 | 1;
  };
  type AdminGroupAccess = {
    id: number | null;
    rules: number[];
  };
}
