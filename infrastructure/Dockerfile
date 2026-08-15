FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        ca-certificates \
        ripgrep && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY workspace ./workspace

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1 \
    MEKA_WORKSPACE_ROOT=/data/workspace

CMD ["uvicorn", "workspace.servers.filesystem_http:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
