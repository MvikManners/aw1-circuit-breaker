# =====================================================================
# Stage 1: Build & Packaging Sandbox
# =====================================================================
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY dist/aw1_circuit_breaker-0.2.1-py3-none-any.whl .
RUN pip install --no-cache-dir --user aw1_circuit_breaker-0.2.1-py3-none-any.whl

# =====================================================================
# Stage 2: Hardened Rootless Runtime
# =====================================================================
FROM python:3.13-slim AS runtime

# Create unprivileged service user and group
RUN groupadd -g 10001 aw1group && \
    useradd -u 10001 -g aw1group -s /bin/bash -m aw1user

WORKDIR /app

# Copy installed site-packages from builder
COPY --from=builder /root/.local /home/aw1user/.local
ENV PATH=/home/aw1user/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy application source tree
COPY --chown=aw1user:aw1group core/ /app/core/
COPY --chown=aw1user:aw1group laveto_wisdom/ /app/laveto_wisdom/
COPY --chown=aw1user:aw1group gunicorn.conf.py /app/gunicorn.conf.py

# Create writable storage paths with unprivileged ownership
RUN mkdir -p /app/lvt_backend /app/logs && \
    chown -R aw1user:aw1group /app/lvt_backend /app/logs

USER aw1user:aw1group

EXPOSE 8000

STOPSIGNAL SIGTERM

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/wisdom/').read()" || exit 1

ENTRYPOINT ["gunicorn", "--config", "/app/gunicorn.conf.py", "core:create_app()"]
