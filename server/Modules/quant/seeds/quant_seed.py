"""
Quant 模块种子数据

该模块包含Quant模块的种子数据生成函数。
"""

from Modules.admin.models.admin_rule import AdminRule
from Modules.common.libs.database.sql.session import db_session_manager
from Modules.common.libs.time.utils import now


def seed_quant_data():
    """生成Quant模块的种子数据"""
    print("正在生成Quant模块的种子数据...")

    # 初始化数据库会话
    db_session_manager.init_session_maker()

    # 使用上下文管理器获取会话
    with db_session_manager.get_sync_session() as session:
        # 创建量化管理菜单规则
        create_quant_rules(session)

    print("✅ Quant模块种子数据生成完成!")


def create_quant_rules(session):
    """创建量化管理菜单规则"""

    # 检查是否已存在配置
    existing_rule = session.query(AdminRule).filter_by(name="量化管理").first()
    if existing_rule:
        print("量化管理菜单规则已存在，跳过创建")
        return

    # 创建量化管理主菜单
    menu1 = AdminRule(
        name="量化管理",
        type=1,
        status=1,
        pid=0,
        path="/quant",
        icon="LineChartOutlined",
        redirect="/quant/dashboard",
        component="",
        level=1,
        sort=2,
        target="_self",
        created_at=now(),
    )
    session.add(menu1)
    session.commit()
    session.refresh(menu1)
    print(f"✓ 创建规则: {menu1.name}")

    menu2 = AdminRule(
        name="控制台",
        type=3,
        status=1,
        pid=menu1.id,
        path="/quant/dashboard",
        icon="HomeOutlined",
        redirect="",
        component="./quant/dashboard/index",
        level=2,
        sort=1,
        target="_self",
        created_at=now(),
    )
    session.add(menu2)
    session.commit()
    session.refresh(menu2)
    print(f"✓ 创建规则: {menu2.name}")

    # 创建概念管理子菜单
    menu2 = AdminRule(
        name="数据管理",
        type=2,
        status=1,
        pid=menu1.id,
        path="/quant/data",
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
    print(f"✓ 创建规则: {menu2.name}")

    # 概念数据
    menu3 = AdminRule(
        name="概念数据",
        type=3,
        status=1,
        pid=menu2.id,
        path="/quant/data/concept",
        icon="StockOutlined",
        redirect="",
        component="./quant/data/concept/index",
        level=3,
        sort=1,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 概念数据日志
    menu3 = AdminRule(
        name="概念数据日志",
        type=3,
        status=1,
        pid=menu2.id,
        path="/quant/data/concept_log",
        icon="StockOutlined",
        redirect="",
        component="./quant/data/concept_log/index",
        level=3,
        sort=2,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 行业数据
    menu3 = AdminRule(
        name="行业数据",
        type=3,
        status=1,
        pid=menu2.id,
        path="/quant/data/industry",
        icon="StockOutlined",
        redirect="",
        component="./quant/data/industry/index",
        level=3,
        sort=3,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 行业数据日志
    menu3 = AdminRule(
        name="行业数据日志",
        type=3,
        status=1,
        pid=menu2.id,
        path="/quant/data/industry_log",
        icon="StockOutlined",
        redirect="",
        component="./quant/data/industry_log/index",
        level=3,
        sort=4,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    # 股票数据
    menu3 = AdminRule(
        name="股票数据",
        type=3,
        status=1,
        pid=menu2.id,
        path="/quant/data/stock",
        icon="StockOutlined",
        redirect="",
        component="./quant/data/stock/index",
        level=3,
        sort=5,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    print("✅ 量化管理菜单规则创建完成!")
