# 测试指南

本文档介绍了 Py Small Admin 的测试最佳实践，帮助您编写高质量的测试代码。

## 目录

- [测试概述](#测试概述)
- [后端测试](#后端测试)
- [前端测试](#前端测试)
- [集成测试](#集成测试)
- [端到端测试](#端到端测试)
- [测试覆盖率](#测试覆盖率)

## 测试概述

### 测试金字塔

```
         /\
        /  \      E2E Tests (少量)
       /----\
      /      \    Integration Tests (适量)
     /--------\
    /          \  Unit Tests (大量)
   /____________\
```

| 测试类型 | 数量 | 速度 | 成本 | 目的 |
|---------|------|------|------|------|
| 单元测试 | 多 | 快 | 低 | 验证单个函数/类的正确性 |
| 集成测试 | 中 | 中 | 中 | 验证模块间交互的正确性 |
| E2E测试 | 少 | 慢 | 高 | 验证用户场景的正确性 |

### 测试原则

1. **测试先行**：先写测试，再写代码 (TDD)
2. **独立性**：每个测试应该独立运行
3. **可重复性**：测试结果应该一致
4. **可读性**：测试代码应该易于理解
5. **快速反馈**：测试应该快速执行

## 后端测试

### 单元测试

使用 pytest 编写单元测试。

#### 安装依赖

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

#### 项目结构

```
server/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest 配置和 fixtures
│   ├── unit/                 # 单元测试
│   │   ├── test_services/
│   │   │   ├── test_auth_service.py
│   │   │   └── test_admin_service.py
│   │   └── test_utils/
│   │       └── test_password.py
│   ├── integration/          # 集成测试
│   │   ├── test_api/
│   │   │   ├── test_auth_api.py
│   │   │   └── test_admin_api.py
│   │   └── test_database/
│   │       └── test_repository.py
│   └── e2e/                  # 端到端测试
│       └── test_scenarios.py
```

#### pytest 配置

创建 `pytest.ini`：

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --strict-markers
    --cov=Modules
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End to end tests
    slow: Slow running tests
```

#### conftest.py 配置

```python
# tests/conftest.py
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from Modules.main import app
from config.database import Base, get_db


# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator:
    """创建测试数据库会话"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator:
    """创建测试客户端"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis"""
    return MagicMock()


@pytest.fixture
def mock_celery():
    """Mock Celery"""
    return MagicMock()
```

#### 编写单元测试

```python
# tests/unit/test_services/test_auth_service.py
import pytest
from unittest.mock import AsyncMock, patch

from Modules.admin.services.auth_service import AuthService


class TestAuthService:
    """测试 AuthService"""

    @pytest.fixture
    def auth_service(self, db_session, mock_redis):
        """创建 AuthService 实例"""
        return AuthService(db_session, mock_redis)

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service):
        """测试登录成功"""
        # Arrange
        login_data = {
            "username": "admin",
            "password": "admin123",
            "captcha": "1234",
            "captcha_id": "test_captcha_id"
        }

        with patch('Modules.admin.services.auth_service.CaptchaService') as mock_captcha:
            mock_captcha.return_value.verify_captcha = AsyncMock(return_value=True)

            with patch.object(auth_service, '_verify_password', return_value=True):
                with patch.object(auth_service, '_generate_tokens', return_value=("access_token", "refresh_token")):
                    # Act
                    result = await auth_service.login(login_data)

                    # Assert
                    assert result["code"] == 200
                    assert "access_token" in result["data"]
                    assert "refresh_token" in result["data"]

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_service):
        """测试登录失败 - 无效凭据"""
        # Arrange
        login_data = {
            "username": "admin",
            "password": "wrong_password",
            "captcha": "1234",
            "captcha_id": "test_captcha_id"
        }

        with patch('Modules.admin.services.auth_service.CaptchaService') as mock_captcha:
            mock_captcha.return_value.verify_captcha = AsyncMock(return_value=True)

            with patch.object(auth_service, '_verify_password', return_value=False):
                # Act
                result = await auth_service.login(login_data)

                # Assert
                assert result["code"] == 400
                assert "用户名或密码错误" in result["message"]

    @pytest.mark.asyncio
    async def test_login_invalid_captcha(self, auth_service):
        """测试登录失败 - 验证码错误"""
        # Arrange
        login_data = {
            "username": "admin",
            "password": "admin123",
            "captcha": "wrong_captcha",
            "captcha_id": "test_captcha_id"
        }

        with patch('Modules.admin.services.auth_service.CaptchaService') as mock_captcha:
            mock_captcha.return_value.verify_captcha = AsyncMock(return_value=False)

            # Act
            result = await auth_service.login(login_data)

            # Assert
            assert result["code"] == 400
            assert "验证码错误" in result["message"]
```

### 集成测试

```python
# tests/integration/test_api/test_auth_api.py
import pytest


class TestAuthAPI:
    """测试认证 API"""

    @pytest.mark.asyncio
    async def test_generate_captcha(self, client: AsyncClient):
        """测试生成验证码"""
        # Act
        response = await client.post("/api/admin/common/generate_captcha")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "captcha_id" in data["data"]
        assert "image" in data["data"]

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """测试登录成功"""
        # 先创建测试用户
        # ...

        # 获取验证码
        captcha_response = await client.post("/api/admin/common/generate_captcha")
        captcha_data = captcha_response.json()["data"]

        # Act
        login_response = await client.post(
            "/api/admin/common/login",
            data={
                "username": "admin",
                "password": "admin123",
                "captcha": "1234",
                "captcha_id": captcha_data["captcha_id"]
            }
        )

        # Assert
        assert login_response.status_code == 200
        data = login_response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client: AsyncClient):
        """测试登录 - 缺少必填字段"""
        # Act
        response = await client.post(
            "/api/admin/common/login",
            data={"username": "admin"}
        )

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """测试访问受保护端点 - 无令牌"""
        # Act
        response = await client.get("/api/admin/admin/index")

        # Assert
        assert response.status_code == 401
```

### Mock 和 Patch

使用 mock 对象隔离依赖：

```python
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_with_mock():
    """使用 mock 测试"""
    # 创建 mock 对象
    mock_service = AsyncMock()
    mock_service.get_user.return_value = {
        "id": 1,
        "username": "admin"
    }

    # 使用 patch
    with patch('Modules.admin.services.auth_service.SomeService', return_value=mock_service):
        # 测试代码
        result = await mock_service.get_user(1)
        assert result["username"] == "admin"

    # 验证 mock 被调用
    mock_service.get_user.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_with_patch():
    """使用 patch 测试"""
    with patch('Modules.admin.services.redis_service.redis') as mock_redis:
        mock_redis.get.return_value = b"cached_value"

        # 测试代码
        result = await some_function_using_redis()

        # 验证
        mock_redis.get.assert_called_once()
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行特定文件
pytest tests/unit/test_services/test_auth_service.py

# 运行特定测试
pytest tests/unit/test_services/test_auth_service.py::TestAuthService::test_login_success

# 显示详细输出
pytest -v

# 显示测试覆盖率
pytest --cov=Modules --cov-report=html

# 运行标记为 slow 的测试
pytest -m slow

# 并行运行测试（需要 pytest-xdist）
pytest -n auto
```

## 前端测试

### 单元测试

使用 Jest + React Testing Library。

#### 安装依赖

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

#### Jest 配置

创建 `jest.config.js`：

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
  ],
  coverageThresholds: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```

#### setupTests.js

```javascript
// src/setupTests.js
import '@testing-library/jest-dom';

// Mock browser APIs
global.matchMedia = jest.fn((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: jest.fn(),
  removeListener: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;
```

#### 编写组件测试

```typescript
// src/pages/Login/__tests__/index.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../index';

// Mock API
jest.mock('@/services/login', () => ({
  login: jest.fn(),
}));

// Mock router
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Login Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
  };

  test('renders login form', () => {
    renderLogin();

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('shows validation errors for empty fields', async () => {
    const user = userEvent.setup();
    renderLogin();

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  test('submits form with valid data', async () => {
    const user = userEvent.setup();
    const { login } = require('@/services/login');
    login.mockResolvedValue({ success: true, token: 'test-token' });

    renderLogin();

    await user.type(screen.getByLabelText(/username/i), 'admin');
    await user.type(screen.getByLabelText(/password/i), 'admin123');

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith({
        username: 'admin',
        password: 'admin123',
      });
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('shows error message on login failure', async () => {
    const user = userEvent.setup();
    const { login } = require('@/services/login');
    login.mockRejectedValue(new Error('Invalid credentials'));

    renderLogin();

    await user.type(screen.getByLabelText(/username/i), 'admin');
    await user.type(screen.getByLabelText(/password/i), 'wrong');

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
```

#### Hook 测试

```typescript
// src/hooks/useRequest/__tests__/index.test.ts
import { renderHook, act } from '@testing-library/react';
import { useRequest } from '../index';

describe('useRequest', () => {
  test('initial state', () => {
    const { result } = renderHook(() => useRequest());
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });

  test('successful request', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockRequest = jest.fn().mockResolvedValue(mockData);

    const { result } = renderHook(() => useRequest(mockRequest));

    await act(async () => {
      await result.current.run();
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
  });

  test('failed request', async () => {
    const mockError = new Error('Request failed');
    const mockRequest = jest.fn().mockRejectedValue(mockError);

    const { result } = renderHook(() => useRequest(mockRequest));

    await act(async () => {
      await result.current.run();
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toEqual(mockError);
  });
});
```

#### 运行测试

```bash
# 运行所有测试
npm test

# 运行特定文件
npm test Login

# 运行测试并生成覆盖率报告
npm test -- --coverage

# 监听模式
npm test -- --watch

# 更新快照
npm test -- -u
```

### 组件集成测试

```typescript
// src/pages/Admin/__tests__/AdminList.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import AdminList from '../AdminList';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

describe('AdminList Integration', () => {
  test('fetches and displays admins', async () => {
    const queryClient = createTestQueryClient();

    // Mock API response
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            code: 200,
            data: {
              items: [
                { id: 1, name: 'Admin 1', username: 'admin1' },
                { id: 2, name: 'Admin 2', username: 'admin2' },
              ],
              total: 2,
            },
          }),
      })
    ) as jest.Mock;

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AdminList />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Admin 1')).toBeInTheDocument();
      expect(screen.getByText('Admin 2')).toBeInTheDocument();
    });
  });
});
```

## 端到端测试

使用 Playwright 进行 E2E 测试。

### 安装

```bash
npm install --save-dev @playwright/test
```

### 配置

创建 `playwright.config.ts`：

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:8000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E 测试示例

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    await expect(page.locator('input[type="text"]').first()).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.fill('input[type="text"]', 'invalid-user');
    await page.fill('input[type="password"]', 'wrong-password');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=用户名或密码错误')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');

    // Wait for captcha and solve it (mock in test environment)
    const captchaImage = page.locator('img[alt*="验证码"]');
    await expect(captchaImage).toBeVisible();

    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=欢迎')).toBeVisible();
  });

  test('should logout and redirect to login', async ({ page }) => {
    // Login first
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('text=退出登录');

    // Should redirect to login
    await expect(page).toHaveURL('/login');
  });
});

