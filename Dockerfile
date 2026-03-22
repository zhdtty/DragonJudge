# DragonJudge - A股情绪龙头助手
# 使用Python 3.11 + Poetry构建

# 构建阶段
FROM python:3.11-slim as builder

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry==1.7.1

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 配置Poetry（不创建虚拟环境）
RUN poetry config virtualenvs.create false

# 安装依赖
RUN poetry install --no-dev --no-interaction --no-ansi

# 运行阶段
FROM python:3.11-slim as runtime

# 设置工作目录
WORKDIR /app

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY src/ ./src/
COPY docs/ ./docs/
COPY tests/ ./tests/
COPY dragonjudge.py ./
COPY README.md ./

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 创建日志目录
RUN mkdir -p /app/logs

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 默认命令
CMD ["python", "dragonjudge.py", "--help"]
