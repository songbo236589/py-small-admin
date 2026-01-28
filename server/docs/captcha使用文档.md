# Captcha 模块使用文档

## 概述

`libs/captcha` 模块是一个功能强大的验证码服务库，提供了多种类型的验证码生成和验证功能。该模块支持图片验证码和数学题验证码，具有高度可配置性，并与缓存系统无缝集成，确保验证码的安全性和时效性。

该模块主要包含以下文件：

- `captcha_service.py`: 验证码服务核心类和便捷函数
- `image_generator.py`: 图片验证码生成器
- `utils.py`: 验证码工具函数和类型定义
- `__init__.py`: 模块导出接口
- `config/captcha.py`: 验证码配置类

## 主要功能

- 多种验证码类型支持（图片验证码、数学题验证码）
- 高度可配置的验证码生成参数
- 自动过期管理和一次性使用验证
- 与缓存系统的无缝集成
- 图片扭曲变形和干扰元素
- 类型安全的接口设计
- 统一的错误处理和日志记录

## 安装与导入

```python
from Modules.common.libs.captcha import (
    # 验证码服务类
    CaptchaService,
    get_captcha_service,
    
    # 数据类型
    CaptchaResult,
    
    # 便捷函数
    generate_captcha,
)
```

## 验证码配置

### 基本配置

验证码配置通过 `CaptchaConfig` 类管理，支持环境变量配置：

```python
from config.captcha import CaptchaConfig

# 获取验证码配置
config = CaptchaConfig()
print(config.length)  # 验证码长度，默认为4
print(config.width)   # 图片宽度，默认为120
print(config.height)  # 图片高度，默认为50
```

### 环境变量配置

可以通过环境变量配置验证码：

```bash
# 验证码基本配置
CAPTCHA_LENGTH=6
CAPTCHA_WIDTH=160
CAPTCHA_HEIGHT=60
CAPTCHA_FONT_SIZE=40
CAPTCHA_CHAR_TYPE=alphanumeric

# 验证码样式配置
CAPTCHA_BACKGROUND_COLOR="[255,255,255]"
CAPTCHA_TEXT_COLOR="[0,0,0]"
CAPTCHA_NOISE_LINE_COUNT=5
CAPTCHA_NOISE_POINT_COUNT=150

# 验证码安全配置
CAPTCHA_DISTORTION=true
CAPTCHA_DISTORTION_LEVEL=0.6
CAPTCHA_EXPIRE_SECONDS=300
CAPTCHA_REDIS_KEY_PREFIX=captcha:

# 验证码类型配置
CAPTCHA_DEFAULT_TYPE=image
```

**注意**：
- 颜色配置使用列表格式：`"[R,G,B]"`，如 `"[255,255,255]"`
- 颜色范围配置使用嵌套列表格式：`"[[minR,maxR],[minG,maxG],[minB,maxB]]"`，如 `"[[100,200],[100,200],[100,200]]"`
- 默认验证码类型为 `image`（图片验证码），也可以设置为 `math`（数学题验证码）

## 验证码服务类

### CaptchaService 类

`CaptchaService` 是核心的验证码服务类，提供所有验证码操作方法。

#### 初始化验证码服务

```python
from Modules.common.libs.captcha import CaptchaService

# 创建验证码服务实例
captcha_service = CaptchaService()

# 或者使用单例模式获取实例
from Modules.common.libs.captcha import get_captcha_service
captcha_service = get_captcha_service()
```

#### 生成图片验证码

```python
from config.captcha import CaptchaType

# 生成图片验证码
captcha_result = await captcha_service.generate_captcha(CaptchaType.IMAGE)

print(f"验证码ID: {captcha_result.captcha_id}")
print(f"验证码类型: {captcha_result.captcha_type}")
print(f"过期时间: {captcha_result.expire_seconds}秒")
print(f"图片数据长度: {len(captcha_result.image_data)}字节")

# captcha_result.image_data 包含PNG格式的图片数据
# 可以直接用于HTTP响应
```

#### 生成数学题验证码

```python
# 生成数学题验证码
captcha_result = await captcha_service.generate_captcha(CaptchaType.MATH)

print(f"验证码ID: {captcha_result.captcha_id}")
print(f"验证码类型: {captcha_result.captcha_type}")
print(f"过期时间: {captcha_result.expire_seconds}秒")
print(f"图片数据长度: {len(captcha_result.image_data)}字节")
# 注意：数学题验证码也返回图片数据，而不是文本
```

#### 验证验证码

