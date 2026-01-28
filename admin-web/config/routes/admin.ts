export default [
  {
    path: '/',
    redirect: '/admin/dashboard',
  },
  {
    path: '/admin',
    redirect: '/admin/dashboard',
  },
  {
    path: '/admin/dashboard',
    component: './admin/dashboard/index',
  },
  {
    path: '/admin/auth/admin',
    component: './admin/auth/admin/index',
  },
  {
    path: '/admin/auth/group',
    component: './admin/auth/group/index',
  },
  {
    path: '/admin/auth/rule',
    component: './admin/auth/rule/index',
  },
  {
    path: '/admin/sys/sys_config',
    component: './admin/sys/sys_config/index',
  },
  {
    path: '/admin/sys/upload',
    component: './admin/sys/upload/index',
  },
];
