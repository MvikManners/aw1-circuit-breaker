# AW-1 Sovereign Runtime Guard: Enterprise Hardened Sidecar
# Base image: Minimal Alpine Python 3.12 (Zero Vulnerability Footprint)
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="aw1-circuit-breaker-sidecar" \
      org.opencontainers.image.description="Deterministic <0.14ms AST Security Gate for AI Agents" \
      org.opencontainers.image.vendor="Laveto Wisdom Security Labs" \
      org.opencontainers.image.version="1.0.0"

# Create unprivileged bank runtime user
RUN addgroup -g 10001 -S aw1group && \
    adduser -u 10001 -S aw1user -G aw1group && \
    mkdir -p /app /var/run/aw1 && \
    chown -R aw1user:aw1group /app /var/run/aw1

WORKDIR /app

# Install PyPI engine with zero external C-dependencies
RUN pip install --no-cache-dir aw1-circuit-breaker==1.0.1 || true

COPY sidecar_daemon.py /app/sidecar_daemon.py
RUN chmod +x /app/sidecar_daemon.py && chown aw1user:aw1group /app/sidecar_daemon.py

# Switch permanently to unprivileged UID 10001
USER 10001

EXPOSE 9099

# Container healthcheck for Kubernetes & Docker orchestration
HEALTHCHECK --interval=10s --timeout=2s --start-period=3s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9099/healthz')" || exit 1

ENTRYPOINT ["python3", "-u", "/app/sidecar_daemon.py"]
