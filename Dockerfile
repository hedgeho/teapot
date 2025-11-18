FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
COPY uv.lock .
COPY modules ./modules

RUN uv sync # --frozen

COPY . .

RUN mkdir -p teapot/.reticulum && cp node_config teapot/.reticulum/config

CMD ["uv", "run", "main.py"]