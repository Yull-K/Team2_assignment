FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

WORKDIR /app

# 라이브러리 먼저 설치 (코드가 바뀌어도 이 단계는 재사용됨)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# 코드 복사
COPY . .
RUN uv sync --frozen

ENV ENV=prod
EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "wapang.main:app", "--host", "0.0.0.0", "--port", "8000"]
