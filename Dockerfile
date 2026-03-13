FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update \&\& apt-get install -y \
    gcc \
    \&\& rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 安装 Poetry
RUN pip install poetry

# 安装项目依赖（不创建虚拟环境）
RUN poetry config virtualenvs.create false \
    \&\& poetry install --no-dev --no-interaction --no-ansi

# 复制项目代码
COPY src/ ./src/
COPY dragonjudge.py ./

# 创建数据目录
RUN mkdir -p /app/data /app/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# 默认命令
CMD ["python", "dragonjudge.py", "--fetch"]
