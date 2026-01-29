#!/usr/bin/env python3
"""
注册文档到 VitePress 配置文件

用法:
    python register-doc.py --path guides/quick-start.md --title "快速开始"
    python register-doc.py --path api/user-api.md --title "用户API"
"""

import argparse
import re
from pathlib import Path

# 配置文件路径
CONFIG_FILE = (
    Path(__file__).parent.parent.parent.parent / "dosc" / ".vitepress" / "config.mts"
)


def find_function(content, function_name):
    """查找函数定义"""
    pattern = rf"function\s+{function_name}\s*\([^)]*\)\s*{{"
    match = re.search(pattern, content)
    return match if match else None


def add_to_nav(content, doc_path, doc_title):
    """添加到导航"""
    # 查找 createNav 函数
    nav_match = find_function(content, "createNav")
    if not nav_match:
        print("❌ 错误: 未找到 createNav 函数")
        return False, content

    # 提取函数内容
    start_pos = nav_match.end()
    end_pos = content.find("}", start_pos)
    if end_pos == -1:
        print("❌ 错误: createNav 函数格式不正确")
        return False, content

    nav_content = content[start_pos:end_pos]

    # 检查是否已存在
    if doc_path in nav_content:
        print(f"⚠️  警告: 文档 '{doc_path}' 已在导航中")
        return True, content

    # 构建新的导航项
    nav_item = f"    {{ text: '{doc_title}', link: '{doc_path}' }},"

    # 在 return 语句后添加
    return_pattern = r"return\s*\["
    return_match = re.search(return_pattern, nav_content)
    if return_match:
        insert_pos = start_pos + return_match.end()
        new_content = content[:insert_pos] + "\n" + nav_item + content[insert_pos:]
        print(f"✅ 成功: 已添加到导航")
        return True, new_content
    else:
        print("❌ 错误: 未找到 return 语句")
        return False, content


def add_to_sidebar(content, doc_path, doc_title):
    """添加到侧边栏"""
    # 查找 createSidebar 函数
    sidebar_match = find_function(content, "createSidebar")
    if not sidebar_match:
        print("❌ 错误: 未找到 createSidebar 函数")
        return False, content

    # 提取函数内容
    start_pos = sidebar_match.end()
    end_pos = content.find("}", start_pos)
    if end_pos == -1:
        print("❌ 错误: createSidebar 函数格式不正确")
        return False, content

    sidebar_content = content[start_pos:end_pos]

    # 检查是否已存在
    if doc_path in sidebar_content:
        print(f"⚠️  警告: 文档 '{doc_path}' 已在侧边栏中")
        return True, content

    # 确定文档类型
    if doc_path.startswith("/guides/"):
        section_name = "指南"
        section_key = "/guides/"
    elif doc_path.startswith("/api/"):
        section_name = "API"
        section_key = "/api/"
    elif doc_path.startswith("/tutorials/"):
        section_name = "教程"
        section_key = "/tutorials/"
    else:
        print(f"⚠️  警告: 无法确定文档类型，将添加到指南部分")
        section_name = "指南"
        section_key = "/guides/"

    # 检查部分是否存在
    section_pattern = rf"'{section_key}':\s*\["
    section_match = re.search(section_pattern, sidebar_content)

    if section_match:
        # 部分存在，添加到 items
        section_start = start_pos + section_match.end()
        items_pattern = r"items:\s*\["
        items_match = re.search(items_pattern, sidebar_content[section_start:])

        if items_match:
            items_pos = section_start + items_match.end()
            sidebar_item = f'          {{ text: "{doc_title}", link: "{doc_path}" }},\n'
            new_content = content[:items_pos] + sidebar_item + content[items_pos:]
            print(f"✅ 成功: 已添加到侧边栏（{section_name}部分）")
            return True, new_content
        else:
            print("❌ 错误: 未找到 items 数组")
            return False, content
    else:
        # 部分不存在，创建新部分
        new_section = f"""
    '{section_key}': [
      {{
        text: '{section_name}',
        items: [
          {{ text: "{doc_title}", link: "{doc_path}" }},
        ],
      }},
    """

        # 在 return 语句前添加
        return_pattern = r"return\s*\{"
        return_match = re.search(return_pattern, sidebar_content)
        if return_match:
            insert_pos = start_pos + return_match.start()
            new_content = content[:insert_pos] + new_section + content[insert_pos:]
            print(f"✅ 成功: 已创建新侧边栏部分（{section_name}）")
            return True, new_content
        else:
            print("❌ 错误: 未找到 return 语句")
            return False, content


def register_document(doc_path, doc_title):
    """注册文档到配置文件"""
    # 1. 读取配置文件
    if not CONFIG_FILE.exists():
        print(f"❌ 错误: 配置文件不存在: {CONFIG_FILE}")
        return False

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"📝 注册文档: {doc_path}")
    print(f"   标题: {doc_title}")
    print()

    # 2. 添加到导航
    success, content = add_to_nav(content, doc_path, doc_title)
    if not success:
        return False

    # 3. 添加到侧边栏
    success, content = add_to_sidebar(content, doc_path, doc_title)
    if not success:
        return False

    # 4. 保存配置文件
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print()
        print(f"✅ 成功: 配置文件已更新: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ 错误: 保存配置文件失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="注册文档到 VitePress 配置文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --path guides/quick-start.md --title "快速开始"
  %(prog)s --path api/user-api.md --title "用户API"
  %(prog)s --path tutorials/first-app.md --title "创建第一个应用"
        """,
    )

    parser.add_argument("--path", required=True, help="文档路径（相对于 dosc/ 目录）")
    parser.add_argument("--title", required=True, help="文档标题")

    args = parser.parse_args()

    # 验证路径格式
    if not args.path.startswith("/"):
        args.path = "/" + args.path

    success = register_document(args.path, args.title)

    if success:
        print()
        print("📝 下一步:")
        print("1. 检查配置文件: dosc/.vitepress/config.mts")
        print("2. 启动开发服务器: cd dosc && npm run docs:dev")
        print("3. 访问 http://localhost:5173 查看效果")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
