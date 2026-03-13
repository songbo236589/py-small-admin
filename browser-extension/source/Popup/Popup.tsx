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

      const cookieData = {
        cookies: cookies.map((cookie) => ({
          name: cookie.name,
          value: cookie.value,
          domain: cookie.domain,
          path: cookie.path,
          secure: cookie.secure,
          httpOnly: cookie.httpOnly,
          expirationDate: cookie.expirationDate,
          storeId: cookie.storeId,
        })),
        userAgent: navigator.userAgent,
      };

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
      console.log('🔍 [Cookie 调试] Cookie Stores:', cookieStores);
      console.log('🔍 [Cookie 调试] 平台配置:', state.platforms);

      // 按平台分组 Cookies
      const platformCookiesMap = new Map<string, chrome.cookies.Cookie[]>();

      // 改进的域名匹配函数 - 确保捕获所有相关域名的 Cookie
      const matchesDomain = (cookieDomain: string, platformDomain: string): boolean => {
        // 标准化域名（移除前导点）
        const normalizedCookie = cookieDomain.replace(/^\./, '').toLowerCase();
        const normalizedPlatform = platformDomain.toLowerCase();

        // 1. 完全匹配
        if (normalizedCookie === normalizedPlatform) {
          return true;
        }

        // 2. Cookie 域是平台域的子域名 (e.g., edith.xiaohongshu.com matches xiaohongshu.com)
        if (normalizedCookie.endsWith('.' + normalizedPlatform)) {
          return true;
        }

        // 3. 平台域是 Cookie 域的子域名 (e.g., xiaohongshu.com matches .xiaohongshu.com)
        if (normalizedPlatform.endsWith('.' + normalizedCookie)) {
          return true;
        }

        // 4. Cookie 域包含平台域作为部分 (e.g., www.xiaohongshu.com matches xiaohongshu.com)
        if (normalizedCookie.includes(normalizedPlatform) && normalizedPlatform.length > 0) {
          // 确保是完整的域名部分匹配，不是部分字符串匹配
          const cookieParts = normalizedCookie.split('.');
          const platformParts = normalizedPlatform.split('.');
          // 如果平台域的所有部分都出现在 Cookie 域中（按顺序），则匹配
          let platformIndex = 0;
          for (const cookiePart of cookieParts) {
            if (cookiePart === platformParts[platformIndex]) {
              platformIndex++;
              if (platformIndex >= platformParts.length) {
                return true;
              }
            }
          }
        }

        // 5. 平台域包含 Cookie 域作为部分
        if (normalizedPlatform.includes(normalizedCookie) && normalizedCookie.length > 0) {
          const platformParts = normalizedPlatform.split('.');
          const cookieParts = normalizedCookie.split('.');
          let cookieIndex = 0;
          for (const platformPart of platformParts) {
            if (platformPart === cookieParts[cookieIndex]) {
              cookieIndex++;
              if (cookieIndex >= cookieParts.length) {
                return true;
              }
            }
          }
        }

        return false;
      };

      // 2. 遍历所有 Cookie Store
      for (const store of cookieStores) {
        // 3. 获取当前 Store 的所有 Cookies
        const storeCookies = await new Promise<chrome.cookies.Cookie[]>((resolve) => {
          chrome.cookies.getAll({ storeId: store.id }, (cookies) => resolve(cookies || []));
        });
        console.log(`🔍 [Cookie 调试] Store ${store.id}: 获取到 ${storeCookies.length} 个 Cookie`);

        // 打印所有 Cookie 名称和域名（用于调试）
        const cookieSummary = storeCookies.map(c => ({
          name: c.name,
          domain: c.domain,
          value: c.value.substring(0, 20) + '...'
        }));
        console.log(`🔍 [Cookie 调试] Store ${store.id} Cookie 列表:`, cookieSummary);

        // 4. 根据平台域名过滤并分组 Cookies
        for (const cookie of storeCookies) {
          // 标准化 cookie domain（移除前导点）
          const cookieDomain = cookie.domain.replace(/^\./, '');

          // 检查是否匹配任何平台
          for (const platform of state.platforms) {
            let matched = false;
            for (const domain of platform.domains) {
              const isMatch = matchesDomain(cookieDomain, domain);
              if (isMatch) {
                console.log(`✅ [域名匹配] Cookie "${cookie.name}" (${cookieDomain}) 匹配平台 "${platform.name}" (${domain})`);
                // 找到匹配的平台，将 cookie 添加到对应平台
                if (!platformCookiesMap.has(platform.id)) {
                  platformCookiesMap.set(platform.id, []);
                }
                platformCookiesMap.get(platform.id)!.push(cookie);
                matched = true;
                break;
              }
            }
            if (matched) break;
          }
        }
      }

      // 🔥 特殊处理：针对小红书平台，使用 chrome.cookies.get() 单独获取关键 Cookie
      // 因为 chrome.cookies.getAll() 可能无法获取到某些 Cookie（如 a1）
      const xiaohongshuPlatform = state.platforms.find(p => p.id === 'xiaohongshu');
      if (xiaohongshuPlatform) {
        console.log('🔍 [小红书特殊处理] 尝试单独获取关键 Cookie...');

        // 需要单独获取的关键 Cookie 名称
        const criticalCookieNames = ['a1', 'webId', 'gid', 'webId'];

        for (const cookieName of criticalCookieNames) {
          try {
            const cookie = await new Promise<chrome.cookies.Cookie | null>((resolve) => {
              chrome.cookies.get(
                { url: 'https://www.xiaohongshu.com', name: cookieName },
                (c) => resolve(c || null)
              );
            });

            if (cookie) {
              console.log(`✅ [小红书特殊处理] 成功获取 Cookie: ${cookieName}`);

              // 将 Cookie 添加到 platformCookiesMap
              if (!platformCookiesMap.has('xiaohongshu')) {
                platformCookiesMap.set('xiaohongshu', []);
              }

              // 检查是否已经存在（避免重复）
              const existingCookies = platformCookiesMap.get('xiaohongshu')!;
              const exists = existingCookies.some(c => c.name === cookie.name);

              if (!exists) {
                platformCookiesMap.get('xiaohongshu')!.push(cookie);
                console.log(`  ➕ 已添加到 Cookie 列表`);
              } else {
                console.log(`  ℹ️ Cookie 已存在，跳过`);
              }
            } else {
              console.log(`⚠️ [小红书特殊处理] Cookie 不存在: ${cookieName}`);
            }
          } catch (error) {
            console.error(`❌ [小红书特殊处理] 获取 Cookie 失败 (${cookieName}):`, error);
          }
        }
      }

      // 🔥 特殊处理：针对今日头条平台，使用 chrome.cookies.get() 单独获取关键 Cookie
      // 因为某些关键 Cookie 可能被标记为 httpOnly 或有特殊限制
      const toutiaoPlatform = state.platforms.find(p => p.id === 'toutiao');
      if (toutiaoPlatform) {
        console.log('🔍 [今日头条特殊处理] 尝试单独获取关键 Cookie...');

        // 需要单独获取的关键 Cookie 名称
        const criticalCookieNames = ['sessionid', 'sid_tt', 'odin_tt', 'csrftoken', 'passport_csrf_token'];

        for (const cookieName of criticalCookieNames) {
          try {
            const cookie = await new Promise<chrome.cookies.Cookie | null>((resolve) => {
              chrome.cookies.get(
                { url: 'https://www.toutiao.com', name: cookieName },
                (c) => resolve(c || null)
              );
            });

            if (cookie) {
              console.log(`✅ [今日头条特殊处理] 成功获取 Cookie: ${cookieName}`);

              // 将 Cookie 添加到 platformCookiesMap
              if (!platformCookiesMap.has('toutiao')) {
                platformCookiesMap.set('toutiao', []);
              }

              // 检查是否已经存在（避免重复）
              const existingCookies = platformCookiesMap.get('toutiao')!;
              const exists = existingCookies.some(c => c.name === cookie.name);

              if (!exists) {
                platformCookiesMap.get('toutiao')!.push(cookie);
                console.log(`  ➕ 已添加到 Cookie 列表`);
              } else {
                console.log(`  ℹ️ Cookie 已存在，跳过`);
              }
            } else {
              console.log(`⚠️ [今日头条特殊处理] Cookie 不存在: ${cookieName}`);
            }
          } catch (error) {
            console.error(`❌ [今日头条特殊处理] 获取 Cookie 失败 (${cookieName}):`, error);
          }
        }
      }

      // 打印最终分组的 Cookie 结果
      console.log('📊 [Cookie 调试] 最终分组结果:');
      for (const [platformId, cookies] of platformCookiesMap.entries()) {
        const platform = state.platforms.find(p => p.id === platformId);
        console.log(`  📦 ${platform?.name || platformId}: ${cookies.length} 个 Cookie`);
        console.log(`     Cookie 名称列表:`, cookies.map(c => c.name));
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
              {hasCookies && !fp.sent && (
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
