#!/usr/bin/env python3
"""
数据库迁移工具

提供完整的数据库迁移命令行接口，支持多模块独立的数据库迁移管理。
每个模块都有自己独立的迁移系统，可以独立管理和执行数据库变更。

使用示例:
    python -m commands.migrate init --module example
    python -m commands.migrate create --module example --message "添加示例数据表"
    python -m commands.migrate up --module example
    python -m commands.migrate down --module example
    python -m commands.migrate list
"""

import argparse
import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from alembic import command
    from alembic.config import Config as AlembicConfig
    from alembic.runtime.migration import MigrationContext
    from loguru import logger

    # 清理SQLModel元数据，避免旧表名冲突
    from sqlmodel import SQLModel

    from Modules.common.libs.config import Config as AppConfig

    # 导入项目相关模块
    from Modules.common.libs.database.sql.engine import get_db_engine
    from Modules.common.models.base_model import BaseModel

    SQLModel.metadata.clear()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包，并且在项目根目录下运行此脚本")
    sys.exit(1)


class ModuleDiscovery:
    """模块发现器 - 负责自动发现项目中的所有模块"""

    def __init__(self):
        """初始化模块发现器"""
        self.modules_path = project_root / "Modules"
        self._discovered_modules = None

    def discover_modules(self) -> list[str]:
        """
        扫描Modules目录，发现所有模块

        Returns:
            List[str]: 模块名称列表
        """
        if self._discovered_modules is not None:
            return self._discovered_modules

        modules = []

        if not self.modules_path.exists():
            logger.error(f"Modules目录不存在: {self.modules_path}")
            return modules

        # 扫描Modules目录下的所有子目录
        for item in self.modules_path.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                # 检查是否是有效的模块（包含models目录）
                models_path = item / "models"
                if models_path.exists() and models_path.is_dir():
                    # 检查是否有__init__.py文件
                    init_file = models_path / "__init__.py"
                    if init_file.exists():
                        modules.append(item.name)
                        logger.debug(f"发现模块: {item.name}")

        self._discovered_modules = sorted(modules)
        return self._discovered_modules

    def get_module_models(self, module_name: str) -> list[type]:
        """
        获取指定模块的所有模型类

        Args:
            module_name: 模块名称

        Returns:
            List[Type]: 模型类列表
        """
        models = []

        try:
            # 导入模块的models包
            models_package = f"Modules.{module_name}.models"
            module = importlib.import_module(models_package)

            # 获取所有继承自BaseModel的类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseModel)
                    and obj != BaseModel
                    and obj.__module__ == models_package
                ):
                    models.append(obj)
                    logger.debug(f"发现模型 {module_name}.{name}")

        except ImportError as e:
            logger.error(f"无法导入模块 {module_name}: {e}")

        return models

    def validate_module_structure(self, module_name: str) -> bool:
        """
        验证模块结构是否符合要求

        Args:
            module_name: 模块名称

        Returns:
            bool: 验证结果
        """
        module_path = self.modules_path / module_name

        # 检查模块目录是否存在
        if not module_path.exists():
            logger.error(f"模块目录不存在: {module_path}")
            return False

        # 检查models目录是否存在
        models_path = module_path / "models"
        if not models_path.exists():
            logger.error(f"models目录不存在: {models_path}")
            return False

        # 检查是否有模型文件
        model_files = list(models_path.glob("*.py"))
        if not model_files:
            logger.warning(f"模块 {module_name} 没有找到模型文件")
            return False

        return True


