"""
分表创建器

专门负责从SQLModel模型创建分表,支持动态修改表名、表注释等。
"""

import re
import time

from loguru import logger
from sqlalchemy import inspect, text


class ShardingTableCreator:
    """
    分表创建器 - 专注表创建

    功能:
    1. 从模型复制表结构
    2. 创建分表
    3. 检查表是否存在
    4. 使用分布式锁避免重复创建
    """

    def __init__(self, model, engine=None):
        """
        初始化分表创建器

        Args:
            model: SQLModel模型类
            engine: 数据库引擎(可选,延迟获取)
        """
        self.model = model
        self._engine = engine
        self.base_table_name = self._extract_base_table_name()
        self._cache_manager = None  # 延迟初始化缓存管理器

    @property
    def engine(self):
        """延迟获取数据库引擎"""
        if self._engine is None:
            from ..sql.engine import get_db_engine

            self._engine = get_db_engine()
        return self._engine

    @property
    def cache_manager(self):
        """延迟获取缓存管理器"""
        if self._cache_manager is None:
            from .cache_utils import ShardingCacheManager

            self._cache_manager = ShardingCacheManager()
        return self._cache_manager

    def _extract_base_table_name(self):
        """
        从模型表名中提取基础表名(去掉可能的年份后缀)

        Returns:
            str: 基础表名
        """
        table_name = self.model.__tablename__

        # 尝试去掉年份后缀(如 "_2024")

        # 匹配末尾的 _数字 模式(支持4位年份、6位年月、8位年月日)
        match = re.search(r"_(\d{4}|\d{6}|\d{8})$", table_name)
        if match:
            return table_name[: match.start()]

        return table_name

    def _get_original_table_sql(self, table_name):
        """
        获取原始表的 CREATE TABLE SQL

        Args:
            table_name: 表名

        Returns:
            str: 原始表的 CREATE TABLE SQL
        """
        # 使用 SHOW CREATE TABLE 获取原始表的完整 SQL
        # 注意: SHOW CREATE TABLE 不支持参数化查询,使用字符串拼接
        # 需要验证表名以防止 SQL 注入
        if not table_name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"无效的表名: {table_name}")

        with self.engine.connect() as conn:
            result = conn.execute(text(f"SHOW CREATE TABLE `{table_name}`"))
            row = result.fetchone()
            if row and len(row) > 1:
                return row[1]

        # 如果获取失败,返回空字符串
        return ""

    def _check_table_exists_from_db(self, table_name):
        """
        检查表是否存在(从数据库)

        Args:
            table_name: 表名

        Returns:
            bool: 表是否存在
        """
        inspector = inspect(self.engine)
        exists = inspector.has_table(table_name)
        return exists

    def _execute_create_table_sql(self, sql):
        """
        执行 CREATE TABLE SQL

        Args:
            sql: CREATE TABLE SQL 语句
        """
        with self.engine.begin() as conn:
            conn.execute(text(sql))

    def _release_lock(self, lock_key):
        """释放分布式锁"""
        self.cache_manager.cache_delete(lock_key)

    # ==================== 表创建方法 ====================

    def create_sharded_table(self, table_suffix, table_comment=None):
        """
        创建分表

        Args:
            table_suffix: 表名后缀(如 "2024", "202401")
            table_comment: 表注释,如果为None则使用模型的表注释

        Returns:
            bool: 是否创建成功
        """
        try:
            # 生成完整表名
            table_name = f"{self.base_table_name}{table_suffix}"

            # 检查表是否已存在(从缓存)
            cache_key = f"{self.cache_manager.cache_prefix}{table_name}"
            cached = self.cache_manager.cache_get(cache_key)
            if str(cached) == "1" or cached == 1:
                return True

            # 获取原始表的 CREATE TABLE SQL
            original_sql = self._get_original_table_sql(self.base_table_name)

            if not original_sql:
                logger.error(
                    f"[创建分表-失败] 表名: {table_name}, 无法获取原始表的 CREATE TABLE SQL: {self.base_table_name}"
                )
                return False

            # 替换表名(使用更精确的替换逻辑)
            new_sql = original_sql.replace(
                f"CREATE TABLE `{self.base_table_name}`", f"CREATE TABLE `{table_name}`"
            )

            # 如果指定了新的表注释,替换表注释
            if table_comment:
                # 替换 COMMENT='xxx' 为 COMMENT='yyy'

                new_sql = re.sub(
                    r"COMMENT='[^']*'", f"COMMENT='{table_comment}'", new_sql
                )

            # 使用 CREATE TABLE IF NOT EXISTS 避免表已存在错误
            new_sql = new_sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")

            # 执行SQL
            self._execute_create_table_sql(new_sql)

            logger.info(f"[创建分表-成功] 表名: {table_name}")

            # 立即更新缓存为"1"(表存在)
            cache_key = f"{self.cache_manager.cache_prefix}{table_name}"
            self.cache_manager.cache_set(cache_key, "1")

            return True

        except Exception as e:
            # 捕获表已存在异常,视为表已存在
            error_msg = str(e)
            if "already exists" in error_msg or "1050" in error_msg:
                # 立即更新缓存为"1"(表存在)
                table_name = f"{self.base_table_name}{table_suffix}"
                cache_key = f"{self.cache_manager.cache_prefix}{table_name}"
                self.cache_manager.cache_set(cache_key, "1")

                return True

            logger.error(f"[创建分表-失败] 表名: {table_name}, 错误: {e}")
            return False

    def table_exists(self, table_name):
        """
        检查表是否存在(带缓存)

        Args:
            table_name: 表名

        Returns:
            bool: 表是否存在
        """
        return self.cache_manager.check_table_exists_with_cache(
            table_name, self._check_table_exists_from_db
        )

    def ensure_table_exists(self, table_suffix, table_comment=None):
        """
        确保表存在(使用Redis分布式锁)

        Args:
            table_suffix: 表名后缀
            table_comment: 表注释

        Returns:
            bool: 表是否存在
        """
        # 生成完整表名
        table_name = f"{self.base_table_name}{table_suffix}"

        # 先检查缓存
        if self.table_exists(table_name):
            return True

        # 如果缓存可用,使用分布式锁
        acquired = self.cache_manager.acquire_lock(table_name)

        if acquired:
            # 获取锁成功
            # 双重检查
            if self.table_exists(table_name):
                self.cache_manager.release_lock(table_name)
                return True

            # 创建表
            result = self.create_sharded_table(table_suffix, table_comment)
            self.cache_manager.release_lock(table_name)
            return result
        else:
            # 获取锁失败,等待1秒后重试

            time.sleep(1)
            return self.table_exists(table_name)

    def batch_create_tables(self, suffixes, table_comment=None):
        """
        批量创建表

        Args:
            suffixes: 表名后缀列表
            table_comment: 表注释

        Returns:
            dict[str, bool]: 表名到成功状态的映射
        """
        results = {}
        for suffix in suffixes:
            table_name = f"{self.base_table_name}{suffix}"
            results[table_name] = self.create_sharded_table(
                table_suffix=suffix,
                table_comment=table_comment,
            )

        success_count = sum(1 for v in results.values() if v)
        logger.info(
            f"[批量创建表-完成] 总数: {len(suffixes)}, 成功: {success_count}, 失败: {len(suffixes) - success_count}"
        )

        return results
