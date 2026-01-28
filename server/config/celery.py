import json
from typing import Any

from kombu import Queue
from loguru import logger
from pydantic import Field

from config.base import BaseConfig


class CeleryConfig(BaseConfig):
    """
    Celery + RabbitMQ 配置类

    该配置类基于 Pydantic Settings，专门为 Celery 库提供配置支持。
    所有环境变量都需要以 "CELERY_" 为前缀。

    设计特点：
    - 支持 RabbitMQ 作为消息代理（Broker）
    - 支持 Redis 作为结果存储（Result Backend）
    - 完整的 Worker 并发和性能配置
    - 灵活的任务队列和路由配置
    - 支持定时任务调度（Celery Beat）
    - 集成 Flower 监控工具配置
    - 支持任务重试、超时控制
    - 时区感知的定时任务

    环境变量格式：
    - 简单配置：CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
    - 嵌套配置：CELERY_WORKER__CONCURRENCY=4
    - 嵌套配置使用双下划线 "__" 作为分隔符

    使用示例：
        config = CeleryConfig()

        # 在 Celery 应用中使用
        from celery import Celery
        app = Celery('myapp')
        app.conf.broker_url = config.broker_url
        app.conf.result_backend = config.result_backend
        app.conf.worker_concurrency = config.worker_concurrency

    环境变量完整示例：
        # ========== Broker 配置 ==========
        CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
        CELERY_BROKER_CONNECTION_RETRY=true
        CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP=true

        # ========== Result Backend 配置 ==========
        CELERY_RESULT_BACKEND=redis://localhost:6379/2
        CELERY_RESULT_EXPIRES=3600
        CELERY_RESULT_EXTENDED=true

        # ========== Worker 配置 ==========
        CELERY_WORKER__CONCURRENCY=4
        CELERY_WORKER__PREFETCH_MULTIPLIER=4
        CELERY_WORKER__MAX_TASKS_PER_CHILD=1000
        CELERY_WORKER__DISABLE_RATE_LIMITS=false

        # ========== 任务配置 ==========
        CELERY_TASK_DEFAULT_QUEUE=default
        CELERY_TASK_DEFAULT_EXCHANGE=default
        CELERY_TASK_DEFAULT_ROUTING_KEY=default
        CELERY_TASK_DEFAULT_TIME_LIMIT=3600
        CELERY_TASK_DEFAULT_SOFT_TIME_LIMIT=3000
        CELERY_TASK_DEFAULT_MAX_RETRIES=3
        CELERY_TASK_DEFAULT_RETRY_DELAY=60
        CELERY_TASK_TRACK_STARTED=true
        CELERY_TASK_ACKS_LATE=true

        # ========== 序列化配置 ==========
        CELERY_TASK_SERIALIZER=json
        CELERY_RESULT_SERIALIZER=json
        CELERY_ACCEPT_CONTENT=json,pickle

        # ========== 时区配置 ==========
        CELERY_TIMEZONE=Asia/Shanghai
        CELERY_ENABLE_UTC=true

        # ========== 安全配置 ==========
        CELERY_TASK_SEND_SENT_EVENT=true
        CELERY_TASK_SEND_STARTED_EVENT=true
        CELERY_TASK_SEND_SUCCESS_EVENT=true
        CELERY_TASK_SEND_FAILURE_EVENT=true
        CELERY_TASK_SEND_RETRY_EVENT=true

        # ========== Flower 监控配置 ==========
        CELERY_FLOWER__PORT=5555
        CELERY_FLOWER__HOST=0.0.0.0
        CELERY_FLOWER__BASIC_AUTH=admin:password
        CELERY_FLOWER__BROKER_API=http://localhost:15672/api/
    """

    model_config = BaseConfig.model_config | {"env_prefix": "CELERY_"}

    # ==================== Broker 配置 ====================

    # 消息代理 URL（Broker URL）
    # 支持多种消息代理，根据需求选择：
    #
    # ========== RabbitMQ（推荐用于生产环境）==========
    # 格式: amqp://user:password@host:port/vhost
    # 示例: amqp://guest:guest@localhost:5672//
    # 带密码: amqp://username:password@localhost:5672/myvhost
    # SSL连接: amqps://username:password@localhost:5671/vhost
    # 优点: 消息可靠性高、支持高级路由、持久化、官方推荐
    # 缺点: 部署复杂、资源占用较高
    #
    # ========== Redis（推荐用于开发/中小规模）==========
    # 格式: redis://host:port/db
    # 示例: redis://localhost:6379/0
    # 带密码: redis://:password@localhost:6379/0
    # Unix Socket: redis+socket:///var/run/redis/redis.sock
    # 优点: 部署简单、性能高、资源占用少
    # 缺点: 消息可靠性不如 RabbitMQ、不支持高级路由
    #
    # ========== 其他支持的 Broker ==========
    # Amazon SQS: sqs://access_key:secret_key@
    # MongoDB: mongodb://localhost:27017/celery
    # CouchDB: couchdb://localhost:5984/celery
    # Zookeeper: zookeeper://localhost:2181/celery
    #
    # 建议:
    #   - 生产环境使用 RabbitMQ（可靠性高）
    #   - 开发环境使用 Redis（部署简单）
    #   - 可通过环境变量 CELERY_BROKER_URL 切换
    broker_url: str = Field(
        default="amqp://guest:guest@localhost:5672//",
        description="消息代理 URL",
    )

    # 连接失败时是否自动重试
    # True: 连接失败后会自动尝试重新连接
    # False: 连接失败后直接抛出异常，不重试
    # 建议在生产环境中设置为 True，提高系统可用性
    broker_connection_retry: bool = Field(
        default=True,
        description="连接失败时是否自动重试",
    )

    # 启动时连接失败是否重试
    # True: Worker 启动时如果连接失败，会自动重试
    # False: Worker 启动时如果连接失败，直接退出
    # 建议设置为 True，避免因临时网络问题导致启动失败
    broker_connection_retry_on_startup: bool = Field(
        default=True,
        description="启动时连接失败是否重试",
    )

    # 最大重试次数
    # 当 broker_connection_retry=True 时生效
    # 控制连接失败后的最大重试次数
    # 超过此次数后，如果仍然连接失败，则抛出异常
    # 建议根据网络稳定性调整，通常 3-10 次比较合适
    broker_connection_max_retries: int = Field(
        default=5,
        description="最大重试次数",
    )

    # 重试延迟时间（秒）
    # 每次重试之间的等待时间
    # 避免频繁重试导致服务器压力过大
    # 建议设置为 5-10 秒，根据实际情况调整
    broker_connection_retry_delay: int = Field(
        default=5,
        description="重试延迟时间（秒）",
    )

    # 是否使用 SSL 连接 RabbitMQ
    # True: 使用 SSL/TLS 加密连接，更安全
    # False: 使用普通明文连接
    # 生产环境建议设置为 True，确保数据传输安全
    # 需要在 RabbitMQ 服务器端配置 SSL 证书
    broker_use_ssl: bool = Field(
        default=False,
        description="是否使用 SSL 连接 RabbitMQ",
    )

    # Broker 传输选项
    # 用于配置 Broker 连接的额外参数
    # 例如: {'max_retries': 3, 'interval_start': 0, 'interval_step': 0.2}
    # 可以设置连接池、重试策略等高级选项
    # 一般情况下不需要配置，使用默认值即可
    broker_transport_options: dict[str, Any] = Field(
        default_factory=lambda: {},
        description="Broker 传输选项",
    )

    # ==================== Result Backend 配置 ====================

    # 任务结果存储 URL
    # 用于存储任务执行结果、状态和返回值
    # 支持: Redis, RabbitMQ, Database, Memcached 等
    # 示例: redis://localhost:6379/2
    # redis://:password@host:port/db
    # db://+driver://user:password@host:port/database
    # 建议使用 Redis，性能好且支持过期时间
    result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="任务结果存储 URL",
    )

    # 任务结果过期时间（秒）
    # 0 表示永不过期
    # 超过此时间后，任务结果会被自动删除
    # 避免结果存储占用过多内存
    # 建议根据业务需求设置，通常 3600-86400 秒（1-24小时）
    # 对于需要长期保存的结果，可以设置为 0
    result_expires: int = Field(
        default=3600,
        description="任务结果过期时间（秒）",
    )

    # 是否扩展结果格式
    # True: 结果包含更多信息（任务名、参数、执行时间等）
    # False: 只包含基本的任务结果
    # 建议设置为 True，便于调试和监控
    # 扩展格式会占用更多存储空间
    result_extended: bool = Field(
        default=True,
        description="是否扩展结果格式",
    )

    # Result Backend 传输选项
    # 用于配置 Result Backend 连接的额外参数
    # 例如 Redis 连接池配置、重试策略等
    # 一般情况下不需要配置，使用默认值即可
    result_backend_transport_options: dict[str, Any] = Field(
        default_factory=lambda: {},
        description="Result Backend 传输选项",
    )

    # ==================== Worker 配置 ====================

    # Worker 执行池类型
    # 支持: prefork, threads, solo, gevent, eventlet
    # prefork: 多进程（默认），适合 CPU 密集型任务，充分利用多核 CPU
    # threads: 多线程，适合 I/O 密集型任务，内存占用小，但受 GIL 限制
    # solo: 单线程，适合调试或需要串行执行的任务
    # gevent: 协程，适合高并发 I/O 密集型任务，需要安装 gevent（Windows 不推荐）
    # eventlet: 协程，适合高并发 I/O 密集型任务，需要安装 eventlet（Windows 不推荐）
    # 建议根据任务类型选择：
    #   - CPU 密集型：prefork
    #   - I/O 密集型：threads（Windows 推荐）
    #   - 高并发 I/O：gevent/eventlet（Linux 推荐）
    #   - 调试环境：solo
    worker_pool: str = Field(
        default="threads",
        description="Worker 执行池类型",
    )

    # Worker 并发数（同时执行的任务数量）
    # 建议设置为 CPU 核心数
    # 过多会导致上下文切换开销，过少会浪费 CPU 资源
    # I/O 密集型任务可以设置得更高（如 CPU 核心数的 2-4 倍）
    # CPU 密集型任务建议设置为 CPU 核心数
    # 可以通过命令: celery -A app inspect active 查看实际负载
    worker_concurrency: int = Field(
        default=4,
        description="Worker 并发数",
    )

    # 预取倍数
    # 控制每个 Worker 预取的任务数量 = worker_concurrency * prefetch_multiplier
    # 例如: concurrency=4, prefetch_multiplier=4，则每个 Worker 预取 16 个任务
    # 预取可以减少网络往返，提高吞吐量
    # 但会占用更多内存，且任务分配可能不均衡
    # 建议设置为 1-4，根据任务执行时间调整
    # 任务执行时间短，可以设置大一些；任务执行时间长，设置小一些
    worker_prefetch_multiplier: int = Field(
        default=4,
        description="预取倍数",
    )

    # 每个 Worker 处理的最大任务数
    # 达到此数量后，Worker 进程会自动重启
    # 用于防止内存泄漏和资源累积
    # 设置为 None 表示不限制
    # 建议设置为 1000-5000，根据任务复杂度调整
    # 如果任务有内存泄漏问题，可以设置得小一些（如 100-500）
    worker_max_tasks_per_child: int = Field(
        default=1000,
        description="每个 Worker 处理的最大任务数",
    )

    # 是否禁用速率限制
    # True: 禁用所有任务的速率限制
    # False: 启用速率限制（基于 task_default_rate_limit）
    # 速率限制用于控制任务执行频率，防止系统过载
    # 建议设置为 False，除非确定不需要速率限制
    worker_disable_rate_limits: bool = Field(
        default=False,
        description="是否禁用速率限制",
    )

    # Worker 日志格式
    # 使用 Python logging 的格式字符串
    # 可用变量: asctime（时间）, levelname（日志级别）, processName（进程名）, message（消息）
    # 建议保持默认格式，便于阅读和调试
    worker_log_format: str = Field(
        default="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        description="Worker 日志格式",
    )

    # Worker 任务日志格式
    # 专门用于任务执行的日志格式
    # 额外可用变量: task_name（任务名）, task_id（任务ID）
    # 建议保持默认格式，便于追踪特定任务的日志
    worker_task_log_format: str = Field(
        default="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
        description="Worker 任务日志格式",
    )

    # ==================== 任务配置 ====================

    # 默认队列名称
    # 所有未指定队列的任务都会发送到此队列
    # 队列名称用于任务路由和 Worker 订阅
    # 建议使用有意义的名称，如 'default', 'high_priority', 'low_priority'
    # 可以通过 task_queues 配置多个队列
    # 可以通过 task_routes 将不同任务路由到不同队列
    task_default_queue: str = Field(
        default="default",
        description="默认队列名称",
    )

    # 默认交换机名称
    # RabbitMQ 的交换机用于接收和路由消息
    # 默认使用 direct 类型的交换机
    # 一般情况下与队列名称相同即可
    # 高级用法: 可以配置不同类型的交换机（direct, topic, fanout）
    task_default_exchange: str = Field(
        default="default",
        description="默认交换机名称",
    )

    # 默认路由键
    # 用于将消息路由到特定的队列
    # 在 direct 交换机中，routing_key 必须与队列名完全匹配
    # 在 topic 交换机中，routing_key 支持通配符匹配
    # 一般情况下与队列名称相同即可
    task_default_routing_key: str = Field(
        default="default",
        description="默认路由键",
    )

    # 默认速率限制
    # 格式: '数量/时间单位'，例如: '100/m'（每分钟 100 个）
    # 支持的时间单位: s（秒）, m（分）, h（小时）, d（天）
    # 空字符串表示不限制
    # 用于防止任务执行过快导致系统过载
    # 建议根据系统承载能力设置，如 '1000/m'
    task_default_rate_limit: str = Field(
        default="",
        description="默认速率限制",
    )

    # 默认硬超时时间（秒）
    # 任务执行时间超过此限制会被强制终止（SIGKILL）
    # 硬超时无法被任务捕获和处理
    # 用于防止任务无限期运行
    # 建议设置为合理的最大执行时间，如 3600（1小时）
    # 对于长时间运行的任务，可以设置得更大
    task_default_time_limit: int = Field(
        default=3600,
        description="默认硬超时时间（秒）",
    )

    # 默认软超时时间（秒）
    # 任务执行时间超过此限制会抛出 SoftTimeLimitExceeded 异常
    # 软超时可以被任务捕获和处理，用于优雅地终止任务
    # 建议设置为硬超时的 80-90%，如硬超时 3600，软超时 3000
    # 任务可以捕获异常进行清理工作，然后退出
    task_default_soft_time_limit: int = Field(
        default=3000,
        description="默认软超时时间（秒）",
    )

    # 默认最大重试次数
    # 任务失败后的最大重试次数
    # 设置为 0 表示不重试
    # 重试次数达到上限后，任务状态变为 FAILURE
    # 建议根据任务重要性设置，重要任务可以重试多次（如 5-10 次）
    # 非重要任务可以设置较少重试次数（如 1-3 次）
    task_default_max_retries: int = Field(
        default=3,
        description="默认最大重试次数",
    )

    # 默认重试延迟（秒）
    # 任务失败后，等待多少秒再重试
    # 避免立即重试导致同样的问题
    # 建议设置为 60-300 秒，根据实际情况调整
    # 对于临时性错误（如网络超时），可以设置较短延迟
    # 对于持续性错误（如服务不可用），可以设置较长延迟
    task_default_retry_delay: int = Field(
        default=60,
        description="默认重试延迟（秒）",
    )

    # 是否跟踪任务开始时间
    # True: 任务开始执行时，状态变为 STARTED
    # False: 任务状态直接从 PENDING 变为 SUCCESS/FAILURE
    # 建议设置为 True，便于监控任务执行进度
    # 但会增加一些存储开销
    task_track_started: bool = Field(
        default=True,
        description="是否跟踪任务开始时间",
    )

    # 是否延迟确认（任务完成后才确认）
    # True: 任务执行完成后才向 Broker 发送确认
    # False: 任务开始执行时就发送确认
    # 延迟确认可以防止任务丢失（Worker 崩溃时任务会被重新分配）
    # 但可能导致重复执行（如果任务完成后 Worker 崩溃）
    # 建议设置为 True，任务需要保证幂等性
    # 如果任务不能重复执行，设置为 False 并配合 task_reject_on_worker_lost
    task_acks_late: bool = Field(
        default=True,
        description="是否延迟确认",
    )

    # Worker 丢失时是否拒绝任务
    # 当 task_acks_late=False 时生效
    # True: Worker 丢失时，任务会被重新分配
    # False: Worker 丢失时，任务状态变为 FAILURE
    # 建议设置为 True，提高任务可靠性
    # 配合 task_acks_late=False 使用，避免任务丢失
    task_reject_on_worker_lost: bool = Field(
        default=True,
        description="Worker 丢失时是否拒绝任务",
    )

    # 是否同步执行任务（仅用于测试）
    # True: 任务会同步执行，不通过 Celery
    # False: 任务会异步执行，通过 Celery
    # 仅用于开发和测试环境，便于调试
    # 生产环境必须设置为 False，否则无法异步执行任务
    task_always_eager: bool = Field(
        default=False,
        description="是否同步执行任务（仅用于测试）",
    )

    # 同步执行时是否传播异常
    # 当 task_always_eager=True 时生效
    # True: 任务异常会传播到调用者
    # False: 任务异常被捕获，返回异常对象
    # 建议设置为 True，便于测试时发现问题
    task_eager_propagates: bool = Field(
        default=True,
        description="同步执行时是否传播异常",
    )

    # ==================== 序列化配置 ====================

    # 任务序列化格式
    # 支持: json, pickle, msgpack, yaml
    # json: 安全、可读性好，但只支持基本数据类型
    # pickle: 支持所有 Python 对象，但不安全（可能执行任意代码）
    # msgpack: 二进制格式，性能好，但可读性差
    # 建议使用 json，安全性最高
    # 如果需要传递复杂对象，可以考虑 pickle，但要注意安全问题
    task_serializer: str = Field(
        default="json",
        description="任务序列化格式",
    )

    # 结果序列化格式
    # 支持: json, pickle, msgpack, yaml
    # 通常与 task_serializer 保持一致
    # 建议使用 json，安全性最高
    result_serializer: str = Field(
        default="json",
        description="结果序列化格式",
    )

    # 接受的内容类型列表
    # 用于安全验证，防止恶意代码执行
    # 建议只包含 'json'，拒绝 'pickle'
    # 如果使用 pickle，会有安全风险（可能执行任意代码）
    # 生产环境强烈建议只接受 json
    accept_content: list[str] = Field(
        default_factory=lambda: ["json"],
        description="接受的内容类型列表",
    )

    # ==================== 时区配置 ====================

    # 时区设置
    # 用于定时任务调度（Celery Beat）
    # 确保定时任务在正确的本地时间执行
    # 常用时区: Asia/Shanghai, Asia/Tokyo, America/New_York, Europe/London
    # 必须与系统时区或业务时区一致
    # 建议设置为服务器所在时区或业务主要时区
    timezone: str = Field(
        default="Asia/Shanghai",
        description="时区设置",
    )

    # 是否使用 UTC 时间
    # True: 所有时间都使用 UTC
    # False: 使用配置的 timezone
    # 建议设置为 True，便于跨时区协作
    # 定时任务会根据 timezone 自动转换为本地时间
    enable_utc: bool = Field(
        default=True,
        description="是否使用 UTC 时间",
    )

    # ==================== 安全配置 ====================

    # 是否发送任务发送事件
    # True: 任务发送时会产生事件
    # False: 不发送事件
    # 事件会被 Flower 等监控工具捕获
    # 建议设置为 True，便于监控任务发送情况
    task_send_sent_event: bool = Field(
        default=True,
        description="是否发送任务发送事件",
    )

    # 是否发送任务开始事件
    # True: 任务开始执行时会产生事件
    # False: 不发送事件
    # 需要 task_track_started=True 才会生效
    # 建议设置为 True，便于监控任务执行进度
    task_send_started_event: bool = Field(
        default=True,
        description="是否发送任务开始事件",
    )

    # 是否发送任务成功事件
    # True: 任务成功完成时会产生事件
    # False: 不发送事件
    # 建议设置为 True，便于监控任务成功情况
    task_send_success_event: bool = Field(
        default=True,
        description="是否发送任务成功事件",
    )

    # 是否发送任务失败事件
    # True: 任务失败时会产生事件
    # False: 不发送事件
    # 建议设置为 True，便于监控任务失败情况和错误排查
    task_send_failure_event: bool = Field(
        default=True,
        description="是否发送任务失败事件",
    )

    # 是否发送任务重试事件
    # True: 任务重试时会产生事件
    # False: 不发送事件
    # 建议设置为 True，便于监控任务重试情况
    task_send_retry_event: bool = Field(
        default=True,
        description="是否发送任务重试事件",
    )

    # ==================== Celery Beat 配置 ====================

    # Beat 调度器文件名
    # 用于存储定时任务状态和下次执行时间
    # 文件通常存储在当前工作目录
    # 建议使用默认名称，便于识别
    # 可以指定完整路径，如: /var/lib/celery/celerybeat-schedule
    beat_schedule_filename: str = Field(
        default="celerybeat-schedule",
        description="Beat 调度器文件名",
    )

    # Beat 最大循环间隔（秒）
    # Beat 调度器检查任务的频率
    # 间隔越短，任务调度越精确，但 CPU 占用越高
    # 建议设置为 5-10 秒，平衡精度和性能
    # 对于高频任务（每分钟多次），可以设置得更小（如 1 秒）
    beat_max_loop_interval: int = Field(
        default=5,
        description="Beat 最大循环间隔（秒）",
    )

    # Beat 日志级别
    # 支持: DEBUG, INFO, WARNING, ERROR, CRITICAL
    # DEBUG: 最详细的日志
    # INFO: 一般信息（推荐）
    # WARNING: 只记录警告和错误
    # ERROR: 只记录错误
    # 建议生产环境使用 INFO 或 WARNING
    beat_loglevel: str = Field(
        default="INFO",
        description="Beat 日志级别",
    )

    # ==================== Flower 监控配置 ====================

    # Flower 监控工具配置
    # Flower 是 Celery 的 Web 监控界面
    # 可以实时查看任务状态、Worker 状态、任务统计等
    # 配置项:
    #   - port: 监控端口（默认 5555）
    #   - host: 监听地址（0.0.0.0 表示监听所有接口）
    #   - basic_auth: 基本认证，格式: 'user:password'
    #   - broker_api: RabbitMQ 管理接口 URL，用于获取队列信息
    #   - max_tasks: 最大任务显示数
    #   - max_workers: 最大 Worker 显示数
    #   - inspect_timeout: 检查超时时间（秒）
    #   - pool_recycler: 连接池回收时间（秒）
    flower: dict[str, Any] = Field(
        default_factory=lambda: {
            "port": 5555,
            "host": "0.0.0.0",
            "basic_auth": "",
            "broker_api": "",
            "max_tasks": 10000,
            "max_workers": 100,
            "inspect_timeout": 5,
            "pool_recycler": 3600,
        },
        description="Flower 监控工具配置",
    )

    # ==================== 任务模块配置 ====================

    # 任务模块列表（JSON 格式）
    # 用于指定需要加载的任务模块
    # 在 .env 文件中配置，格式为 JSON 数组
    # 示例:
    #   CELERY_INCLUDE_JSON='["Modules.admin.tasks.default_tasks", "Modules.tasks.email_tasks"]'
    # 可以动态加载不同的任务模块，无需修改代码
    include_json: str = Field(
        default='["Modules.admin.tasks.default_tasks"]',
        description="任务模块列表（JSON 格式）",
    )

    # 任务模块列表（计算属性）
    # 根据 include_json 自动转换为列表
    # 供 Celery 使用
    @property
    def include(self) -> list[str]:
        """
        将 JSON 配置转换为任务模块列表

        Returns:
            list[str]: 任务模块列表
        """
        try:
            return json.loads(self.include_json)
        except json.JSONDecodeError as e:
            logger.error(f"解析任务模块列表失败: {e}")
            logger.warning("使用默认任务模块配置")
            return ["Modules.admin.tasks.default_tasks"]

    # ==================== 定时任务配置 ====================

    # 定时任务调度配置（JSON 格式）
    # 用于定义定时任务的调度规则
    # 在 .env 文件中配置，格式为 JSON 对象
    # 注意：schedule 字段可以是数字（秒数）或字符串（crontab 表达式）
    # 示例（数字）:
    #   CELERY_BEAT_SCHEDULE_JSON='{
    #     "task_print_hello": {
    #       "task": "Modules.admin.tasks.default_tasks.print_hello_task",
    #       "schedule": 60.0
    #     }
    #   }'
    # 示例（crontab）:
    #   CELERY_BEAT_SCHEDULE_JSON='{
    #     "task_cleanup_data": {
    #       "task": "Modules.tasks.data_tasks.cleanup_data",
    #       "schedule": "crontab(hour=2, minute=0)"
    #     }
    #   }'
    beat_schedule_json: str = Field(
        default="",
        description="定时任务调度配置（JSON 格式）",
    )

    # 定时任务调度配置（计算属性）
    # 根据 beat_schedule_json 自动转换为 dict
    # 供 Celery 使用
    @property
    def beat_schedule(self) -> dict[str, Any]:
        """
        将 JSON 配置转换为定时任务调度配置

        Returns:
            dict[str, Any]: 定时任务调度配置
        """
        try:
            schedule_dict = json.loads(self.beat_schedule_json)
            # 转换 schedule 字符串为实际对象
            for task_config in schedule_dict.values():
                schedule_value = task_config.get("schedule")

                # 如果 schedule 是数字字符串，转换为 float
                if (
                    isinstance(schedule_value, str)
                    and schedule_value.replace(".", "").isdigit()
                ):
                    task_config["schedule"] = float(schedule_value)

                # 如果 schedule 是 crontab 字符串，保持原样（Celery 会自动解析）
                # 例如: "crontab(hour=2, minute=0)"

            return schedule_dict
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"解析定时任务配置失败: {e}")
            logger.warning("使用默认定时任务配置")
            return {
                "task_print_hello": {
                    "task": "Modules.admin.tasks.default_tasks.print_hello_task",
                    "schedule": 60.0,
                }
            }

    # ==================== 任务队列配置 ====================

    # 任务队列配置（JSON 格式）
    # 用于定义多个队列，实现任务优先级和隔离
    # 在 .env 文件中配置，格式为 JSON 数组
    # 示例:
    #   CELERY_TASK_QUEUES_JSON='[{"name": "default", "exchange": "default", "routing_key": "default"}]'
    #   CELERY_TASK_QUEUES_JSON='[
    #     {"name": "default", "exchange": "default", "routing_key": "default"},
    #     {"name": "high_priority", "exchange": "high_priority", "routing_key": "high_priority"},
    #     {"name": "low_priority", "exchange": "low_priority", "routing_key": "low_priority"}
    #   ]'
    # 可以通过 task_routes 将不同任务路由到不同队列
    # Worker 可以订阅特定队列，实现任务隔离
    task_queues_json: str = Field(
        default="",
        description="任务队列配置（JSON 格式）",
    )

    # 任务队列配置列表（计算属性）
    # 根据 task_queues_json 自动转换为 Queue 对象列表
    # 供 Celery 使用
    @property
    def task_queues(self) -> list[Queue]:
        """
        将 JSON 配置转换为 Queue 对象列表

        Returns:
            list[Queue]: Queue 对象列表
        """
        try:
            queues_dict = json.loads(self.task_queues_json)
            queues = []
            for q in queues_dict:
                queues.append(
                    Queue(
                        q["name"],
                        exchange=q.get("exchange", q["name"]),
                        routing_key=q.get("routing_key", q["name"]),
                    )
                )
            return queues
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"解析队列配置失败: {e}")
            logger.warning("使用默认队列配置")
            return [Queue("default", exchange="default", routing_key="default")]

    # 任务路由配置
    # 用于将不同任务路由到不同的队列
    # 支持多种路由方式:
    #   1. 基于任务名路由: {'tasks.email': {'queue': 'email_queue'}}
    #   2. 基于任务名模式: {'tasks.*': {'queue': 'default'}}
    #   3. 基于任务参数: {'tasks.process': {'queue': lambda args: 'high' if args.get('priority') == 'high' else 'low'}}
    # 示例:
    #   {
    #     'tasks.send_email': {'queue': 'email_queue', 'routing_key': 'email'},
    #     'tasks.process_image': {'queue': 'image_queue', 'routing_key': 'image'},
    #     'tasks.*': {'queue': 'default'}
    #   }
    # 建议根据业务需求配置，实现任务优先级和隔离
    task_routes: dict[str, Any] = Field(
        default_factory=lambda: {},
        description="任务路由配置",
    )

    # ==================== FastAPI 集成配置 ====================

    # 是否在 FastAPI 应用启动时验证 Celery 连接
    # True: 应用启动时验证 Celery 是否能正常连接到 Broker
    # False: 不验证连接，直接启动应用
    # 开发环境建议设置为 True，便于及时发现连接问题
    # 生产环境可根据情况设置，如果 Broker 暂时不可用，可以设置为 False 避免启动失败
    verify_on_startup: bool = Field(
        default=True,
        description="是否在应用启动时验证 Celery 连接",
    )

    # ==================== 其他配置 ====================

    # 任务压缩算法
    # 支持: gzip, bzip2, zlib
    # 空字符串表示不压缩
    # 压缩可以减少网络传输量，但会增加 CPU 开销
    # 建议对于大任务（参数或结果 > 1KB）启用压缩
    # 常用: gzip（压缩率高，速度快）
    task_compression: str = Field(
        default="",
        description="任务压缩算法",
    )

    # 任务压缩阈值（字节）
    # 超过此大小的任务会被压缩
    # 0 表示总是压缩
    # 建议设置为 1024-4096 字节（1-4KB）
    # 根据任务大小和网络带宽调整
    task_compression_threshold: int = Field(
        default=1024,
        description="任务压缩阈值（字节）",
    )

    # 结果压缩算法
    # 支持: gzip, bzip2, zlib
    # 空字符串表示不压缩
    # 压缩可以减少存储空间，但会增加 CPU 开销
    # 建议对于大结果启用压缩
    result_compression: str = Field(
        default="",
        description="结果压缩算法",
    )

    # 结果压缩阈值（字节）
    # 超过此大小的结果会被压缩
    # 0 表示总是压缩
    # 建议设置为 1024-4096 字节（1-4KB）
    # 根据结果大小和存储成本调整
    result_compression_threshold: int = Field(
        default=1024,
        description="结果压缩阈值（字节）",
    )
