import { AvatarDropdown, AvatarName, Footer, Question } from '@/components';
import { TOKEN_KEYS } from '@/config/config';
import {
  clearTokens,
  getMenuTree,
  getSystemConfig,
  currentUser as queryCurrentUser,
} from '@/services/admin/common/api';
import storage from '@/utils/storage';
import { ConfigProvider } from '@ant-design/charts';
import * as allIcons from '@ant-design/icons';
import { LinkOutlined } from '@ant-design/icons';
import type { Settings as LayoutSettings } from '@ant-design/pro-components';
import { PageContainer } from '@ant-design/pro-components';
import '@ant-design/v5-patch-for-react-19';
import type { RunTimeLayoutConfig } from '@umijs/max';
import { Helmet, history, Link } from '@umijs/max';
import { Breadcrumb } from 'antd';
import React from 'react';
import defaultSettings from '../config/defaultSettings';

const isDev = process.env.NODE_ENV === 'development';
const loginPath = '/login';

/**
 * @see https://umijs.org/docs/api/runtime-config#getinitialstate
 * */
export async function getInitialState(): Promise<{
  settings?: Partial<LayoutSettings>;
  currentUser?: API.AdminCurrentUser;
  loading?: boolean;
  fetchUserInfo?: () => Promise<API.AdminCurrentUser | undefined>;
  menuData?: API.AdminMenuItem[];
  breadcrumbData?: any[];
  systemConfig?: API.AdminSystemConfig;
}> {
  const fetchUserInfo = async (): Promise<API.AdminCurrentUser | undefined> => {
    try {
      // 先检查是否有 access_token
      const accessToken = storage.get(TOKEN_KEYS.ACCESS_TOKEN);

      if (!accessToken) {
        history.push(loginPath);
        return undefined;
      }

      // 有 token，请求用户信息
      const userResponse = await queryCurrentUser();
      return userResponse?.data as API.AdminCurrentUser | undefined;
    } catch (_error) {
      // 请求失败，清除 token 并跳转登录页
      clearTokens();
      history.push(loginPath);
    }
    return undefined;
  };

  const fetchMenuData = async (): Promise<API.AdminMenuItem[]> => {
    try {
      const menuResponse = await getMenuTree();
      return menuResponse?.data || [];
    } catch (_error) {
      console.error('获取菜单数据失败:', _error);
      return [];
    }
  };

  const fetchSystemConfig = async (): Promise<API.AdminSystemConfig | undefined> => {
    try {
      const configResponse = await getSystemConfig();
      return configResponse?.data as API.AdminSystemConfig | undefined;
    } catch (_error) {
      console.error('获取系统配置失败:', _error);
      return undefined;
    }
  };

  // 如果不是登录页面，执行
  const { location } = history;
  const systemConfig = await fetchSystemConfig();
  if (location.pathname !== loginPath) {
    const currentUser = await fetchUserInfo();
    if (currentUser) {
      const menuData = await fetchMenuData();

      return {
        fetchUserInfo,
        currentUser,
        menuData,
        systemConfig,
        settings: defaultSettings as Partial<LayoutSettings>,
        breadcrumbData: [], // 初始化面包屑数据
      };
    }
  }
  return {
    fetchUserInfo,
    settings: defaultSettings as Partial<LayoutSettings>,
    systemConfig,
    breadcrumbData: [], // 初始化面包屑数据
  };
}

// 获取图标组件
const getIconComponent = (iconName?: string) => {
  if (!iconName) return undefined;

  const IconComponent = (allIcons as any)[iconName];
  if (!IconComponent) {
    console.warn(`Icon "${iconName}" not found in @ant-design/icons`);
    return undefined;
  }

  return React.createElement(IconComponent);
};

// 转换菜单数据格式，适配 ProLayout
const transformMenuData = (menuData: API.AdminMenuItem[]): any[] => {
  return menuData
    .filter((item) => {
      return item.type === 1 || item.type === 2 || item.type === 3;
    })
    .map((item) => ({
      key: item.path,
      path: item.path,
      name: item.name,
      icon: getIconComponent(item.icon),
      component: item.component,
      redirect: item.redirect,
      target: item.target,
      routes:
        item.children && item.children.length > 0 ? transformMenuData(item.children) : undefined,
    }));
};

