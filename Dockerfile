# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
# libpq-dev 는 PostgreSQL과 연동하는 애플리케이션 개발할 때 필요
RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# numpy를 먼저 설치 (의존성 우선순위 때문..)
RUN pip install --no-cache-dir numpy
# langgraph-api 와 langserve 간 의존성 충돌 일어남. langserve만 일단 유지하고 버전 낮춤.
# RUN pip install --no-cache-dir sse-starlette==2.1.3
RUN pip install --no-cache-dir sse-starlette==1.8.2

# requirements.txt 복사 후 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 프로덕션 환경에서는 gunicorn + uvicorn 고려
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]