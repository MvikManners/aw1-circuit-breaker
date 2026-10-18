# =====================================================================
# AW-1 & Laveto Wisdom Enterprise Production Gunicorn Configuration
# =====================================================================
import os
import multiprocessing

# Network Binding
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = int(os.getenv("GUNICORN_BACKLOG", "2048"))

# Concurrency Architecture: (2 x CPUs) + 1 workers, 4 threads per worker
workers = int(os.getenv("GUNICORN_WORKERS", (multiprocessing.cpu_count() * 2) + 1))
worker_class = "gthread"
threads = int(os.getenv("GUNICORN_THREADS", "4"))
worker_connections = 1000

# Memory Leak Mitigation & Worker Recycling
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))

# Timeouts & Graceful Drain
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "15"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

# Security & Concurrency Safety
# preload_app MUST be False when using SQLite WAL mode to avoid inherited file descriptors
preload_app = False

# Logging Configuration
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "/home/LavetoLab/logs/gunicorn_access.log")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "/home/LavetoLab/logs/gunicorn_error.log")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss'

# Process Identification
proc_name = "aw1-circuit-breaker-engine"

def on_starting(server):
    server.log.info("🚀 AW-1 Circuit Breaker WSGI Gateway Initializing...")

def worker_int(worker):
    worker.log.warning(f"⚠️ Worker {worker.pid} received INT/QUIT signal. Draining in-flight audits...")

def worker_abort(worker):
    worker.log.error(f"🛑 Worker {worker.pid} received ABORT signal.")
