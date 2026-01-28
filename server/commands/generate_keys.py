#!/usr/bin/env python3
"""
密钥生成工具

用于生成和更新 .env 文件中的安全密钥：
- APP_ADMIN_X_API_KEY: 管理员接口验证的API密钥
- JWT_SECRET_KEY: JWT认证密钥

使用示例:
    python -m commands.generate_keys --all
    python -m commands.generate_keys --api-key
    python -m commands.generate_keys --jwt-secret
    python -m commands.generate_keys --all --dry-run
"""

import argparse
import re
import secrets
import string
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from loguru import logger
except ImportError:
    print("警告: 无法导入 loguru，将使用 print 替代")
    logger = None


class KeyGenerator:
    """密钥生成器"""

    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """
        生成API密钥

        Args:
            length: 密钥长度，默认32位

        Returns:
            str: 生成的API密钥
        """
        # 使用字母、数字和部分特殊字符
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_jwt_secret(length: int = 64) -> str:
        """
        生成JWT密钥

        Args:
            length: 密钥长度，默认64位（满足JWT安全要求）

        Returns:
            str: 生成的JWT密钥
        """
        # JWT密钥需要包含字母和数字，确保复杂度
        alphabet = string.ascii_letters + string.digits
        secret = "".join(secrets.choice(alphabet) for _ in range(length))

        # 验证密钥复杂度
        if not (re.search(r"[A-Za-z]", secret) and re.search(r"[0-9]", secret)):
            # 如果随机生成的密钥不符合要求，重新生成
            return KeyGenerator.generate_jwt_secret(length)

        return secret


class EnvFileManager:
    """环境文件管理器"""

    def __init__(self, env_path: Path | None = None):
        """
        初始化环境文件管理器

        Args:
            env_path: .env文件路径，默认为项目根目录下的.env
        """
        self.env_path = env_path or project_root / ".env"
        self.content = ""
        self.lines = []

    def read_env_file(self) -> bool:
        """
        读取.env文件内容

        Returns:
            bool: 读取是否成功
        """
        if not self.env_path.exists():
            if logger:
                logger.error(f".env文件不存在: {self.env_path}")
            else:
                print(f"错误: .env文件不存在: {self.env_path}")
            return False

        try:
            with open(self.env_path, encoding="utf-8") as f:
                self.content = f.read()
                self.lines = self.content.splitlines(keepends=True)
            return True
        except Exception as e:
            if logger:
                logger.error(f"读取.env文件失败: {e}")
            else:
                print(f"错误: 读取.env文件失败: {e}")
            return False

    def update_key(self, key_name: str, new_value: str) -> bool:
        """
        更新指定密钥的值

        Args:
            key_name: 密钥名称
            new_value: 新的密钥值

        Returns:
            bool: 更新是否成功
        """
        key_found = False
        updated_lines = []

        # 正则表达式匹配键值对
        pattern = re.compile(rf"^{re.escape(key_name)}\s*=\s*(.*)$")

        for line in self.lines:
            line_stripped = line.rstrip()
            match = pattern.match(line_stripped)

            if match:
                # 保留原有的注释和格式
                # 提取引号类型
                old_value = match.group(1).strip()
                quote_type = ""

                if old_value.startswith('"') and old_value.endswith('"'):
                    quote_type = '"'
                elif old_value.startswith("'") and old_value.endswith("'"):
                    quote_type = "'"

                # 构建新行
                new_line = f"{key_name}={quote_type}{new_value}{quote_type}\n"
                updated_lines.append(new_line)
                key_found = True

                if logger:
                    logger.info(f"已更新 {key_name}")
                else:
                    print(f"已更新 {key_name}")
            else:
                updated_lines.append(line)

        if not key_found:
            if logger:
                logger.warning(f"未找到 {key_name}，将在文件末尾添加")
            else:
                print(f"警告: 未找到 {key_name}，将在文件末尾添加")
            updated_lines.append(f'{key_name}="{new_value}"\n')

        self.lines = updated_lines
        return True

    def write_env_file(self) -> bool:
        """
        写入.env文件

        Returns:
            bool: 写入是否成功
        """
        try:
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.writelines(self.lines)
            return True
        except Exception as e:
            if logger:
                logger.error(f"写入.env文件失败: {e}")
            else:
                print(f"错误: 写入.env文件失败: {e}")
            return False

    def get_current_value(self, key_name: str) -> str | None:
        """
        获取当前密钥值

        Args:
            key_name: 密钥名称

        Returns:
            Optional[str]: 当前密钥值，如果不存在则返回None
        """
        pattern = re.compile(rf"^{re.escape(key_name)}\s*=\s*(.*)$")

        for line in self.lines:
            line_stripped = line.rstrip()
            match = pattern.match(line_stripped)

            if match:
                value = match.group(1).strip()
                # 去除引号
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                return value

        return None


