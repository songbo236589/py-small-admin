#!/bin/bash
# ===================================================================
# MySQL 数据库备份脚本
# ===================================================================
# 功能: 备份MySQL数据库到指定目录
# 使用: ./backup.sh [dev|prod]
# ===================================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认配置
MYSQL_CONTAINER="py-small-admin-mysql"
MYSQL_DATABASE="fastapi_db"
MYSQL_USER="root"
MYSQL_PASSWORD="root123456"
BACKUP_DIR="$SCRIPT_DIR/mysql-backups"
BACKUP_FILE_PREFIX="mysql_backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${BACKUP_FILE_PREFIX}_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

# 检查Docker是否安装
check_docker() {
    print_step "检查Docker环境..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装"
        exit 1
    fi

    print_info "Docker环境检查通过"
}

# 检查MySQL容器是否运行
check_mysql_container() {
    print_step "检查MySQL容器状态..."

    if ! docker ps --format "{{.Names}}" | grep -q "^${MYSQL_CONTAINER}$"; then
        print_error "MySQL容器未运行: $MYSQL_CONTAINER"
        print_info "请先启动服务: ./start.sh"
        exit 1
    fi

    print_info "MySQL容器运行正常"
}

# 创建备份目录
create_backup_dir() {
    print_step "创建备份目录..."

    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_info "备份目录已创建: $BACKUP_DIR"
    else
        print_info "备份目录已存在: $BACKUP_DIR"
    fi
}

# 执行数据库备份
backup_database() {
    print_step "开始备份数据库..."
    print_info "数据库: $MYSQL_DATABASE"
    print_info "备份文件: $BACKUP_FILE"

    # 执行备份
    docker exec "$MYSQL_CONTAINER" mysqldump \
        -u"$MYSQL_USER" \
        -p"$MYSQL_PASSWORD" \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --quick \
        --lock-tables=false \
        "$MYSQL_DATABASE" | gzip > "$BACKUP_FILE"

    if [ $? -eq 0 ]; then
        print_info "数据库备份成功"
    else
        print_error "数据库备份失败"
        exit 1
    fi
}

# 显示备份文件信息
show_backup_info() {
    print_step "备份文件信息..."

    if [ -f "$BACKUP_FILE" ]; then
        local file_size=$(du -h "$BACKUP_FILE" | cut -f1)
        print_info "文件大小: $file_size"
        print_info "文件路径: $BACKUP_FILE"
    fi
}

# 清理旧备份
cleanup_old_backups() {
    print_step "清理旧备份（保留最近${RETENTION_DAYS}天）..."

    local deleted_count=$(find "$BACKUP_DIR" -name "${BACKUP_FILE_PREFIX}_*.sql.gz" -mtime +$RETENTION_DAYS -type f -delete -print | wc -l)

    if [ $deleted_count -gt 0 ]; then
        print_info "已删除 $deleted_count 个旧备份文件"
    else
        print_info "没有需要清理的旧备份"
    fi
}

# 列出所有备份文件
list_backups() {
    print_step "现有备份文件列表..."

    if [ "$(ls -A $BACKUP_DIR/*.sql.gz 2>/dev/null)" ]; then
        ls -lh "$BACKUP_DIR"/*.sql.gz | awk '{print $9, $5}'
    else
        print_info "没有备份文件"
    fi
}

# 恢复数据库
restore_database() {
    local backup_file="$1"

    if [ -z "$backup_file" ]; then
        print_error "请指定要恢复的备份文件"
        print_info "用法: ./backup.sh restore <backup_file>"
        exit 1
    fi

    if [ ! -f "$backup_file" ]; then
        print_error "备份文件不存在: $backup_file"
        exit 1
    fi

    print_warn "警告: 将恢复数据库，现有数据将被覆盖！"
    read -p "确认恢复数据库？(yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        print_info "已取消恢复操作"
        exit 0
    fi

    print_step "开始恢复数据库..."
    print_info "备份文件: $backup_file"

    # 解压并恢复
    gunzip < "$backup_file" | docker exec -i "$MYSQL_CONTAINER" mysql \
        -u"$MYSQL_USER" \
        -p"$MYSQL_PASSWORD" \
        "$MYSQL_DATABASE"

    if [ $? -eq 0 ]; then
        print_info "数据库恢复成功"
    else
        print_error "数据库恢复失败"
        exit 1
    fi
}

# 主函数
main() {
    local action="${1:-backup}"
    local env_type="${2:-dev}"

    echo ""
    print_info "======================================"
    print_info "Py Small Admin MySQL 备份脚本"
    print_info "======================================"
    print_info "操作类型: $action"
    print_info "环境类型: $env_type"
    echo ""

    # 切换到docker目录
    cd "$SCRIPT_DIR"

    # 根据环境类型调整配置
    if [ "$env_type" = "prod" ]; then
        MYSQL_CONTAINER="py-small-admin-mysql-prod"
        MYSQL_PASSWORD="${MYSQL_PASSWORD_PROD:-root123456}"
        RETENTION_DAYS=30
    fi

    # 检查Docker环境
    check_docker

    # 检查MySQL容器
    check_mysql_container

    # 创建备份目录
    create_backup_dir

    # 根据操作类型执行相应操作
    case "$action" in
        backup)
            # 执行备份
            backup_database

            # 显示备份信息
            show_backup_info

            # 清理旧备份
            cleanup_old_backups

            # 列出所有备份
            list_backups

            echo ""
            print_info "======================================"
            print_info "备份完成！"
            print_info "======================================"
            echo ""
            print_info "常用命令："
            echo "  - 恢复数据库: ./backup.sh restore <backup_file>"
            echo "  - 列出备份:  ./backup.sh list"
            echo ""
            ;;

        restore)
            # 恢复数据库
            restore_database "$3"
            ;;

        list)
            # 列出所有备份
            list_backups
            ;;

        *)
            print_error "未知操作: $action"
            echo ""
            print_info "可用操作："
            echo "  - backup:  备份数据库（默认）"
            echo "  - restore: 恢复数据库"
            echo "  - list:    列出所有备份"
            echo ""
            print_info "用法示例："
            echo "  - 备份数据库: ./backup.sh backup dev"
            echo "  - 恢复数据库: ./backup.sh restore dev /path/to/backup.sql.gz"
            echo "  - 列出备份:   ./backup.sh list"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
