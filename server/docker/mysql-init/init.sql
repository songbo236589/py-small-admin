-- ===================================================================
-- MySQL 初始化脚本 - Py Small Admin
-- ===================================================================
-- 说明:
-- - 此脚本在MySQL容器首次启动时自动执行
-- - 用于创建数据库用户和权限
-- - 请根据实际需求修改配置
-- ===================================================================

-- ===================================================================
-- 创建数据库用户（如果不存在）
-- ===================================================================

-- 创建应用用户（如果不存在）
CREATE USER IF NOT EXISTS 'fastapi_user'@'%' IDENTIFIED BY 'fastapi_password';

-- ===================================================================
-- 授予权限
-- ===================================================================

-- 授予fastapi_db的所有权限给fastapi_user
GRANT ALL PRIVILEGES ON fastapi_db.* TO 'fastapi_user'@'%';

-- 授予Redis用户访问权限（如果需要）
-- CREATE USER IF NOT EXISTS 'redis_user'@'%' IDENTIFIED BY 'redis_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON fastapi_db.* TO 'redis_user'@'%';

-- ===================================================================
-- 刷新权限
-- ===================================================================

FLUSH PRIVILEGES;

-- ===================================================================
-- 创建基础表（可选）
-- ===================================================================
-- 注意：实际的表结构由Alembic迁移管理，这里只创建必要的配置表

-- 创建系统配置表（如果不存在）
CREATE TABLE IF NOT EXISTS `fa_admin_sys_config` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `config_key` varchar(100) NOT NULL COMMENT '配置键',
    `config_value` text COMMENT '配置值',
    `config_type` varchar(20) DEFAULT 'string' COMMENT '配置类型',
    `group_name` varchar(50) DEFAULT 'default' COMMENT '分组名称',
    `description` varchar(255) DEFAULT NULL COMMENT '配置描述',
    `is_system` tinyint(1) DEFAULT 0 COMMENT '是否系统配置',
    `sort` int(11) DEFAULT 0 COMMENT '排序',
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_config_key` (`config_key`),
    KEY `idx_group_name` (`group_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ===================================================================
-- 插入默认配置（可选）
-- ===================================================================

-- 插入默认系统配置
INSERT INTO `fa_admin_sys_config` (`config_key`, `config_value`, `config_type`, `group_name`, `description`, `is_system`, `sort`) VALUES
('site_name', 'Py Small Admin', 'string', 'site', '网站名称', 1, 1),
('site_description', 'Py Small Admin 管理系统', 'string', 'site', '网站描述', 1, 2),
('site_keywords', 'python,fastapi,admin', 'string', 'site', '网站关键词', 1, 3),
('site_copyright', '© 2024 Py Small Admin', 'string', 'site', '版权信息', 1, 4),
('upload_max_size', '104857600', 'number', 'upload', '最大上传大小（字节）', 1, 1),
('upload_allowed_types', 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx', 'string', 'upload', '允许上传的文件类型', 1, 2)
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- ===================================================================
-- 完成提示
-- ===================================================================

SELECT 'MySQL初始化脚本执行完成！' AS message;
