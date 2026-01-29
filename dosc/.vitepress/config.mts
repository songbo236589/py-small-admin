import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  lang: 'zh-CN',
  title: "Py Small Admin",
  description: "基于 Python 的轻量级后台管理系统文档",
  base:'/',
  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
    ['meta', { name: 'description', content: '基于 Python 的轻量级后台管理系统文档' }],
    ['meta', { name: 'keywords', content: 'Python, Admin, 后台管理, 文档' }],
    ['link', { rel: 'icon', href: '/favicon.ico' }],

    // Open Graph
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'Py Small Admin - 基于 Python 的轻量级后台管理系统' }],
    ['meta', { property: 'og:description', content: '基于 Python 的轻量级后台管理系统文档' }],
    ['meta', { property: 'og:image', content: '/logo.png' }],
    // ['meta', { property: 'og:url', content: 'https://yourdomain.com' }],
    ['meta', { property: 'og:site_name', content: 'Py Small Admin' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],

    // Twitter Card
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: 'Py Small Admin - 基于 Python 的轻量级后台管理系统' }],
    ['meta', { name: 'twitter:description', content: '基于 Python 的轻量级后台管理系统文档' }],
    ['meta', { name: 'twitter:image', content: '/logo.png' }],

    // Canonical
    // ['link', { rel: 'canonical', href: 'https://yourdomain.com' }]
  ],
  markdown: {
    //显示行数
    lineNumbers: true,
    //中文配置
    container:{
      tipLabel: "提示",
      warningLabel: "警告",
      noteLabel: "注意",
      dangerLabel: "危险",
      detailsLabel: "详情",
      infoLabel: "信息",
    }
  },
  lastUpdated:true,
  themeConfig: {
    logo: '/logo.png',
    nav: createNav(),
    sidebar: createSidebar(),

    // 最后更新时间
    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'medium',
        timeStyle: 'medium'
      }
    },
    docFooter:{
      prev: "上一页",
      next: "下一页",
    },
    // 编辑链接
    // editLink: {
    //   pattern: 'https://github.com/yourusername/py-small-admin/edit/main/dosc/:path',
    //   text: '在 GitHub 上编辑此页'
    // },

    // 目录显示
    outline: {
      level: [2, 3],
      label: '页面导航'
    },

    // 页脚配置
    footer: {
      message: '基于 MIT 许可发布',
      copyright: 'Copyright © 2024 Py Small Admin'
    },
    returnToTopLabel: "回到顶部",
    sidebarMenuLabel: "菜单",
    darkModeSwitchLabel: "主题",
    lightModeSwitchTitle: "切换到浅色模式",
    darkModeSwitchTitle: "切换到深色模式",
    outlineTitle: "目录",
    // 搜索配置
    search:{
      provider:'local',
      options:{
        translations:{
          button: {
            buttonText: '搜索文档',
            buttonAriaLabel: '搜索文档'
          },
          modal:{
            displayDetails:'显示详细信息列表',
            resetButtonTitle: '清除查询条件',
            backButtonTitle:'后退',
            noResultsText: '无法找到相关结果',
            footer:{
              selectText: '选择',
              closeText: '关闭',
              navigateText: '切换'
            }
          }
        }
      }
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/songbo236589/py-small-admin' }
    ]
  }
})


/**
 * @type {()=>import('./theme-default/config').DefaultTheme.NavItem[]}
 */
function createNav() {
  return [
      { text: '首页', link: '/' },
      { text: '文档写作指南', link: '/guides/writing-guide' }
    ];
}

function createSidebar() {
  return {
    '/guides/': [
      {
        text: '指南',
        items: [
          { text: '文档写作指南', link: '/guides/writing-guide' }
        ]
      }
    ]
  };
}