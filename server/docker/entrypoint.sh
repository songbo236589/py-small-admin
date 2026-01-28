#!/bin/bash
set -e

# 颜色输出
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

# 等待服务就绪
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    print_info "等待 $service_name ($host:$port) 启动..."

    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            print_info "$service_name 已就绪!"
            return 0
        fi
        print_warn "等待 $service_name... (尝试 $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service_name 在 $max_attempts 次尝试后仍未就绪"
    exit 1
}

# 检查环境变量
check_env_vars() {
    if [ -z "$SERVICE_TYPE" ]; then
        print_error "未设置 SERVICE_TYPE 环境变量"
        print_info "可用的服务类型: fastapi, celery-worker, celery-beat, flower"
        exit 1
    fi
}

# 启动FastAPI
start_fastapi() {
    print_info "启动 FastAPI 服务..."

    # 等待依赖服务
    if [ "$WAIT_FOR_DEPENDENCIES" = "true" ]; then
        wait_for_service "${DB_CONNECTIONS__MYSQL__HOST:-mysql}" "${DB_CONNECTIONS__MYSQL__PORT:-3306}" "MySQL"
        wait_for_service "${DB_REDIS__DEFAULT__HOST:-redis}" "${DB_REDIS__DEFAULT__PORT:-6379}" "Redis"
        wait_for_service "${CELERY_BROKER_HOST:-rabbitmq}" "${CELERY_BROKER_PORT:-5672}" "RabbitMQ"
    fi

    # 执行数据库迁移(可选)
    if [ "$RUN_MIGRATIONS" = "true" ]; then
        print_info "执行数据库迁移..."
        alembic upgrade head || print_warn "数据库迁移失败,继续启动..."
    fi

    # 启动FastAPI
    exec uvicorn Modules.main:app \
        --host 0.0.0.0 \
        --port "${APP_PORT:-8009}" \
        --workers "${FASTAPI_WORKERS:-1}" \
        --log-level "${LOG_LEVEL:-INFO}"
}

# 启动Celery Worker
start_celery_worker() {
    print_info "启动 Celery Worker 服务..."

    # 等待依赖服务
    if [ "$WAIT_FOR_DEPENDENCIES" = "true" ]; then
        wait_for_service "${CELERY_BROKER_HOST:-rabbitmq}" "${CELERY_BROKER_PORT:-5672}" "RabbitMQ"
        wait_for_service "${DB_REDIS__DEFAULT__HOST:-redis}" "${DB_REDIS__DEFAULT__PORT:-6379}" "Redis"
        wait_for_service "${DB_CONNECTIONS__MYSQL__HOST:-mysql}" "${DB_CONNECTIONS__MYSQL__PORT:-3306}" "MySQL"
    fi

    # 启动Celery Worker
    exec celery -A Modules.common.libs.celery.celery_service.celery_app worker \
        --loglevel="${CELERY_WORKER_LOGLEVEL:-INFO}" \
        --concurrency="${CELERY_WORKER_CONCURRENCY:-4}" \
        --pool="${CELERY_WORKER_POOL:-threads}" \
        --max-tasks-per-child="${CELERY_WORKER_MAX_TASKS_PER_CHILD:-1000}" \
        --prefetch-multiplier="${CELERY_WORKER_PREFETCH_MULTIPLIER:-4}" \
        --queues="${CELERY_WORKER_QUEUES:-default,email_queues,quant_concept_queues,quant_industry_queues,quant_stock_queues}"
}

# 启动Celery Beat
start_celery_beat() {
    print_info "启动 Celery Beat 服务..."

    # 等待依赖服务
    if [ "$WAIT_FOR_DEPENDENCIES" = "true" ]; then
        wait_for_service "${CELERY_BROKER_HOST:-rabbitmq}" "${CELERY_BROKER_PORT:-5672}" "RabbitMQ"
    fi

    # 启动Celery Beat
    exec celery -A Modules.common.libs.celery.celery_service.celery_app beat \
        --loglevel="${CELERY_BEAT_LOGLEVEL:-INFO}" \
        --pidfile=/tmp/celerybeat.pid \
        --scheduler="${CELERY_BEAT_SCHEDULER:-redbeat.RedBeatScheduler}"
}

# 启动Flower
start_flower() {
    print_info "启动 Flower 监控服务..."

    # 等待依赖服务
    if [ "$WAIT_FOR_DEPENDENCIES" = "true" ]; then
        wait_for_service "${CELERY_BROKER_HOST:-rabbitmq}" "${CELERY_BROKER_PORT:-5672}" "RabbitMQ"
    fi

    # 启动Flower
    exec celery -A Modules.common.libs.celery.celery_service.celery_app flower \
        --port="${CELERY_FLOWER_PORT:-5555}" \
        --host=0.0.0.0 \
        --basic_auth="${CELERY_FLOWER_BASIC_AUTH:-admin:123456}" \
        --broker_api="${CELERY_FLOWER_BROKER_API:-http://rabbitmq:15672/api/}"
}

# 主函数
main() {
    print_info "======================================"
    print_info "Py Small Admin Docker 容器启动"
    print_info "======================================"
    print_info "服务类型: ${SERVICE_TYPE}"
    print_info "运行环境: ${APP_ENV:-development}"
    print_info "======================================"

    check_env_vars

    case "$SERVICE_TYPE" in
        fastapi)
            start_fastapi
            ;;
        celery-worker)
            start_celery_worker
            ;;
        celery-beat)
            start_celery_beat
            ;;
        flower)
            start_flower
            ;;
        *)
            print_error "未知的服务类型: $SERVICE_TYPE"
            print_info "可用的服务类型: fastapi, celery-worker, celery-beat, flower"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