// e2e/admin.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Admin Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should display admin list', async ({ page }) => {
    await page.goto('/admin/auth/admin');
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('tr').nth(1)).toContainText('超级管理员');
  });

  test('should create new admin', async ({ page }) => {
    await page.goto('/admin/auth/admin');
    await page.click('text=添加');

    await page.fill('input[name="name"]', 'Test Admin');
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'Test123456');
    await page.fill('input[name="phone"]', '13800138000');

    await page.click('button:has-text("确定")');

    // Should show success message
    await expect(page.locator('text=添加成功')).toBeVisible();
  });

  test('should edit admin', async ({ page }) => {
    await page.goto('/admin/auth/admin');
    await page.click('tr:nth-child(2) button:has-text("编辑")');

    await page.fill('input[name="name"]', 'Updated Admin');
    await page.click('button:has-text("确定")');

    await expect(page.locator('text=更新成功')).toBeVisible();
    await expect(page.locator('text=Updated Admin')).toBeVisible();
  });

  test('should delete admin', async ({ page }) => {
    await page.goto('/admin/auth/admin');
    const initialCount = await page.locator('table tbody tr').count();

    await page.click('tr:nth-child(2) button:has-text("删除")');
    await page.click('button:has-text("确定")');

    await expect(page.locator('text=删除成功')).toBeVisible();
    const finalCount = await page.locator('table tbody tr').count();
    expect(finalCount).toBe(initialCount - 1);
  });
});
```

### 运行 E2E 测试

```bash
# 运行所有测试
npx playwright test

