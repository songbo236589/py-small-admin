#!/bin/bash
# ===================================================================
# Docker 资源清理脚本
# ===================================================================
# 功能: 清理Docker未使用的资源（镜像、容器、网络、数据卷）
# 使用: ./clean.sh [--all]
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

    print_info "Docker环境检查通过"
}

# 显示当前资源使用情况
show_current_usage() {
    print_step "当前Docker资源使用情况..."
    docker system df
    echo ""
}

# 停止所有Py Small Admin容器
stop_containers() {
    print_step "停止Py Small Admin容器..."

    local containers=$(docker ps -a --filter "name=py-small-admin" --format "{{.Names}}" || true)

    if [ -n "$containers" ]; then
        echo "$containers" | xargs -r docker stop
        print_info "容器已停止"
    else
        print_info "没有运行中的Py Small Admin容器"
    fi
}

# 删除所有Py Small Admin容器
remove_containers() {
    print_step "删除Py Small Admin容器..."

    local containers=$(docker ps -a --filter "name=py-small-admin" --format "{{.Names}}" || true)

    if [ -n "$containers" ]; then
        echo "$containers" | xargs -r docker rm
        print_info "容器已删除"
    else
        print_info "没有Py Small Admin容器"
    fi
}

# 删除未使用的镜像
remove_unused_images() {
    print_step "删除未使用的Docker镜像..."
    local removed=$(docker image prune -f | grep "Total reclaimed space" || echo "0B")
    print_info "已删除未使用的镜像: $removed"
}

# 删除所有Py Small Admin镜像
remove_all_images() {
    print_step "删除所有Py Small Admin镜像..."

    local images=$(docker images --filter "reference=py-small-admin" --format "{{.ID}}" || true)

    if [ -n "$images" ]; then
        echo "$images" | xargs -r docker rmi -f
        print_info "镜像已删除"
    else
        print_info "没有Py Small Admin镜像"
    fi
}

# 删除未使用的网络
remove_unused_networks() {
    print_step "删除未使用的Docker网络..."
    local removed=$(docker network prune -f | grep "Total reclaimed space" || echo "0B")
    print_info "已删除未使用的网络: $removed"
}

# 删除Py Small Admin网络
remove_networks() {
    print_step "删除Py Small Admin网络..."

    local networks=$(docker network ls --filter "name=py-small-admin" --format "{{.Name}}" || true)

    if [ -n "$networks" ]; then
        echo "$networks" | xargs -r docker network rm
        print_info "网络已删除"
    else
        print_info "没有Py Small Admin网络"
    fi
}

# 删除未使用的数据卷
remove_unused_volumes() {
    print_step "删除未使用的Docker数据卷..."
    local removed=$(docker volume prune -f | grep "Total reclaimed space" || echo "0B")
    print_info "已删除未使用的数据卷: $removed"
}

# 删除Py Small Admin数据卷
remove_volumes() {
    print_step "删除Py Small Admin数据卷..."

    local volumes=$(docker volume ls --filter "name=py-small-admin" --format "{{.Name}}" || true)

    if [ -n "$volumes" ]; then
        print_warn "警告: 将删除所有数据卷，数据将丢失！"
        read -p "确认删除数据卷？(yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "$volumes" | xargs -r docker volume rm
            print_info "数据卷已删除"
        else
            print_info "已取消删除数据卷"
        fi
    else
        print_info "没有Py Small Admin数据卷"
    fi
}

# 清理构建缓存
remove_build_cache() {
    print_step "清理Docker构建缓存..."
    local removed=$(docker builder prune -f | grep "Total reclaimed space" || echo "0B")
    print_info "已清理构建缓存: $removed"
}

# 显示清理后的资源使用情况
show_final_usage() {
    print_step "清理后的Docker资源使用情况..."
    docker system df
    echo ""
}

# 主函数
main() {
    local clean_all="${1:-}"

    echo ""
    print_info "======================================"
    print_info "Py Small Admin Docker 清理脚本"
    print_info "======================================"
    if [ "$clean_all" = "--all" ]; then
        print_warn "警告: 将删除所有Py Small Admin相关资源！"
    fi
    echo ""

    # 切换到docker目录
    cd "$SCRIPT_DIR"

    # 检查Docker环境
    check_docker

    # 显示当前资源使用情况
    show_current_usage

    # 停止容器
    stop_containers

    # 删除容器
    remove_containers

    # 删除网络
    remove_networks

    # 删除未使用的网络
    remove_unused_networks

    # 删除未使用的镜像
    remove_unused_images

    # 清理构建缓存
    remove_build_cache

    # 如果是全部清理
    if [ "$clean_all" = "--all" ]; then
        # 删除所有镜像
        remove_all_images

        # 删除数据卷
        remove_volumes

        # 删除未使用的数据卷
        remove_unused_volumes
    else
        # 仅删除未使用的数据卷
        remove_unused_volumes
    fi

    # 显示清理后的资源使用情况
    show_final_usage

    echo ""
    print_info "======================================"
    print_info "清理完成！"
    print_info "======================================"
    echo ""
    print_info "常用命令："
    echo "  - 启动服务:   ./start.sh"
    echo "  - 停止服务:   ./stop.sh"
    echo "  - 查看资源:   docker system df"
    echo ""
}

# 执行主函数
main "$@"
