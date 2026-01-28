"""
Admin 模块种子数据

该模块包含Admin模块的种子数据生成函数。
"""

from Modules.admin.models.admin_admin import AdminAdmin
from Modules.admin.models.admin_group import AdminGroup
from Modules.admin.models.admin_rule import AdminRule
from Modules.admin.models.admin_sys_config import AdminSysConfig
from Modules.admin.models.admin_upload import AdminUpload
from Modules.common.libs.config import Config
from Modules.common.libs.database.sql.session import db_session_manager
from Modules.common.libs.password.password import PasswordService
from Modules.common.libs.time.utils import now


def seed_admin_data():
    """生成Admin模块的种子数据"""
    print("正在生成Admin模块的种子数据...")

    # 初始化数据库会话
    db_session_manager.init_session_maker()

    # 使用上下文管理器获取会话
    with db_session_manager.get_sync_session() as session:
        # 创建管理员组
        group_id = create_admin_groups(session)

        # 图片数据
        create_admin_uploads(session)

        # 创建管理员规则
        create_admin_rules(session)

        # 创建系统配置
        create_admin_sys_configs(session)

        # 创建管理员账号
        create_admin_accounts(session, group_id)

    print("✅ Admin模块种子数据生成完成!")


def create_admin_uploads(session):
    """创建图片数据"""

    # 检查是否已存在图片数据
    existing_rule = session.query(AdminUpload).first()
    if existing_rule:
        print("图片数据已存在，跳过创建")
        return
    # 创建图片数据
    upload1 = AdminUpload(
        original_name="logo.png",
        filename="logo.png",
        file_path="/logo.png",
        file_size=10000,
        mime_type="image/png",
        file_ext=".png",
        file_hash="111111111111111",
        storage_type="local",
        file_type="image",
        width=608,
        height=608,
        thumbnail_filename="",
        thumbnail_path="",
        created_at=now(),
    )

    session.add(upload1)
    session.commit()
    session.refresh(upload1)

    upload2 = AdminUpload(
        original_name="favicon.ico",
        filename="favicon.ico",
        file_path="/favicon.ico",
        file_size=100,
        mime_type="image/ico",
        file_ext=".ico",
        file_hash="22222222222222",
        storage_type="local",
        file_type="image",
        width=32,
        height=32,
        thumbnail_filename="",
        thumbnail_path="",
        created_at=now(),
    )

    session.add(upload2)
    session.commit()
    session.refresh(upload2)

    upload3 = AdminUpload(
        original_name="upload_watermark_image.png",
        filename="upload_watermark_image.png",
        file_path="/upload_watermark_image.png",
        file_size=6666666,
        mime_type="image/png",
        file_ext=".png",
        file_hash="333333333333",
        storage_type="local",
        file_type="image",
        width=200,
        height=200,
        thumbnail_filename="",
        thumbnail_path="",
        created_at=now(),
    )

    session.add(upload3)
    session.commit()
    session.refresh(upload3)
    print("创建图片数据成功")


def create_admin_groups(session):
    """创建管理员组"""
    # 检查是否已存在
    existing_group = session.query(AdminGroup).filter_by(name="超级管理员").first()
    if existing_group:
        print("管理员组 '超级管理员' 已存在，跳过创建")
        return [existing_group]

    # 创建新的管理员组
    group = AdminGroup(
        name="超级管理员",
        content="拥有系统所有权限的超级管理员组",
        status=1,
        rules="",  # 初始为空，后续可以分配权限
        created_at=now(),
        updated_at=now(),
    )

    session.add(group)
    session.commit()
    session.refresh(group)

    print(f"✓ 创建管理员组: {group.name}")
    return group.id


