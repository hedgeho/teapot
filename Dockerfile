FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
COPY uv.lock .
COPY modules ./modules

RUN apt-get update && \
    apt-get install -y libpcap-dev procps && \
    rm -rf /var/lib/apt/lists/*

RUN uv sync # --frozen

COPY . .

RUN mkdir -p teapot/.reticulum && cp node_config teapot/.reticulum/config

## Fix ownership for non-root user
#RUN touch /app/teapot/icmp/icmp_tunnel.log
#RUN chown -R 1000:1000 /app

CMD ["uv", "run", "main.py"]