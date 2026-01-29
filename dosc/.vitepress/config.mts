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
      { text: '文档写作指南', link: '/guides/writing-guide' },
      { text: '快速开始', link: '/server/getting-started' },
      { text: '架构设计', link: '/guides/architecture-overview' },
      { text: '模块开发', link: '/server/module-development' },
      { text: '任务与队列', link: '/server/celery/celery-guide' },
      { text: '部署与运维', link: '/server/deployment/deployment-guide' }
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
      },
      {
        text: '架构设计',
        items: [
          { text: '架构概览', link: '/guides/architecture-overview' },
          { text: '分层架构说明', link: '/guides/layered-architecture' },
          { text: '设计模式应用', link: '/guides/design-patterns' },
          { text: '最佳实践', link: '/guides/best-practices' }
        ]
      }
    ],
    '/server/': [
      {
        text: '快速开始',
        items: [
          { text: '快速开始', link: '/server/getting-started' },
          { text: '项目结构说明', link: '/server/project-structure' },
          { text: '开发环境搭建', link: '/server/development-setup' },
          { text: '第一个接口开发', link: '/server/first-api' }
        ]
      },
      {
        text: '核心模块开发',
        items: [
          { text: '模块开发指南', link: '/server/module-development' },
          { text: 'Admin 模块详解', link: '/server/admin-module' },
          { text: 'Quant 模块详解', link: '/server/quant-module' },
          { text: 'Common 模块详解', link: '/server/common-module' }
        ]
      },
      {
        text: 'API 开发指南',
        items: [
          { text: '路由开发指南', link: '/server/api-development/routing-guide' },
          { text: '控制器开发指南', link: '/server/api-development/controller-guide' },
          { text: '服务层开发指南', link: '/server/api-development/service-guide' },
          { text: '模型开发指南', link: '/server/api-development/model-guide' },
          { text: '验证器开发指南', link: '/server/api-development/validator-guide' },
          { text: '分页开发指南', link: '/server/api-development/pagination-guide' }
        ]
      },
      {
        text: '数据库相关',
        items: [
          { text: '数据库使用指南', link: '/server/database/database-guide' },
          { text: '数据库迁移指南', link: '/server/database/migration-guide' },
          { text: '关系映射指南', link: '/server/database/relationship-guide' },
          { text: '查询优化指南', link: '/server/database/query-optimization' },
          { text: '分表使用指南', link: '/server/database/sharding-guide' }
        ]
      },
      {
        text: '认证与权限',
        items: [
          { text: 'JWT 使用指南', link: '/server/authentication/jwt-guide' },
          { text: 'RBAC 权限模型', link: '/server/authentication/rbac-guide' }
        ]
      },
      {
        text: '任务与队列',
        items: [
          { text: 'Celery 基础指南', link: '/server/celery/celery-guide' },
          { text: '任务开发指南', link: '/server/celery/task-development' },
          { text: '队列管理指南', link: '/server/celery/queue-management' },
          { text: '监控指南', link: '/server/celery/monitoring' }
        ]
      },
      {
        text: '部署与运维',
        items: [
          { text: '部署指南', link: '/server/deployment/deployment-guide' },
          { text: '监控指南', link: '/server/deployment/monitoring' },
          { text: '日志指南', link: '/server/deployment/logging' },
          { text: '故障排查', link: '/server/deployment/troubleshooting' }
        ]
      }
    ]
  };
}