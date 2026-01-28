declare namespace API {
  type AdminRuleList = {
    id: number;
    path: string;
    component: string;
    redirect: string;
    icon: string;
    name: string;
    type: 1 | 2 | 3;
    status: 1 | 0;
    pid: number;
    sort: number;
    target: string;
    created_at: string;
    updated_at: string | null;
  };
  type AdminRuleForm = {
    id: number | null;
    path: string;
    component: string;
    redirect: string;
    icon: string;
    name: string;
    type: 1 | 2 | 3;
    status: 1 | 0;
    pid: number;
    sort: number;
    target: string;
  };
}
