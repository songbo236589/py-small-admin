# 设计模式应用

本文档介绍 Py Small Admin 中使用的设计模式。

## 概述

设计模式是解决常见软件设计问题的可重用解决方案。Py Small Admin 在多个层面应用了多种设计模式，提高了代码的可维护性、可扩展性和可重用性。

## 使用的设计模式

### 1. MVC 模式 (Model-View-Controller)

#### 描述

MVC 模式将应用程序分为三个核心部分：模型（Model）、视图（View）和控制器（Controller）。

#### 在项目中的应用

```
Model (模型层)      → 数据模型和业务逻辑
View (路由层)        → API 接口定义
Controller (控制器层) → 请求处理和业务协调
```

#### 示例

```python
# Model
class AdminAdmin(BaseTableModel, table=True):
    username: str
    password: str

# View (Routes)
router.get("/index")(controller.index)

# Controller
class AdminController:
    async def index(self, page: int):
        return await self.admin_service.index({"page": page})
```

#### 优势

- **职责分离**: 每个部分有明确的职责
- **易于维护**: 修改某一部分不影响其他部分
- **可重用**: 模型可以在多个视图中使用

### 2. 服务层模式 (Service Layer Pattern)

#### 描述

服务层模式将业务逻辑从控制器和模型中分离出来，形成一个独立的服务层。

#### 在项目中的应用

```python
# 服务层
class AdminService(BaseService):
    async def add(self, data: dict):
        # 业务逻辑
        pass

# 控制器调用服务
class AdminController:
    def __init__(self):
        self.admin_service = AdminService()

    async def add(self, data):
        return await self.admin_service.add(data)
```

#### 优势

- **业务逻辑集中**: 所有业务逻辑在服务层
- **可重用**: 服务方法可被多个控制器调用
- **易于测试**: 可以单独测试业务逻辑

### 3. 仓储模式 (Repository Pattern)

#### 描述

仓储模式将数据访问逻辑封装在仓储类中，提供类似集合的接口来访问数据。

#### 在项目中的应用

```python
# BaseService 作为基础仓储
class BaseService:
    async def common_add(self, data, model_class):
        # 通用的添加逻辑
        pass

    async def common_update(self, id, data, model_class):
        # 通用的更新逻辑
        pass

    async def common_destroy(self, id, model_class):
        # 通用的删除逻辑
        pass
```

#### 优势

- **数据访问封装**: 数据库操作封装在服务层
- **易于切换**: 可以轻松切换数据源
- **代码复用**: 通用的 CRUD 操作可复用

### 4. 工厂模式 (Factory Pattern)

#### 描述

工厂模式提供创建对象的接口，让子类决定实例化哪个类。

#### 在项目中的应用

```python
# 配置工厂
class ConfigRegistry:
    @classmethod
    def load(cls):
        # 加载配置
        pass

# 使用配置
ConfigRegistry.load()
Config.get("app.name")
```

#### 优势

- **解耦**: 客户端不需要知道具体实现
- **扩展性**: 易于添加新的配置类型
- **统一管理**: 集中管理配置实例

### 5. 单例模式 (Singleton Pattern)

#### 描述

单例模式确保一个类只有一个实例，并提供全局访问点。

#### 在项目中的应用

```python
# 配置单例
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# 使用
config = Config()
```

#### 优势

- **资源节约**: 避免重复创建实例
- **全局访问**: 提供全局访问点
- **一致性**: 确保使用同一个实例

### 6. 策略模式 (Strategy Pattern)

#### 描述

策略模式定义一系列算法，将每个算法封装起来，并使它们可以互换。

#### 在项目中的应用

```python
# 密码加密策略
class PasswordService:
    def __init__(self, algorithm: str = "bcrypt"):
        self.algorithm = algorithm

    def hash_password(self, password: str) -> str:
        if self.algorithm == "bcrypt":
            return self._bcrypt_hash(password)
        elif self.algorithm == "pbkdf2":
            return self._pbkdf2_hash(password)
```

#### 优势

- **算法可替换**: 可以轻松切换加密算法
- **扩展性**: 易于添加新的加密算法
- **代码清晰**: 每个算法独立实现

### 7. 装饰器模式 (Decorator Pattern)

#### 描述

装饰器模式动态地给对象添加额外的职责。

#### 在项目中的应用

```python
# 参数验证装饰器
def validate_request_data(request_model):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 验证逻辑
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 使用
@validate_request_data(AdminAddRequest)
async def add(self, username: str, password: str):
    pass
```

#### 优势

- **功能扩展**: 动态添加功能
- **代码复用**: 装饰器可复用
- **代码简洁**: 减少重复代码

### 8. 观察者模式 (Observer Pattern)

#### 描述

观察者模式定义对象间的一对多依赖关系，当一个对象改变状态时，所有依赖它的对象都会收到通知。

#### 在项目中的应用

```python
# 事件系统
class EventManager:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def notify(self, event_type, data):
        for listener in self.listeners.get(event_type, []):
            listener(data)
```

#### 优势

- **松耦合**: 观察者和被观察者松耦合
- **扩展性**: 易于添加新的观察者
- **实时性**: 实时通知状态变化

### 9. 依赖注入模式 (Dependency Injection)

#### 描述

