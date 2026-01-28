# Time 模块使用文档

## 概述

`libs/time` 模块是一个强大的时间处理库，提供了时区管理和时间工具函数，支持应用配置的时区设置。该模块主要包含两个子模块：

- `timezone.py`: 时区管理模块，负责管理应用的时区设置
- `utils.py`: 时间工具函数模块，提供时区感知的时间处理工具函数

## 主要功能

- 时区管理和初始化
- 时区感知的时间获取和格式化
- 时间解析和转换
- 与项目配置系统的集成
- 线程安全的时区操作

## 安装与导入

```python
from Modules.common.libs.time import (
    # 时区管理
    TimezoneManager,
    get_timezone_manager,
    init_timezone,
    set_timezone,
    get_timezone,
    get_timezone_string,
    is_valid_timezone,
    
    # 时间工具
    now,
    utc_now,
    format_datetime,
    parse_datetime,
    to_timezone,
    to_utc,
    from_utc,
    isoformat,
    timestamp,
    from_timestamp,
    add_time,
    time_diff,
    is_same_day,
    start_of_day,
    end_of_day,
)
```

## 时区管理

### TimezoneManager 类

`TimezoneManager` 是一个单例类，负责管理应用的时区设置。

#### 初始化时区

```python
# 从配置初始化时区
init_timezone()
```

这会从应用配置中读取时区设置（默认为 `Asia/Shanghai`），如果配置无效，则使用默认时区作为降级策略。

#### 获取和设置时区

```python
# 获取当前时区对象
tz = get_timezone()

# 获取当前时区字符串
tz_str = get_timezone_string()
print(tz_str)  # 输出: Asia/Shanghai

# 设置时区
set_timezone("UTC")
set_timezone("America/New_York")
```

#### 验证时区

```python
from Modules.common.libs.time import is_valid_timezone

# 验证时区字符串是否有效
print(is_valid_timezone("Asia/Shanghai"))  # True
print(is_valid_timezone("Invalid/Timezone"))  # False
```

#### 时区管理器高级用法

```python
# 获取时区管理器实例
manager = get_timezone_manager()

# 清空时区对象缓存
manager.clear_cache()

# 获取已缓存的时区列表
cached_timezones = manager.get_cached_timezones()
print(cached_timezones)
```

## 时间工具函数

### 获取当前时间

```python
from Modules.common.libs.time import now, utc_now

# 获取当前时间（应用配置时区）
current_time = now()
print(current_time)  # 2023-12-25 10:30:00+08:00

# 获取当前UTC时间
utc_time = utc_now()
print(utc_time)  # 2023-12-25 02:30:00+00:00
```

### 时间格式化

```python
from Modules.common.libs.time import format_datetime, isoformat

# 格式化时间
formatted = format_datetime(current_time, "%Y年%m月%d日 %H:%M:%S")
print(formatted)  # 2023年12月25日 10:30:00

# 获取ISO格式时间字符串
iso_str = isoformat(current_time)
print(iso_str)  # 2023-12-25T10:30:00+08:00

# 使用当前时间
iso_str_now = isoformat()
print(iso_str_now)  # 当前时间的ISO格式
```

### 时间解析

```python
from Modules.common.libs.time import parse_datetime, from_timestamp

# 解析时间字符串
dt = parse_datetime("2023-12-25 10:30:00")
print(dt)  # 2023-12-25 10:30:00+08:00

# 自定义格式解析
dt_custom = parse_datetime("2023/12/25 10:30", "%Y/%m/%d %H:%M")
print(dt_custom)  # 2023-12-25 10:30:00+08:00

# 从时间戳创建时间对象
ts = 1703490600.0
dt_from_ts = from_timestamp(ts)
print(dt_from_ts)  # 2023-12-25 10:30:00+08:00
```

### 时区转换

```python
from Modules.common.libs.time import to_timezone, to_utc, from_utc

# 转换到指定时区
utc_time = to_timezone(current_time, "UTC")
print(utc_time)  # 2023-12-25 02:30:00+00:00

# 转换为UTC时间
utc_time = to_utc(current_time)
print(utc_time)  # 2023-12-25 02:30:00+00:00

# 从UTC时间转换为应用配置时区
local_time = from_utc(utc_time)
print(local_time)  # 2023-12-25 10:30:00+08:00
```

### 时间戳操作

```python
from Modules.common.libs.time import timestamp

# 获取时间戳
ts = timestamp(current_time)
print(ts)  # 1703490600.0

# 使用当前时间
ts_now = timestamp()
print(ts_now)  # 当前时间的时间戳
```

### 时间计算

```python
from Modules.common.libs.time import add_time, time_diff

# 时间加减
future_time = add_time(current_time, days=1, hours=2, minutes=30)
print(future_time)  # 2023-12-26 13:00:00+08:00

# 计算时间差
dt1 = now()
dt2 = add_time(dt1, hours=2)
diff_seconds = time_diff(dt2, dt1)
print(diff_seconds)  # 7200.0 (2小时)

# 与当前时间比较
diff_from_now = time_diff(dt1)
print(diff_from_now)  # 0.0 (如果是同一时间)
```

### 日期比较