def create_admin_rules(session):
    """创建菜单规则"""

    # 检查是否已存在配置
    existing_rule = session.query(AdminRule).first()
    if existing_rule:
        print("菜单规则已存在，跳过创建")
        return
    # 创建系统管理菜单

    menu1 = AdminRule(
        name="系统管理",
        type=1,
        status=1,
        pid=0,
        path="/admin",
        icon="SettingOutlined",
        redirect="/admin/dashboard",
        component="",
        level=1,
        sort=1,
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
        path="/admin/dashboard",
        icon="HomeOutlined",
        redirect="",
        component="./admin/dashboard/index",
        level=2,
        sort=1,
        target="_self",
        created_at=now(),
    )
    session.add(menu2)
    session.commit()
    session.refresh(menu2)
    print(f"✓ 创建规则: {menu2.name}")

    menu2 = AdminRule(
        name="配置/文件",
        type=2,
        status=1,
        pid=menu1.id,
        path="/admin/sys",
        icon="SettingOutlined",
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

    menu3 = AdminRule(
        name="系统配置",
        type=3,
        status=1,
        pid=menu2.id,
        path="/admin/sys/sys_config",
        icon="SettingOutlined",
        redirect="",
        component="./admin/sys/sys_config/index",
        level=2,
        sort=1,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    menu3 = AdminRule(
        name="文件管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/admin/sys/upload",
        icon="FileDoneOutlined",
        redirect="",
        component="./admin/sys/upload/index",
        level=2,
        sort=2,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    menu2 = AdminRule(
        name="权限管理",
        type=2,
        status=1,
        pid=menu1.id,
        path="/admin/auth",
        icon="SafetyOutlined",
        redirect="",
        component="",
        level=2,
        sort=3,
        target="_self",
        created_at=now(),
    )
    session.add(menu2)
    session.commit()
    session.refresh(menu2)
    print(f"✓ 创建规则: {menu2.name}")

    menu3 = AdminRule(
        name="管理员管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/admin/auth/admin",
        icon="UserOutlined",
        redirect="",
        component="./admin/auth/admin/index",
        level=3,
        sort=1,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    menu3 = AdminRule(
        name="角色管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/admin/auth/group",
        icon="TeamOutlined",
        redirect="",
        component="./admin/auth/group/index",
        level=3,
        sort=2,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")

    menu3 = AdminRule(
        name="菜单管理",
        type=3,
        status=1,
        pid=menu2.id,
        path="/admin/auth/rule",
        icon="MenuOutlined",
        redirect="",
        component="./admin/auth/rule/index",
        level=3,
        sort=3,
        target="_self",
        created_at=now(),
    )
    session.add(menu3)
    session.commit()
    session.refresh(menu3)
    print(f"✓ 创建规则: {menu3.name}")


def create_admin_accounts(session, group_id):
    """创建管理员账号"""
    username = Config.get("app.default_admin_username")
    password = Config.get("app.default_admin_password")
    existing_admin = session.query(AdminAdmin).filter_by(username=username).first()
    if existing_admin:
        print("管理员账号 'admin' 已存在，跳过创建")

    # 密码管理器
    password_service = PasswordService()
    hashed_password = password_service.hash_password(password)
    # 创建新的管理员账号
    admin = AdminAdmin(
        name="超级管理员",
        username=username,
        password=hashed_password,
        phone="13800138000",
        status=1,
        group_id=group_id,
        created_at=now(),
        updated_at=now(),
    )

    session.add(admin)
    session.commit()
    session.refresh(admin)
    print(f"✓ 创建管理员账号: {admin.username} ({admin.name})")


def create_admin_sys_configs(session):
    """创建系统配置"""
    print("正在创建系统配置...")

    # 检查是否已存在配置
    existing_config = session.query(AdminSysConfig).first()
    if existing_config:
        print("系统配置已存在，跳过创建")
        return

    current_time = now()

    # 系统基础配置
    system_configs = [
        {
            "config_key": "site_name",
            "config_value": "Py Small Admin",
            "value_type": "string",
            "description": "网站名称",
            "group_code": "system",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "site_description",
            "config_value": "基于 FastAPI 的轻量级后台管理系统",
            "value_type": "string",
            "description": "网站描述",
            "group_code": "system",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "site_keywords",
            "config_value": "admin,fastapi,python",
            "value_type": "string",
            "description": "网站关键词",
            "group_code": "system",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "site_logo",
            "config_value": "1",
            "value_type": "int",
            "description": "网站Logo",
            "group_code": "system",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "site_favicon",
            "config_value": "2",
            "value_type": "int",
            "description": "网站图标",
            "group_code": "system",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "copyright",
            "config_value": "2025 Py Small Admin",
            "value_type": "string",
            "description": "版权信息",
            "group_code": "system",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "site_content",
            "config_value": "<p>我们是一个简单的后台<p>",
            "value_type": "string",
            "description": "关于我们",
            "group_code": "system",
            "created_at": current_time,
            "updated_at": current_time,
        },
    ]

    # 邮件配置
    email_configs = [
        {
            "config_key": "smtp_host",
            "config_value": "smtp.qq.com",
            "value_type": "string",
            "description": "SMTP服务器",
            "group_code": "email",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "smtp_port",
            "config_value": "587",
            "value_type": "int",
            "description": "SMTP端口",
            "group_code": "email",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "smtp_username",
            "config_value": "997786358@qq.com",
            "value_type": "string",
            "description": "SMTP用户名",
            "group_code": "email",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "smtp_password",
            "config_value": "mqgtpekykbzgbdfj",
            "value_type": "string",
            "description": "SMTP密码",
            "group_code": "email",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "mail_from_address",
            "config_value": "997786358@qq.com",
            "value_type": "string",
            "description": "发件人地址",
            "group_code": "email",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "mail_from_name",
            "config_value": "Py Small Admin",
            "value_type": "string",
            "description": "发件人名称",
            "group_code": "email",
            "created_at": current_time,
            "updated_at": current_time,
        },
    ]

    # 文件上传配置
    upload_configs = [
        {
            "config_key": "upload_storage_type",
            "config_value": "local",
            "value_type": "string",
            "description": "存储类型(local/aliyun_oss/tencent_oss/qiniu_oss)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_image_max_size",
            "config_value": "10",
            "value_type": "int",
            "description": "图片最大文件大小(MB)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_image_allowed_types",
            "config_value": '["jpg","jpeg","png","gif","bmp","webp"]',
            "value_type": "json",
            "description": "允许的图片类型",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_video_max_size",
            "config_value": "50",
            "value_type": "int",
            "description": "视频最大文件大小(MB)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_video_allowed_types",
            "config_value": '["mp4","avi","mov","wmv","flv","mkv"]',
            "value_type": "json",
            "description": "允许的视频类型",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_document_max_size",
            "config_value": "20",
            "value_type": "int",
            "description": "文档最大文件大小(MB)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_document_allowed_types",
            "config_value": '["pdf","doc","docx","xls","xlsx","ppt","pptx","txt"]',
            "value_type": "json",
            "description": "允许的文档类型",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_audio_max_size",
            "config_value": "20",
            "value_type": "int",
            "description": "音频最大文件大小(MB)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_audio_allowed_types",
            "config_value": '["mp3","wav","aac","flac","ogg","m4a"]',
            "value_type": "json",
            "description": "允许的音频类型",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_compress_enabled",
            "config_value": "true",
            "value_type": "bool",
            "description": "是否启用图片压缩",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_compress_quality",
            "config_value": "85",
            "value_type": "int",
            "description": "图片压缩质量(1-100)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_compress_max_width",
            "config_value": "1920",
            "value_type": "int",
            "description": "图片最大宽度(px)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_compress_max_height",
            "config_value": "1080",
            "value_type": "int",
            "description": "图片最大高度(px)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_enabled",
            "config_value": "true",
            "value_type": "bool",
            "description": "是否启用水印",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_type",
            "config_value": "text",
            "value_type": "string",
            "description": "水印类型(text/image)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_text",
            "config_value": "Py Small Admin",
            "value_type": "string",
            "description": "水印文字",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_position",
            "config_value": "bottom-right",
            "value_type": "string",
            "description": "水印位置(top-left/top-right/bottom-left/bottom-right/center)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_opacity",
            "config_value": "0.5",
            "value_type": "string",
            "description": "水印透明度(0-1)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_font_size",
            "config_value": "20",
            "value_type": "int",
            "description": "水印字体大小(px)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_font_color",
            "config_value": "#FFFFFF",
            "value_type": "string",
            "description": "水印字体颜色(十六进制)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_font_path",
            "config_value": "assets/fonts/SourceHanSansSC-Regular.otf",
            "value_type": "string",
            "description": "水印字体文件路径（相对于项目根目录）。",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_image",
            "config_value": "3",
            "value_type": "string",
            "description": "水印图片路径",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_image_scale",
            "config_value": "0.2",
            "value_type": "string",
            "description": "水印图片缩放比例(0-1)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_watermark_margin",
            "config_value": "10",
            "value_type": "int",
            "description": "水印边距(px)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_thumbnail_enabled",
            "config_value": "true",
            "value_type": "bool",
            "description": "是否生成缩略图",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_thumbnail_width",
            "config_value": "300",
            "value_type": "int",
            "description": "缩略图宽度(px)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_thumbnail_height",
            "config_value": "300",
            "value_type": "int",
            "description": "缩略图高度(px)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_thumbnail_suffix",
            "config_value": "_thumb",
            "value_type": "string",
            "description": "缩略图文件名后缀",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "config_key": "upload_thumbnail_quality",
            "config_value": "80",
            "value_type": "int",
            "description": "缩略图质量(1-100)",
            "group_code": "upload",
            "created_at": current_time,
            "updated_at": current_time,
        },
    ]

    # 合并所有配置
    all_configs = system_configs + email_configs + upload_configs

    # 批量创建配置
    for config_data in all_configs:
        config = AdminSysConfig(**config_data)
        session.add(config)
        print(f"✓ 创建配置: {config_data['config_key']} ({config_data['group_code']})")

    session.commit()
    print("✅ 系统配置创建完成!")
