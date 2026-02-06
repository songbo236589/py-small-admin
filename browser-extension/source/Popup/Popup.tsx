import React, { useCallback, useState, useEffect } from 'react';
import { Button, Card, Input, Space, Typography, message } from 'antd';
import { SettingOutlined, CheckCircleOutlined, LoadingOutlined, CopyOutlined } from '@ant-design/icons';
import axios from 'axios';
import './styles.less';

const { Text, Paragraph } = Typography;

interface Platform {
  id: string;
  name: string;
  domains: string[];
  icon?: string;
}

interface FetchedPlatform {
  platform: Platform;
  cookies: chrome.cookies.Cookie[];
  domains: Set<string>;
  sent: boolean;
  sending: boolean;
}

interface PopupState {
  allowedDomains: string[];
  configVisible: boolean;
  apiBaseUrl: string;
  fetched: boolean;
  loading: boolean;
  platforms: Platform[];
  selectedPlatforms: string[];
  fetchedPlatforms: FetchedPlatform[];
}

const Popup: React.FC = () => {
  const [state, setState] = useState<PopupState>({
    allowedDomains: [],
    configVisible: false,
    apiBaseUrl: localStorage.getItem('apiBaseUrl') || 'http://localhost:8000',
    fetched: false,
    loading: false,
    platforms: [],
    selectedPlatforms: [],
    fetchedPlatforms: [],
  });

  // 获取平台列表
  const fetchPlatforms = useCallback(async () => {
    try {
      const response = await axios.get(`${state.apiBaseUrl}/api/content/extension/platform/index`);

      if (response.data.code === 200 && response.data.data) {
        const platforms: Platform[] = response.data.data.items || response.data.data;
        setState((prev) => ({
          ...prev,
          platforms,
          allowedDomains: platforms.flatMap((p: Platform) => p.domains || []),
        }));
        return platforms;
      }
      return [];
    } catch (error) {
      console.error('获取平台列表失败:', error);
      message.error('获取平台列表失败，请检查后端地址配置');
      return [];
    }
  }, [state.apiBaseUrl]);

  // 从 Chrome Storage 读取配置
  useEffect(() => {
    chrome.storage.local.get(['apiBaseUrl', 'selectedPlatforms'], (result: { [key: string]: string | string[] }) => {
      if (result.apiBaseUrl) {
        setState((prev) => ({ ...prev, apiBaseUrl: result.apiBaseUrl as string }));
      }
      if (result.selectedPlatforms) {
        setState((prev) => ({ ...prev, selectedPlatforms: result.selectedPlatforms as string[] }));
      }
    });

    // 初始化时自动获取平台列表
    fetchPlatforms();
  }, [fetchPlatforms]);

  // 复制 Cookies 为 JSON 格式
  const copyCookiesAsJson = async (cookies: chrome.cookies.Cookie[], platformName: string) => {
    try {
      // 将 Cookies 转换为 JSON 格式
      const cookiesJson = JSON.stringify(
        cookies.map((cookie) => ({
          name: cookie.name,
          value: cookie.value,
          domain: cookie.domain,
          path: cookie.path,
          secure: cookie.secure,
          httpOnly: cookie.httpOnly,
          expirationDate: cookie.expirationDate,
        })),
        null,
        2
      );

      // 复制到剪贴板
      await navigator.clipboard.writeText(cookiesJson);
      message.success(`${platformName} 的 Cookies 已复制`);
    } catch (error) {
      console.error('复制失败:', error);
      message.error('复制失败，请重试');
    }
  };

  // 发送单个平台的 Cookies 到后端
  const sendPlatformCookies = async (platformId: string, cookies: chrome.cookies.Cookie[]) => {
    try {
      // 更新状态为发送中
      setState((prev) => ({
        ...prev,
        fetchedPlatforms: prev.fetchedPlatforms.map((fp) =>
          fp.platform.id === platformId ? { ...fp, sending: true } : fp
        ),
      }));

      const cookieData = cookies.map((cookie) => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        secure: cookie.secure,
        httpOnly: cookie.httpOnly,
        expirationDate: cookie.expirationDate,
        storeId: cookie.storeId,
      }));

      await axios.post(`${state.apiBaseUrl}/api/content/extension/platform_account/import_cookies`, cookieData);

      // 更新状态为已发送
      setState((prev) => ({
        ...prev,
        fetchedPlatforms: prev.fetchedPlatforms.map((fp) =>
          fp.platform.id === platformId ? { ...fp, sending: false, sent: true } : fp
        ),
      }));

      message.success('发送成功');
      return true;
    } catch (error) {
      // 更新状态为发送失败
      setState((prev) => ({
        ...prev,
        fetchedPlatforms: prev.fetchedPlatforms.map((fp) =>
          fp.platform.id === platformId ? { ...fp, sending: false } : fp
        ),
      }));

      console.error('提交 Cookies 失败:', error);
      let errorMsg = '发送失败';
      if (error && typeof error === 'object') {
        if ('response' in error && error.response && typeof error.response === 'object') {
          if ('data' in error.response && error.response.data && typeof error.response.data === 'object') {
            if ('message' in error.response.data && typeof error.response.data.message === 'string') {
              errorMsg = error.response.data.message;
            }
          }
        } else if ('message' in error && typeof error.message === 'string') {
          errorMsg = error.message;
        }
      }
      message.error(errorMsg);
      throw error;
    }
  };

  // 一键获取登录信息（仅本地获取，不发送到后端）
  const onGetLoginInfo = async () => {
    setState((prev) => ({ ...prev, loading: true, fetched: false }));
    try {
      // 检查平台配置
      if (!state.platforms || state.platforms.length === 0) {
        message.warning('暂无可用的平台配置');
        setState((prev) => ({ ...prev, loading: false }));
        return;
      }

      // 1. 获取所有 Cookie Stores（处理多容器场景）
      const cookieStores = await new Promise<chrome.cookies.CookieStore[]>((resolve) => {
        chrome.cookies.getAllCookieStores((stores) => resolve(stores));
      });

      // 按平台分组 Cookies
      const platformCookiesMap = new Map<string, chrome.cookies.Cookie[]>();

      // 2. 遍历所有 Cookie Store
      for (const store of cookieStores) {
        // 3. 获取当前 Store 的所有 Cookies
        const storeCookies = await new Promise<chrome.cookies.Cookie[]>((resolve) => {
          chrome.cookies.getAll({ storeId: store.id }, (cookies) => resolve(cookies || []));
        });

        // 4. 根据平台域名过滤并分组 Cookies
        for (const cookie of storeCookies) {
          // 标准化 cookie domain（移除前导点）
          const cookieDomain = cookie.domain.replace(/^\./, '');

          // 检查是否匹配任何平台
          for (const platform of state.platforms) {
            for (const domain of platform.domains) {
              if (cookieDomain.includes(domain) || domain.includes(cookieDomain)) {
                // 找到匹配的平台，将 cookie 添加到对应平台
                if (!platformCookiesMap.has(platform.id)) {
                  platformCookiesMap.set(platform.id, []);
                }
                platformCookiesMap.get(platform.id)!.push(cookie);
                break;
              }
            }
          }
        }
      }

      // 5. 构建 fetchedPlatforms 数组
      const fetchedPlatforms: FetchedPlatform[] = state.platforms.map((platform) => ({
        platform,
        cookies: platformCookiesMap.get(platform.id) || [],
        domains: new Set(
          (platformCookiesMap.get(platform.id) || []).map((c) => c.domain)
        ),
        sent: false,
        sending: false,
      }));

      const platformsWithCookies = fetchedPlatforms.filter((fp) => fp.cookies.length > 0);

      if (platformsWithCookies.length === 0) {
        message.warning('未找到相关平台的登录信息，请先在对应网站登录');
        setState((prev) => ({ ...prev, loading: false }));
        return;
      }

      message.success(`成功获取 ${platformsWithCookies.length} 个平台的登录信息`);
      setState((prev) => ({ ...prev, loading: false, fetched: true, fetchedPlatforms }));
    } catch (error: unknown) {
      let errorMsg = '获取登录信息失败';
      if (error && typeof error === 'object') {
        if ('response' in error && error.response && typeof error.response === 'object') {
          if ('data' in error.response && error.response.data && typeof error.response.data === 'object') {
            if ('message' in error.response.data && typeof error.response.data.message === 'string') {
              errorMsg = error.response.data.message;
            }
          }
        } else if ('message' in error && typeof error.message === 'string') {
          errorMsg = error.message;
        }
      }
      message.error(errorMsg);
      setState((prev) => ({ ...prev, loading: false }));
    }
  };

  // 切换配置面板
  const onToggleConfig = () => {
    setState((prev) => ({ ...prev, configVisible: !prev.configVisible }));
  };

  // 更新后端地址
  const onApiBaseUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    localStorage.setItem('apiBaseUrl', newUrl);
    chrome.storage.local.set({ apiBaseUrl: newUrl });
    setState((prev) => ({ ...prev, apiBaseUrl: newUrl }));
  };

  // 渲染按钮状态
  const renderButton = () => {
    if (state.loading) {
      return (
        <Button type="primary" block icon={<LoadingOutlined />} disabled>
          正在获取...
        </Button>
      );
    }

    return (
      <Button type="primary" block onClick={onGetLoginInfo}>
        {state.fetched ? '重新获取' : '一键获取登录信息'}
      </Button>
    );
  };

  // 渲染获取到的平台列表
  const renderFetchedPlatforms = () => {
    if (!state.fetched || state.fetchedPlatforms.length === 0) {
      return null;
    }

    return (
      <div className="fetched-platforms-list">
        <Text type="secondary" style={{ fontSize: '12px', marginBottom: '8px', display: 'block' }}>
          获取到的平台：
        </Text>
        {state.fetchedPlatforms.map((fp) => {
          const hasCookies = fp.cookies.length > 0;
          return (
            <div key={fp.platform.id} className="fetched-platform-item">
              <div className="platform-info">
                <span className="platform-name">{fp.platform.name}</span>
                {hasCookies ? (
                  <span
                    className="platform-status success clickable"
                    onClick={() => copyCookiesAsJson(fp.cookies, fp.platform.name)}
                  >
                    已获取 {fp.cookies.length} 个 Cookie <CopyOutlined />
                  </span>
                ) : (
                  <span className="platform-status empty">未登录</span>
                )}
              </div>
              {hasCookies && fp.platform.id === 'zhihu' && !fp.sent && (
                <Button
                  type="primary"
                  size="small"
                  onClick={() => sendPlatformCookies(fp.platform.id, fp.cookies)}
                  loading={fp.sending}
                  disabled={fp.sending}
                >
                  {fp.sending ? '发送中...' : '发送到后端'}
                </Button>
              )}
              {fp.sent && (
                <span className="sent-badge">
                  <CheckCircleOutlined style={{ color: '#52c41a' }} /> 已发送
                </span>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="popup-container">
      <Card className="popup-card">
        <div className="popup-header">
          <Space>
            <img src="/assets/icons/icon-32.png" alt="Logo" className="logo" />
            <Text strong>Py Small Admin</Text>
          </Space>
          <Button
            type="text"
            icon={<SettingOutlined />}
            onClick={onToggleConfig}
            className="config-btn"
          />
        </div>

        <Paragraph className="description">
          一键获取各技术平台的登录信息
        </Paragraph>

        {state.configVisible && (
          <div className="config-panel">
            <Text type="secondary" style={{ fontSize: '12px' }}>
              后端地址
            </Text>
            <Input
              value={state.apiBaseUrl}
              placeholder="http://localhost:8000"
              onChange={onApiBaseUrlChange}
              style={{ marginTop: '8px' }}
            />
          </div>
        )}

        <div className="action-panel">{renderButton()}</div>

        {renderFetchedPlatforms()}

        {!state.fetched && state.platforms.length > 0 && (
          <div className="platform-list">
            <Text type="secondary" style={{ fontSize: '12px' }}>
              支持的平台：
            </Text>
            <div className="platform-tags">
              {state.platforms.map((platform) => (
                <span key={platform.id} className="platform-tag">
                  {platform.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Popup;