```python
from Modules.common.libs.time import is_same_day, start_of_day, end_of_day

# 判断是否为同一天
dt1 = now()
dt2 = add_time(dt1, hours=5)
print(is_same_day(dt1, dt2))  # True

dt3 = add_time(dt1, days=1)
print(is_same_day(dt1, dt3))  # False

# 获取一天的开始和结束时间
day_start = start_of_day(current_time)
print(day_start)  # 2023-12-25 00:00:00+08:00

day_end = end_of_day(current_time)
print(day_end)  # 2023-12-25 23:59:59+999999+08:00

# 使用当前日期
today_start = start_of_day()
today_end = end_of_day()
```

## 配置集成

Time 模块与应用配置系统紧密集成。时区设置可以通过应用配置进行指定：

```python
# 在配置文件中设置时区
# config/app.py
APP_CONFIG = {
    "timezone": "Asia/Shanghai",  # 默认时区
    # 其他配置...
}
```

如果配置中没有指定时区或指定的时区无效，模块将使用以下降级策略：

1. 尝试使用 `Asia/Shanghai` 作为默认时区
2. 如果默认时区也失败，则使用 `UTC` 时区

## 最佳实践

### 1. 初始化时区

在应用启动时初始化时区：

```python
# 在应用启动代码中
from Modules.common.libs.time import init_timezone

# 初始化时区
init_timezone()
```

### 2. 使用时区感知的时间

始终使用时区感知的时间对象，避免时区混淆：

```python
from Modules.common.libs.time import now, to_utc

# 获取当前时间（已包含时区信息）
current_time = now()

# 转换为UTC进行存储或传输
utc_time = to_utc(current_time)
```

### 3. 时间存储和传输

建议使用UTC时间进行存储和传输，显示时再转换为本地时区：

```python
from Modules.common.libs.time import to_utc, from_utc, format_datetime

# 存储时间（使用UTC）
storage_time = to_utc(now())

# 传输时间（使用ISO格式的UTC时间）
transmission_time = format_datetime(storage_time)

# 显示时间（转换为本地时区）
display_time = from_utc(storage_time)
display_str = format_datetime(display_time, "%Y年%m月%d日 %H:%M:%S")
```

### 4. 错误处理

模块内置了完善的错误处理和降级策略，但在关键业务逻辑中仍建议进行错误处理：

```python
from Modules.common.libs.time import parse_datetime, now
from loguru import logger

try:
    # 尝试解析用户输入的时间
    user_time = parse_datetime(user_input)
except Exception as e:
    logger.error(f"解析用户时间失败: {e}")
    # 使用当前时间作为降级
    user_time = now()
```

## 常见问题

### Q: 如何处理夏令时？

A: 模块使用 Python 的 `zoneinfo` 库，自动处理夏令时。只需使用标准的时区标识符（如 `America/New_York`），系统会自动处理夏令时转换。

### Q: 如何处理没有时区信息的时间对象？

A: 模块会自动为没有时区信息的时间对象添加应用配置的时区。你也可以手动指定：

```python
from datetime import datetime
from Modules.common.libs.time import get_timezone

# 创建无时区信息的时间对象
naive_dt = datetime(2023, 12, 25, 10, 30)

# 添加时区信息
tz = get_timezone()
aware_dt = naive_dt.replace(tzinfo=tz)
```

### Q: 如何处理数据库中的时间？

A: 建议在数据库中存储UTC时间，在应用层进行时区转换：

```python
# 存储到数据库（UTC时间）
db_time = to_utc(now())

# 从数据库读取后转换为本地时间
local_time = from_utc(db_time)
```

## API 参考

### 时区管理函数

| 函数 | 描述 |
|------|------|
| `init_timezone()` | 从配置初始化时区 |
| `set_timezone(timezone_str)` | 设置时区 |
| `get_timezone()` | 获取当前时区对象 |
| `get_timezone_string()` | 获取当前时区字符串 |
| `is_valid_timezone(timezone_str)` | 验证时区字符串是否有效 |

### 时间工具函数

| 函数 | 描述 |
|------|------|
| `now()` | 获取当前时间（应用配置时区） |
| `utc_now()` | 获取当前UTC时间 |
| `format_datetime(dt, fmt)` | 格式化时间 |
| `parse_datetime(dt_str, fmt, apply_timezone)` | 解析时间字符串 |
| `to_timezone(dt, timezone_str)` | 时区转换 |
| `to_utc(dt)` | 转换为UTC时间 |
| `from_utc(dt)` | 从UTC时间转换为应用配置时区 |
| `isoformat(dt)` | 获取ISO格式时间字符串 |
| `timestamp(dt)` | 获取时间戳 |
| `from_timestamp(ts, apply_timezone)` | 从时间戳创建时间对象 |
| `add_time(dt, **kwargs)` | 时间加减 |
| `time_diff(dt1, dt2)` | 计算时间差 |
| `is_same_day(dt1, dt2)` | 判断是否为同一天 |
| `start_of_day(dt)` | 获取一天的开始时间 |
| `end_of_day(dt)` | 获取一天的结束时间 |

## 版本历史

- v1.0.0: 初始版本，提供基本的时区管理和时间工具函数