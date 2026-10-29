# AW-1 Enterprise Security Sidecar
Deterministic <0.14ms AST runtime policy gate for autonomous AI agents in Kubernetes & Docker.

## Enterprise Architecture
- **Footprint:** <25MB uncompressed Alpine container
- **Execution Overhead:** <0.14ms mean latency
- **Supply Chain:** Zero external runtime dependencies
- **Security Posture:** Non-root (UID 10001), read-only rootfs, `capabilities: drop ALL`
- **Statutory Standards:** NIST AI RMF 1.0 (Govern 1.2, Protect 2.1), SOC 2 Type II (CC6.1/CC6.6)

## Quick Start (Docker Compose)
```bash
docker compose up -d
curl http://localhost:9099/healthz
```

## Kubernetes Deployment
Deploy alongside any AI agent container:
```bash
kubectl apply -f kubernetes-sidecar.yaml
```
