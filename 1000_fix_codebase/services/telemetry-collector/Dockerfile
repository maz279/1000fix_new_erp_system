# Telemetry Collector (CD-M02-03) - High-throughput Go Ingestion Pipeline (50k epm)
# Stage 1: Build binary
FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download || true
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o telemetry-collector main.go

# Stage 2: Minimal runtime image
FROM alpine:3.20
RUN apk --no-cache add ca-certificates tzdata
WORKDIR /root/
COPY --from=builder /app/telemetry-collector .
EXPOSE 8084
CMD ["./telemetry-collector"]
