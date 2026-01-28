# ===================================================================
# Nginx Dockerfile - 生产环境
# ===================================================================

FROM nginx:1.25-alpine

# 安装必要的工具
RUN apk add --no-cache \
    curl \
    tzdata

# 设置时区
ENV TZ=Asia/Shanghai

# 创建SSL证书目录
RUN mkdir -p /etc/nginx/ssl /var/www/certbot

# 复制Nginx配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 创建日志目录
RUN mkdir -p /var/log/nginx

# 暴露端口
EXPOSE 80 443

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
