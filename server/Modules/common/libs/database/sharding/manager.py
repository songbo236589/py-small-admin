"""
分表管理器

提供统一的分表管理功能，包括表路由、表管理、数据查询和数据写入。
"""

from loguru import logger
from sqlalchemy import text

from ...time.utils import now

# 常量配置
MAX_TABLES_PER_QUERY = 50  # 单次查询最大表数


class ShardingManager:
    """
    分表管理器 - 简单直接

    功能:
    1. 表路由 - 根据分表键计算表名
    2. 表管理 - 检查、创建表
    3. 数据查询 - 单表查询、跨表查询
    4. 数据写入 - 插入、批量插入、更新
    """

    def __init__(self, model, sharding_strategy, engine=None):
        """
        初始化分表管理器

        Args:
            model: SQLModel模型类
            sharding_strategy: 分表策略实例
            engine: 数据库引擎(可选,延迟获取)
        """
        self.model = model
        self.sharding_strategy = sharding_strategy
        self._engine = engine
        self._table_creator = None
        self._cache_manager = None  # 延迟初始化缓存管理器
        self._field_mapping = self._extract_field_mapping()
        self._primary_keys = self._extract_primary_keys()

    @property
    def engine(self):
        """延迟获取数据库引擎"""
        if self._engine is None:
            from ..sql.engine import get_db_engine

            self._engine = get_db_engine()
        return self._engine

    @property
    def table_creator(self):
        """延迟获取表创建器"""
        if self._table_creator is None:
            from .table_creator import ShardingTableCreator

            self._table_creator = ShardingTableCreator(self.model, self.engine)
        return self._table_creator

    @property
    def cache_manager(self):
        """延迟获取缓存管理器"""
        if self._cache_manager is None:
            from .cache_utils import ShardingCacheManager

            self._cache_manager = ShardingCacheManager()
        return self._cache_manager

    @property
    def table_prefix(self):
        """获取表名前缀"""
        return self.table_creator.base_table_name

    def _extract_field_mapping(self):
        """从模型中提取字段映射"""
        field_mapping = {}
        for column in self.model.__table__.columns:
            field_mapping[column.name] = column.name
        return field_mapping

    def _extract_primary_keys(self):
        """从模型中提取主键字段"""
        return [pk.name for pk in self.model.__table__.primary_key]

    # ==================== 表路由 ====================

    def get_table_name(self, sharding_key_value) -> str:
        """
        根据分表键值获取表名

        Args:
            sharding_key_value: 分表键的值

        Returns:
            str: 完整的表名
        """
        return self.sharding_strategy.get_table_name(
            sharding_key_value, self.table_prefix
        )

    # ==================== 表管理 ====================

    def table_exists(self, table_name) -> bool:
        """
        检查表是否存在(带缓存)

        Args:
            table_name: 表名

        Returns:
            bool: 表是否存在
        """
        return self.cache_manager.check_table_exists_with_cache(
            table_name, self.table_creator._check_table_exists_from_db
        )

    def ensure_table_exists(self, table_name) -> bool:
        """
        确保表存在

        Args:
            table_name: 表名

        Returns:
            bool: 表是否存在
        """
        # 先检查缓存
        if self.table_exists(table_name):
            return True

        # 从表名提取后缀
        table_suffix = table_name.replace(self.table_prefix, "")

        # 使用表创建器创建表
        return self.table_creator.ensure_table_exists(table_suffix)

    def warm_up_tables(self, suffixes):
        """
        预热表(创建指定的分表)

        Args:
            suffixes: 表名后缀列表
        """
        if not suffixes:
            logger.info("未指定表名后缀,跳过预热")
            return

        for suffix in suffixes:
            table_name = f"{self.table_prefix}{suffix}"
            self.ensure_table_exists(table_name)

        logger.info(f"预热表完成: {suffixes}")

    # ==================== 查询方法 ====================

    def query_single_table(
        self,
        table_name,
        conditions=None,
        limit=None,
        offset=0,
        order_by=None,
    ):
        """
        查询单张表的数据

        Args:
            table_name: 表名
            conditions: 查询条件字典
            limit: 返回记录数限制
            offset: 偏移量
            order_by: 排序规则

        Returns:
            list[dict]: 查询结果
        """
        # 检查表是否存在
        if not self.table_exists(table_name):
            logger.warning(f"[分表管理器-查询单表-表不存在] 表名: {table_name}")
            return []

        # 构建查询条件
        where_clause, params = self._build_where_clause(conditions or {})

        # 构建排序
        order_clause = ""
        if order_by:
            order_clause = f"ORDER BY {order_by}"

        # 构建限制
        limit_clause = ""
        if limit is not None:
            limit_clause = f"LIMIT {limit}"
            if offset > 0:
                limit_clause += f" OFFSET {offset}"

        # 构建SQL
        sql = f"""
            SELECT * FROM {table_name}
            WHERE {where_clause}
            {order_clause}
            {limit_clause}
        """

        # 执行查询
        try:
            return self._execute_query(sql, params)
        except Exception as e:
            logger.error(f"[分表管理器-查询单表-失败] 表名: {table_name}, 错误: {e}")
            return []

    def query_multi_tables(
        self,
        sharding_key_range=None,
        conditions=None,
        limit=None,
        order_by=None,
        max_tables=None,
    ):
        """
        查询多张表的数据(跨表查询)

        Args:
            sharding_key_range: 分表键范围(起始值, 结束值)
            conditions: 查询条件字典
            limit: 返回记录数限制
            order_by: 排序规则
            max_tables: 最大查询表数限制

        Returns:
            list[dict]: 查询结果(已合并和排序)
        """
        # 如果没有指定分表键范围,无法跨表查询
        if sharding_key_range is None:
            logger.warning("[分表管理器-跨表查询-失败] 未指定分表键范围,无法跨表查询")
            return []

        start_value, end_value = sharding_key_range

        # 获取涉及的表名
        table_names = self.sharding_strategy.get_table_names_by_range(
            start_value, end_value, self.table_prefix
        )

        # 限制查询表数量
        if max_tables is not None and len(table_names) > max_tables:
            logger.warning(
                f"[分表管理器-跨表查询-限制表数量] 跨表查询涉及的表数量过多: {len(table_names)}, 限制为: {max_tables}"
            )
            table_names = table_names[:max_tables]

        # 查询每张表
        all_data = []
        for table_name in table_names:
            if not self.table_exists(table_name):
                continue

            data = self.query_single_table(
                table_name=table_name,
                conditions=conditions,
                order_by=order_by,
            )
            all_data.extend(data)

        # 合并和排序
        all_data = self._merge_and_sort(all_data, order_by)

        # 应用limit
        if limit is not None:
            all_data = all_data[:limit]

        return all_data

    def count(self, sharding_key_range=None, conditions=None) -> int:
        """
        统计数据数量

        Args:
            sharding_key_range: 分表键范围(起始值, 结束值)
            conditions: 查询条件字典

        Returns:
            int: 数据数量
        """
        # 如果没有指定分表键范围,无法统计
        if sharding_key_range is None:
            logger.warning("未指定分表键范围,无法统计")
            return 0

        start_value, end_value = sharding_key_range

        # 获取涉及的表名
        table_names = self.sharding_strategy.get_table_names_by_range(
            start_value, end_value, self.table_prefix
        )

        # 统计每张表的数据量
        total_count = 0
        for table_name in table_names:
            if not self.table_exists(table_name):
                continue

            # 构建查询条件
            where_clause, params = self._build_where_clause(conditions or {})

            # 构建SQL
            sql = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause}"

            try:
                count = self._execute_query_scalar(sql, params)
                if count is not None:
                    total_count += int(count)
            except Exception as e:
                logger.error(f"统计失败: {table_name}, 错误: {e}")

        return total_count

    # ==================== 写入方法 ====================

    def insert(self, sharding_key_value, data, on_duplicate="UPDATE") -> bool:
        """
        插入单条数据

        Args:
            sharding_key_value: 分表键的值
            data: 数据字典
            on_duplicate: 重复时的处理方式

        Returns:
            bool: 是否成功
        """
        # 获取表名
        table_name = self.get_table_name(sharding_key_value)

        # 确保表存在
        if not self.ensure_table_exists(table_name):
            logger.error(f"表创建失败: {table_name}")
            return False

        # 构建SQL
        sql, params = self._build_insert_sql(
            table_name, data, self._field_mapping, self._primary_keys, on_duplicate
        )

        # 执行SQL
        try:
            self._execute_update(sql, params)
            return True
        except Exception as e:
            logger.error(f"插入数据失败: {table_name}, 错误: {e}")
            return False

    def batch_insert(self, data_list, on_duplicate="UPDATE") -> int:
        """
        批量插入数据

        Args:
            data_list: 数据列表
            on_duplicate: 重复时的处理方式

        Returns:
            int: 成功插入的记录数
        """
        if not data_list:
            return 0

        # 按表分组
        data_by_table = {}
        for data in data_list:
            # 提取分表键值
            sharding_key_value = self.sharding_strategy.extract_sharding_key_value(data)

            # 获取表名
            table_name = self.get_table_name(sharding_key_value)

            if table_name not in data_by_table:
                data_by_table[table_name] = []

            data_by_table[table_name].append(data)

        # 批量写入每张表
        success_count = 0
        for table_name, table_data_list in data_by_table.items():
            # 确保表存在
            if not self.ensure_table_exists(table_name):
                logger.error(f"[分表管理器-批量插入-表创建失败] 表名: {table_name}")
                continue

            # 构建批量插入SQL
            sql, params = self._build_batch_insert_sql(
                table_name,
                table_data_list,
                self._field_mapping,
                self._primary_keys,
                on_duplicate,
            )

            # 执行SQL
            try:
                self._execute_update(sql, params)
                success_count += len(table_data_list)
            except Exception as e:
                logger.error(
                    f"[分表管理器-批量插入-失败] 表名: {table_name}, 错误: {e}"
                )

        return success_count

    def update(self, sharding_key_value, pk_values, data) -> bool:
        """
        更新数据

        Args:
            sharding_key_value: 分表键的值
            pk_values: 主键值字典
            data: 要更新的数据字典

        Returns:
            bool: 是否成功
        """
        # 获取表名
        table_name = self.get_table_name(sharding_key_value)

        # 检查表是否存在
        if not self.table_exists(table_name):
            logger.warning(f"表不存在: {table_name}")
            return False

        # 构建更新SQL
        sql, params = self._build_update_sql(
            table_name, pk_values, data, self._field_mapping
        )

        # 执行SQL
        try:
            result = self._execute_update(sql, params)
            if result.rowcount > 0:
                return True
            else:
                logger.warning(f"更新数据失败: 记录不存在, {table_name}")
                return False
        except Exception as e:
            logger.error(f"更新数据失败: {table_name}, 错误: {e}")
            return False

    def upsert(self, sharding_key_value, data) -> bool:
        """
        插入或更新数据

        Args:
            sharding_key_value: 分表键的值
            data: 数据字典

        Returns:
            bool: 是否成功
        """
        return self.insert(sharding_key_value, data, on_duplicate="UPDATE")

    # ==================== 私有方法 ====================

    def _execute_query(self, sql, params):
        """执行查询SQL"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params)
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row, strict=True)) for row in rows]

    def _execute_update(self, sql, params):
        """执行更新/插入SQL"""
        with self.engine.begin() as conn:
            return conn.execute(text(sql), params)

    def _execute_query_scalar(self, sql, params):
        """执行标量查询SQL"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params)
            return result.scalar()

    def _build_where_clause(self, conditions):
        """构建WHERE子句"""
        if not conditions:
            return "1=1", {}

        clauses = []
        params = {}

        for key, value in conditions.items():
            if value is None:
                clauses.append(f"{key} IS NULL")
            else:
                clauses.append(f"{key} = :{key}")
                params[key] = value

        where_clause = " AND ".join(clauses)
        return where_clause, params

    def _build_insert_sql(
        self, table_name, data, field_mapping, primary_keys, on_duplicate
    ):
        """构建INSERT SQL"""

        # 过滤有效字段
        valid_fields = []
        values = []
        params = {}

        for key, value in data.items():
            if key in field_mapping and value is not None:
                valid_fields.append(key)
                values.append(f":{key}")
                params[key] = value

        # 添加时间戳
        if "created_at" in field_mapping and "created_at" not in data:
            valid_fields.append("created_at")
            values.append(":created_at")
            params["created_at"] = now()

        # 构建SQL
        sql = f"""
            INSERT INTO `{table_name}` ({", ".join(f"`{f}`" for f in valid_fields)})
            VALUES ({", ".join(values)})
        """

        # 添加ON DUPLICATE KEY UPDATE
        if on_duplicate == "UPDATE":
            update_fields = []
            for key in valid_fields:
                if key not in primary_keys and key != "created_at":
                    update_fields.append(f"`{key}` = VALUES(`{key}`)")

            if "updated_at" in field_mapping:
                update_fields.append("`updated_at` = :updated_at")
                params["updated_at"] = now()

            if update_fields:
                sql += f" ON DUPLICATE KEY UPDATE {', '.join(update_fields)}"

        return sql, params

    def _build_batch_insert_sql(
        self, table_name, data_list, field_mapping, primary_keys, on_duplicate
    ):
        """构建批量INSERT SQL"""

        if not data_list:
            return "", {}

        # 使用第一条数据构建字段列表
        first_data = data_list[0]

        # 过滤有效字段
        valid_fields = []
        for key in first_data.keys():
            if key in field_mapping:
                valid_fields.append(key)

        # 添加时间戳字段
        if "created_at" in field_mapping and "created_at" not in valid_fields:
            valid_fields.append("created_at")
        if "updated_at" in field_mapping and "updated_at" not in valid_fields:
            valid_fields.append("updated_at")

        # 构建批量VALUES子句
        values_clauses = []
        params = {}

        for i, data in enumerate(data_list):
            value_placeholders = []
            for key in valid_fields:
                # 使用唯一的参数名,避免冲突
                param_name = f"p_{i}_{key.replace('_', '_')}"
                value_placeholders.append(f":{param_name}")

                # 设置参数值
                if key == "created_at" and key not in data:
                    params[param_name] = now()
                elif key == "updated_at":
                    params[param_name] = now()
                elif key in data and data[key] is not None:
                    params[param_name] = data[key]
                else:
                    params[param_name] = None

            values_clauses.append(f"({', '.join(value_placeholders)})")

        # 构建SQL
        sql = f"""
            INSERT INTO `{table_name}` ({", ".join(f"`{f}`" for f in valid_fields)})
            VALUES {", ".join(values_clauses)}
        """

        # 添加ON DUPLICATE KEY UPDATE
        if on_duplicate == "UPDATE":
            update_fields = []
            for key in valid_fields:
                if key not in primary_keys and key != "created_at":
                    update_fields.append(f"`{key}` = VALUES(`{key}`)")

            if "updated_at" in field_mapping:
                update_fields.append("`updated_at` = VALUES(`updated_at`)")

            if update_fields:
                sql += f" ON DUPLICATE KEY UPDATE {', '.join(update_fields)}"

        return sql, params

    def _build_update_sql(self, table_name, pk_values, data, field_mapping):
        """构建UPDATE SQL"""

        # 构建SET子句
        set_fields = []
        params = {}

        for key, value in data.items():
            if key in field_mapping and value is not None:
                set_fields.append(f"`{key}` = :{key}")
                params[key] = value

        # 添加更新时间
        if "updated_at" in field_mapping:
            set_fields.append("`updated_at` = :updated_at")
            params["updated_at"] = now()

        # 构建WHERE子句
        where_clauses = []
        for key, value in pk_values.items():
            if key in field_mapping:
                where_clauses.append(f"`{key}` = :pk_{key}")
                params[f"pk_{key}"] = value

        where_clause = " AND ".join(where_clauses)

        # 构建SQL
        sql = f"""
            UPDATE `{table_name}`
            SET {", ".join(set_fields)}
            WHERE {where_clause}
        """

        return sql, params

    def _merge_and_sort(self, all_data, order_by=None):
        """合并和排序数据"""
        if not all_data:
            return []

        if not order_by:
            return all_data

        # 解析排序规则
        order_field, order_direction = self._parse_order_by(order_by)

        # 排序(处理None值,将其放在最后)
        reverse = order_direction.upper() == "DESC"

        def sort_key(item):
            value = item.get(order_field)
            # 将None值转换为最大值,使其排在最后
            return (value is None, value if value is not None else "")

        all_data.sort(key=sort_key, reverse=reverse)

        return all_data

    def _parse_order_by(self, order_by):
        """解析排序规则"""
        parts = order_by.split()
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return parts[0], "DESC"
