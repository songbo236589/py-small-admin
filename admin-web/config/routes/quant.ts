export default [
  {
    path: '/quant',
    redirect: '/quant/dashboard',
  },
  {
    path: '/quant/dashboard',
    component: './quant/dashboard/index',
  },
  {
    path: '/quant/data/concept',
    component: './quant/data/concept/index',
  },
  {
    path: '/quant/data/concept_log',
    component: './quant/data/concept_log/index',
  },
  {
    path: '/quant/data/industry_log',
    component: './quant/data/industry_log/index',
  },
  {
    path: '/quant/data/industry',
    component: './quant/data/industry/index',
  },
  {
    path: '/quant/data/stock',
    component: './quant/data/stock/index',
  },
];
