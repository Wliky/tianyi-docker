FROM python:3.9-slim

LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="天翼云盘签到 Docker容器化版本"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制文件
COPY requirements.txt .
COPY app/ ./app/
COPY config/ ./config/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据目录
RUN mkdir -p /app/data /app/logs

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python", "app/main.py"]