```python
# 验证用户输入的验证码
captcha_id = "用户提交的验证码ID"
user_answer = "用户输入的答案"

is_valid = await captcha_service.verify_captcha(captcha_id, user_answer)

if is_valid:
    print("验证码验证成功")
else:
    print("验证码验证失败或已过期")
```

#### 获取验证码图片

```python
# 获取已生成验证码的图片
captcha_id = "已存在的验证码ID"
image_data = await captcha_service.get_captcha_image(captcha_id)

if image_data:
    print(f"获取到图片数据，长度: {len(image_data)}字节")
    # 可以用于重新显示验证码图片
else:
    print("验证码不存在或已过期")
```

#### 刷新验证码

```python
# 延长验证码的过期时间
captcha_id = "已存在的验证码ID"
refreshed_result = await captcha_service.refresh_captcha(captcha_id)

if refreshed_result:
    print(f"验证码已刷新，新的过期时间: {refreshed_result.expire_seconds}秒")
    print(f"图片数据长度: {len(refreshed_result.image_data)}字节")
else:
    print("验证码不存在或已过期")
```

#### 获取验证码统计信息

```python
# 获取验证码服务统计信息
stats = await captcha_service.get_captcha_stats()

print(f"当前活跃验证码数量: {stats['active_captchas']}")
print(f"配置信息: {stats['config']}")
```

## 便捷函数

模块提供了一系列便捷函数，简化验证码操作：

```python
from Modules.common.libs.captcha import generate_captcha
from config.captcha import CaptchaType

# 生成验证码（默认为配置中的默认类型，通常是图片验证码）
captcha_result = await generate_captcha()
# 或者指定类型
image_captcha = await generate_captcha(CaptchaType.IMAGE)
```

## 验证码类型

### CaptchaType 枚举

```python
from config.captcha import CaptchaType

# 支持的验证码类型
print(CaptchaType.IMAGE)  # 图片验证码
print(CaptchaType.MATH)   # 数学题验证码
```

### CaptchaCharType 枚举

```python
from config.captcha import CaptchaCharType

# 支持的字符类型
print(CaptchaCharType.NUMERIC)      # 纯数字
print(CaptchaCharType.ALPHA)         # 纯字母
print(CaptchaCharType.ALPHANUMERIC)  # 字母数字混合
print(CaptchaCharType.MIXED)         # 包含特殊字符
```

## 验证码结果

### CaptchaResult 类

```python
from Modules.common.libs.captcha import CaptchaResult
from config.captcha import CaptchaType

# CaptchaResult 包含以下字段
captcha_result = CaptchaResult(
    captcha_id="唯一标识符",
    captcha_type=CaptchaType.IMAGE,
    image_data=b"PNG图片数据",  # 图片验证码和数学题验证码都包含图片数据
    expire_seconds=300,
    metadata={"length": 4}    # 额外元数据
)

# 可以使用 model_dump 方法转换为字典，自动处理图片数据
data_dict = captcha_result.model_dump()
# image_data 会被转换为 base64 Data URL 格式
```

## 实际应用场景

### 1. Web API 集成

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from Modules.common.libs.captcha import generate_captcha
from config.captcha import CaptchaType

app = FastAPI()

