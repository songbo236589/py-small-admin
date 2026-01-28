// 登录相关类型定义

declare namespace API {
  type IdArrayQequest = {
    id_array: Key[];
  };
  type ResponseCommonList = {
    id: number;
    name: string;
  };
  type ResponseData = {
    code: number;
    message: string;
    data: T;
  };
  type ListQequest = {
    page?: number;
    limit?: number;
    current?: number;
    pageSize?: number;
    status?: number;
    created_at?: [];
    updated_at?: [];
    name?: string;
    title?: string;
    sort?: string;
  };
  type StatusQequest = {
    status: 0 | 1;
  };
  type SortQequest = {
    sort: number;
  };

  // 登录参数
  type AdminLoginParams = {
    username: string;
    password: string;
    captcha?: string;
    captcha_id?: string;
  };

  // 登录结果
  type AdminLoginResult = {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
    refresh_expires_in: number;
    access_expires_at: string;
    refresh_expires_at: string;
  };

  // 验证码结果
  type AdminCaptchaResult = {
    captcha_id: string;
    image_data: string; // 后端返回的是 image 字段，已经是完整的 data URL
    expire_seconds?: number; // 后端返回的是 expire_seconds
  };

  // 角色类型
  export type AdminCurrentUserRole = {
    id: number;
    name: string;
    code: string;
  };

  // 部门类型
  export type AdminCurrentUserDepartment = {
    id: number;
    name: string;
    code: string;
    is_main?: number;
  };

  // 当前用户信息
  export type AdminCurrentUser = {
    id?: number;
    username?: string;
    email?: string;
    real_name?: string;
    avatar?: string;
    phone?: string;
    gender?: number;
    birthday?: string | null;
    signature?: string;
    title?: string;
    status?: number;
    is_superuser?: number;
    last_login_at?: string;
    last_login_ip?: string;
    login_count?: number;
    password_updated_at?: string;
    two_factor_enabled?: number;
    roles?: AdminCurrentUserRole[];
    permissions?: string[];
    departments?: AdminCurrentUserDepartment[];
  };

  // 修改密码参数
  type AdminChangePasswordParams = {
    old_password: string;
    new_password: string;
    confirm_password: string;
  };

  // 修改密码结果
  type AdminChangePasswordResult = {
    success: boolean;
    message: string;
  };

  // 菜单项类型
  type AdminMenuItem = {
    id: number;
    name: string;
    path: string;
    icon?: string;
    type: number;
    target?: string;
    sort: number;
    component?: string;
    redirect?: string;
    children?: AdminMenuItem[];
  };

  // 菜单树响应类型
  type AdminMenuTreeResult = {
    code: number;
    message: string;
    data: AdminMenuItem[];
  };

  // 项目配置信息响应类型
  type AdminSystemConfig = {
    // 网站名称
    site_name: string;
    // 网站描述
    site_description: string;
    // 网站关键词
    site_keywords: string;
    // 版权信息
    copyright: string;

    site_logo?: number;
    site_logo_data?: API.AdminUploadList[];
    site_favicon?: number;
    site_favicon_data?: API.AdminUploadList[];

    // 上传文件配置信息
    upload: API.AdminUploadConfigForm;
  };
}
