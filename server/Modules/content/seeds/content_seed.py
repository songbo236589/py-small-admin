"""
Content 模块种子数据

该模块包含Content模块的种子数据生成函数。
"""

from Modules.admin.models.admin_rule import AdminRule
from Modules.common.libs.database.sql.session import db_session_manager
from Modules.common.libs.time.utils import now


def seed_content_data():
    """生成Content模块的种子数据"""
    print("正在生成Content模块的种子数据...")

    # 初始化数据库会话
    db_session_manager.init_session_maker()

    # 使用上下文管理器获取会话
    with db_session_manager.get_sync_session() as session:
        # 创建内容管理菜单规则
        create_content_rules(session)

    print("✅ Content模块种子数据生成完成!")


def create_content_rules(session):
    """创建内容管理菜单规则"""

    # 检查是否已存在配置
    existing_rule = session.query(AdminRule).filter_by(name="内容管理").first()
    if existing_rule:
        print("内容管理菜单规则已存在，跳过创建")
        return

    # 创建内容管理主菜单
    menu1 = AdminRule(
        name="内容管理",
        type=1,
        status=1,
        pid=0,
        path="/content",
        icon="ReadOutlined",
        redirect="/content/dashboard",
        component="",
        level=1,
        sort=3,
        target="_self",
        created_at=now(),
    )
    session.add(menu1)
    session.commit()
    session.refresh(menu1)
    print(f"✓ 创建规则: {menu1.name}")

    # 创建控制台菜单
    menu2 = AdminRule(
        name="控制台",
        type=3,
        status=1,
        pid=menu1.id,
        path="/content/dashboard",
        icon="HomeOutlined",
        redirect="",
        component="./content/dashboard/index",
        level=2,
        sort=1,
        target="_self",
        created_at=now(),
    )
    session.add(menu2)
    session.commit()
    session.refresh(menu2)
    print(f"✓ 创建规则: {menu2.name}")

    # 创建内容管理分组菜单
    menu2 = AdminRule(
        name="内容管理",
        type=2,
        status=1,
        pid=menu1.id,
        path="/content/manage",
        icon="AppstoreOutlined",
        redirect="",
        component="",
        level=2,
        sort=2,
        target="_self",
        created_at=now(),
    )
    session.add(menu2)
    session.commit()
    session.refresh(menu2)
    print(f"✓ 创建规则: {menu2.name} (分组)")

    # 文章管理菜单（level=3）
    menu3 = AdminRule(
        name="文章管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/content/manage/article",
        icon="FileTextOutlined",
        redirect="",
        component="./content/article/index",
        level=3,
        sort=1,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 分类管理菜单（level=3）
    menu3 = AdminRule(
        name="分类管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/content/manage/category",
        icon="FolderOutlined",
        redirect="",
        component="./content/category/index",
        level=3,
        sort=2,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 标签管理菜单（level=3）
    menu3 = AdminRule(
        name="标签管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/content/manage/tag",
        icon="TagsOutlined",
        redirect="",
        component="./content/tag/index",
        level=3,
        sort=3,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 平台账号管理菜单（level=3）
    menu3 = AdminRule(
        name="平台账号",
        type=3,
        status=1,
        pid=menu2.id,
        path="/content/manage/platform_account",
        icon="UserSwitchOutlined",
        redirect="",
        component="./content/platform_account/index",
        level=3,
        sort=4,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 话题管理菜单（level=3）
    menu3 = AdminRule(
        name="话题管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/content/manage/topic",
        icon="FireOutlined",
        redirect="",
        component="./content/topic/index",
        level=3,
        sort=5,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 发布管理菜单（level=3）
    menu3 = AdminRule(
        name="发布管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/content/manage/publish",
        icon="SendOutlined",
        redirect="",
        component="./content/publish/index",
        level=3,
        sort=6,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    print("✅ 内容管理菜单规则创建完成!")