@app.get("/api/captcha")
async def get_captcha():
    """获取验证码"""
    try:
        # 生成图片验证码
        captcha_result = await generate_captcha(CaptchaType.IMAGE)
        
        # 返回验证码ID和图片
        return Response(
            content=captcha_result.image_data,
            media_type="image/png",
            headers={
                "X-Captcha-ID": captcha_result.captcha_id,
                "X-Captcha-Expires": str(captcha_result.expire_seconds)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="验证码生成失败")

@app.post("/api/verify-captcha")
async def verify_captcha_endpoint(captcha_id: str, answer: str):
    """验证验证码"""
    try:
        from Modules.common.libs.captcha import get_captcha_service
        captcha_service = get_captcha_service()
        is_valid = await captcha_service.verify_captcha(captcha_id, answer)
        
        if is_valid:
            return {"success": True, "message": "验证码验证成功"}
        else:
            return {"success": False, "message": "验证码验证失败或已过期"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="验证码验证失败")
```

### 2. 用户登录验证

```python
from fastapi import Form, HTTPException
from Modules.common.libs.captcha import generate_captcha, get_captcha_service
from config.captcha import CaptchaType

@app.post("/api/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    captcha_id: str = Form(...),
    captcha_answer: str = Form(...)
):
    """用户登录"""
    # 1. 验证验证码
    captcha_service = get_captcha_service()
    if not await captcha_service.verify_captcha(captcha_id, captcha_answer):
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 2. 验证用户名和密码
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 3. 生成访问令牌
    token = await generate_access_token(user)
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/login/captcha")
async def get_login_captcha():
    """获取登录验证码"""
    captcha_result = await generate_captcha(CaptchaType.IMAGE)
    
    return Response(
        content=captcha_result.image_data,
        media_type="image/png",
        headers={"X-Captcha-ID": captcha_result.captcha_id}
    )
```

### 3. 数学题验证码

```python
@app.get("/api/math-captcha")
async def get_math_captcha():
    """获取数学题验证码"""
    try:
        captcha_result = await generate_captcha(CaptchaType.MATH)
        
        # 返回图片和验证码ID
        return Response(
            content=captcha_result.image_data,
            media_type="image/png",
            headers={
                "X-Captcha-ID": captcha_result.captcha_id,
                "X-Captcha-Expires": str(captcha_result.expire_seconds)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="数学题验证码生成失败")

@app.post("/api/verify-math-captcha")
async def verify_math_captcha(captcha_id: str, answer: str):
    """验证数学题验证码"""
    from Modules.common.libs.captcha import get_captcha_service
    captcha_service = get_captcha_service()
    is_valid = await captcha_service.verify_captcha(captcha_id, answer)
    
    return {"valid": is_valid}
```

### 4. 验证码刷新

```python
from Modules.common.libs.captcha import get_captcha_service

@app.post("/api/refresh-captcha/{captcha_id}")
async def refresh_captcha(captcha_id: str):
    """刷新验证码（延长过期时间）"""
    captcha_service = get_captcha_service()
    refreshed_result = await captcha_service.refresh_captcha(captcha_id)
    
    if refreshed_result:
        return Response(
            content=refreshed_result.image_data,
            media_type="image/png",
            headers={
                "X-Captcha-ID": refreshed_result.captcha_id,
                "X-Captcha-Expires": str(refreshed_result.expire_seconds)
            }
        )
    else:
        raise HTTPException(status_code=404, detail="验证码不存在或已过期")
```

## 图片生成器配置

### ImageGenerator 类

`ImageGenerator` 负责生成验证码图片，支持多种自定义配置：

```python
from Modules.common.libs.captcha.image_generator import ImageGenerator
from config.captcha import CaptchaConfig

# 创建图片生成器
generator = ImageGenerator()

# 生成验证码文本
text = generator.generate_text()
print(f"验证码文本: {text}")

# 生成验证码图片
image_data = generator.generate_image(text)
print(f"图片数据长度: {len(image_data)}字节")
```

### 字体配置

```python
# 使用自定义字体
config = CaptchaConfig()
config.font_path = "/path/to/your/font.ttf"  # 设置自定义字体路径
config.font_size = 40                        # 设置字体大小

generator = ImageGenerator()
```

### 干扰元素配置

```python
# 配置干扰线
config.noise_line_count = 5  # 干扰线数量
config.noise_line_color_range = (
    (100, 200),  # R范围
    (100, 200),  # G范围
    (100, 200)   # B范围
)

# 配置干扰点
config.noise_point_count = 150  # 干扰点数量
config.noise_point_color_range = (
    (150, 255),  # R范围
    (150, 255),  # G范围
    (150, 255)   # B范围
)
```

### 扭曲变形配置

```python
# 启用扭曲变形
config.distortion = True
config.distortion_level = 0.6  # 扭曲程度 (0-1)
```

## 工具函数

### 字符集工具

```python
from Modules.common.libs.captcha.utils import get_character_set, generate_random_text

# 获取不同类型的字符集
numeric_chars = get_character_set("numeric")        # "0123456789"
alpha_chars = get_character_set("alpha")           # "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphanumeric_chars = get_character_set("alphanumeric")  # 字母数字混合
mixed_chars = get_character_set("mixed")            # 包含特殊字符

# 生成随机文本
random_text = generate_random_text(6, alphanumeric_chars)
print(f"随机文本: {random_text}")
```

### 数学题生成

```python
from Modules.common.libs.captcha.utils import generate_math_question

# 生成数学题
question, answer = generate_math_question()
print(f"问题: {question}")
print(f"答案: {answer}")
```

### 验证码ID生成

```python
from Modules.common.libs.captcha.utils import generate_captcha_id

# 生成唯一的验证码ID
captcha_id = generate_captcha_id()
print(f"验证码ID: {captcha_id}")
```

## 最佳实践

### 1. 验证码安全

```python
# 设置合理的过期时间
config.expire_seconds = 300  # 5分钟

# 启用扭曲变形增加识别难度
config.distortion = True
config.distortion_level = 0.6

# 添加干扰元素
config.noise_line_count = 5
config.noise_point_count = 150

# 使用混合字符类型
config.char_type = CaptchaCharType.ALPHANUMERIC
```

### 2. 错误处理

```python
from Modules.common.libs.captcha import generate_captcha, get_captcha_service
from loguru import logger

async def safe_generate_captcha():
    """安全的验证码生成"""
    try:
        captcha_result = await generate_captcha()
        return captcha_result
    except Exception as e:
        logger.error(f"验证码生成失败: {e}")
        # 返回默认验证码或错误信息
        return None

async def safe_verify_captcha(captcha_id: str, answer: str):
    """安全的验证码验证"""
    try:
        if not captcha_id or not answer:
            return False
            
        captcha_service = get_captcha_service()
        is_valid = await captcha_service.verify_captcha(captcha_id, answer)
        
        if is_valid:
            logger.info(f"验证码验证成功: {captcha_id}")
        else:
            logger.warning(f"验证码验证失败: {captcha_id}")
            
        return is_valid
    except Exception as e:
        logger.error(f"验证码验证异常: {e}")
        return False
```

### 3. 性能优化

```python
# 使用单例模式获取验证码服务
from Modules.common.libs.captcha import get_captcha_service

def get_captcha_service_cached():
    """获取缓存的验证码服务实例"""
    return get_captcha_service()

# 批量预生成验证码（适用于高并发场景）
async def pre_generate_captchas(count: int = 10):
    """预生成验证码池"""
    captcha_service = get_captcha_service()
    captcha_pool = []
    
    for _ in range(count):
        captcha_result = await captcha_service.generate_captcha()
        captcha_pool.append(captcha_result)
    
    return captcha_pool
```

### 4. 前端集成

```javascript
// 前端JavaScript示例
class CaptchaManager {
    constructor() {
        this.currentCaptchaId = null;
    }
    
    async loadCaptcha() {
        try {
            const response = await fetch('/api/captcha');
            if (response.ok) {
                this.currentCaptchaId = response.headers.get('X-Captcha-ID');
                const blob = await response.blob();
                const imageUrl = URL.createObjectURL(blob);
                
                // 更新页面上的验证码图片
                document.getElementById('captcha-image').src = imageUrl;
            }
        } catch (error) {
            console.error('加载验证码失败:', error);
        }
    }
    
    async verifyCaptcha(answer) {
        if (!this.currentCaptchaId || !answer) {
            return false;
        }
        
        try {
            const response = await fetch('/api/verify-captcha', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    captcha_id: this.currentCaptchaId,
                    answer: answer
                })
            });
            
            const result = await response.json();
            return result.success;
        } catch (error) {
            console.error('验证码验证失败:', error);
            return false;
        }
    }
    
    async refreshCaptcha() {
        if (this.currentCaptchaId) {
            try {
                const response = await fetch(`/api/refresh-captcha/${this.currentCaptchaId}`);
                if (response.ok) {
                    this.currentCaptchaId = response.headers.get('X-Captcha-ID');
                    const blob = await response.blob();
                    const imageUrl = URL.createObjectURL(blob);
                    
                    document.getElementById('captcha-image').src = imageUrl;
                }
            } catch (error) {
                console.error('刷新验证码失败:', error);
                // 如果刷新失败，重新加载验证码
                this.loadCaptcha();
            }
        }
    }
}

