# 代码规范

本文档介绍了 Py Small Admin 的代码规范，帮助团队保持代码一致性和可维护性。

## 目录

- [通用规范](#通用规范)
- [后端代码规范](#后端代码规范)
- [前端代码规范](#前端代码规范)
- [Git 规范](#git-规范)
- [文档规范](#文档规范)

## 通用规范

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | 小写下划线 | `admin_service.py`, `user_controller.ts` |
| 变量名 | 小写下划线 (Python) / 小驼峰 (JS/TS) | `user_name`, `userName` |
| 常量名 | 大写下划线 | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| 函数名 | 小写下划线 (Python) / 小驼峰 (JS/TS) | `get_user()`, `getUser()` |
| 类名 | 大驼峰 | `UserService`, `UserService` |
| 私有成员 | 下划线前缀 (Python) | `_private_method` |

### 注释规范

#### 文件注释

```python
# -*- coding: utf-8 -*-
"""
管理员服务模块

本模块提供管理员相关的业务逻辑处理，包括：
- 管理员列表查询
- 管理员创建和更新
- 管理员删除和状态管理

Author: Your Name
Created: 2024-01-01
"""
```

```typescript
/**
 * 管理员服务类
 *
 * 提供管理员相关的业务逻辑处理
 *
 * @module services/admin
 * @author Your Name
 * @created 2024-01-01
 */
```

#### 函数注释

```python
async def get_admin_by_id(
    db: AsyncSession,
    admin_id: int
) -> Optional[AdminModel]:
    """
    根据 ID 获取管理员信息

    Args:
        db: 数据库会话
        admin_id: 管理员 ID

    Returns:
        管理员模型对象，不存在时返回 None

    Raises:
        ValueError: 当 admin_id 无效时

    Example:
        >>> admin = await get_admin_by_id(db, 1)
        >>> if admin:
        ...     print(admin.username)
    """
    pass
```

```typescript
/**
 * 根据 ID 获取管理员信息
 *
 * @param id - 管理员 ID
 * @param options - 请求选项
 * @returns 管理员信息
 *
 * @example
 * ```typescript
 * const admin = await getAdminById(1);
 * console.log(admin.username);
 * ```
 */
async function getAdminById(
  id: number,
  options?: RequestOptions
): Promise<Admin | null> {
  // ...
}
```

### 代码格式化

#### 最大行宽

- Python: 120 字符
- TypeScript: 100 字符

#### 缩进

- 统一使用 2 个空格（TypeScript）
- 统一使用 4 个空格（Python）

#### 空行

- 函数之间：2 行
- 类之间：2 行
- 逻辑块之间：1 行

## 后端代码规范

### Python 代码规范 (PEP 8)

#### 使用 Ruff 进行代码检查

项目使用 Ruff 进行代码格式化和检查：

```bash
# 安装 Ruff
pip install ruff

# 检查代码
ruff check .

# 自动修复
ruff check --fix .

# 格式化代码
ruff format .
```

#### Ruff 配置

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.lint.isort]
known-first-party = ["Modules", "config"]
```

### 导入顺序

```python
# 1. 标准库导入
import asyncio
from datetime import datetime
from typing import Optional

# 2. 第三方库导入
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# 3. 本地应用导入
from Modules.admin.models import AdminModel
from config.constants import ErrorMessages
```

### 类型注解

所有函数都应该有类型注解：

```python
# ✅ 正确
async def get_user(
    user_id: int,
    include_deleted: bool = False
) -> Optional[UserModel]:
    pass

# ❌ 错误
async def get_user(user_id, include_deleted=False):
    pass
```

### 异常处理

```python
# ✅ 正确：捕获具体异常
try:
    result = await database.execute(query)
except IntegrityError as e:
    logger.error(f"Database integrity error: {e}")
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Resource already exists"
    )

# ❌ 错误：捕获所有异常
try:
    result = await database.execute(query)
except Exception:
    pass
```

### 日志记录

```python
from loguru import logger

# ✅ 正确：使用适当的日志级别
logger.debug("Debug information")
logger.info("User logged in", extra={"user_id": user.id})
logger.warning("High memory usage", extra={"usage": "90%"})
logger.error("Database connection failed", exc_info=True)

# ❌ 错误：使用 print
print("Something happened")
```

### 数据库操作

```python
# ✅ 正确：使用上下文管理器
async with AsyncSession(db_engine) as session:
    async with session.begin():
        result = await session.execute(select(AdminModel))
        admins = result.scalars().all()

# ❌ 错误：忘记关闭会话
session = AsyncSession(db_engine)
result = await session.execute(select(AdminModel))
```

### 字符串格式化

```python
# ✅ 推荐：f-string
name = "Alice"
greeting = f"Hello, {name}!"

# ✅ 可接受：format()
greeting = "Hello, {}!".format(name)

# ❌ 不推荐：% 格式化
greeting = "Hello, %s!" % name
```

### 列表推导式

```python
# ✅ 正确：简单推导式
names = [user.name for user in users if user.active]

# ✅ 正确：复杂情况使用生成器表达式
total = sum(
    order.amount
    for order in orders
    if order.status == "completed"
)

# ❌ 错误：过于复杂的推导式
result = [
    (x, y, z)
    for x in range(10)
    for y in range(10)
    if x > y
    for z in range(10)
    if y > z
]
```

### 类定义

```python
class UserService:
    """用户服务类"""

    def __init__(self, db: AsyncSession, redis: Redis):
        """初始化服务"""
        self.db = db
        self.redis = redis

    async def get_user(self, user_id: int) -> Optional[UserModel]:
        """获取用户"""
        pass

    async def create_user(self, user_data: UserCreate) -> UserModel:
        """创建用户"""
        pass

    async def _hash_password(self, password: str) -> str:
        """私有方法：哈希密码"""
        pass
```

## 前端代码规范

### TypeScript 代码规范

#### 使用 Biome 进行代码检查

项目使用 Biome 进行代码格式化和检查：

```bash
# 安装 Biome
npm install --save-dev @biomejs/biome

# 检查代码
npx @biomejs/biome check .

# 自动修复
npx @biomejs/biome check --write .

# 格式化代码
npx @biomejs/biome format --write .
```

#### Biome 配置

```json
{
  "linter": {
    "recommended": true,
    "rules": {
      "style": {
        "noNonNullAssertion": "error",
        "useConst": "error",
        "useTemplate": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      },
      "correctness": {
        "noUnusedVariables": "error"
      }
    }
  },
  "formatter": {
    "indentStyle": "space",
    "lineWidth": 100,
    "indentWidth": 2
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingCommas": "all",
      "semicolons": "always"
    }
  }
}
```

### 变量声明

```typescript
// ✅ 正确：使用 const
const API_URL = 'https://api.example.com';
const config = { timeout: 5000 };

// ✅ 正确：需要重新赋值时使用 let
let count = 0;
count += 1;

// ❌ 错误：不使用 var
var name = 'Alice';

// ❌ 错误：const 重新赋值
const items = [];
items.push(1);  // 应该使用 let
```

### 函数声明

```typescript
// ✅ 推荐：箭头函数
const getUser = async (id: number): Promise<User> => {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
};

// ✅ 可接受：函数声明
async function getUser(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// ❌ 错误：使用 any
const getUser = async (id): Promise<any> => {
  // ...
};
```

### 组件定义

```typescript
// ✅ 正确：函数组件 + Hooks
interface UserListProps {
  users: User[];
  onUserClick: (user: User) => void;
}

const UserList: React.FC<UserListProps> = ({ users, onUserClick }) => {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  return (
    <ul>
      {users.map(user => (
        <li key={user.id} onClick={() => onUserClick(user)}>
          {user.name}
        </li>
      ))}
    </ul>
  );
};

export default UserList;
```

### Hooks 使用

```typescript
// ✅ 正确：使用自定义 Hook
const useUser = (id: number) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(id).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [id]);

  return { user, loading };
};

// ✅ 正确：使用 Hook
function UserProfile({ userId }: { userId: number }) {
  const { user, loading } = useUser(userId);

  if (loading) return <div>Loading...</div>;
  return <div>{user?.name}</div>;
}

// ❌ 错误：在条件语句中使用 Hook
function BadComponent({ condition }: { condition: boolean }) {
  if (condition) {
    const [state, setState] = useState(null);  // 错误！
  }
}
```

### 类型定义

```typescript
// ✅ 正确：使用 interface 定义对象类型
interface User {
  id: number;
  name: string;
  email: string;
  createdAt: Date;
}

// ✅ 正确：使用 type 定义联合类型
type Status = 'pending' | 'active' | 'inactive';

// ✅ 正确：泛型类型
interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

// ✅ 正解：枚举
enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}
```

### 异步处理

```typescript
// ✅ 正确：使用 async/await
const loadData = async () => {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    setData(data);
  } catch (error) {
    console.error('Failed to load data:', error);
  }
};

