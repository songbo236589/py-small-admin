#!/usr/bin/env python3
"""
模块创建工具

提供完整的模块创建命令行接口，支持快速创建标准化的模块结构。
每个模块都遵循项目的标准目录结构和代码规范。

使用示例:
    python -m commands.create_module create --module user
    python -m commands.create_module create --module user --full
    python -m commands.create_module list
    python -m commands.create_module validate --module user
"""

import argparse
import re
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from loguru import logger
except ImportError:
    print("警告: 无法导入 loguru，将使用 print 替代")

    class Logger:
        """简单的日志记录器，用于替代 loguru"""

        @staticmethod
        def info(message: str):
            print(f"INFO: {message}")

        @staticmethod
        def error(message: str):
            print(f"ERROR: {message}")

        @staticmethod
        def warning(message: str):
            print(f"WARNING: {message}")

        @staticmethod
        def debug(message: str):
            print(f"DEBUG: {message}")

    logger = Logger()


class ModuleValidator:
    """模块验证器 - 验证模块结构是否完整"""

    def __init__(self):
        """初始化模块验证器"""
        self.modules_path = project_root / "Modules"

    def validate_module_name(self, module_name: str) -> tuple[bool, str]:
        """
        验证模块名称是否有效

        Args:
            module_name: 模块名称

        Returns:
            Tuple[bool, str]: (是否有效, 错误消息)
        """
        # 检查是否为空
        if not module_name:
            return False, "模块名称不能为空"

        # 检查是否是有效的Python标识符
        if not re.match(r"^[a-z][a-z0-9_]*$", module_name):
            return False, "模块名称必须以小写字母开头，只能包含小写字母、数字和下划线"

        # 检查是否是Python保留关键字
        python_keywords = {
            "False",
            "None",
            "True",
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
        }
        if module_name in python_keywords:
            return False, f"模块名称不能是Python保留关键字: {module_name}"

        return True, ""

    def check_module_exists(self, module_name: str) -> bool:
        """
        检查模块是否已存在

        Args:
            module_name: 模块名称

        Returns:
            bool: 模块是否存在
        """
        module_path = self.modules_path / module_name
        return module_path.exists()

    def check_required_directories(self, module_name: str) -> tuple[bool, list[str]]:
        """
        检查必需目录是否存在

        Args:
            module_name: 模块名称

        Returns:
            Tuple[bool, List[str]]: (是否全部存在, 缺失的目录列表)
        """
        module_path = self.modules_path / module_name
        required_dirs = [
            "controllers",
            "controllers/v1",
            "models",
            "queues",
            "routes",
            "seeds",
            "services",
            "tasks",
            "validators",
        ]

        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = module_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        return len(missing_dirs) == 0, missing_dirs

    def check_required_files(self, module_name: str) -> tuple[bool, list[str]]:
        """
        检查必需文件是否存在

        Args:
            module_name: 模块名称

        Returns:
            Tuple[bool, List[str]]: (是否全部存在, 缺失的文件列表)
        """
        module_path = self.modules_path / module_name
        required_files = [
            "controllers/v1/test_controller.py",
            "routes/test.py",
        ]

        missing_files = []
        for file_name in required_files:
            file_path = module_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        return len(missing_files) == 0, missing_files

    def validate_module(self, module_name: str) -> bool:
        """
        验证模块结构是否完整

        Args:
            module_name: 模块名称

        Returns:
            bool: 验证是否通过
        """
        logger.info(f"验证模块 {module_name} 的结构")

        # 检查模块目录是否存在
        module_path = self.modules_path / module_name
        if not module_path.exists():
            logger.error(f"模块目录不存在: {module_path}")
            return False

        # 检查必需目录
        dirs_valid, missing_dirs = self.check_required_directories(module_name)
        if not dirs_valid:
            logger.error(f"缺少目录: {', '.join(missing_dirs)}")
            return False

        # 检查必需文件
        files_valid, missing_files = self.check_required_files(module_name)
        if not files_valid:
            logger.error(f"缺少文件: {', '.join(missing_files)}")
            return False

        logger.info(f"模块 {module_name} 结构验证通过")
        return True