// 使用示例
const captchaManager = new CaptchaManager();

// 页面加载时获取验证码
document.addEventListener('DOMContentLoaded', () => {
    captchaManager.loadCaptcha();
    
    // 点击刷新按钮
    document.getElementById('refresh-captcha').addEventListener('click', () => {
        captchaManager.refreshCaptcha();
    });
    
    // 表单提交时验证验证码
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const captchaAnswer = document.getElementById('captcha-answer').value;
        const isValid = await captchaManager.verifyCaptcha(captchaAnswer);
        
        if (isValid) {
            // 验证码正确，提交表单
            e.target.submit();
        } else {
            // 验证码错误，显示错误信息
            alert('验证码错误，请重新输入');
            captchaManager.loadCaptcha();
        }
    });
});
```

## 常见问题

### Q: 如何自定义验证码样式？

A: 可以通过修改 `CaptchaConfig` 配置来自定义验证码样式：

**方式一：通过代码配置**

```python
from config.captcha import CaptchaConfig

config = CaptchaConfig()

# 修改尺寸
config.width = 200
config.height = 80

# 修改颜色（代码中使用元组格式）
config.background_color = (240, 240, 240)  # 浅灰色背景
config.text_color = (50, 50, 50)          # 深灰色文字

# 修改字体
config.font_size = 42
config.font_path = "/path/to/custom/font.ttf"

