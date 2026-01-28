import { TOKEN_KEYS } from '@/config/config';
import { request } from '@/utils/request';
import storage from '@/utils/storage';

// 登录接口
export async function login(body: API.AdminLoginParams) {
  return request<API.AdminLoginResult>({
    method: 'POST',
    url: '/admin/common/login',
    data: body,
    config: {
      skipAuth: true, // 登录时不需要token
    },
  });
}

// 生成验证码
export async function generateCaptcha() {
  return await request<API.AdminCaptchaResult>({
    method: 'POST',
    url: '/admin/common/generate_captcha',
    data: {},
    config: {
      skipAuth: true, // 验证码不需要token
    },
  });
}

// 保存token信息到localStorage
export const saveTokens = (loginResult: API.AdminLoginResult) => {
  try {
    // 保存所有token相关信息
    if (loginResult.access_token) {
      storage.set(TOKEN_KEYS.ACCESS_TOKEN, loginResult.access_token);
    }
    if (loginResult.refresh_token) {
      storage.set(TOKEN_KEYS.REFRESH_TOKEN, loginResult.refresh_token);
    }
    if (loginResult.token_type) {
      storage.set(TOKEN_KEYS.TOKEN_TYPE, loginResult.token_type);
    }
    if (loginResult.expires_in) {
      storage.set(TOKEN_KEYS.EXPIRES_IN, loginResult.expires_in);
    }
    if (loginResult.refresh_expires_in) {
      storage.set(TOKEN_KEYS.REFRESH_EXPIRES_IN, loginResult.refresh_expires_in);
    }
    if (loginResult.access_expires_at) {
      storage.set(TOKEN_KEYS.ACCESS_EXPIRES_AT, loginResult.access_expires_at);
    }
    if (loginResult.refresh_expires_at) {
      storage.set(TOKEN_KEYS.REFRESH_EXPIRES_AT, loginResult.refresh_expires_at);
    }
  } catch (error) {
    console.error('Failed to save tokens:', error);
  }
};

// 清除tokens和用户信息
export const clearTokens = () => {
  try {
    storage.remove(TOKEN_KEYS.ACCESS_TOKEN);
    storage.remove(TOKEN_KEYS.REFRESH_TOKEN);
    storage.remove(TOKEN_KEYS.TOKEN_TYPE);
    storage.remove(TOKEN_KEYS.EXPIRES_IN);
    storage.remove(TOKEN_KEYS.REFRESH_EXPIRES_IN);
    storage.remove(TOKEN_KEYS.ACCESS_EXPIRES_AT);
    storage.remove(TOKEN_KEYS.REFRESH_EXPIRES_AT);
    storage.remove(TOKEN_KEYS.CURRENT_USER);
    storage.clear();
  } catch (error) {
    console.error('Failed to clear tokens:', error);
  }
};

// 获取当前用户信息
export const getCurrentUser = (): API.AdminCurrentUser | null => {
  try {
    return storage.get(TOKEN_KEYS.CURRENT_USER);
  } catch (error) {
    console.error('Failed to get current user:', error);
    return null;
  }
};

// 保存用户信息
export const saveCurrentUser = (user: API.AdminCurrentUser) => {
  try {
    storage.set(TOKEN_KEYS.CURRENT_USER, user);
  } catch (error) {
    console.error('Failed to save current user:', error);
  }
};

// 获取token类型
export const getTokenType = () => {
  try {
    return storage.get(TOKEN_KEYS.TOKEN_TYPE, 'Bearer');
  } catch (error) {
    console.error('Failed to get token type:', error);
    return 'Bearer';
  }
};
// 获取当前的用户
export async function currentUser() {
  // 先检查本地存储中是否有用户信息
  const cachedUser = getCurrentUser();
  if (cachedUser) {
    return {
      data: cachedUser,
    };
  }
  const response = await request<API.AdminCurrentUser>({
    method: 'GET',
    url: '/admin/common/current',
  });

  // 请求成功后，保存用户信息到本地存储
  if (response.code === 200) {
    saveCurrentUser(response.data);
    return response;
  } else {
    return null;
  }
}

// 退出登录接口
export async function outLogin() {
  const refreshTokenValue = storage.get(TOKEN_KEYS.REFRESH_TOKEN) as string;
  return request<Record<string, any>>({
    method: 'POST',
    url: '/admin/common/logout',
    data: {
      refresh_token: refreshTokenValue,
    },
  });
}

// 修改密码接口
export async function changePassword(body: API.AdminChangePasswordParams) {
  return request<API.AdminChangePasswordResult>({
    method: 'POST',
    url: '/admin/common/change_password',
    data: body,
  });
}

// 刷新令牌接口
export async function refreshAccessToken(refreshTokenValue: string) {
  return request<API.AdminLoginResult>({
    method: 'POST',
    url: '/admin/common/refresh',
    data: { refresh_token: refreshTokenValue },
    config: {
      skipAuth: true, // 刷新token时不需要验证旧的access token
    },
  });
}

// 获取菜单树
export async function getMenuTree() {
  return request<API.AdminMenuItem[]>({
    method: 'GET',
    url: '/admin/common/get_menu_tree',
  });
}
// 获取项目配置信息
export async function getSystemConfig() {
  return request<API.AdminSystemConfig>({
    method: 'GET',
    url: '/admin/common/get_system_config',
    config: {
      skipAuth: true, // 刷新token时不需要验证旧的access token
    },
  });
}