class MigrationManager:
    """迁移管理器 - 负责管理各模块的数据库迁移"""

    def __init__(self):
        """初始化迁移管理器"""
        self.module_discovery = ModuleDiscovery()
        self._db_config = None

    def _get_db_config(self) -> dict[str, Any]:
        """获取数据库配置"""
        if self._db_config is None:
            try:
                # 获取默认连接配置
                default_connection = AppConfig.get("database.default", "mysql")
                connections = AppConfig.get("database.connections", {})
                self._db_config = connections.get(default_connection, {})
            except Exception as e:
                logger.error(f"获取数据库配置失败: {e}")
                self._db_config = {}

        return self._db_config

    def _get_database_url(self) -> str:
        """获取数据库连接URL"""
        # 尝试从配置构建URL
        config = self._get_db_config()
        if config.get("url"):
            return config["url"]

        # 构建URL
        driver = config.get("driver", "mysql")
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 3306)
        database = config.get("database", "forge")
        username = config.get("username", "forge")
        password = config.get("password", "")
        charset = config.get("charset", "utf8mb4")

        # 根据驱动类型构建URL
        if driver == "mysql":
            # MySQL 使用 mysqlclient 驱动
            url = f"mysql+mysqldb://{username}:{password}@{host}:{port}/{database}"
        elif driver == "pgsql":
            # PostgreSQL
            url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
        elif driver == "sqlite":
            # SQLite
            url = f"sqlite:///{database}"
        elif driver == "sqlsrv":
            # SQL Server
            url = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"不支持的数据库驱动: {driver}")

        # 添加额外参数
        params = []
        if driver == "mysql":
            params.append(f"charset={charset}")
            # 注意：time_zone 不能作为连接参数，应该在连接后通过 SQL 设置

        if params:
            url += "?" + "&".join(params)

        return url

    def _get_migration_dir(self, module_name: str) -> Path:
        """获取模块的迁移目录"""
        return project_root / "Modules" / module_name / "migrations"

    def _get_versions_dir(self, module_name: str) -> Path:
        """获取模块的迁移版本目录"""
        return self._get_migration_dir(module_name) / "versions"

    def init_migration(self, module_name: str) -> bool:
        """
        为指定模块初始化迁移系统

        Args:
            module_name: 模块名称

        Returns:
            bool: 初始化是否成功
        """
        logger.info(f"正在初始化模块 {module_name} 的迁移系统...")

        # 验证模块结构
        if not self.module_discovery.validate_module_structure(module_name):
            logger.error(f"模块 {module_name} 结构验证失败")
            return False

        # 创建迁移目录结构
        migration_dir = self._get_migration_dir(module_name)
        versions_dir = self._get_versions_dir(module_name)

        try:
            # 创建目录
            migration_dir.mkdir(parents=True, exist_ok=True)
            versions_dir.mkdir(parents=True, exist_ok=True)

            # 创建__init__.py文件
            (migration_dir / "__init__.py").touch()
            (versions_dir / "__init__.py").touch()

            # 创建alembic.ini配置文件
            alembic_ini_content = self._generate_alembic_ini(module_name)
            (migration_dir / "alembic.ini").write_text(
                alembic_ini_content, encoding="utf-8"
            )

            # 创建env.py环境配置文件
            env_py_content = self._generate_env_py(module_name)
            (migration_dir / "env.py").write_text(env_py_content, encoding="utf-8")

            # 创建script.py.mako模板文件
            script_mako_content = self._generate_script_mako()
            (migration_dir / "script.py.mako").write_text(
                script_mako_content, encoding="utf-8"
            )

            logger.info(f"模块 {module_name} 迁移系统初始化完成")
            return True

        except Exception as e:
            logger.error(f"初始化模块 {module_name} 迁移系统失败: {e}")
            return False

    def _generate_alembic_ini(self, module_name: str) -> str:
        """生成alembic.ini配置文件内容"""
        return f"""# Alembic配置文件 - 模块 {module_name}

[alembic]
# 迁移脚本路径
script_location = Modules/{module_name}/migrations

# 模板文件路径
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# 版本路径分隔符
version_path_separator = os

# 数据库连接URL
# 注意：此配置项由env.py动态设置，此处保留仅为文档目的
# 实际连接参数从项目配置文件中读取，支持多种数据库类型
sqlalchemy.url =

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    def _generate_env_py(self, module_name: str) -> str:
        """生成env.py环境配置文件内容"""
        return f'''"""
Alembic环境配置 - 模块 {module_name}
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
    from Modules.{module_name}.models import *  # 导入模块中的所有模型
    from Modules.common.models.base_model import BaseModel
    from sqlmodel import SQLModel

    # 获取 SQLModel 的元数据，这包含了所有已注册的模型
    target_metadata = SQLModel.metadata

except ImportError as e:
    print(f"警告: 无法导入模块 {module_name} 的模型: {{e}}")
    target_metadata = None

# Alembic配置对象
config = context.config

# 设置数据库URL - 直接从配置文件获取
try:
    from Modules.common.libs.config import Config

    # 获取数据库配置
    default_connection = Config.get("database.default", "mysql")
    connections = Config.get("database.connections", {{}})
    db_config = connections.get(default_connection, {{}})

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
            database_url = f"mysql+mysqldb://{{username}}:{{password}}@{{host}}:{{port}}/{{database}}"
            # 添加额外参数
            params = [f"charset={{charset}}"]
            database_url += "?" + "&".join(params)
        elif driver == "pgsql":
            database_url = f"postgresql+asyncpg://{{username}}:{{password}}@{{host}}:{{port}}/{{database}}"
        elif driver == "sqlite":
            database_url = f"sqlite:///{{database}}"
        elif driver == "sqlsrv":
            database_url = f"mssql+pyodbc://{{username}}:{{password}}@{{host}}:{{port}}/{{database}}"
        else:
            raise ValueError(f"不支持的数据库驱动: {{driver}}")

    # 设置数据库URL到Alembic配置
    config.set_main_option("sqlalchemy.url", database_url)
    print(f"成功设置数据库URL: {{database_url}}")

