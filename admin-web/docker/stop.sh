#!/bin/bash

# ===================================================================
# 前端 Docker 快速停止脚本
# ===================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 停止开发环境
stop_dev() {
    print_info "停止开发环境..."
    docker-compose down
    print_info "开发环境已停止"
}

# 停止生产环境
stop_prod() {
    print_info "停止生产环境..."
    docker-compose -f docker-compose.prod.yml down
    print_info "生产环境已停止"
}

# 停止所有环境
stop_all() {
    print_info "停止所有环境..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    print_info "所有环境已停止"
}

# 清理所有资源
clean_all() {
    print_warn "这将删除所有容器、网络和数据卷"
    read -p "确认清理? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "清理所有资源..."
        docker-compose down -v
        docker-compose -f docker-compose.prod.yml down -v
        print_info "清理完成"
    else
        print_info "取消清理"
    fi
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  dev       停止开发环境"
    echo "  prod      停止生产环境"
    echo "  all       停止所有环境"
    echo "  clean     清理所有资源（包括数据卷）"
    echo "  help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev       # 停止开发环境"
    echo "  $0 prod      # 停止生产环境"
    echo "  $0 all       # 停止所有环境"
}

# 主函数
main() {
    OPTION=${1:-help}

    case $OPTION in
        dev)
            stop_dev
            ;;
        prod)
            stop_prod
            ;;
        all)
            stop_all
            ;;
        clean)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "未知选项: $OPTION"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