依赖注入模式将依赖对象的创建和使用分离，通过构造函数或方法注入依赖。

#### 在项目中的应用

```python
# 控制器依赖注入
class AdminController:
    def __init__(self):
        self.admin_service = AdminService()

    async def add(self, data):
        return await self.admin_service.add(data)
```

#### 优势

- **松耦合**: 降低组件间的耦合
- **易于测试**: 可以注入模拟对象进行测试
- **灵活性**: 可以轻松替换实现

### 10. 模板方法模式 (Template Method Pattern)

#### 描述

模板方法模式在基类中定义算法的骨架，将某些步骤延迟到子类中实现。

#### 在项目中的应用

```python
# BaseService 提供模板方法
class BaseService:
    async def common_add(self, data, model_class, pre_operation_callback=None):
        # 模板方法
        if pre_operation_callback:
            pre_result = await pre_operation_callback(data, session)
            if isinstance(pre_result, JSONResponse):
                return pre_result
            data, session = pre_result

        # 创建实例
        instance = model_class(**data)
        session.add(instance)
        await session.commit()

        return success(None)

# 子类使用模板方法
class AdminService(BaseService):
    async def add(self, data):
        return await self.common_add(
            data=data,
            model_class=AdminAdmin,
            pre_operation_callback=self._pre_add,
        )

    async def _pre_add(self, data, session):
        # 自定义前置操作
        return data, session
```

#### 优势

- **代码复用**: 通用逻辑在基类中实现
- **灵活性**: 子类可以自定义某些步骤
- **一致性**: 确保算法结构一致

## 设计原则

### 1. 单一职责原则 (Single Responsibility Principle)

一个类应该只有一个引起它变化的原因。

**示例**：

```python
# ✅ 好的设计
class AdminService:
    """只负责管理员业务逻辑"""
    pass

class PasswordService:
    """只负责密码处理"""
    pass

# ❌ 不好的设计
class AdminService:
    """负责太多职责"""
    def add_admin(self): pass
    def hash_password(self): pass
    def send_email(self): pass
```

### 2. 开闭原则 (Open/Closed Principle)

软件实体应该对扩展开放，对修改关闭。

**示例**：

```python
# ✅ 好的设计 - 使用策略模式
class PasswordService:
    def hash_password(self, password, algorithm="bcrypt"):
        if algorithm == "bcrypt":
            return self._bcrypt_hash(password)
        # 可以轻松添加新的算法

# ❌ 不好的设计 - 需要修改代码
class PasswordService:
    def hash_password(self, password):
        # 添加新算法需要修改这里
        pass
```

### 3. 里氏替换原则 (Liskov Substitution Principle)

子类必须能够替换父类而不影响程序的正确性。

**示例**：

```python
# ✅ 好的设计
class BaseService:
    async def common_add(self, data, model_class):
        pass

class AdminService(BaseService):
    # 可以替换 BaseService
    pass

# ❌ 不好的设计
class AdminService(BaseService):
    async def common_add(self, data, model_class):
        # 改变了基类行为
        raise NotImplementedError()
```

### 4. 接口隔离原则 (Interface Segregation Principle)

客户端不应该依赖它不需要的接口。

**示例**：

```python
# ✅ 好的设计 - 小而专一的接口
class Addable:
    async def add(self, data): pass

class Updatable:
    async def update(self, id, data): pass

class Deletable:
    async def delete(self, id): pass

# ❌ 不好的设计 - 臃肿的接口
class CRUD:
    async def add(self, data): pass
    async def update(self, id, data): pass
    async def delete(self, id): pass
    async def search(self, query): pass
    async def export(self, data): pass
```

### 5. 依赖倒置原则 (Dependency Inversion Principle)

高层模块不应该依赖低层模块，两者都应该依赖抽象。

**示例**：

```python
# ✅ 好的设计 - 依赖抽象
class AdminController:
    def __init__(self, admin_service: AdminService):
        self.admin_service = admin_service

# ❌ 不好的设计 - 依赖具体实现
class AdminController:
    def __init__(self):
        self.admin_service = AdminService()
```

## 最佳实践

### 1. 选择合适的设计模式

不是所有情况都需要使用设计模式，根据实际情况选择。

### 2. 不要过度设计

简单的问题用简单的解决方案，避免过度使用设计模式。

### 3. 保持代码简洁

设计模式应该让代码更清晰，而不是更复杂。

### 4. 遵循项目规范

遵循项目的架构设计和编码规范。

## 常见问题

### 1. 什么时候使用设计模式？

**答案**：

- 当遇到常见问题时，考虑使用相应的设计模式
- 当代码变得复杂时，考虑使用设计模式简化
- 当需要提高代码复用性时，考虑使用设计模式

### 2. 如何选择合适的设计模式？

**答案**：

- 了解各种设计模式的适用场景
- 根据具体问题选择最合适的设计模式
- 参考类似问题的解决方案

### 3. 设计模式会增加代码量吗？

**答案**：

- 短期来看，可能会增加一些代码
- 长期来看，会减少重复代码，提高可维护性

## 相关链接

- [架构概览](./architecture-overview.md)
- [分层架构说明](./layered-architecture.md)
- [最佳实践](./best-practices.md)
- [服务层开发指南](../server/api-development/service-guide.md)

---

通过理解设计模式，您可以编写更好的代码。
