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
    { text: '快速开始', link: '/guide/getting-started/' },
    { text: '后端开发', link: '/guide/backend/' },
    { text: '前端开发', link: '/guide/frontend/' },
    { text: 'API 文档', link: '/api/' },
    { text: '部署运维', link: '/deploy/' },
    { text: '常见问题', link: '/faq/' },
  ];
}

function createSidebar() {
  return {
    '/guide/': {
      base: '/guide/',
      items: [
        {
          text: '项目介绍',
          items: [
            { text: '项目概述', link: 'introduction/' },
            { text: '功能特性', link: 'introduction/features' },
          ],
        },
        {
          text: '快速开始',
          items: [
            { text: '环境要求', link: 'getting-started/' },
            { text: '安装指南', link: 'getting-started/install' },
            { text: '快速启动', link: 'getting-started/quick-start' },
            { text: '目录结构', link: 'getting-started/directory' },
            { text: '配置说明', link: 'getting-started/configuration' },
          ],
        },
        {
          text: '工具指南',
          items: [
            { text: '浏览器扩展', link: 'browser-extension' },
          ],
        },
        {
          text: '命令行工具',
          items: [
            { text: '工具概览', link: 'cli-commands/' },
            { text: '数据库迁移', link: 'cli-commands/migrate' },
            { text: '数据库填充', link: 'cli-commands/seed' },
            { text: 'Celery 管理', link: 'cli-commands/celery-manager' },
            { text: '模块创建', link: 'cli-commands/create-module' },
            { text: '密钥生成', link: 'cli-commands/generate-keys' },
          ],
        },
        {
          text: '后端开发',
          items: [
            { text: '开发环境搭建', link: 'backend/' },
            { text: '后端架构', link: 'backend/architecture' },
            { text: '模块开发规范', link: 'backend/module-guide' },
            { text: '数据库设计',
              items: [
                { text: '数据库概览', link: 'backend/database/' },
                { text: '模型定义', link: 'backend/database/models' },
                { text: 'Admin 模块表结构', link: 'backend/database/admin-models' },
                { text: 'Quant 模块表结构', link: 'backend/database/quant-models' },
                { text: '数据库迁移', link: 'backend/database/migrations' },
              ],
            },
            { text: 'API 开发',
              items: [
                { text: 'API 开发规范', link: 'backend/api/' },
                { text: 'Admin 模块 API', link: 'backend/api/admin-api' },
                { text: 'Quant 模块 API', link: 'backend/api/quant-api' },
                { text: 'Content 模块 API', link: 'backend/api/content-api' },
                { text: '认证授权', link: 'backend/api/authentication' },
              ],
            },
            { text: '异步任务',
              items: [
                { text: '异步任务开发', link: 'backend/async/' },
                { text: 'Celery 使用指南', link: 'backend/async/celery-guide' },
                { text: '任务清单', link: 'backend/async/task-list' },
              ],
            },
            { text: '特色功能',
              items: [
                { text: '文件上传', link: 'backend/features/upload' },
                { text: '缓存使用', link: 'backend/features/cache' },
                { text: '日志系统', link: 'backend/features/log' },
                { text: '数据验证', link: 'backend/features/validation' },
                { text: '异常处理', link: 'backend/features/exception' },
                { text: '浏览器自动化', link: 'backend/features/browser' },
                { text: '内容发布', link: 'backend/features/content-publish' },
              ],
            },
            { text: '配置系统',
              items: [
                { text: '配置概览', link: 'backend/config/' },
                { text: '环境变量', link: 'backend/config/env-variables' },
              ],
            },
          ],
        },
        {
          text: '前端开发',
          items: [
            { text: '开发环境搭建', link: 'frontend/' },
            { text: '前端架构', link: 'frontend/architecture' },
            { text: '页面开发',
              items: [
                { text: '页面开发规范', link: 'frontend/pages/' },
                { text: 'Admin 模块页面', link: 'frontend/pages/admin-pages' },
                { text: 'Quant 模块页面', link: 'frontend/pages/quant-pages' },
              ],
            },
            { text: '组件开发',
              items: [
                { text: '组件开发规范', link: 'frontend/components/' },
                { text: '通用组件', link: 'frontend/components/common-comps' },
                { text: '上传组件', link: 'frontend/components/upload-comps' },
                { text: '布局组件', link: 'frontend/components/layout-comps' },
              ],
            },
            { text: 'API 服务',
              items: [
                { text: 'API 服务封装', link: 'frontend/services/' },
                { text: '请求工具', link: 'frontend/services/request' },
                { text: 'API 列表', link: 'frontend/services/api-list' },
              ],
            },
            { text: '特色功能',
              items: [
                { text: '路由配置', link: 'frontend/features/routing' },
                { text: '状态管理', link: 'frontend/features/state' },
                { text: '认证流程', link: 'frontend/features/auth' },
                { text: '权限控制', link: 'frontend/features/permission' },
                { text: 'Excel 导入导出', link: 'frontend/features/excel' },
              ],
            },
            { text: '配置系统',
              items: [
                { text: '配置概览', link: 'frontend/config/' },
                { text: '代理配置', link: 'frontend/config/proxy' },
                { text: '环境变量', link: 'frontend/config/env-variables' },
              ],
            },
          ],
        },
      ],
    },
    '/api/': {
      base: '/api/',
      items: [
        { text: 'API 概览', link: '/' },
        { text: '认证接口', link: 'authentication' },
        { text: 'Admin 模块',
          items: [
            { text: '管理员管理', link: 'admin/admin' },
            { text: '角色管理', link: 'admin/group' },
            { text: '菜单管理', link: 'admin/rule' },
            { text: '系统配置', link: 'admin/sys-config' },
            { text: '文件上传', link: 'admin/upload' },
          ],
        },
        { text: 'Quant 模块',
          items: [
            { text: '股票管理', link: 'quant/stock' },
            { text: '行业管理', link: 'quant/industry' },
            { text: '概念管理', link: 'quant/concept' },
            { text: '行业历史', link: 'quant/industry-log' },
            { text: '概念历史', link: 'quant/concept-log' },
            { text: 'K线数据', link: 'quant/stock-kline' },
          ],
        },
        { text: '错误码说明', link: 'error-codes' },
      ],
    },
    '/deploy/': {
      base: '/deploy/',
      items: [
        { text: '部署概览', link: 'index' },
        { text: '环境准备', link: 'environment' },
        { text: '环境变量配置', link: 'env-config' },
        { text: '后端部署',
          items: [
            { text: '后端部署', link: 'backend/deploy' },
            { text: 'Docker 部署', link: 'backend/docker' },
            { text: 'Celery 部署', link: 'backend/celery' },
          ],
        },
        { text: '前端部署',
          items: [
            { text: '前端构建', link: 'frontend/build' },
            { text: 'Nginx 配置', link: 'frontend/nginx' },
          ],
        },
        { text: '数据库',
          items: [
            { text: '数据库迁移', link: 'database/migration' },
            { text: '数据备份', link: 'database/backup' },
          ],
        },
        { text: '监控运维',
          items: [
            { text: '日志管理', link: 'monitoring/logs' },
            { text: 'Celery 监控', link: 'monitoring/flower' },
            { text: '性能优化', link: 'monitoring/performance' },
          ],
        },
        { text: '常见问题', link: 'troubleshooting' },
      ],
    },
    '/faq/': {
      base: '/faq/',
      items: [
        { text: 'FAQ 概览', link: 'index' },
        { text: '开发问题',
          items: [
            { text: '后端问题', link: 'development/backend' },
            { text: '前端问题', link: 'development/frontend' },
          ],
        },
        { text: '部署问题', link: 'deployment' },
        { text: '业务问题', link: 'business' },
        { text: '最佳实践',
          items: [
            { text: '代码规范', link: 'best-practices/code-style' },
            { text: '安全建议', link: 'best-practices/security' },
            { text: '性能优化', link: 'best-practices/performance' },
            { text: '测试指南', link: 'best-practices/testing' },
          ],
        },
      ],
    },
  };
}