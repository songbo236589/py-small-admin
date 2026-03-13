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
    component: './content/manage/article/index',
  },
  {
    path: '/content/manage/category',
    component: './content/manage/category/index',
  },
  {
    path: '/content/manage/tag',
    component: './content/manage/tag/index',
  },
  {
    path: '/content/manage/platform_account',
    component: './content/manage/platform_account/index',
  },
  {
    path: '/content/manage/topic',
    component: './content/manage/topic/index',
  },
  {
    path: '/content/manage/publish',
    component: './content/manage/publish/index',
  },
];
