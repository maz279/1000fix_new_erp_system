# rmm-collector (CD-M05-04 companion) — the deployment runbook
# for the L5 telemetry service. It runs WHERE its agents are, not
# necessarily in compose; this Dockerfile is the container path.
FROM python:3.12-slim
WORKDIR /app
COPY src/ /app/
# stdlib only — no pip installs (the L5 discipline)
CMD ["python", "-u", "-m", "rmm_collector"]
