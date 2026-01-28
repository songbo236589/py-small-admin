#!/bin/bash
# ===================================================================
# Docker 服务停止脚本
# ===================================================================
# 功能: 一键停止所有Docker服务
# 使用: ./stop.sh [dev|prod] [--remove-volumes]
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

# 检查Docker是否安装
check_docker() {
    print_step "检查Docker环境..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装"
        exit 1
    fi

    print_info "Docker环境检查通过"
}

# 停止服务
stop_services() {
    print_step "停止Docker服务..."
    docker-compose -f "$1" down "$2"
    print_info "Docker服务已停止"
}

# 显示容器状态
show_containers() {
    print_step "显示运行中的容器..."
    local running_containers=$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep py-small-admin || true)

    if [ -n "$running_containers" ]; then
        echo "$running_containers"
    else
        print_info "没有运行中的Py Small Admin容器"
    fi
}

# 显示磁盘使用情况
show_disk_usage() {
    print_step "显示Docker磁盘使用情况..."
    docker system df
}

# 主函数
main() {
    local env_type="${1:-dev}"
    local remove_volumes=""
    local compose_file="docker-compose.yml"

    echo ""
    print_info "======================================"
    print_info "Py Small Admin Docker 停止脚本"
    print_info "======================================"
    print_info "环境类型: $env_type"
    echo ""

    # 切换到docker目录
    cd "$SCRIPT_DIR"

    # 检查是否删除数据卷
    if [ "$2" = "--remove-volumes" ]; then
        remove_volumes="--volumes"
        print_warn "警告: 将删除所有数据卷，数据将丢失！"
        read -p "确认删除数据卷？(yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            print_info "已取消操作"
            exit 0
        fi
    fi

    # 根据环境类型选择配置文件
    if [ "$env_type" = "prod" ]; then
        compose_file="docker-compose.prod.yml"
    fi

    # 检查Docker环境
    check_docker

    # 停止服务
    stop_services "$compose_file" "$remove_volumes"

    # 显示容器状态
    show_containers

    # 显示磁盘使用情况
    show_disk_usage

    echo ""
    print_info "======================================"
    print_info "服务停止完成！"
    print_info "======================================"
    echo ""
    print_info "常用命令："
    echo "  - 启动服务:   ./start.sh"
    echo "  - 清理资源:   ./clean.sh"
    echo "  - 查看容器:   docker ps -a"
    echo ""
}

# 执行主函数
main "$@"
