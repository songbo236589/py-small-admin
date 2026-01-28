"""
SQLModel 基类

提供通用的模型基类，包含常用字段和方法。
"""

from sqlalchemy import event
from sqlmodel import SQLModel

from ..libs.config import Config


class BaseModel(SQLModel):
    """
    所有模型的基类（⚠️ 不建表）

    作用：
    - 统一 Pydantic / SQLModel 配置
    - 支持 ORM → Pydantic 序列化
    """


class BaseTableModel(BaseModel):
    """
    所有数据库表模型的基类（子类需显式 table=True）

    提供：
    - id 主键
    - created_at / updated_at 自动维护
    - 表注释支持
    """

    # 类变量存储数据库配置信息
    _db_config: dict[str, str] = {}
    # 表注释，子类可以重写此属性
    __table_comment__: str | None = None

    def __init_subclass__(cls, **kwargs):
        """
        子类创建时自动执行（⚠️ 必须调用 super）

        功能：
        - 自动补全 __tablename__
        - 仅对 table=True 的模型生效
        """
        super().__init_subclass__(**kwargs)
        # 检查是否是表模型
        has_field = any(
            hasattr(value, "__class__") and "FieldInfo" in value.__class__.__name__
            for value in cls.__dict__.values()
        )
        if has_field:
            # 获取数据库配置并存储到类变量中
            try:
                db_config = Config.get("database")
                if db_config:
                    # 获取默认连接名称
                    default_connection = db_config.default
                    # 获取对应连接的配置
                    connection_config = db_config.connections.get(
                        default_connection, {}
                    )

                    # 存储配置信息到类变量
                    cls._db_config = {
                        "prefix": connection_config.get("prefix", ""),
                        "engine": connection_config.get("engine", "InnoDB"),
                        "charset": connection_config.get("charset", "utf8mb4"),
                        "collate": connection_config.get(
                            "collate", "utf8mb4_unicode_ci"
                        ),
                    }
            except Exception:
                # 如果获取配置失败，使用空字典
                cls._db_config = {}

            # 检查类自己的__dict__中是否有__tablename__，而不是继承来的
            has_own_tablename = "__tablename__" in cls.__dict__

            if not has_own_tablename:
                table_name = cls._convert_to_snake_case(cls.__name__)
                # 应用表名前缀
                prefix = cls._db_config.get("prefix", "")
                if prefix:
                    cls.__tablename__ = f"{prefix}{table_name}"
                else:
                    cls.__tablename__ = table_name

            # 智能合并子类的 __table_args__ 和父类的表配置
            cls._merge_table_args()

            # 注册事件监听器，自动处理 ForeignKey 表名前缀
            cls._register_foreign_key_prefix_handler()

    @classmethod
    def _register_foreign_key_prefix_handler(cls):
        """
        注册事件监听器，自动为 ForeignKey 添加表名前缀

        监听 ForeignKeyConstraint 的 before_parent_attach 事件，
        在外键约束添加到表之前，自动为目标表名添加配置的前缀。
        """
        from sqlalchemy import ForeignKeyConstraint

        prefix = cls._db_config.get("prefix", "")
        if not prefix:
            return

        # 定义事件处理函数
        def receive_before_parent_attach(target, parent):
            """
            在外键约束添加到表之前处理

            Args:
                target: ForeignKeyConstraint 对象
                parent: Table 对象
            """
            # 只处理 ForeignKeyConstraint
            if not isinstance(target, ForeignKeyConstraint):
                return

            # 遍历所有外键元素（每个元素是一个 ForeignKey 对象）
            for fk in target.elements:
                # 获取 _colspec 属性（格式为 "table_name.column_name"）
                if hasattr(fk, "_colspec"):
                    old_colspec = fk._colspec
                    # 检查是否是字符串类型
                    if isinstance(old_colspec, str) and "." in old_colspec:
                        table_name, column_name = old_colspec.rsplit(".", 1)

                        # 检查是否需要添加前缀
                        if table_name and not table_name.startswith(prefix):
                            # 创建新的表名
                            new_table_name = f"{prefix}{table_name}"
                            # 更新 _colspec
                            fk._colspec = f"{new_table_name}.{column_name}"

        # 注册事件监听器
        event.listen(
            ForeignKeyConstraint, "before_parent_attach", receive_before_parent_attach
        )

    @classmethod
    def _convert_to_snake_case(cls, name: str) -> str:
        """
        将驼峰命名转换为下划线命名并添加复数形式

        Args:
            name: 类名（驼峰命名）

        Returns:
            str: 转换后的表名（下划线命名+复数）
        """
        import re

        # 将驼峰命名转换为下划线命名
        # 例如：AdminAdmin -> admin_admin, AdminGroup -> admin_group
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        snake_case = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        # 添加复数形式
        # 如果单词已经以s结尾，直接添加es，否则添加s
        if snake_case.endswith("s"):
            return snake_case + "es"
        else:
            return snake_case + "s"

    @classmethod
    def _get_table_args(cls) -> dict[str, str]:
        """
        获取表参数配置

        用于配置 SQLAlchemy/SQLModel 表的特定参数，主要用于 MySQL 数据库。

        Returns:
            dict[str, str]: 包含表参数配置的字典
        """
        # MySQL 表配置（从类变量中获取）
        engine = cls._db_config.get("engine", "InnoDB")
        charset = cls._db_config.get("charset", "utf8mb4")
        collation = cls._db_config.get("collate", "utf8mb4_unicode_ci")

        table_args = {
            "mysql_engine": engine,
            "mysql_charset": charset,
            "mysql_collate": collation,
        }

        # 如果有表注释，添加到表参数中
        if cls.__table_comment__:
            table_args["mysql_comment"] = cls.__table_comment__

        return table_args

    @classmethod
    def _merge_table_args(cls):
        """
        智能合并子类的 __table_args__ 和父类的表配置

        功能：
        - 如果子类没有定义 __table_args__，使用父类的默认表配置
        - 如果子类定义了 __table_args__，智能合并索引/约束和表配置
        - 支持元组形式（包含索引/约束）和字典形式（仅表参数）
        - 自动为索引名称添加表前缀
        """
        # 获取父类的表配置字典
        table_args_dict = cls._get_table_args()

        # 检查子类是否定义了 __table_args__
        has_own_table_args = "__table_args__" in cls.__dict__

        # 如果子类没有定义 __table_args__，直接使用父类的表配置
        if not has_own_table_args:
            cls.__table_args__ = table_args_dict
            return

        # 获取子类定义的 __table_args__
        child_table_args = cls.__dict__["__table_args__"]
        # 处理空元组或 None 的情况
        if not child_table_args:
            cls.__table_args__ = table_args_dict
            return

        # 如果子类定义的是元组（包含索引/约束）
        if isinstance(child_table_args, tuple):
            # 导入 Index 类
            from sqlalchemy import Index

            # 获取表前缀
            prefix = cls._db_config.get("prefix", "")

            # 处理元组中的索引对象，为索引名称添加前缀
            processed_items = []
            for item in child_table_args:
                if isinstance(item, Index):
                    # 检查索引名称是否需要添加前缀
                    index_name = item.name
                    if (
                        index_name
                        and prefix
                        and not index_name.startswith(f"idx_{prefix}")
                        and not index_name.startswith(f"uq_{prefix}")
                    ):
                        # 添加前缀到索引名称
                        new_name = f"idx_{prefix}{index_name}"
                        # 创建新的 Index 对象
                        new_index = Index(new_name, *item.expressions)
                        processed_items.append(new_index)
                    else:
                        # 不需要添加前缀，直接使用原索引
                        processed_items.append(item)
                else:
                    # 非索引对象，直接添加
                    processed_items.append(item)

            # 检查元组最后一个元素是否是字典
            if processed_items and isinstance(processed_items[-1], dict):
                # 合并字典（子类的配置优先）
                merged_dict = {**table_args_dict, **processed_items[-1]}
                # 重新构建元组
                cls.__table_args__ = tuple(processed_items[:-1]) + (merged_dict,)
            else:
                # 直接添加表配置字典到元组末尾
                cls.__table_args__ = tuple(processed_items) + (table_args_dict,)

        # 如果子类定义的是字典（仅表参数）
        elif isinstance(child_table_args, dict):
            # 合并字典（子类的配置优先）
            cls.__table_args__ = {**table_args_dict, **child_table_args}

        # 其他类型，直接使用父类的表配置
        else:
            cls.__table_args__ = table_args_dict