# 运行特定文件
npx playwright test admin.spec.ts

# 调试模式
npx playwright test --debug

# 显示浏览器
npx playwright test --headed

# 生成测试报告
npx playwright show-report
```

## 测试覆盖率

### 后端覆盖率

```bash
# 生成覆盖率报告
pytest --cov=Modules --cov-report=html

# 在浏览器中查看
open htmlcov/index.html
```

### 前端覆盖率

```bash
# 生成覆盖率报告
npm test -- --coverage

# 在浏览器中查看
open coverage/lcov-report/index.html
```

### 覆盖率目标

| 类型 | 目标 |
|------|------|
| 语句覆盖率 | ≥ 80% |
| 分支覆盖率 | ≥ 75% |
| 函数覆盖率 | ≥ 80% |
| 行覆盖率 | ≥ 80% |

## 测试最佳实践

### 后端测试

1. **每个测试只验证一件事**
2. **使用描述性的测试名称**
3. **遵循 AAA 模式**：Arrange, Act, Assert
4. **Mock 外部依赖**
5. **测试边界条件**
6. **测试错误路径**

### 前端测试

1. **测试用户行为，不是实现细节**
2. **使用 data-testid 选择器**
3. **避免测试样式**
4. **Mock API 调用**
5. **测试可访问性**

### E2E 测试

1. **只测试关键用户流程**
2. **保持测试稳定**
3. **使用等待策略**
4. **避免硬编码延迟**
5. **清理测试数据**

## 持续集成

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd server
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: |
          cd server
          pytest --cov=Modules --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd admin-web
          npm ci
      - name: Run tests
        run: |
          cd admin-web
          npm test -- --coverage --watchAll=false
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd admin-web
          npm ci
          npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd admin-web
          npm run build
          npx playwright test
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: admin-web/playwright-report/
```