class ModuleCreator:
    """模块创建器 - 负责创建新模块的完整结构"""

    def __init__(self):
        """初始化模块创建器"""
        self.modules_path = project_root / "Modules"
        self.validator = ModuleValidator()

    def create_module(self, module_name: str) -> bool:
        """
        创建新模块

        Args:
            module_name: 模块名称

        Returns:
            bool: 创建是否成功
        """
        logger.info(f"正在创建模块 {module_name}...")

        # 验证模块名称
        is_valid, error_msg = self.validator.validate_module_name(module_name)
        if not is_valid:
            logger.error(f"模块名称无效: {error_msg}")
            return False

        # 检查模块是否已存在
        if self.validator.check_module_exists(module_name):
            logger.warning(f"模块 {module_name} 已存在，将强制覆盖")

        # 创建目录结构
        if not self._create_directory_structure(module_name):
            return False

        # 创建 __init__.py 文件
        if not self._create_init_files(module_name):
            return False

        # 创建控制器文件
        if not self._create_controller(module_name):
            return False

        # 创建路由文件
        if not self._create_routes(module_name):
            return False

        logger.info(f"模块 {module_name} 创建完成")
        return True

    def _create_directory_structure(self, module_name: str) -> bool:
        """
        创建目录结构

        Args:
            module_name: 模块名称

        Returns:
            bool: 创建是否成功
        """
        logger.info(f"创建模块 {module_name} 的目录结构...")

        module_path = self.modules_path / module_name
        directories = [
            "controllers",
            "controllers/v1",
            "models",
            "queues",
            "routes",
            "seeds",
            "services",
            "tasks",
            "validators",
        ]

        try:
            # 创建模块主目录
            module_path.mkdir(exist_ok=True)

            # 创建子目录
            for dir_name in directories:
                dir_path = module_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"创建目录: {dir_path}")

            return True

        except Exception as e:
            logger.error(f"创建目录结构失败: {e}")
            return False

    def _create_init_files(self, module_name: str) -> bool:
        """
        创建所有 __init__.py 文件

        Args:
            module_name: 模块名称

        Returns:
            bool: 创建是否成功
        """
        logger.info(f"创建模块 {module_name} 的 __init__.py 文件...")

        module_path = self.modules_path / module_name
        class_name = "".join(word.capitalize() for word in module_name.split("_"))

        init_files = {
            "": f'''"""
{class_name}模块

本模块包含 {module_name} 相关的所有功能。
"""
''',
            "controllers": f'''"""
{class_name}控制器

包含 {module_name} 模块的所有控制器。
"""
''',
            "controllers/v1": f'''"""
{class_name} V1控制器

包含 {module_name} 模块的 V1 版本控制器。
"""
''',
            "models": f'''"""
{class_name}模型

包含 {module_name} 模块的所有数据模型。
"""
''',
            "queues": f'''"""
{class_name}队列

包含 {module_name} 模块的异步任务队列。
"""
''',
            "routes": f'''"""
{class_name}模块路由包
"""

from fastapi import APIRouter

from .test import router as router_test

# 创建主路由器
main_router = APIRouter(prefix="/{module_name}")


# {module_name} - 测试接口
main_router.include_router(router_test)
''',
            "seeds": f'''"""
{class_name}种子数据

包含 {module_name} 模块的种子数据。
"""
''',
            "services": f'''"""
{class_name}服务

包含 {module_name} 模块的所有业务逻辑服务。
"""
''',
            "tasks": f'''"""
{class_name}任务

包含 {module_name} 模块的任务。
"""
''',
            "validators": f'''"""
{class_name}验证器

包含 {module_name} 模块的所有数据验证器。
"""
''',
        }

        try:
            for init_file, content in init_files.items():
                if init_file:
                    file_path = module_path / init_file / "__init__.py"
                else:
                    file_path = module_path / "__init__.py"
                file_path.write_text(content, encoding="utf-8")
                logger.debug(f"创建文件: {file_path}")

            return True

        except Exception as e:
            logger.error(f"创建 __init__.py 文件失败: {e}")
            return False

    def _create_controller(self, module_name: str) -> bool:
        """
        创建控制器文件

        Args:
            module_name: 模块名称

        Returns:
            bool: 创建是否成功
        """
        logger.info(f"创建模块 {module_name} 的控制器文件...")

        module_path = self.modules_path / module_name
        controller_file = module_path / "controllers" / "v1" / "test_controller.py"

        # 转换模块名称为类名
        class_name = "".join(word.capitalize() for word in module_name.split("_"))

        content = f'''"""
{class_name} 测试理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi.responses import JSONResponse

from Modules.common.libs.responses.response import success


class TestController:
    """测试控制器 - 是一个实例"""

    async def index(
        self,
    ) -> JSONResponse:
        """测试方法"""
        return success([], "测试{class_name}模块")
'''

        try:
            controller_file.write_text(content, encoding="utf-8")
            logger.debug(f"创建文件: {controller_file}")
            return True

        except Exception as e:
            logger.error(f"创建控制器文件失败: {e}")
            return False

    def _create_routes(self, module_name: str) -> bool:
        """
        创建路由文件（只包含一个示例接口）

        Args:
            module_name: 模块名称

        Returns:
            bool: 创建是否成功
        """
        logger.info(f"创建模块 {module_name} 的路由文件...")

        module_path = self.modules_path / module_name
        routes_file = module_path / "routes" / "test.py"

        # 转换模块名称为类名
        class_name = "".join(word.capitalize() for word in module_name.split("_"))

        content = f'''"""
{class_name}模块 测试路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.{module_name}.controllers.v1.test_controller import TestController

# 创建路由器
router = APIRouter(prefix="/test", tags=["{class_name}管理"])
# 创建控制器实例
controller = TestController()

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="{class_name}模块示例接口",
)(controller.index)
'''

        try:
            routes_file.write_text(content, encoding="utf-8")
            logger.debug(f"创建文件: {routes_file}")
            return True

        except Exception as e:
            logger.error(f"创建路由文件失败: {e}")
            return False


