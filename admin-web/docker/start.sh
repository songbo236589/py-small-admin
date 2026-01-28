#!/bin/bash

# ===================================================================
# 前端 Docker 快速启动脚本
# ===================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    print_info "Docker 已安装: $(docker --version)"
}

# 检查 Docker Compose 是否安装
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    print_info "Docker Compose 已安装"
}

# 检查后端网络
check_backend_network() {
    ENV=$1
    if [ "$ENV" = "dev" ]; then
        NETWORK="py-small-admin-network"
    else
        NETWORK="py-small-admin-network-prod"
    fi

    if ! docker network inspect "$NETWORK" &> /dev/null; then
        print_warn "后端网络 $NETWORK 不存在"
        read -p "是否创建网络? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker network create "$NETWORK"
            print_info "网络 $NETWORK 创建成功"
        else
            print_error "无法启动，需要后端网络"
            exit 1
        fi
    else
        print_info "后端网络 $NETWORK 已存在"
    fi
}

# 启动开发环境
start_dev() {
    print_info "启动开发环境..."
    check_backend_network "dev"
    docker-compose up -d
    print_info "开发环境启动成功"
    print_info "访问地址: http://localhost:8000"
}

# 启动生产环境
start_prod() {
    print_info "启动生产环境..."

    # 检查环境变量文件
    if [ ! -f .env.production ]; then
        print_warn ".env.production 文件不存在"
        if [ -f .env.production.example ]; then
            read -p "是否从 .env.production.example 创建? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cp .env.production.example .env.production
                print_warn "请编辑 .env.production 文件配置环境变量"
                read -p "按 Enter 继续..."
            else
                print_error "无法启动，需要 .env.production 文件"
                exit 1
            fi
        fi
    fi

    check_backend_network "prod"
    docker-compose -f docker-compose.prod.yml up -d --build
    print_info "生产环境启动成功"
    print_info "访问地址: http://localhost:80"
}

# 停止服务
stop() {
    ENV=$1
    if [ "$ENV" = "prod" ]; then
        print_info "停止生产环境..."
        docker-compose -f docker-compose.prod.yml down
    else
        print_info "停止开发环境..."
        docker-compose down
    fi
    print_info "服务已停止"
}

# 查看日志
logs() {
    ENV=$1
    if [ "$ENV" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose logs -f
    fi
}

# 重新构建
rebuild() {
    ENV=$1
    if [ "$ENV" = "prod" ]; then
        print_info "重新构建生产环境..."
        docker-compose -f docker-compose.prod.yml build --no-cache
    else
        print_info "重新构建开发环境..."
        docker-compose build --no-cache
    fi
    print_info "构建完成"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令] [环境]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  logs      查看日志"
    echo "  rebuild   重新构建镜像"
    echo "  help      显示帮助信息"
    echo ""
    echo "环境:"
    echo "  dev       开发环境 (默认)"
    echo "  prod      生产环境"
    echo ""
    echo "示例:"
    echo "  $0 start dev      # 启动开发环境"
    echo "  $0 start prod     # 启动生产环境"
    echo "  $0 stop dev       # 停止开发环境"
    echo "  $0 logs dev       # 查看开发环境日志"
}

# 主函数
main() {
    check_docker
    check_docker_compose

    COMMAND=${1:-help}
    ENV=${2:-dev}

    case $COMMAND in
        start)
            if [ "$ENV" = "prod" ]; then
                start_prod
            else
                start_dev
            fi
            ;;
        stop)
            stop $ENV
            ;;
        restart)
            stop $ENV
            if [ "$ENV" = "prod" ]; then
                start_prod
            else
                start_dev
            fi
            ;;
        logs)
            logs $ENV
            ;;
        rebuild)
            rebuild $ENV
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
