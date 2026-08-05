# CI 无头执行镜像
FROM python:3.11-slim

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN playwright install chromium --with-deps

# 复制项目代码
COPY . .

# 默认运行（可通过 -k 过滤）
ENV HEADLESS=true
CMD ["pytest", "-v", "--alluredir=reports/allure-results"]