except Exception as e:
    print(f"警告: 无法从配置文件获取数据库URL: {{e}}")
    # 如果配置文件获取失败，使用默认值
    # 注意：这个默认值仅用于紧急情况，实际应该通过配置文件设置
    default_url = "mysql+mysqldb://root:root@127.0.0.1:3306/fastapi_db?charset=utf8mb4"
    config.set_main_option("sqlalchemy.url", default_url)
    print(f"使用默认数据库URL: {{default_url}}")
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
            connections = Config.get("database.connections", {{}})
            db_config = connections.get(default_connection, {{}})
            table_prefix = db_config.get("prefix", "fa_")
        except Exception:
            table_prefix = "fa_"

        # 检查表名是否属于当前模块
        expected_prefix = f"{{table_prefix}}{module_name}_"
        if name.startswith(expected_prefix):
            return True
        # 排除其他模块的表
        return False

    # 处理索引对象
    if type_ == "index" and name:
        try:
            from Modules.common.libs.config import Config
            default_connection = Config.get("database.default", "mysql")
            connections = Config.get("database.connections", {{}})
            db_config = connections.get(default_connection, {{}})
            table_prefix = db_config.get("prefix", "fa_")
        except Exception:
            table_prefix = "fa_"
        # 索引名称格式：ix_表名_字段名 或 uq_表名_字段名
        # 直接检查索引名称中是否包含模块的表名
        expected_table_name = f"{{table_prefix}}{module_name}"
        if expected_table_name in name:
            return True
        return False

    # 处理约束对象（外键等）
    if type_ == "constraint" and name:
        try:
            from Modules.common.libs.config import Config
            default_connection = Config.get("database.default", "mysql")
            connections = Config.get("database.connections", {{}})
            db_config = connections.get(default_connection, {{}})
            table_prefix = db_config.get("prefix", "fa_")
        except Exception:
            table_prefix = "fa_"

        # 约束名称通常包含表名
        expected_table_name = f"{{table_prefix}}{module_name}"
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
        connections = Config.get("database.connections", {{}})
        db_config = connections.get(default_connection, {{}})
        table_prefix = db_config.get("prefix", "fa_")
        version_table = f"{{table_prefix}}{module_name}_alembic_versions"
        print(f"使用版本表: {{version_table}}")
    except Exception as e:
        print(f"警告: 无法获取表前缀配置: {{e}}")
        version_table = f"fa_{module_name}_alembic_versions"
        print(f"使用默认版本表: {{version_table}}")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
        version_table=version_table,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """在'在线'模式下运行迁移"""
    config_section = config.get_section(config.config_ini_section) or {{}}
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
            connections = Config.get("database.connections", {{}})
            db_config = connections.get(default_connection, {{}})
            table_prefix = db_config.get("prefix", "fa_")
            version_table = f"{{table_prefix}}{module_name}_alembic_versions"
            print(f"使用版本表: {{version_table}}")
        except Exception as e:
            print(f"警告: 无法获取表前缀配置: {{e}}")
            version_table = f"fa_{module_name}_alembic_versions"
            print(f"使用默认版本表: {{version_table}}")

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
'''

    def _generate_script_mako(self) -> str:
        """生成script.py.mako模板文件内容"""
        return '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''

    def create_migration(self, module_name: str, message: str) -> bool:
        """
        为指定模块创建新的迁移文件

        Args:
            module_name: 模块名称
            message: 迁移描述

        Returns:
            bool: 创建是否成功
        """
        logger.info(f"正在为模块 {module_name} 创建迁移: {message}")

        # 检查迁移系统是否已初始化
        migration_dir = self._get_migration_dir(module_name)
        if not migration_dir.exists():
            logger.error(f"模块 {module_name} 的迁移系统未初始化，请先运行 init 命令")
            return False

        try:
            # 创建Alembic配置
            alembic_cfg = AlembicConfig(str(migration_dir / "alembic.ini"))

            # 处理Windows编码问题
            if os.name == "nt":  # Windows系统
                os.environ["PYTHONIOENCODING"] = "utf-8"

            # 生成迁移
            # 在生成迁移前清理SQLModel元数据，避免旧表名冲突
            from sqlmodel import SQLModel

            SQLModel.metadata.clear()
            # 使用sql=False来强制生成迁移，忽略数据库状态
            command.revision(alembic_cfg, autogenerate=True, message=message, sql=False)

            logger.info(f"模块 {module_name} 迁移创建完成")
            return True

        except Exception as e:
            logger.error(f"创建模块 {module_name} 迁移失败: {e}")
            return False

    def upgrade(
        self, module_name: str | None = None, revision: str | None = None
    ) -> bool:
        """
        执行迁移升级

        Args:
            module_name: 模块名称，如果为None则升级所有模块
            revision: 目标版本，如果为None则升级到最新版本

        Returns:
            bool: 升级是否成功
        """
        if module_name:
            return self._upgrade_module(module_name, revision)
        else:
            # 升级所有模块
            modules = self.module_discovery.discover_modules()
            success = True
            for mod in modules:
                if not self._upgrade_module(mod, revision):
                    success = False
            return success

    def _upgrade_module(self, module_name: str, revision: str | None = None) -> bool:
        """升级单个模块"""
        logger.info(
            f"正在升级模块 {module_name}" + (f" 到版本 {revision}" if revision else "")
        )

        # 检查迁移系统是否已初始化
        migration_dir = self._get_migration_dir(module_name)
        if not migration_dir.exists():
            logger.warning(f"模块 {module_name} 的迁移系统未初始化，跳过")
            return True

        try:
            # 创建Alembic配置
            alembic_cfg = AlembicConfig(str(migration_dir / "alembic.ini"))

            # 执行升级
            if revision:
                command.upgrade(alembic_cfg, revision)
            else:
                command.upgrade(alembic_cfg, "head")

            logger.info(f"模块 {module_name} 升级完成")
            return True

        except Exception as e:
            logger.error(f"升级模块 {module_name} 失败: {e}")
            return False

    def downgrade(self, module_name: str, revision: str | None = None) -> bool:
        """
        执行迁移降级

        Args:
            module_name: 模块名称
            revision: 目标版本，如果为None则降级一个版本

        Returns:
            bool: 降级是否成功
        """
        logger.info(
            f"正在降级模块 {module_name}" + (f" 到版本 {revision}" if revision else "")
        )

        # 检查迁移系统是否已初始化
        migration_dir = self._get_migration_dir(module_name)
        if not migration_dir.exists():
            logger.error(f"模块 {module_name} 的迁移系统未初始化")
            return False

        try:
            # 创建Alembic配置
            alembic_cfg = AlembicConfig(str(migration_dir / "alembic.ini"))

            # 执行降级
            if revision:
                command.downgrade(alembic_cfg, revision)
            else:
                command.downgrade(alembic_cfg, "-1")

            logger.info(f"模块 {module_name} 降级完成")
            return True

        except Exception as e:
            logger.error(f"降级模块 {module_name} 失败: {e}")
            return False

    def list_modules(self) -> None:
        """列出所有模块及其状态"""
        modules = self.module_discovery.discover_modules()

        if not modules:
            print("未发现任何模块")
            return

        print("\n发现的模块:")
        print("-" * 60)
        print(f"{'模块名称':<20} {'迁移状态':<15} {'当前版本':<15} {'版本表':<20}")
        print("-" * 60)

        for module_name in modules:
            migration_dir = self._get_migration_dir(module_name)
            if migration_dir.exists():
                try:
                    # 获取系统表前缀配置
                    table_prefix = AppConfig.get("database.table_prefix", "fa_")
                    version_table = f"{table_prefix}{module_name}_alembic_versions"

                    # 使用数据库引擎直接创建连接
                    engine = get_db_engine()
                    with engine.connect() as connection:
                        # 为特定模块配置MigrationContext
                        context = MigrationContext.configure(
                            connection, opts={"version_table": version_table}
                        )
                        current_rev = context.get_current_revision()

                        if current_rev:
                            current_rev = current_rev[:8]  # 显示前8位
                        else:
                            current_rev = "无"

                        status = "已初始化"
                except Exception:
                    status = "错误"
                    current_rev = "未知"
                    version_table = "未知"
            else:
                status = "未初始化"
                current_rev = "-"
                version_table = "-"

            print(
                f"{module_name:<20} {status:<15} {current_rev:<15} {version_table:<20}"
            )

        print("-" * 60)

    def history(self, module_name: str) -> None:
        """查看模块的迁移历史"""
        logger.info(f"查看模块 {module_name} 的迁移历史")

        # 检查迁移系统是否已初始化
        migration_dir = self._get_migration_dir(module_name)
        if not migration_dir.exists():
            logger.error(f"模块 {module_name} 的迁移系统未初始化")
            return

        try:
            # 创建Alembic配置
            alembic_cfg = AlembicConfig(str(migration_dir / "alembic.ini"))

            # 显示历史
            command.history(alembic_cfg)

        except Exception as e:
            logger.error(f"获取模块 {module_name} 迁移历史失败: {e}")

    def current(self, module_name: str) -> None:
        """查看模块的当前版本"""
        logger.info(f"查看模块 {module_name} 的当前版本")

        # 检查迁移系统是否已初始化
        migration_dir = self._get_migration_dir(module_name)
        if not migration_dir.exists():
            logger.error(f"模块 {module_name} 的迁移系统未初始化")
            return

        try:
            # 创建Alembic配置
            alembic_cfg = AlembicConfig(str(migration_dir / "alembic.ini"))

            # 显示当前版本
            command.current(alembic_cfg)

        except Exception as e:
            logger.error(f"获取模块 {module_name} 当前版本失败: {e}")

    def validate(self, module_name: str) -> bool:
        """
        验证模块迁移系统

        Args:
            module_name: 模块名称

        Returns:
            bool: 验证是否通过
        """
        logger.info(f"验证模块 {module_name} 的迁移系统")

        # 验证模块结构
        if not self.module_discovery.validate_module_structure(module_name):
            logger.error(f"模块 {module_name} 结构验证失败")
            return False

        # 检查迁移系统是否已初始化
        migration_dir = self._get_migration_dir(module_name)
        if not migration_dir.exists():
            logger.error(f"模块 {module_name} 的迁移系统未初始化")
            return False

        # 检查必要文件
        required_files = ["alembic.ini", "env.py", "script.py.mako"]
        for file_name in required_files:
            file_path = migration_dir / file_name
            if not file_path.exists():
                logger.error(f"缺少必要文件: {file_path}")
                return False

        # 检查versions目录
        versions_dir = migration_dir / "versions"
        if not versions_dir.exists():
            logger.error(f"versions目录不存在: {versions_dir}")
            return False

        logger.info(f"模块 {module_name} 迁移系统验证通过")
        return True


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="数据库迁移工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m commands.migrate init --module example
  python -m commands.migrate create --module example --message "添加示例数据表"
  python -m commands.migrate up --module example
  python -m commands.migrate down --module example
  python -m commands.migrate list
  python -m commands.migrate history --module example
  python -m commands.migrate current --module example
  python -m commands.migrate validate --module example
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化模块迁移系统")
    init_parser.add_argument("--module", "-m", required=True, help="模块名称")

    # create 命令
    create_parser = subparsers.add_parser("create", help="创建迁移文件")
    create_parser.add_argument("--module", "-m", required=True, help="模块名称")
    create_parser.add_argument("--message", "-msg", required=True, help="迁移描述")

    # up 命令
    up_parser = subparsers.add_parser("up", help="执行迁移升级")
    up_parser.add_argument(
        "--module", "-m", help="模块名称（可选，不指定则升级所有模块）"
    )
    up_parser.add_argument("--revision", "-r", help="目标版本（可选）")

    # down 命令
    down_parser = subparsers.add_parser("down", help="执行迁移降级")
    down_parser.add_argument("--module", "-m", required=True, help="模块名称")
    down_parser.add_argument("--revision", "-r", help="目标版本（可选）")

    # list 命令
    subparsers.add_parser("list", help="列出所有模块及其状态")

    # history 命令
    history_parser = subparsers.add_parser("history", help="查看迁移历史")
    history_parser.add_argument("--module", "-m", required=True, help="模块名称")

    # current 命令
    current_parser = subparsers.add_parser("current", help="查看当前版本")
    current_parser.add_argument("--module", "-m", required=True, help="模块名称")

    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证模块迁移系统")
    validate_parser.add_argument("--module", "-m", required=True, help="模块名称")

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建迁移管理器
    migration_manager = MigrationManager()

    try:
        if args.command == "init":
            success = migration_manager.init_migration(args.module)
            sys.exit(0 if success else 1)

        elif args.command == "create":
            success = migration_manager.create_migration(args.module, args.message)
            sys.exit(0 if success else 1)

        elif args.command == "up":
            success = migration_manager.upgrade(args.module, args.revision)
            sys.exit(0 if success else 1)

        elif args.command == "down":
            success = migration_manager.downgrade(args.module, args.revision)
            sys.exit(0 if success else 1)

        elif args.command == "list":
            migration_manager.list_modules()

        elif args.command == "history":
            migration_manager.history(args.module)

        elif args.command == "current":
            migration_manager.current(args.module)

        elif args.command == "validate":
            success = migration_manager.validate(args.module)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行命令失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
