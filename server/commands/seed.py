#!/usr/bin/env python3
"""
数据库填充工具

提供完整的数据库填充命令行接口，支持模块化的种子数据管理。
每个模块都有自己独立的种子数据系统，可以独立管理和执行种子数据。

使用示例:
    python -m commands.seed run --module admin
    python -m commands.seed run-all
    python -m commands.seed list
    python -m commands.seed validate --module admin
    python -m commands.seed dry-run --module admin
"""

import argparse
import importlib
import inspect
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from loguru import logger

    from Modules.common.libs.database.sql.engine import db_engine_manager

    # 导入项目相关模块
    from Modules.common.libs.database.sql.session import db_session_manager
    from Modules.common.models.base_model import BaseTableModel
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

            # 获取所有继承自BaseTableModel的类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseTableModel)
                    and obj != BaseTableModel
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

    def has_seeds(self, module_name: str) -> bool:
        """
        检查模块是否有种子数据

        Args:
            module_name: 模块名称

        Returns:
            bool: 是否有种子数据
        """
        seeds_path = self.modules_path / module_name / "seeds"
        return seeds_path.exists() and seeds_path.is_dir()

    def get_seed_files(self, module_name: str) -> list[Path]:
        """
        获取模块的所有种子数据文件

        Args:
            module_name: 模块名称

        Returns:
            List[Path]: 种子数据文件列表
        """
        seeds_path = self.modules_path / module_name / "seeds"
        if not seeds_path.exists():
            return []

        seed_files = []
        for file_path in seeds_path.glob("*_seed.py"):
            if file_path.is_file():
                seed_files.append(file_path)

        return sorted(seed_files)

    def get_seed_classes(self, module_name: str) -> list[type]:
        """
        获取模块的所有种子数据类

        Args:
            module_name: 模块名称

        Returns:
            List[Type]: 种子数据类列表
        """
        seed_classes = []

        try:
            # 导入模块的seeds包
            seeds_package = f"Modules.{module_name}.seeds"
            module = importlib.import_module(seeds_package)

            # 获取所有以Seed结尾的类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith("Seed") and obj.__module__ == seeds_package:
                    seed_classes.append(obj)
                    logger.debug(f"发现种子类 {module_name}.{name}")

        except ImportError as e:
            logger.error(f"无法导入模块 {module_name} 的种子数据: {e}")

        return seed_classes