// ✅ 正确：Promise 并行处理
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
]);

// ❌ 错误：忽略错误处理
const loadData = async () => {
  const response = await fetch('/api/data');
  const data = await response.json();  // 可能失败
  setData(data);
};
```

### 条件语句

```typescript
// ✅ 推荐：三元运算符（简单条件）
const message = isLoading ? 'Loading...' : 'Done';

// ✅ 推荐：可选链
const city = user?.address?.city ?? 'Unknown';

// ✅ 推荐：空值合并
const name = inputName ?? 'Anonymous';

// ❌ 不推荐：嵌套三元运算符
const result = condition1
  ? value1
  : condition2
    ? value2
    : value3;
```

### 数组操作

```typescript
// ✅ 正确：使用 map
const names = users.map(user => user.name);

// ✅ 正确：使用 filter
const activeUsers = users.filter(user => user.isActive);

// ✅ 正确：使用 reduce
const total = orders.reduce((sum, order) => sum + order.amount, 0);

// ✅ 正确：使用 find
const user = users.find(u => u.id === 1);

// ✅ 正确：使用 some/every
const hasActive = users.some(user => user.isActive);
const allActive = users.every(user => user.isActive);

// ❌ 错误：使用 for 循环进行数组操作
const names = [];
for (const user of users) {
  names.push(user.name);
}
```

### 样式规范

```typescript
// ✅ 推荐：使用 CSS Modules
import styles from './UserList.module.css';

