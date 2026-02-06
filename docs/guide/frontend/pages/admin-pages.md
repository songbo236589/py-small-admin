# Admin 模块页面

本文档介绍了 Admin 模块的页面。

## 页面列表

| 页面 | 路由 | 功能 |
|------|------|------|
| 仪表盘 | `/admin/dashboard` | 系统概览 |
| 管理员列表 | `/admin/auth/admin` | 管理员管理 |
| 角色组列表 | `/admin/auth/group` | 角色管理 |
| 菜单规则列表 | `/admin/auth/rule` | 菜单管理 |
| 系统配置 | `/admin/sys/sys_config` | 系统参数配置 |
| 文件上传 | `/admin/sys/upload` | 文件管理 |

## 仪表盘

### 功能说明

仪表盘展示系统的整体运行状态和关键指标。

### 主要功能

- 显示系统信息卡片（服务器信息、运行时间等）
- 显示管理员统计（总数、活跃数、今日新增）
- 显示系统配置状态

### 组件结构

```
dashboard/
  ├── components/
  │   ├── StatCard.tsx      # 统计卡片
  │   └── SystemInfo.tsx    # 系统信息
  └── index.tsx             # 页面入口
```

### 示例代码

```typescript
import { Card, Statistic, Row, Col } from 'antd';
import { useRequest } from 'ahooks';

const Dashboard = () => {
  const { data: stats } = useRequest(getDashboardStats);

  return (
    <Row gutter={16}>
      <Col span={6}>
        <Card>
          <Statistic title="管理员总数" value={stats?.total} />
        </Card>
      </Col>
    </Row>
  );
};
```

## 管理员列表

### 功能说明

管理系统员账号，包括创建、编辑、删除、重置密码等操作。

### 主要功能

- 查看管理员列表（支持搜索、分页、排序）
- 添加管理员
- 编辑管理员信息
- 删除管理员
- 重置管理员密码
- 批量删除管理员

### 表格列配置

| 列名 | 字段 | 说明 |
|------|------|------|
| ID | id | 主键 |
| 用户名 | username | 登录用户名 |
| 昵称 | nickname | 显示名称 |
| 邮箱 | email | 联系邮箱 |
| 角色 | group | 所属角色组 |
| 状态 | status | 启用/禁用 |
| 创建时间 | created_at | 注册时间 |
| 操作 | actions | 编辑/删除按钮 |

### API 接口

```typescript
// 获取列表
GET /api/admin/index

// 创建
POST /api/admin/add

// 编辑
PUT /api/admin/update/:id

// 删除
DELETE /api/admin/destroy/:id

// 批量删除
DELETE /api/admin/destroy_all

// 重置密码
PUT /api/admin/reset_password/:id
```

## 角色组列表

### 功能说明

管理系统角色组，配置角色权限。

### 主要功能

- 查看角色组列表
- 添加角色组
- 编辑角色组信息
- 配置角色权限
- 删除角色组
- 批量删除角色组

### 权限配置

权限使用树形结构进行配置：

```
系统管理
├── 管理员管理 (查看/新增/编辑/删除)
├── 角色管理 (查看/新增/编辑/删除)
└── 菜单管理 (查看/新增/编辑/删除)
```

### API 接口

```typescript
// 获取列表
GET /api/group/index

// 创建
POST /api/group/add

// 编辑
PUT /api/group/update/:id

// 删除
DELETE /api/group/destroy/:id

// 批量删除
DELETE /api/group/destroy_all

// 获取菜单树
GET /api/group/menu_tree

// 保存权限
POST /api/group/save_rules
```

## 菜单规则列表

### 功能说明

管理系统菜单规则，配置前端路由和权限。

### 主要功能

- 查看菜单规则列表（树形表格）
- 添加菜单规则
- 编辑菜单规则信息
- 删除菜单规则
- 批量删除菜单规则

### 菜单类型

| 类型 | 值 | 说明 |
|------|-----|------|
| 目录 | 0 | 一级目录，无路由 |
| 菜单 | 1 | 有路由的页面菜单 |
| 按钮 | 2 | 页面内的权限按钮 |

### API 接口

```typescript
// 获取列表
GET /api/rule/index

// 创建
POST /api/rule/add

// 编辑
PUT /api/rule/update/:id

// 删除
DELETE /api/rule/destroy/:id

// 批量删除
DELETE /api/rule/destroy_all

// 获取菜单树
GET /api/rule/tree
```

## 系统配置

### 功能说明

管理系统级配置参数。

### 主要功能

- 查看系统配置
- 更新系统配置
- 测试邮件发送

### 配置项

| 配置项 | 说明 |
|--------|------|
| site_name | 网站名称 |
| site_keywords | 网站关键词 |
| site_description | 网站描述 |
| email_host | 邮件服务器 |
| email_port | 邮件端口 |
| email_username | 邮件用户名 |
| email_password | 邮件密码 |

### API 接口

```typescript
// 获取配置
GET /api/sys_config/index

// 更新配置
PUT /api/sys_config/update

// 测试邮件
POST /api/sys_config/test_email
```

## 文件上传

### 功能说明

管理系统上传的文件。

### 主要功能

- 查看文件列表（按类型分类）
- 上传图片
- 上传文档
- 上传视频
- 上传音频
- 删除文件

### 文件类型

| 类型 | 扩展名 |
|------|--------|
| 图片 | jpg, png, gif, webp |
| 文档 | pdf, doc, docx, xls, xlsx |
| 视频 | mp4, avi, mov |
| 音频 | mp3, wav, aac |

### API 接口

```typescript
// 获取列表
GET /api/upload/index

// 上传文件
POST /api/upload/upload

// 删除文件
DELETE /api/upload/destroy/:id
```

## 通用组件

### ProTable 配置

Admin 模块使用 ProTable 组件作为列表页的基础：

```typescript
<ProTable
  columns={columns}
  request={async (params) => {
    const res = await getList(params);
    return {
      data: res.data.items,
      success: true,
      total: res.data.total,
    };
  }}
  rowKey="id"
  search={{
    labelWidth: 'auto',
  }}
  pagination={{
    defaultPageSize: 10,
    showSizeChanger: true,
  }}
  toolBarRender={() => [
    <Button type="primary" onClick={handleAdd}>
      新建
    </Button>
  ]}
/>
```

### 表单处理

使用 Modal + Form 处理新增/编辑：

```typescript
const [modalVisible, setModalVisible] = useState(false);
const [editingId, setEditingId] = useState<number>();

const handleEdit = (record: any) => {
  setEditingId(record.id);
  form.setFieldsValue(record);
  setModalVisible(true);
};

const handleSubmit = async () => {
  const values = await form.validateFields();
  if (editingId) {
    await update(editingId, values);
  } else {
    await add(values);
  }
  setModalVisible(false);
  actionRef.current?.reload();
};
```