// ProLayout 支持的api https://procomponents.ant.design/components/layout
// export const layout: RunTimeLayoutConfig = ({ initialState, setInitialState }) => {
export const layout: RunTimeLayoutConfig = ({ initialState, setInitialState }) => {
  return {
    actionsRender: () => [<Question key="doc" />],
    avatarProps: {
      title: <AvatarName />,
      render: (_, avatarChildren) => {
        return <AvatarDropdown menu={true}>{avatarChildren}</AvatarDropdown>;
      },
    },
    // waterMarkProps: {
    //   content: initialState?.currentUser?.real_name,
    // },
    contentStyle: {
      minHeight: 'calc(100vh - 160px)',
    },
    footerRender: () => <Footer copyright={initialState?.systemConfig?.copyright} />,
    onPageChange: () => {
      const { location } = history;
      // 如果没有登录，重定向到 login
      if (!initialState?.currentUser && location.pathname !== loginPath) {
        history.push(loginPath);
      }
    },
    links: isDev
      ? [
          <Link key="openapi" to="/umi/plugin/openapi" target="_blank">
            <LinkOutlined />
            <span>OpenAPI 文档</span>
          </Link>,
        ]
      : [],
    menuHeaderRender: undefined,
    // 自定义 403 页面
    // unAccessible: <div>unAccessible</div>,
    // 配置菜单数据
    menu: {
      locale: false,
      autoClose: false,
      request: async () => {
        const menuData = initialState?.menuData || [];
        return transformMenuData(menuData);
      },
    },
    // 增加一个 loading 的状态
    // childrenRender: (children) => {
    //   // if (initialState?.loading) return <PageLoading />;
    //   return (
    //     <>
    //       {children}
    //       {isDev && (
    //         <SettingDrawer
    //           disableUrlParams
    //           enableDarkTheme
    //           settings={initialState?.settings}
    //           onSettingChange={(settings) => {
    //             setInitialState((preInitialState) => ({
    //               ...preInitialState,
    //               settings,
    //             }));
    //           }}
    //         />
    //       )}
    //     </>
    //   );
    // },
    childrenRender: (children: React.ReactNode) => {
      return (
        <>
          <Helmet>
            {initialState?.systemConfig?.site_favicon_data?.[0]?.url && (
              <link rel="icon" href={initialState.systemConfig.site_favicon_data[0].url} />
            )}
            {initialState?.systemConfig?.site_description && (
              <meta name="description" content={initialState.systemConfig.site_description} />
            )}
            {initialState?.systemConfig?.site_keywords && (
              <meta name="keywords" content={initialState.systemConfig.site_keywords} />
            )}
          </Helmet>
          <PageContainer
            fixedHeader={true}
            title={false}
            breadcrumbRender={(props: any) => {
              const items = props.breadcrumb?.items || [];
              setInitialState((s) => ({
                ...s,
                breadcrumbData: items,
              }));
              // 转换为新格式
              const breadcrumbItems = items.map((route: any) => ({
                key: route.linkPath || route.path || Math.random().toString(36).substring(2, 9),
                title: route.breadcrumbName || route.title || '未命名',
              }));

              return <Breadcrumb items={breadcrumbItems} />;
            }}
          >
            <ConfigProvider
              line={{
                autoFit: true,
                margin: 10,
                height: 400,
                animate: { enter: { type: 'pathIn', duration: 1000 } },
                shapeField: 'smooth',
                slider: { x: {} }, // 缩略轴
                axis: {
                  x: {
                    line: true, // 是否显示轴线
                    arrow: true, // 是否显示箭头
                  },
                  y: {
                    line: true, // 是否显示轴线
                    arrow: true, // 是否显示箭头
                  },
                },
                viewStyle: {
                  viewFill: '#ffffff',
                  viewRadius: 10,
                },
              }}
            >
              {children}
            </ConfigProvider>
          </PageContainer>
        </>
      );
    },
    ...initialState?.settings,
    title: initialState?.systemConfig?.site_name || defaultSettings.title,
    logo: initialState?.systemConfig?.site_logo_data?.[0]?.url || defaultSettings.logo,
    menuItemRender: (menuItemProps, defaultDom) => {
      if (menuItemProps.isUrl || !menuItemProps.path) {
        return defaultDom;
      }
      // 支持二级菜单显示icon
      return (
        <Link to={menuItemProps.path} style={{ display: 'flex', gap: '10px' }}>
          {menuItemProps.pro_layout_parentKeys &&
            menuItemProps.pro_layout_parentKeys.length > 1 &&
            menuItemProps.icon}
          {defaultDom}
        </Link>
      );
    },
  };
};
