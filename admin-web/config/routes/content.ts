export default [
  {
    path: '/content',
    redirect: '/content/dashboard',
  },
  {
    path: '/content/dashboard',
    component: './content/dashboard/index',
  },
  {
    path: '/content/manage/article',
    component: './content/article/index',
  },
  {
    path: '/content/manage/category',
    component: './content/category/index',
  },
  {
    path: '/content/manage/tag',
    component: './content/tag/index',
  },
  {
    path: '/content/manage/platform_account',
    component: './content/platform_account/index',
  },
  {
    path: '/content/manage/topic',
    component: './content/topic/index',
  },
  {
    path: '/content/manage/publish',
    component: './content/publish/index',
  },
];
