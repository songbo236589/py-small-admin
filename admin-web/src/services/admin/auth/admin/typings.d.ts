declare namespace API {
  // 列表参数
  type AdminAdminList = {
    id: number;
    username: string;
    name: string;
    phone: string;
    group_name: string;
    status: number; // 0-禁用，1-启用
    created_at: string; // datetime
    updated_at: string; // datetime
  };

  type AdminAdminForm = {
    id: number | null;
    username: string;
    name: string;
    phone: string;
    password: string;
    status: 0 | 1;
    group_id: number | null;
  };
}
