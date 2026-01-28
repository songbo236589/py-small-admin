"""
文件上传配置类

该配置类基于 Pydantic Settings，可以从环境变量中读取配置。
所有环境变量都需要以 "UPLOAD_" 为前缀，例如：UPLOAD_MAX_FILE_SIZE, UPLOAD_DIR 等。

使用示例：
    config = UploadConfig()
    max_size = config.max_file_size
"""

from enum import Enum

from pydantic import Field

from config.base import BaseConfig


class FilenameRule(str, Enum):
    """
    文件命名规则枚举

    使用 Enum 的好处：
    - 防止 FILENAME_RULE 拼写错误
    - IDE 可自动补全
    - 代码中可安全判断命名规则
    """

    uuid = "uuid"
    timestamp = "timestamp"
    md5 = "md5"
    original = "original"


class PathRule(str, Enum):
    """
    文件路径规则枚举

    使用 Enum 的好处：
    - 防止 PATH_RULE 拼写错误
    - IDE 可自动补全
    - 代码中可安全判断路径规则
    """

    ymd = "Y-m-d"  # 年-月-日
    ym = "Y-m"  # 年-月
    y = "Y"  # 年


class UploadConfig(BaseConfig):
    """
    文件上传配置类

    该配置类存储文件上传的基础配置和敏感信息（如云存储密钥）。
    """

    # 继承 BaseConfig 的配置，并添加环境变量前缀
    # 这意味着所有环境变量都需要以 "UPLOAD_" 开头
    model_config = BaseConfig.model_config | {"env_prefix": "UPLOAD_"}

    # ==================== 基础配置 ====================

    # 上传根目录
    # 本地存储时，文件将保存在此目录下
    # 环境变量: UPLOAD_DIR
    # 开发环境: ./uploads（相对路径）
    # 生产环境: /var/www/uploads 或 /data/uploads（绝对路径）
    dir: str = Field(default="./uploads", description="上传根目录")

    # URL 访问前缀
    # 用于静态文件访问的 URL 路径前缀
    # 环境变量: UPLOAD_URL_PREFIX
    # 开发环境: /uploads
    # 生产环境: /static 或自定义路径
    url_prefix: str = Field(default="/uploads", description="URL 访问前缀")

    # 文件命名规则
    # 可选值: uuid（UUID命名）, timestamp（时间戳命名）, md5（MD5哈希命名）, original（原始文件名，重复时自动加数字后缀）
    # 环境变量: UPLOAD_FILENAME_RULE
    filename_rule: FilenameRule = Field(
        default=FilenameRule.uuid, description="文件命名规则"
    )

    # 文件路径规则
    # 可选值: Y-m-d（年-月-日）, Y-m（年-月）, Y（年）
    # 环境变量: UPLOAD_PATH_RULE
    path_rule: PathRule = Field(
        default=PathRule.ymd, description="文件路径规则(Y-m-d, Y-m, Y等)"
    )

    # ==================== 阿里云 OSS 配置 ====================

    # OSS 访问密钥 ID（敏感信息）
    # 环境变量: UPLOAD_OSS_ACCESS_KEY_ID
    oss_access_key_id: str = Field(default="", description="OSS Access Key ID")

    # OSS 访问密钥 Secret（敏感信息）
    # 环境变量: UPLOAD_OSS_ACCESS_KEY_SECRET
    oss_access_key_secret: str = Field(default="", description="OSS Access Key Secret")

    # OSS 区域节点
    # 例如: oss-cn-hangzhou, oss-cn-beijing
    # 环境变量: UPLOAD_OSS_REGION
    oss_region: str = Field(default="oss-cn-hangzhou", description="OSS 区域节点")

    # OSS Bucket 名称
    # 环境变量: UPLOAD_OSS_BUCKET
    oss_bucket: str = Field(default="", description="OSS Bucket 名称")

    # OSS 端点地址
    # 如果不指定，会根据 region 自动生成
    # 环境变量: UPLOAD_OSS_ENDPOINT
    oss_endpoint: str = Field(default="", description="OSS 端点地址")

    # OSS 内网端点地址
    # 用于 ECS 内网访问 OSS，速度更快且不产生公网流量费用
    # 环境变量: UPLOAD_OSS_INTERNAL_ENDPOINT
    oss_internal_endpoint: str = Field(default="", description="OSS 内网端点地址")

    # OSS 访问域名前缀
    # 用于自定义域名访问
    # 环境变量: UPLOAD_OSS_CDN_DOMAIN
    oss_cdn_domain: str = Field(default="", description="OSS CDN 域名")

    # ==================== 腾讯云 COS 配置 ====================

    # COS 访问密钥 ID（敏感信息）
    # 环境变量: UPLOAD_COS_SECRET_ID
    cos_secret_id: str = Field(default="", description="COS Secret ID")

    # COS 访问密钥 Key（敏感信息）
    # 环境变量: UPLOAD_COS_SECRET_KEY
    cos_secret_key: str = Field(default="", description="COS Secret Key")

    # COS 区域
    # 例如: ap-guangzhou, ap-shanghai, ap-beijing
    # 环境变量: UPLOAD_COS_REGION
    cos_region: str = Field(default="ap-guangzhou", description="COS 区域")

    # COS Bucket 名称
    # 格式: bucket-name-appid
    # 环境变量: UPLOAD_COS_BUCKET
    cos_bucket: str = Field(default="", description="COS Bucket 名称")

    # COS 端点地址
    # 如果不指定，会根据 region 自动生成
    # 环境变量: UPLOAD_COS_ENDPOINT
    cos_endpoint: str = Field(default="", description="COS 端点地址")

    # COS CDN 域名
    # 用于自定义域名访问
    # 环境变量: UPLOAD_COS_CDN_DOMAIN
    cos_cdn_domain: str = Field(default="", description="COS CDN 域名")

    # ==================== 七牛云 Kodo 配置 ====================

    # Kodo 访问密钥（敏感信息）
    # 环境变量: UPLOAD_KODO_ACCESS_KEY
    kodo_access_key: str = Field(default="", description="Kodo Access Key")

    # Kodo 访问密钥 Secret（敏感信息）
    # 环境变量: UPLOAD_KODO_SECRET_KEY
    kodo_secret_key: str = Field(default="", description="Kodo Secret Key")

    # Kodo Bucket 名称
    # 环境变量: UPLOAD_KODO_BUCKET
    kodo_bucket: str = Field(default="", description="Kodo Bucket 名称")

    # Kodo 存储区域
    # 例如: z0（华东）, z1（华北）, z2（华南）, na0（北美）, as0（东南亚）
    # 环境变量: UPLOAD_KODO_REGION
    kodo_region: str = Field(default="z0", description="Kodo 存储区域")

    # Kodo 域名前缀
    # 用于自定义域名访问
    # 环境变量: UPLOAD_KODO_DOMAIN
    kodo_domain: str = Field(default="", description="Kodo 域名")
