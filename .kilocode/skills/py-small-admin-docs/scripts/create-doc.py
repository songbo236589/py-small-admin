#!/usr/bin/env python3
"""
创建 Py Small Admin 文档脚本

用法:
    python create-doc.py --type guide --title "快速开始" --path guides/quick-start.md
    python create-doc.py --type api --title "用户API" --path api/user-api.md
    python create-doc.py --type tutorial --title "创建第一个应用" --path tutorials/first-app.md
"""

import argparse
import os
from pathlib import Path

# 模板文件映射
TEMPLATE_MAP = {
    "guide": "assets/templates/guide-template.md",
    "api": "assets/templates/api-template.md",
    "tutorial": "assets/templates/tutorial-template.md",
}


def validate_filename(filename):
    """验证文件名是否符合规范"""
    # 检查是否使用 kebab-case
    if not filename.replace("-", "").replace("_", "").isalnum():
        print(f"❌ 错误: 文件名 '{filename}' 不符合 kebab-case 规范")
        return False

    # 检查是否使用小写字母
    if filename != filename.lower():
        print(f"❌ 错误: 文件名 '{filename}' 应该使用小写字母")
        return False

    # 检查扩展名
    if not filename.endswith(".md"):
        print(f"❌ 错误: 文件名 '{filename}' 必须以 .md 结尾")
        return False

    return True


def get_template_content(doc_type, title):
    """获取模板内容"""
    template_path = Path(__file__).parent.parent / TEMPLATE_MAP[doc_type]

    if not template_path.exists():
        print(f"❌ 错误: 模板文件不存在: {template_path}")
        return None

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换标题
    content = content.replace("文档标题", title)
    content = content.replace("API 名称", title)
    content = content.replace("教程标题", title)

    return content


def create_document(doc_type, title, output_path):
    """创建文档文件"""
    # 1. 验证文件名
    filename = os.path.basename(output_path)
    if not validate_filename(filename):
        return False

    # 2. 检查文档类型
    if doc_type not in TEMPLATE_MAP:
        print(f"❌ 错误: 不支持的文档类型 '{doc_type}'")
        print(f"   支持的类型: {', '.join(TEMPLATE_MAP.keys())}")
        return False

    # 3. 获取模板内容
    template_content = get_template_content(doc_type, title)
    if not template_content:
        return False

    # 4. 创建目录（如果不存在）
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 5. 创建文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(template_content)
        print(f"✅ 成功: 文档已创建: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 错误: 创建文件失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="创建 Py Small Admin 文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --type guide --title "快速开始" --path guides/quick-start.md
  %(prog)s --type api --title "用户API" --path api/user-api.md
  %(prog)s --type tutorial --title "创建第一个应用" --path tutorials/first-app.md
        """,
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["guide", "api", "tutorial"],
        help="文档类型（guide/api/tutorial）",
    )
    parser.add_argument("--title", required=True, help="文档标题")
    parser.add_argument(
        "--path", required=True, help="输出文件路径（相对于 dosc/ 目录）"
    )

    args = parser.parse_args()

    print(f"🚀 创建文档: {args.title}")
    print(f"   类型: {args.type}")
    print(f"   路径: {args.path}")
    print()

    success = create_document(args.type, args.title, args.path)

    if success:
        print()
        print("📝 下一步:")
        print("1. 编辑文档内容")
        print(
            "2. 注册到配置文件: python scripts/register-doc.py --path <path> --title <title>"
        )
        print("3. 验证文档: python scripts/validate-doc.py <path>")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