# 修改干扰元素
config.noise_line_count = 8
config.noise_point_count = 200
```

**方式二：通过环境变量配置**

```bash
# 修改尺寸
CAPTCHA_WIDTH=200
CAPTCHA_HEIGHT=80

# 修改颜色（环境变量中使用列表格式）
CAPTCHA_BACKGROUND_COLOR="[240,240,240]"
CAPTCHA_TEXT_COLOR="[50,50,50]"

# 修改字体
CAPTCHA_FONT_SIZE=42
CAPTCHA_FONT_PATH="/path/to/custom/font.ttf"

# 修改干扰元素
CAPTCHA_NOISE_LINE_COUNT=8
CAPTCHA_NOISE_POINT_COUNT=200
```

### Q: 如何处理验证码识别失败？

A: 可以通过以下方式提高验证码的可读性：

**方式一：通过代码配置**

```python
# 降低扭曲程度
config.distortion = True
config.distortion_level = 0.3  # 降低扭曲程度

# 减少干扰元素
config.noise_line_count = 2
config.noise_point_count = 50

# 使用更简单的字符集
config.char_type = CaptchaCharType.NUMERIC  # 只使用数字

# 增加字体大小
config.font_size = 48
```

**方式二：通过环境变量配置**

```bash
# 降低扭曲程度
CAPTCHA_DISTORTION=true
CAPTCHA_DISTORTION_LEVEL=0.3

# 减少干扰元素
CAPTCHA_NOISE_LINE_COUNT=2
CAPTCHA_NOISE_POINT_COUNT=50

# 使用更简单的字符集
CAPTCHA_CHAR_TYPE=numeric

# 增加字体大小
CAPTCHA_FONT_SIZE=48
```

### Q: 如何实现验证码的国际化支持？

A: 可以通过自定义数学题生成函数来实现：

```python
from Modules.common.libs.captcha.utils import generate_math_question

def generate_localized_math_question(locale="zh"):
    """生成本地化的数学题"""
    import random
    
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-", "*"])
    
    if locale == "zh":
        if op == "+":
            question = f"{a} 加 {b} 等于多少？"
            answer = str(a + b)
        elif op == "-":
            if a < b:
                a, b = b, a
            question = f"{a} 减 {b} 等于多少？"
            answer = str(a - b)
        else:  # "*"
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            question = f"{a} 乘以 {b} 等于多少？"
            answer = str(a * b)
    else:
        # 默认英文
        if op == "+":
            question = f"{a} + {b} = ?"
            answer = str(a + b)
        elif op == "-":
            if a < b:
                a, b = b, a
            question = f"{a} - {b} = ?"
            answer = str(a - b)
        else:  # "*"
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            question = f"{a} × {b} = ?"
            answer = str(a * b)
    
    return question, answer
```

## API 参考

### CaptchaService 类方法

| 方法 | 描述 |
|------|------|
| `generate_captcha(captcha_type)` | 生成验证码 |
| `verify_captcha(captcha_id, answer)` | 验证验证码 |
| `get_captcha_image(captcha_id)` | 获取验证码图片 |
| `refresh_captcha(captcha_id)` | 刷新验证码 |
| `cleanup_expired_captcha()` | 清理过期验证码 |
| `get_captcha_stats()` | 获取验证码统计信息 |

### 便捷函数

| 函数 | 描述 |
|------|------|
| `generate_captcha(captcha_type)` | 便捷函数：生成验证码 |
| `get_captcha_service()` | 获取验证码服务实例（单例模式） |

### 数据类型

| 类型 | 描述 |
|------|------|
| `CaptchaType` | 验证码类型枚举 |
| `CaptchaResult` | 验证码生成结果 |
| `CaptchaCharType` | 验证码字符类型枚举 |

### 配置类

| 类 | 描述 |
|------|------|
| `CaptchaConfig` | 验证码配置类，支持环境变量配置 |

## 版本历史

- v1.0.0: 初始版本，提供基本的图片和数学题验证码功能
- v1.1.0: 增强图片生成器，支持自定义字体和样式
- v1.2.0: 添加验证码刷新和统计功能
- v1.3.0: 优化性能和错误处理，增加便捷函数
- v1.4.0: 更新配置系统，使用统一的 Config 管理