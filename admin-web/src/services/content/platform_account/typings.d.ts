declare namespace API {
  // 平台账号列表
  type ContentPlatformAccountList = {
    id: number;
    platform: string;
    platform_name: string;
    account_name: string;
    user_agent: string | null;
    status: 0 | 1 | 2;
    last_verified: string | null;
    created_by: number;
    created_at: string;
    updated_at: string;
  };

  // 平台账号表单
  type ContentPlatformAccountForm = {
    id: number | null;
    platform: string;
    account_name: string;
    cookies: string;
    user_agent: string | null;
    status: 0 | 1 | 2;
  };

  // 平台选项
  type PlatformOption = {
    label: string;
    value: string;
  };
}
