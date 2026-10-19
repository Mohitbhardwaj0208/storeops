# StoreOps

End-to-end DevOps platform for a retail store-fleet health API — built with open-source tools only.

**Stack:** FastAPI + PostgreSQL · Docker · GitHub · Jenkins · Trivy · Helm · k3s · ArgoCD · Prometheus/Grafana/Loki · Ansible · OpenTofu

## Phases
- [x] 1. App + Docker + docker-compose
- [ ] 2. Jenkins CI pipeline (test → build → scan → push)
- [ ] 3. Helm chart + manual deploy to k3s (+ OpenTofu for cluster resources)
- [ ] 4. ArgoCD GitOps
- [ ] 5. Prometheus / Grafana / Loki observability
- [ ] 6. Trivy in pipeline + Ansible server rebuild + OpenTofu on AWS
- [ ] 7. Docs, diagram, demo

## Run locally
```bash
docker compose up --build -d
curl http://localhost:8000/health
curl http://localhost:8000/stores
curl -X POST http://localhost:8000/stores/S001/heartbeat
curl http://localhost:8000/metrics
```

## Test
```bash
pip install -r app/requirements.txt
pytest app/tests
```
