"""
Alembic环境配置 - 模块 quant
"""

import os
import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入模块的模型
try:
    # 导入所有模型类以确保它们被注册到元数据中
    from Modules.quant.models import *  # 导入模块中的所有模型
    from Modules.common.models.base_model import BaseModel
    from sqlmodel import SQLModel

    # 获取 SQLModel 的元数据，这包含了所有已注册的模型
    target_metadata = SQLModel.metadata

except ImportError as e:
    print(f"警告: 无法导入模块 quant 的模型: {e}")
    target_metadata = None

# Alembic配置对象
config = context.config

# 设置数据库URL - 直接从配置文件获取
try:
    from Modules.common.libs.config import Config

    # 获取数据库配置
    default_connection = Config.get("database.default", "mysql")
    connections = Config.get("database.connections", {})
    db_config = connections.get(default_connection, {})

    # 构建数据库URL
    if db_config.get("url"):
        database_url = db_config["url"]
    else:
        # 根据配置构建URL
        driver = db_config.get("driver", "mysql")
        host = db_config.get("host", "127.0.0.1")
        port = db_config.get("port", 3306)
        database = db_config.get("database", "forge")
        username = db_config.get("username", "forge")
        password = db_config.get("password", "")
        charset = db_config.get("charset", "utf8mb4")

        # 根据驱动类型构建URL
        if driver == "mysql":
            database_url = f"mysql+mysqldb://{username}:{password}@{host}:{port}/{database}"
            # 添加额外参数
            params = [f"charset={charset}"]
            database_url += "?" + "&".join(params)
        elif driver == "pgsql":
            database_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
        elif driver == "sqlite":
            database_url = f"sqlite:///{database}"
        elif driver == "sqlsrv":
            database_url = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"不支持的数据库驱动: {driver}")

    # 设置数据库URL到Alembic配置
    config.set_main_option("sqlalchemy.url", database_url)
    print(f"成功设置数据库URL: {database_url}")

except Exception as e:
    print(f"警告: 无法从配置文件获取数据库URL: {e}")
    # 如果配置文件获取失败，使用默认值
    # 注意：这个默认值仅用于紧急情况，实际应该通过配置文件设置
    default_url = "mysql+mysqldb://root:root@127.0.0.1:3306/fastapi_db?charset=utf8mb4"
    config.set_main_option("sqlalchemy.url", default_url)
    print(f"使用默认数据库URL: {default_url}")
    print("建议：请在项目配置文件中正确设置数据库连接参数")

# 解释配置文件的日志记录
if config.config_file_name is not None:
    # 禁用Alembic的默认日志配置，避免与项目日志系统冲突
    # fileConfig(config.config_file_name)

    # 使用更简单的日志配置，避免格式字符串问题
    import logging

    # 创建一个简单的格式化器
    formatter = logging.Formatter('%(levelname)-5.5s [%(name)s] %(message)s')

    # 获取Alembic的logger并设置级别
    alembic_logger = logging.getLogger('alembic')
    alembic_logger.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 添加处理器到Alembic logger
    alembic_logger.addHandler(console_handler)

    # 设置SQLAlchemy logger级别为WARNING，减少冗余输出
    sqlalchemy_logger = logging.getLogger('sqlalchemy')
    sqlalchemy_logger.setLevel(logging.WARNING)

# 定义包含对象过滤器，只处理当前模块的表
def include_object(object, name, type_, reflected, compare_to):
    """
    过滤器函数，只处理当前模块的表

    Args:
        object: SQLAlchemy 对象
        name: 对象名称
        type_: 对象类型（table, column, index等）
        reflected: 是否从数据库反射
        compare_to: 比较对象

    Returns:
        bool: True 表示包含该对象，False 表示排除
    """
    # 只处理表对象
    if type_ == "table" and name:
        # 获取表前缀配置
        try:
            from Modules.common.libs.config import Config
            default_connection = Config.get("database.default", "mysql")
            connections = Config.get("database.connections", {})
            db_config = connections.get(default_connection, {})
            table_prefix = db_config.get("prefix", "fa_")
        except Exception:
            table_prefix = "fa_"

        # 检查表名是否属于当前模块
        expected_prefix = f"{table_prefix}quant_"
        if name.startswith(expected_prefix):
            return True
        # 排除其他模块的表
        return False

    # 处理索引对象
    if type_ == "index" and name:
        try:
            from Modules.common.libs.config import Config
            default_connection = Config.get("database.default", "mysql")
            connections = Config.get("database.connections", {})
            db_config = connections.get(default_connection, {})
            table_prefix = db_config.get("prefix", "fa_")
        except Exception:
            table_prefix = "fa_"
        # 索引名称格式：ix_表名_字段名 或 uq_表名_字段名
        # 直接检查索引名称中是否包含模块的表名
        expected_table_name = f"{table_prefix}quant"
        if expected_table_name in name:
            return True
        return False

    # 处理约束对象（外键等）
    if type_ == "constraint" and name:
        try:
            from Modules.common.libs.config import Config
            default_connection = Config.get("database.default", "mysql")
            connections = Config.get("database.connections", {})
            db_config = connections.get(default_connection, {})
            table_prefix = db_config.get("prefix", "fa_")
        except Exception:
            table_prefix = "fa_"

        # 约束名称通常包含表名
        expected_table_name = f"{table_prefix}quant"
        if expected_table_name in name:
            return True
        return False
    return True

def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移"""
    url = config.get_main_option("sqlalchemy.url")

    # 获取表前缀配置
    try:
        from Modules.common.libs.config import Config
        # 获取默认连接配置
        default_connection = Config.get("database.default", "mysql")
        connections = Config.get("database.connections", {})
        db_config = connections.get(default_connection, {})
        table_prefix = db_config.get("prefix", "fa_")
        version_table = f"{table_prefix}quant_alembic_versions"
        print(f"使用版本表: {version_table}")
    except Exception as e:
        print(f"警告: 无法获取表前缀配置: {e}")
        version_table = f"fa_quant_alembic_versions"
        print(f"使用默认版本表: {version_table}")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=version_table,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """在'在线'模式下运行迁移"""
    config_section = config.get_section(config.config_ini_section) or {}
    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # 获取表前缀配置
        try:
            from Modules.common.libs.config import Config
            # 获取默认连接配置
            default_connection = Config.get("database.default", "mysql")
            connections = Config.get("database.connections", {})
            db_config = connections.get(default_connection, {})
            table_prefix = db_config.get("prefix", "fa_")
            version_table = f"{table_prefix}quant_alembic_versions"
            print(f"使用版本表: {version_table}")
        except Exception as e:
            print(f"警告: 无法获取表前缀配置: {e}")
            version_table = f"fa_quant_alembic_versions"
            print(f"使用默认版本表: {version_table}")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=version_table,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
