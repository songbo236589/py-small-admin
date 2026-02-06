# ===================================================================
# Dockerfile - FastAPI 应用
# ===================================================================
# 说明: 多阶段构建，优化镜像大小
#       通过 SERVICE_TYPE 环境变量启动不同服务：
#       - fastapi: FastAPI Web 服务
#       - celery-worker: Celery 异步任务 Worker
#       - celery-beat: Celery 定时任务调度器
#       - flower: Celery 监控服务
# ===================================================================

# ========================================
# Stage 1: Builder
# ========================================
FROM python:3.12-slim as builder

# 设置工作目录
WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖到用户目录
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================
# Stage 2: Runtime
# ========================================
FROM python:3.12-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    TZ=Asia/Shanghai

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 复制已安装的包
COPY --from=builder /root/.local /root/.local

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/uploads

# 暴露端口
EXPOSE 8009 5555

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8009/ || exit 1

# ========================================
# 启动命令（根据 SERVICE_TYPE 启动不同服务）
# ========================================
# 支持的服务类型:
#   - fastapi: FastAPI Web 服务
#   - celery-worker: Celery Worker (admin 队列)
#   - celery-worker-quant: Celery Worker (quant 队列)
#   - celery-beat: Celery Beat 定时任务调度器
#   - flower: Celery 监控服务
# ========================================
CMD if [ "$SERVICE_TYPE" = "celery-worker" ]; then \
    celery -A Modules.common.libs.celery.app worker --pool=threads --loglevel=info --queues=default,email_queues -n worker-admin@%h; \
    elif [ "$SERVICE_TYPE" = "celery-worker-quant" ]; then \
    celery -A Modules.common.libs.celery.app worker --pool=threads --loglevel=info --queues=quant_concept_queues,quant_industry_queues,quant_stock_queues -n worker-quant@%h; \
    elif [ "$SERVICE_TYPE" = "celery-beat" ]; then \
    celery -A Modules.common.libs.celery.app beat --loglevel=info; \
    elif [ "$SERVICE_TYPE" = "flower" ]; then \
    celery -A Modules.common.libs.celery.app flower --port=5555; \
    else \
    uvicorn Modules.main:app --host 0.0.0.0 --port 8009; \
    fi
