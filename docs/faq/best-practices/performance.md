# 性能优化

本文档介绍了 Py Small Admin 的性能优化实践，帮助您构建高性能的后台管理系统。

## 目录

- [性能概述](#性能概述)
- [后端性能优化](#后端性能优化)
- [前端性能优化](#前端性能优化)
- [数据库优化](#数据库优化)
- [缓存优化](#缓存优化)
- [监控和调优](#监控和调优)

## 性能概述

### 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| API 响应时间 | < 200ms | P50 响应时间 |
| API 响应时间 | < 500ms | P95 响应时间 |
| API 响应时间 | < 1000ms | P99 响应时间 |
| 数据库查询 | < 100ms | 单个查询时间 |
| 页面加载时间 | < 2s | 首屏加载 |
| 页面交互时间 | < 100ms | 用户操作响应 |

### 性能优化原则

1. **测量优先**：先测量，后优化
2. **优化瓶颈**：专注于关键路径
3. **权衡取舍**：性能 vs 可维护性
4. **渐进优化**：逐步迭代，持续改进

## 后端性能优化

### 异步编程

#### 使用 async/await

```python
# ✅ 正确：使用异步
async def get_admin_with_permissions(admin_id: int):
    """获取管理员及其权限"""
    admin = await db.get(Admin, admin_id)
    permissions = await db.execute(
        select(Permission).where(Permission.admin_id == admin_id)
    )
    return {**admin, "permissions": permissions}

# ❌ 错误：同步阻塞
def get_admin_with_permissions(admin_id: int):
    admin = db.get(Admin, admin_id)  # 阻塞
    permissions = db.execute(...)  # 阻塞
    return {**admin, "permissions": permissions}
```

#### 并行执行

```python
import asyncio

# ✅ 正确：并行执行
async def get_dashboard_data():
    """获取仪表盘数据"""
    results = await asyncio.gather(
        get_user_count(),
        get_order_count(),
        get_revenue_stats(),
    )
    return {
        "user_count": results[0],
        "order_count": results[1],
        "revenue": results[2],
    }

# ❌ 错误：串行执行
async def get_dashboard_data():
    user_count = await get_user_count()
    order_count = await get_order_count()  # 等待上一个完成
    revenue = await get_revenue_stats()  # 等待上一个完成
    return {
        "user_count": user_count,
        "order_count": order_count,
        "revenue": revenue,
    }
```

### 数据库优化

#### 使用索引

```python
from sqlalchemy import Index

# ✅ 正确：添加索引
class AdminModel(SQLModel):
    __tablename__ = "fa_admin_admins"

    id: int = Field(primary_key=True)
    username: str = Field(index=True)  # 单列索引
    email: str = Field(index=True)
    status: int = Field(index=True)
    created_at: datetime = Field(index=True)

    # 复合索引
    __table_args__ = (
        Index("idx_status_created", "status", "created_at"),
        Index("idx_email_status", "email", "status"),
    )
```

#### 避免 N+1 查询

```python
# ❌ 错误：N+1 查询
async def get_admins_with_groups():
    """获取管理员及其角色组"""
    admins = await db.execute(select(AdminModel))
    result = []
    for admin in admins.scalars():
        group = await db.get(GroupModel, admin.group_id)  # N+1
        result.append({**admin, "group_name": group.name})
    return result

# ✅ 正确：使用 join
async def get_admins_with_groups():
    """获取管理员及其角色组"""
    result = await db.execute(
        select(AdminModel, GroupModel)
        .join(GroupModel, AdminModel.group_id == GroupModel.id)
    )
    return [
        {**admin, "group_name": group.name}
        for admin, group in result
    ]
```

#### 查询优化

```python
# ✅ 只查询需要的字段
async def get_admin_list():
    result = await db.execute(
        select(
            AdminModel.id,
            AdminModel.username,
            AdminModel.name,
        ).where(AdminModel.status == 1)
    )
    return result.all()

# ✅ 使用 limit 限制结果
async def get_admins(page: int = 1, size: int = 10):
    result = await db.execute(
        select(AdminModel)
        .where(AdminModel.status == 1)
        .offset((page - 1) * size)
        .limit(size)
    )
    return result.scalars().all()

# ✅ 使用 exists 代替 count
async def check_username_exists(username: str) -> bool:
    result = await db.execute(
        select(AdminModel.id).where(
            AdminModel.username == username
        ).limit(1)
    )
    return result.first() is not None
```

### 连接池配置

```python
# config/database.py
from sqlalchemy.ext.asyncio import create_async_engine

# ✅ 正确的连接池配置
engine = create_async_engine(
    DATABASE_URL,
    # 连接池大小
    pool_size=10,  # 常驻连接数
    max_overflow=20,  # 最大溢出连接数
    # 连接回收
    pool_recycle=3600,  # 1 小时回收一次
    pool_pre_ping=True,  # 连接前先 ping
    # 超时配置
    pool_timeout=30,  # 获取连接超时
    connect_args={
        "connect_timeout": 10,
    },
)
```

### Redis 缓存

```python
# 使用 Redis 缓存热点数据
from functools import wraps
import hashlib
import json

def cache_result(ttl: int = 300):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"cache:{func.__name__}:{hash_args(args, kwargs)}"

            # 尝试从缓存获取
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)

            # 执行函数
            result = await func(*args, **kwargs)

            # 存入缓存
            await redis.setex(
                key,
                ttl,
                json.dumps(result, default=str)
            )
            return result
        return wrapper
    return decorator

# 使用缓存
@cache_result(ttl=600)
async def get_admin_groups():
    """获取管理员角色组列表（缓存 10 分钟）"""
    result = await db.execute(select(GroupModel))
    return result.scalars().all()
```

### 批量操作

```python
# ✅ 批量插入
async def create_admins_bulk(admins_data: list[dict]):
    """批量创建管理员"""
    admins = [AdminModel(**data) for data in admins_data]
    db.add_all(admins)
    await db.commit()

# ✅ 批量更新
async def update_admins_status(ids: list[int], status: int):
    """批量更新管理员状态"""
    await db.execute(
        update(AdminModel)
        .where(AdminModel.id.in_(ids))
        .values(status=status)
    )
    await db.commit()

# ✅ 批量删除
async def delete_admins(ids: list[int]):
    """批量删除管理员"""
    await db.execute(
        delete(AdminModel).where(AdminModel.id.in_(ids))
    )
    await db.commit()
```

### 响应压缩

```python
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# 启用 Gzip 压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## 前端性能优化

### 代码分割

```typescript
// ✅ 路由懒加载
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const AdminList = lazy(() => import('@/pages/Admin/AdminList'));
const AdminEdit = lazy(() => import('@/pages/Admin/AdminEdit'));

// 使用 Suspense
<Suspense fallback={<PageLoading />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/admin" element={<AdminList />} />
    <Route path="/admin/edit/:id" element={<AdminEdit />} />
  </Routes>
</Suspense>
```

### 组件优化

```typescript
// ✅ 使用 React.memo 避免不必要的重渲染
const UserCard = React.memo(({ user }: { user: User }) => {
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
});

// ✅ 使用 useMemo 缓存计算结果
const UserList = ({ users }: { users: User[] }) => {
  const sortedUsers = useMemo(() => {
    return users.sort((a, b) => a.name.localeCompare(b.name));
  }, [users]);

  return (
    <ul>
      {sortedUsers.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </ul>
  );
};

// ✅ 使用 useCallback 稳定函数引用
const Parent = () => {
  const [count, setCount] = useState(0);

  const handleUserClick = useCallback((user: User) => {
    console.log('User clicked:', user);
  }, []);

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      <UserList users={users} onUserClick={handleUserClick} />
    </div>
  );
};
```

### 虚拟列表

```typescript
// ✅ 使用虚拟列表处理大量数据
import { FixedSizeList } from 'react-window';

const UserList = ({ users }: { users: User[] }) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <UserCard user={users[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={users.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

### 防抖和节流

```typescript
// ✅ 防抖：延迟执行
import { useDebounceFn } from 'ahooks';

const SearchInput = () => {
  const { run: handleSearch } = useDebounceFn(
    (value: string) => {
      // 执行搜索
      searchUsers(value);
    },
    { wait: 500 }
  );

  return <input onChange={e => handleSearch(e.target.value)} />;
};

// ✅ 节流：限制执行频率
import { useThrottleFn } from 'ahooks';

const ScrollHandler = () => {
  const { run: handleScroll } = useThrottleFn(
    () => {
      // 处理滚动
      updatePosition();
    },
    { wait: 100 }
  );

  return <div onScroll={handleScroll} />;
};
```

### 图片优化

```typescript
// ✅ 使用懒加载
const Image = lazy(() => import('next/image'));

<img
  src="/avatar.jpg"
  loading="lazy"
  alt="Avatar"
  width={200}
  height={200}
/>

// ✅ 使用 WebP 格式
<picture>
  <source srcSet="/avatar.webp" type="image/webp" />
  <source srcSet="/avatar.jpg" type="image/jpeg" />
  <img src="/avatar.jpg" alt="Avatar" />
</picture>
```

### 状态管理优化

```typescript
// ✅ 使用 React Query 缓存数据
import { useQuery } from '@tanstack/react-query';

const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
    staleTime: 5 * 60 * 1000,  // 5 分钟内数据视为新鲜
    cacheTime: 10 * 60 * 1000,  // 缓存 10 分钟
  });
};

// ✅ 使用 Pagination 减少数据量
const useUsers = (page: number, size: number) => {
  return useQuery({
    queryKey: ['users', page, size],
    queryFn: () => fetchUsers({ page, size }),
  });
};
```

### 打包优化

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'antd-vendor': ['antd', '@ant-design/icons'],
          'chart-vendor': ['echarts'],
        },
      },
    },
    // 压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
});
```

## 数据库优化

### 索引优化

```sql
-- 添加索引
CREATE INDEX idx_admin_username ON fa_admin_admins(username);
CREATE INDEX idx_admin_status ON fa_admin_admins(status);
CREATE INDEX idx_admin_email ON fa_admin_admins(email);

-- 复合索引（注意列顺序）
CREATE INDEX idx_admin_status_created ON fa_admin_admins(status, created_at);

-- 覆盖索引（包含查询所需的所有列）
CREATE INDEX idx_admin_cover ON fa_admin_admins(status, username, name);
```

### 查询优化

```sql
-- ✅ 使用覆盖索引
SELECT id, username, name
FROM fa_admin_admins
WHERE status = 1
ORDER BY created_at DESC
LIMIT 10;

-- ✅ 避免 SELECT *
SELECT id, username, name
FROM fa_admin_admins
WHERE status = 1;

-- ✅ 使用 EXISTS 代替 IN
SELECT a.id, a.username
FROM fa_admin_admins a
WHERE EXISTS (
    SELECT 1 FROM fa_admin_group_members g
    WHERE g.admin_id = a.id
    AND g.group_id = 1
);

-- ✅ 使用 UNION ALL 代替 UNION（去重）
SELECT username FROM admins_a
UNION ALL
SELECT username FROM admins_b;
```

### 表结构优化

```sql
-- ✅ 选择合适的数据类型
ALTER TABLE fa_admin_admins
MODIFY COLUMN status TINYINT NOT NULL DEFAULT 1;

-- ✅ 添加默认值
ALTER TABLE fa_admin_admins
MODIFY COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- ✅ 使用 ENUM 代替字符串
ALTER TABLE fa_admin_admins
MODIFY COLUMN status ENUM('active', 'inactive', 'deleted') NOT NULL;
```

## 缓存优化

### Redis 缓存策略

```python
# 多级缓存策略
async def get_admin_with_cache(admin_id: int):
    """多级缓存获取管理员"""
    # L1: 应用内存缓存
    if admin := memory_cache.get(f"admin:{admin_id}"):
        return admin

    # L2: Redis 缓存
    key = f"admin:{admin_id}"
    if cached := await redis.get(key):
        admin = AdminModel.parse_raw(cached)
        memory_cache.set(key, admin, ttl=60)
        return admin

    # L3: 数据库
    admin = await db.get(AdminModel, admin_id)
    if admin:
        # 回写缓存
        await redis.setex(key, 3600, admin.json())
        memory_cache.set(key, admin, ttl=60)
    return admin
```

### 缓存预热

```python
async def warmup_cache():
    """缓存预热"""
    # 预加载热点数据
    admins = await db.execute(
        select(AdminModel)
        .where(AdminModel.status == 1)
        .limit(1000)
    )

    pipe = redis.pipeline()
    for admin in admins.scalars():
        key = f"admin:{admin.id}"
        pipe.setex(key, 3600, admin.json())
    await pipe.execute()
```

### 缓存更新

```python
async def update_admin(admin_id: int, data: dict):
    """更新管理员并刷新缓存"""
    # 更新数据库
    await db.execute(
        update(AdminModel)
        .where(AdminModel.id == admin_id)
        .values(**data)
    )

    # 删除缓存
    await redis.delete(f"admin:{admin_id}")

    # 或更新缓存
    admin = await db.get(AdminModel, admin_id)
    await redis.setex(f"admin:{admin_id}", 3600, admin.json())
```

## 监控和调优

### 性能监控

```python
# 添加性能监控装饰器
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start
            logger.info(
                f"Function {func.__name__} executed in {duration:.3f}s"
            )
            # 记录到监控系统
            metrics.record_timing(func.__name__, duration)
    return wrapper

# 使用
@monitor_performance
async def get_admin_list():
    pass
```

### 慢查询日志

```python
# 记录慢查询
from sqlalchemy import event

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
):
    context._query_start_time = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
):
    total = time.perf_counter() - context._query_start_time
    if total > 0.1:  # 超过 100ms
        logger.warning(f"Slow query ({total:.3f}s): {statement}")
```

### 性能分析工具

```bash
# 使用 py-spy 进行性能分析
pip install py-spy

# 监控运行中的进程
py-spy top --pid <PID>

# 生成火焰图
py-spy record --pid <PID> --output profile.svg

# 使用 memory_profiler 分析内存
pip install memory_profiler

# 分析函数内存使用
python -m memory_profiler script.py
```

## 性能检查清单

### 后端检查

- [ ] 使用异步 I/O
- [ ] 避免阻塞操作
- [ ] 并行执行独立任务
- [ ] 使用数据库索引
- [ ] 避免 N+1 查询
- [ ] 只查询需要的字段
- [ ] 使用批量操作
- [ ] 配置连接池
- [ ] 使用缓存
- [ ] 压缩响应数据

### 前端检查

- [ ] 代码分割和懒加载
- [ ] 使用虚拟列表
- [ ] 防抖和节流
- [ ] 图片懒加载
- [ ] 使用 React.memo
- [ ] 缓存计算结果
- [ ] 优化重渲染
- [ ] 使用 CDN
- [ ] 启用 Gzip 压缩
- [ ] 减少包大小

### 数据库检查

- [ ] 添加必要索引
- [ ] 优化慢查询
- [ ] 使用合适的数据类型
- [ ] 定期清理过期数据
- [ ] 分析查询计划
- [ ] 配置合理的缓存
- [ ] 定期维护索引
- [ ] 监控数据库性能