const UserList = () => {
  return <ul className={styles.list}>...</ul>;
};

// ✅ 推荐：使用 Tailwind CSS
const UserList = () => {
  return (
    <ul className="space-y-2">
      ...
    </ul>
  );
};

// ❌ 不推荐：内联样式（复杂样式）
const UserList = () => {
  return (
    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      ...
    </ul>
  );
};
```

## Git 规范

### 分支命名

```
feature/     新功能
  └─ feature/user-management
fix/         修复 Bug
  └─ fix/login-error
hotfix/      紧急修复
  └─ hotfix/security-patch
refactor/    重构
  └─ refactor/admin-service
docs/        文档更新
  └─ docs/api-update
test/        测试相关
  └─ test/add-unit-tests
```

### 提交信息

遵循 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式调整（不影响功能） |
| `refactor` | 重构（既不是新功能也不是修复） |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建过程或辅助工具的变动 |
| `revert` | 回滚之前的提交 |

#### 示例

```bash
# 简单提交
git commit -m "feat(admin): add user management page"

# 详细提交
git commit -m "fix(auth): resolve token expiration issue

- Fix JWT token validation logic
- Add proper error handling for expired tokens
- Update unit tests

Closes #123"
```

### 提交最佳实践

```bash
# ✅ 正确：原子提交
git commit -m "feat(user): add user profile page"

# ✅ 正确：相关修改一起提交
git commit -m "fix(admin): resolve pagination bug and add tests"

# ❌ 错误：过于笼统
git commit -m "update code"

# ❌ 错误：提交不相关的修改
git commit -m "add user feature and fix bug"
```

## 文档规范

### README.md

每个项目/模块应该有清晰的 README：

```markdown
# 项目名称

简短描述项目功能。

## 功能特性

- 特性 1
- 特性 2

## 安装

```bash
npm install
```

## 使用

```typescript
import { Component } from 'package';

// 使用示例
```

## API 文档

详见 [API 文档](./docs/api.md)

## 贡献

欢迎提交 Pull Request。

## 许可证

MIT
```

### API 文档

使用 OpenAPI/Swagger 规范：

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Py Small Admin API",
        version="1.0.0",
        description="后台管理系统 API",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 注释规范

#### 代码注释原则

1. **代码自解释优先**：好的代码不需要过多注释
2. **注释"为什么"而不是"是什么"**
3. **保持注释与代码同步**
4. **避免无意义的注释**

```python
# ✅ 好的注释：解释原因
# 使用缓存减少数据库查询（每个管理员信息基本不变）
@lru_cache(maxsize=128)
async def get_admin_group(group_id: int):
    pass

# ❌ 坏的注释：重复代码
# 设置用户名
username = "admin"

# ❌ 坏的注释：过时的信息
# 这个问题已在 v2.0 中修复
```

## 代码审查清单

### 提交前检查

- [ ] 代码通过 linter 检查
- [ ] 所有测试通过
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有调试代码（console.log、print 等）
- [ ] 没有注释掉的代码
- [ ] 没有添加不必要的依赖

### 审查关注点

1. **正确性**：代码是否正确实现了功能
2. **可读性**：代码是否易于理解
3. **可维护性**：代码是否易于修改和扩展
4. **性能**：是否存在性能问题
5. **安全性**：是否存在安全漏洞
6. **测试**：是否有足够的测试覆盖

## 工具配置

### VS Code 配置

创建 `.vscode/settings.json`：

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.python"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/node_modules": true
  }
}
```

### Pre-commit 钩子

创建 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        types_or: [json, yaml, markdown]
```

安装 hooks：

```bash
pip install pre-commit
pre-commit install
```