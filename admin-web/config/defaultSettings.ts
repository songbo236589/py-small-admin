import type { ProLayoutProps } from '@ant-design/pro-components';

/**
 * @name
 */
const Settings: ProLayoutProps & {
  pwa?: boolean;
  logo?: string;
} = {
  title: 'Ant Design Pro',
  logo: '/logo.svg', // logo
  layout: 'mix',
  contentWidth: 'Fluid',
  token: {
    header: {
      // header 的背景颜色
      colorBgHeader: '#292f33',
      // sider 的标题字体颜色
      colorHeaderTitle: '#fff',
      // menuItem 的字体颜色
      colorTextMenu: '#dfdfdf',
      //menu 的二级字体颜色，比如 footer 和 action 的 icon
      colorTextMenuSecondary: '#dfdfdf',
      // menuItem 的选中字体颜色
      colorTextMenuSelected: '#fff',
      // menuItem hover 的选中字体颜色
      colorTextMenuActive: 'rgba(255,255,255,0.85)',
      // menuItem 的 hover 背景颜色
      colorBgMenuItemHover: '#292f33',
      // menuItem 的选中背景颜色
      colorBgMenuItemSelected: '#1890ff',

      // 右上角字体颜色
      colorTextRightActionsItem: '#dfdfdf',
      // 右上角选中的 hover 颜色
      colorBgRightActionsItemHover: '#292f33',
      // header 高度
      heightLayoutHeader: 56,
    },
    colorTextAppListIconHover: '#ffffff',
    colorTextAppListIcon: '#dfdfdf',
    sider: {
      // 	menu 的背景颜色
      colorMenuBackground: '#ffffff',
      colorBgMenuItemHover: '#f6f6f6',
      colorTextMenu: '#595959',
      colorTextMenuSelected: '#1890ff',
      colorTextMenuActive: '#242424',
    },
  },
  // 把第一级的菜单放置到顶栏中
  splitMenus: true,
  // 是否固定导航
  fixSiderbar: true,
  // 是否固定 header 到顶部
  fixedHeader: true,
  // 全局增加滤镜
  colorWeak: true,
  pwa: false,
};

export default Settings;