class SeedManager:
    """种子数据管理器 - 负责管理各模块的种子数据"""

    def __init__(self):
        """初始化种子数据管理器"""
        self.module_discovery = ModuleDiscovery()

    def run_seeds(self, module_name: str, env: str = "development") -> bool:
        """
        运行指定模块的种子数据

        Args:
            module_name: 模块名称
            env: 环境名称

        Returns:
            bool: 执行是否成功
        """
        logger.info(f"正在运行模块 {module_name} 的种子数据 (环境: {env})...")

        # 验证模块结构
        if not self.module_discovery.validate_module_structure(module_name):
            logger.error(f"模块 {module_name} 结构验证失败")
            return False

        # 检查是否有种子数据
        if not self.module_discovery.has_seeds(module_name):
            logger.warning(f"模块 {module_name} 没有种子数据")
            return True

        try:
            # 导入模块的seeds包
            seeds_package = f"Modules.{module_name}.seeds"
            seeds_module = importlib.import_module(seeds_package)

            # 检查是否有run_seeds函数
            if hasattr(seeds_module, "run_seeds"):
                # 初始化数据库引擎（如果尚未初始化）
                try:
                    db_engine_manager.init_db_engine()
                except Exception as e:
                    logger.warning(f"数据库引擎初始化失败（可能已初始化）: {e}")

                # 初始化数据库会话
                db_session_manager.init_session_maker()

                # 运行种子数据
                run_seeds_func = seeds_module.run_seeds
                run_seeds_func(env)

                logger.info(f"模块 {module_name} 种子数据运行完成")
                return True
            else:
                logger.error(
                    f"模块 {module_name} 的seeds/__init__.py中没有找到run_seeds函数"
                )
                return False

        except Exception as e:
            logger.error(f"运行模块 {module_name} 种子数据失败: {e}")
            return False

    def run_all_seeds(self, env: str = "development") -> bool:
        """
        运行所有模块的种子数据

        Args:
            env: 环境名称

        Returns:
            bool: 执行是否成功
        """
        logger.info(f"正在运行所有模块的种子数据 (环境: {env})...")

        modules = self.module_discovery.discover_modules()
        if not modules:
            logger.warning("没有发现任何模块")
            return True

        success = True
        for module_name in modules:
            if not self.run_seeds(module_name, env):
                success = False

        if success:
            logger.info("所有模块的种子数据运行完成")
        else:
            logger.error("部分模块的种子数据运行失败")

        return success

    def list_modules(self) -> None:
        """列出所有模块及其种子数据状态"""
        modules = self.module_discovery.discover_modules()

        if not modules:
            print("未发现任何模块")
            return

        print("\n模块填充状态:")
        print("-" * 80)

        for module_name in modules:
            # 获取模块模型数量
            models = self.module_discovery.get_module_models(module_name)
            model_count = len(models)

            # 检查是否有种子数据
            has_seeds = self.module_discovery.has_seeds(module_name)

            # 获取种子文件数量
            seed_files = self.module_discovery.get_seed_files(module_name)
            seed_count = len(seed_files)

            # 验证种子数据
            is_valid = self.validate_seeds(module_name)

            # 状态信息
            if has_seeds:
                status = "有填充"
                if is_valid:
                    status += ", 有效"
                else:
                    status += ", 无效"
            else:
                status = "无填充"

            print(
                f"  {module_name}: {status}, {model_count} 模型, {seed_count} 种子文件"
            )

        print("-" * 80)

    def validate_seeds(self, module_name: str) -> bool:
        """
        验证模块的种子数据

        Args:
            module_name: 模块名称

        Returns:
            bool: 验证是否通过
        """
        try:
            # 检查seeds目录是否存在
            if not self.module_discovery.has_seeds(module_name):
                return True  # 没有种子数据也算有效

            # 导入模块的seeds包
            seeds_package = f"Modules.{module_name}.seeds"
            seeds_module = importlib.import_module(seeds_package)

            # 检查是否有run_seeds函数
            if not hasattr(seeds_module, "run_seeds"):
                return False

            # 检查种子文件
            seed_files = self.module_discovery.get_seed_files(module_name)
            if not seed_files:
                return False

            return True

        except Exception as e:
            logger.error(f"验证模块 {module_name} 种子数据失败: {e}")
            return False

    def dry_run(self, module_name: str, env: str = "development") -> bool:
        """
        模拟运行指定模块的种子数据

        Args:
            module_name: 模块名称
            env: 环境名称

        Returns:
            bool: 模拟运行是否成功
        """
        logger.info(f"模拟运行模块 {module_name} 的数据填充 (环境: {env})")

        # 验证模块结构
        if not self.module_discovery.validate_module_structure(module_name):
            logger.error(f"模块 {module_name} 结构验证失败")
            return False

        # 检查是否有种子数据
        if not self.module_discovery.has_seeds(module_name):
            logger.warning(f"模块 {module_name} 没有种子数据")
            return True

        try:
            # 获取种子文件列表
            seed_files = self.module_discovery.get_seed_files(module_name)

            print(f"模拟运行模块 {module_name} 的数据填充 (环境: {env}):")
            for seed_file in seed_files:
                print(f"  将执行: {seed_file.stem}")

            print("模拟运行完成")
            return True

        except Exception as e:
            logger.error(f"模拟运行模块 {module_name} 种子数据失败: {e}")
            return False

    def validate_module(self, module_name: str) -> bool:
        """
        验证模块的种子数据结构

        Args:
            module_name: 模块名称

        Returns:
            bool: 验证是否通过
        """
        logger.info(f"验证模块 {module_name} 填充结构")

        # 验证模块结构
        if not self.module_discovery.validate_module_structure(module_name):
            logger.error(f"模块 {module_name} 结构验证失败")
            return False

        # 检查seeds目录
        seeds_path = project_root / "Modules" / module_name / "seeds"
        if not seeds_path.exists():
            logger.warning(f"模块 {module_name} 没有seeds目录")
            return True

        # 检查__init__.py文件
        init_file = seeds_path / "__init__.py"
        if not init_file.exists():
            logger.error(f"模块 {module_name} 的seeds目录缺少__init__.py文件")
            return False

        # 检查种子文件
        seed_files = self.module_discovery.get_seed_files(module_name)
        if not seed_files:
            logger.warning(f"模块 {module_name} 没有种子数据文件")
            return True

        print(f"模块 {module_name} 填充验证:")
        print(f"  种子文件: {len(seed_files)}")
        for seed_file in seed_files:
            print(f"  - {seed_file.stem}")

        # 验证种子文件内容
        try:
            # 导入模块的seeds包
            seeds_package = f"Modules.{module_name}.seeds"
            seeds_module = importlib.import_module(seeds_package)

            # 检查是否有run_seeds函数
            if not hasattr(seeds_module, "run_seeds"):
                logger.error(
                    f"模块 {module_name} 的seeds/__init__.py中没有找到run_seeds函数"
                )
                return False

            print("✓ 验证通过")
            return True

        except ImportError as e:
            logger.error(f"无法导入模块 {module_name} 的种子数据: {e}")
            return False


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="数据库填充工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m commands.seed run --module admin
  python -m commands.seed run-all
  python -m commands.seed list
  python -m commands.seed validate --module admin
  python -m commands.seed dry-run --module admin
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # run 命令
    run_parser = subparsers.add_parser("run", help="运行指定模块的种子数据")
    run_parser.add_argument("--module", "-m", required=True, help="模块名称")
    run_parser.add_argument(
        "--env", default="development", help="环境名称 (默认: development)"
    )

    # run-all 命令
    run_all_parser = subparsers.add_parser("run-all", help="运行所有模块的种子数据")
    run_all_parser.add_argument(
        "--env", default="development", help="环境名称 (默认: development)"
    )

    # list 命令
    subparsers.add_parser("list", help="列出所有模块的种子数据状态")

    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证模块的种子数据")
    validate_parser.add_argument("--module", "-m", required=True, help="模块名称")

    # dry-run 命令
    dry_run_parser = subparsers.add_parser("dry-run", help="模拟运行种子数据")
    dry_run_parser.add_argument("--module", "-m", required=True, help="模块名称")
    dry_run_parser.add_argument(
        "--env", default="development", help="环境名称 (默认: development)"
    )

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建种子数据管理器
    seed_manager = SeedManager()

    try:
        if args.command == "run":
            success = seed_manager.run_seeds(args.module, args.env)
            sys.exit(0 if success else 1)

        elif args.command == "run-all":
            success = seed_manager.run_all_seeds(args.env)
            sys.exit(0 if success else 1)

        elif args.command == "list":
            seed_manager.list_modules()

        elif args.command == "validate":
            success = seed_manager.validate_module(args.module)
            sys.exit(0 if success else 1)

        elif args.command == "dry-run":
            success = seed_manager.dry_run(args.module, args.env)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行命令失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
