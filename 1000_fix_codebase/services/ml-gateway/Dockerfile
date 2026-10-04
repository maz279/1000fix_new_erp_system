# ml-gateway (CD-M26-01) — the ML inference gateway.
# Runs as a lightweight service; the computation core is stdlib-only.
FROM python:3.12-slim
WORKDIR /app
COPY src/ /app/
# stdlib only — no pip installs (the L5 discipline)
CMD ["python", "-u", "-c", "from ml_gateway import *; print('ml-gateway: dispatch-scoring + demand-forecast ready')"]