def mask_key(key: str, show_chars: int = 4) -> str:
    """
    遮蔽密钥，只显示前几位和后几位

    Args:
        key: 原始密钥
        show_chars: 显示的字符数

    Returns:
        str: 遮蔽后的密钥
    """
    if len(key) <= show_chars * 2:
        return "*" * len(key)

    return key[:show_chars] + "*" * (len(key) - show_chars * 2) + key[-show_chars:]


def confirm_action(message: str) -> bool:
    """
    获取用户确认

    Args:
        message: 确认消息

    Returns:
        bool: 用户是否确认
    """
    while True:
        response = input(f"{message} (y/n): ").lower().strip()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("请输入 y 或 n")


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="密钥生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m commands.generate_keys --all
  python -m commands.generate_keys --api-key
  python -m commands.generate_keys --jwt-secret
  python -m commands.generate_keys --all --dry-run
  python -m commands.generate_keys --api-key --length 64
        """,
    )

    # 密钥类型选项
    key_group = parser.add_mutually_exclusive_group(required=True)
    key_group.add_argument("--all", action="store_true", help="生成所有密钥")
    key_group.add_argument("--api-key", action="store_true", help="只生成API密钥")
    key_group.add_argument("--jwt-secret", action="store_true", help="只生成JWT密钥")

    # 可选参数
    parser.add_argument(
        "--length", type=int, help="密钥长度（API密钥默认32，JWT密钥默认64）"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="预览模式，不实际修改文件"
    )
    parser.add_argument("--env", type=str, help="指定.env文件路径")
    parser.add_argument(
        "--yes", "-y", action="store_true", help="跳过确认步骤，直接执行"
    )

    # 解析参数
    args = parser.parse_args()

    # 创建环境文件管理器
    env_path = None
    if args.env:
        env_path = Path(args.env)
    env_manager = EnvFileManager(env_path)

    # 读取.env文件
    if not env_manager.read_env_file():
        sys.exit(1)

    # 生成密钥
    keys_to_generate = {}

    if args.all or args.api_key:
        api_key_length = args.length or 32
        api_key = KeyGenerator.generate_api_key(api_key_length)
        keys_to_generate["APP_ADMIN_X_API_KEY"] = api_key

    if args.all or args.jwt_secret:
        jwt_key_length = args.length or 64
        jwt_secret = KeyGenerator.generate_jwt_secret(jwt_key_length)
        keys_to_generate["JWT_SECRET_KEY"] = jwt_secret

    # 显示将要生成的密钥
    print("\n将要生成的密钥:")
    print("-" * 50)
    for key_name, key_value in keys_to_generate.items():
        current_value = env_manager.get_current_value(key_name)
        print(f"配置项: {key_name}")
        if current_value:
            print(f"当前值: {mask_key(current_value)}")
        print(f"新值:   {mask_key(key_value)}")
        print(f"长度:   {len(key_value)}")
        print("-" * 50)

    # 如果是预览模式，直接退出
    if args.dry_run:
        print("\n预览模式，未实际修改文件")
        sys.exit(0)

    # 获取用户确认
    if not args.yes:
        if not confirm_action("\n确认要更新这些密钥吗？"):
            print("操作已取消")
            sys.exit(0)

    # 更新密钥
    success = True
    for key_name, key_value in keys_to_generate.items():
        if not env_manager.update_key(key_name, key_value):
            success = False
            break

    if not success:
        print("更新密钥失败")
        sys.exit(1)

    # 写入文件
    if not env_manager.write_env_file():
        print("写入.env文件失败")
        sys.exit(1)

    print("\n密钥更新成功！")


if __name__ == "__main__":
    main()
