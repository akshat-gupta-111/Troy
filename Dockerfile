
FROM python:3.13-slim AS builder


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy


COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev


FROM python:3.13-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*


RUN groupadd --system --gid 999 appuser && \
    useradd --system --gid 999 --uid 999 --create-home appuser


ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY --from=builder /app/.venv /app/.venv

COPY . .


USER appuser


EXPOSE 8000


CMD ["sh", "-c", "uvicorn backend.src.api.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
