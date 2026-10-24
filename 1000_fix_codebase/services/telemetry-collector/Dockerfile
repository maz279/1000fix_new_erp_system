# Telemetry Collector (CD-M02-03) - High-throughput Go Ingestion Pipeline (50k epm)
# Stage 1: Build binary
FROM golang:1.24-alpine@sha256:8bee1901f1e530bfb4a7850aa7a479d17ae3a18beb6e09064ed54cfd245b7191 AS builder
WORKDIR /app
COPY go.mod go.sum* ./
# Fail loudly: without the pgx module the real TimescaleDB flush cannot build.
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o telemetry-collector main.go

# Stage 2: Minimal runtime image
FROM alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc
RUN apk --no-cache add ca-certificates tzdata \
 && addgroup -S -g 10001 telemetry \
 && adduser -S -D -H -u 10001 -G telemetry telemetry
WORKDIR /srv/telemetry
COPY --from=builder /app/telemetry-collector /usr/local/bin/telemetry-collector
# DE-11: refuse to start unless FIX_ENV is local, staging or prod/production.
# Outside local, DATABASE_URL MUST be set: main.go otherwise falls back to the
# development DSN (127.0.0.1:5433/fix_dev), which must never be the silent
# default of a staging/production container.
RUN printf '#!/bin/sh\ncase "$FIX_ENV" in\n  local) ;;\n  staging|prod|production) [ -n "$DATABASE_URL" ] || { echo "refusing to start: DATABASE_URL is required when FIX_ENV=$FIX_ENV"; exit 42; } ;;\n  *) echo "refusing to start: FIX_ENV=$FIX_ENV (DE-11)"; exit 42;;\nesac\nexec /usr/local/bin/telemetry-collector "$@"\n' > /entrypoint.sh \
 && chmod +x /entrypoint.sh
USER 10001
EXPOSE 8084
ENTRYPOINT ["/entrypoint.sh"]
