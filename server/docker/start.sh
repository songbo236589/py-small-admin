#!/bin/bash
# ===================================================================
# Docker 服务启动脚本 - 开发环境
# ===================================================================
# 功能: 一键启动所有Docker服务
# 使用: ./start.sh [dev|prod]
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
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi

    print_info "Docker环境检查通过"
}

# 检查环境变量文件
check_env_file() {
    print_step "检查环境变量文件..."
    local env_file="$1"

    if [ ! -f "$env_file" ]; then
        print_error "环境变量文件不存在: $env_file"
        print_info "请先创建环境变量文件: cp .env.example $env_file"
        exit 1
    fi

    print_info "环境变量文件检查通过: $env_file"
}

# 拉取最新镜像
pull_images() {
    print_step "拉取最新的Docker镜像..."
    docker-compose -f "$1" pull
    print_info "镜像拉取完成"
}

# 构建镜像
build_images() {
    print_step "构建Docker镜像..."
    docker-compose -f "$1" build
    print_info "镜像构建完成"
}

# 启动服务
start_services() {
    print_step "启动Docker服务..."
    docker-compose -f "$1" up -d
    print_info "Docker服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    print_step "等待服务就绪..."
    sleep 10

    # 检查MySQL
    print_info "检查MySQL服务..."
    local mysql_ready=0
    for i in {1..30}; do
        if docker-compose -f "$1" exec -T mysql mysqladmin ping -h localhost -uroot -proot123456 &> /dev/null; then
            mysql_ready=1
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""

    if [ $mysql_ready -eq 1 ]; then
        print_info "MySQL服务已就绪"
    else
        print_warn "MySQL服务可能未完全就绪，请稍后检查"
    fi

    # 检查Redis
    print_info "检查Redis服务..."
    local redis_ready=0
    for i in {1..30}; do
        if docker-compose -f "$1" exec -T redis redis-cli -a redis123456 ping &> /dev/null; then
            redis_ready=1
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""

    if [ $redis_ready -eq 1 ]; then
        print_info "Redis服务已就绪"
    else
        print_warn "Redis服务可能未完全就绪，请稍后检查"
    fi

    # 检查RabbitMQ
    print_info "检查RabbitMQ服务..."
    local rabbitmq_ready=0
    for i in {1..30}; do
        if docker-compose -f "$1" exec -T rabbitmq rabbitmq-diagnostics -q ping &> /dev/null; then
            rabbitmq_ready=1
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""

    if [ $rabbitmq_ready -eq 1 ]; then
        print_info "RabbitMQ服务已就绪"
    else
        print_warn "RabbitMQ服务可能未完全就绪，请稍后检查"
    fi
}

# 显示服务状态
show_status() {
    print_step "显示服务状态..."
    docker-compose -f "$1" ps
}

# 显示访问信息
show_access_info() {
    echo ""
    print_info "======================================"
    print_info "服务启动完成！"
    print_info "======================================"
    echo ""
    print_info "服务访问地址："
    echo "  - FastAPI:     http://localhost:8009"
    echo "  - API文档:     http://localhost:8009/docs"
    echo "  - MySQL:       localhost:3306"
    echo "  - Redis:       localhost:6379"
    echo "  - RabbitMQ:    http://localhost:15672 (admin/admin123)"
    echo "  - Flower:      http://localhost:5555 (admin/123456)"
    echo ""
    print_info "常用命令："
    echo "  - 查看日志:   docker-compose logs -f [service_name]"
    echo "  - 停止服务:   ./stop.sh"
    echo "  - 重启服务:   docker-compose restart [service_name]"
    echo ""
}

# 主函数
main() {
    local env_type="${1:-dev}"
    local compose_file="docker-compose.yml"
    local env_file=".env"

    echo ""
    print_info "======================================"
    print_info "Py Small Admin Docker 启动脚本"
    print_info "======================================"
    print_info "环境类型: $env_type"
    echo ""

    # 切换到docker目录
    cd "$SCRIPT_DIR"

    # 根据环境类型选择配置文件
    if [ "$env_type" = "prod" ]; then
        compose_file="docker-compose.prod.yml"
        env_file=".env.production"
    fi

    # 检查Docker环境
    check_docker

    # 检查环境变量文件
    check_env_file "$env_file"

    # 拉取最新镜像
    pull_images "$compose_file"

    # 构建镜像
    build_images "$compose_file"

    # 启动服务
    start_services "$compose_file"

    # 等待服务就绪
    wait_for_services "$compose_file"

    # 显示服务状态
    show_status "$compose_file"

    # 显示访问信息
    show_access_info
}

# 执行主函数
main "$@"
