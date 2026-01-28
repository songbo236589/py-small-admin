// API配置
export const API_CONFIG = {
  // API Key - 从环境变量获取
  API_KEY: process.env.UMI_APP_API_KEY || 'UMI_APP_API_KEY',
  // API 前缀
  BASE_URL: '/api'
};

// Token存储键名
export const TOKEN_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  TOKEN_TYPE: 'tokenType',
  EXPIRES_IN: 'expires_in',
  REFRESH_EXPIRES_IN: 'refresh_expires_in',
  ACCESS_EXPIRES_AT: 'access_expires_at',
  REFRESH_EXPIRES_AT: 'refresh_expires_at',
  CURRENT_USER: 'currentUser',
};