class ModuleLister:
    """模块列表器 - 列出所有模块"""

    def __init__(self):
        """初始化模块列表器"""
        self.modules_path = project_root / "Modules"
        self.validator = ModuleValidator()

    def list_modules(self, detail: bool = False) -> None:
        """
        列出所有模块

        Args:
            detail: 是否显示详细信息
        """
        if not self.modules_path.exists():
            print("Modules目录不存在")
            return

        modules = []
        for item in self.modules_path.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                modules.append(item.name)

        if not modules:
            print("未发现任何模块")
            return

        modules.sort()

        print("\n发现的模块:")
        print("-" * 60)

        if detail:
            print(f"{'模块名称':<20} {'文件数':<10}")
            print("-" * 45)

            for module_name in modules:
                module_path = self.modules_path / module_name

                # 统计文件数
                file_count = 0
                for file_path in module_path.rglob("*.py"):
                    if file_path.is_file() and file_path.name != "__init__.py":
                        file_count += 1

                print(f"{module_name:<20} {file_count:<10}")
        else:
            for module_name in modules:
                print(f"  - {module_name}")

        print("-" * 60)


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="模块创建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m commands.create_module create --module user
  python -m commands.create_module list
  python -m commands.create_module list --detail
  python -m commands.create_module validate --module user
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # create 命令
    create_parser = subparsers.add_parser("create", help="创建新模块")
    create_parser.add_argument("--module", "-m", required=True, help="模块名称")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有模块")
    list_parser.add_argument("--detail", action="store_true", help="显示详细信息")

    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证模块结构")
    validate_parser.add_argument("--module", "-m", required=True, help="模块名称")

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "create":
            creator = ModuleCreator()
            success = creator.create_module(args.module)
            sys.exit(0 if success else 1)

        elif args.command == "list":
            lister = ModuleLister()
            lister.list_modules(args.detail)

        elif args.command == "validate":
            validator = ModuleValidator()
            success = validator.validate_module(args.module)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        if logger:
            logger.error(f"执行命令失败: {e}")
        else:
            print(f"执行命令失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
