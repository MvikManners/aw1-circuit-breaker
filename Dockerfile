FROM python:3.11-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app
ENTRYPOINT ["python3", "-m", "laveto_wisdom.mcp_server"]
