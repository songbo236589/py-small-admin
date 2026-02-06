/**
 * Background Service Worker
 * Manifest V3 使用 Service Worker 替代 Background Page
 */

// 监听扩展安装事件
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Py Small Admin Login Helper 扩展已安装');
  } else if (details.reason === 'update') {
    console.log('Py Small Admin Login Helper 扩展已更新');
  }
});

// 监听来自 Popup 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getCookies') {
    // 处理获取 Cookie 的请求
    handleGetCookies(request.domains).then(sendResponse);
    return true; // 保持消息通道开放
  }
});

/**
 * 获取指定域名的 Cookies
 */
async function handleGetCookies(domains: string[]): Promise<chrome.cookies.Cookie[]> {
  const allCookies: chrome.cookies.Cookie[] = [];

  for (const domain of domains) {
    const cookies = await new Promise<chrome.cookies.Cookie[]>((resolve) => {
      chrome.cookies.getAll({ domain }, (cookies) => {
        resolve(cookies || []);
      });
    });
    allCookies.push(...cookies);
  }

  return allCookies;
}

// 导出类型供其他模块使用
export {};
