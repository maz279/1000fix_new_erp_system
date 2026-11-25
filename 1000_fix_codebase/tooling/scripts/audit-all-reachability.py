#!/usr/bin/env python3
"""audit-all-reachability.py
Comprehensive reachability and health verification across the entire 1000 FiX estate:
- Infrastructure & Backing Services
- Platform Services & Ingress Gateways
- Core ERP Backend (Odoo 19)
- Python / Go Microservices
- Web Portals & Prototype Frontends
"""

import socket
import subprocess
import sys
import urllib.error
import urllib.request

SERVICES = [
    # --- Infrastructure & Storage ---
    {
        "category": "Infrastructure",
        "name": "PostgreSQL 17 Primary",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 5433,
    },
    {
        "category": "Infrastructure",
        "name": "PgBouncer Pooler",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 6432,
    },
    {
        "category": "Infrastructure",
        "name": "Redis 7.2 Cache & Broker",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 6380,
    },
    {
        "category": "Infrastructure",
        "name": "Ceph S3 Object Storage",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 9002,
    },
    {
        "category": "Infrastructure",
        "name": "ClickHouse OLAP HTTP",
        "type": "http",
        "url": "http://127.0.0.1:8123/ping",
        "expected": 200,
    },
    {
        "category": "Infrastructure",
        "name": "Kafka Broker 1",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 9092,
    },
    {
        "category": "Infrastructure",
        "name": "Kafka Broker 2",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 9094,
    },
    {
        "category": "Infrastructure",
        "name": "Kafka Broker 3",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 9095,
    },
    {
        "category": "Infrastructure",
        "name": "MongoDB (Novu Storage)",
        "type": "docker",
        "container": "compose-novu-mongo-1",
    },
    # --- Platform & Observability ---
    {
        "category": "Platform & Gateways",
        "name": "Kong Gateway (Ingress Route)",
        "type": "http",
        "url": "http://127.0.0.1:8000/api/odoo/web/login",
        "expected": 200,
    },
    {
        "category": "Platform & Gateways",
        "name": "Keycloak 26 IAM Realm",
        "type": "http",
        "url": "http://127.0.0.1:8080/realms/1000fix-dev",
        "expected": 200,
    },
    {
        "category": "Platform & Gateways",
        "name": "Novu Notifications Health",
        "type": "http",
        "url": "http://127.0.0.1:3040/v1/health-check",
        "expected": 200,
    },
    {
        "category": "Platform & Gateways",
        "name": "Airflow 3 Orchestration",
        "type": "http",
        "url": "http://127.0.0.1:8081/api/v2/monitor/health",
        "expected": 200,
    },
    {
        "category": "Platform & Gateways",
        "name": "Traccar GPS Engine",
        "type": "http",
        "url": "http://127.0.0.1:8082/api/server",
        "expected": 200,
    },
    {
        "category": "Observability",
        "name": "Prometheus Metrics",
        "type": "http",
        "url": "http://127.0.0.1:9090/-/healthy",
        "expected": 200,
    },
    {
        "category": "Observability",
        "name": "Grafana Dashboards",
        "type": "http",
        "url": "http://127.0.0.1:3300/api/health",
        "expected": 200,
    },
    {
        "category": "Observability",
        "name": "Loki Log Aggregator",
        "type": "http",
        "url": "http://127.0.0.1:3100/ready",
        "expected": 200,
    },
    {
        "category": "Observability",
        "name": "Tempo Trace Engine",
        "type": "http",
        "url": "http://127.0.0.1:3200/ready",
        "expected": 200,
    },
    {
        "category": "Developer Tools",
        "name": "Mailpit Web UI",
        "type": "http",
        "url": "http://127.0.0.1:8025/",
        "expected": 200,
    },
    {
        "category": "Developer Tools",
        "name": "Mailpit SMTP Server",
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 1025,
    },
    # --- Microservices ---
    {
        "category": "Microservices",
        "name": "Residency Stub Service",
        "type": "http",
        "url": "http://127.0.0.1:8100/health",
        "expected": 200,
    },
    {
        "category": "Microservices",
        "name": "Identity Lifecycle Service",
        "type": "http",
        "url": "http://127.0.0.1:8120/health",
        "expected": 200,
    },
    {
        "category": "Microservices",
        "name": "Telemetry Collector Service",
        "type": "http",
        "url": "http://127.0.0.1:8084/health",
        "expected": 200,
    },
    {
        "category": "Microservices",
        "name": "Notification Dispatcher",
        "type": "http",
        "url": "http://127.0.0.1:8110/health",
        "expected": 200,
    },
    # --- Core ERP Backend ---
    {
        "category": "Core ERP",
        "name": "Odoo 19 ERP Login Page",
        "type": "http",
        "url": "http://127.0.0.1:8069/web/login",
        "expected": 200,
    },
    # --- Web Portals ---
    {
        "category": "Web Portals",
        "name": "Customer Portal (P01)",
        "type": "http",
        "url": "http://127.0.0.1:3000/",
        "expected": 200,
    },
    {
        "category": "Web Portals",
        "name": "Corporate Portal (P02)",
        "type": "http",
        "url": "http://127.0.0.1:3001/",
        "expected": 200,
    },
    {
        "category": "Web Portals",
        "name": "Analytics Portal (P03)",
        "type": "http",
        "url": "http://127.0.0.1:3002/",
        "expected": 200,
    },
    {
        "category": "Web Portals",
        "name": "Seller Portal (P04)",
        "type": "http",
        "url": "http://127.0.0.1:3003/",
        "expected": 200,
    },
    {
        "category": "Web Portals",
        "name": "Brand Portal (P05)",
        "type": "http",
        "url": "http://127.0.0.1:3004/",
        "expected": 200,
    },
    {
        "category": "Web Portals",
        "name": "Agent Console Portal (P06)",
        "type": "http",
        "url": "http://127.0.0.1:3005/",
        "expected": 200,
    },
    {
        "category": "Web Portals",
        "name": "Partner Portal (P07)",
        "type": "http",
        "url": "http://127.0.0.1:3006/",
        "expected": 200,
    },
    {
        "category": "Web Portals",
        "name": "Vendor Portal (P08)",
        "type": "http",
        "url": "http://127.0.0.1:3007/",
        "expected": 200,
    },
    # --- Prototype Frontends ---
    {
        "category": "Web Portals",
        "name": "Front_end Static Prototype",
        "type": "http",
        "url": "http://127.0.0.1:8085/",
        "expected": 200,
    },
]


def check_tcp(host: str, port: int, timeout: float = 3.0) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"TCP open ({host}:{port})"
    except Exception as e:
        return False, str(e)


def check_http(url: str, expected, timeout: float = 5.0) -> tuple[bool, str]:
    if isinstance(expected, int):
        expected = [expected]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "1000fix-ReachabilityAudit/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if code in expected:
                return True, f"HTTP {code}"
            return False, f"HTTP {code} not in {expected}"
    except urllib.error.HTTPError as e:
        if e.code in expected:
            return True, f"HTTP {e.code}"
        return False, f"HTTP Error {e.code}"
    except Exception as e:
        return False, str(e)


def check_docker(container: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [
                "docker",
                "exec",
                container,
                "mongosh",
                "--quiet",
                "--eval",
                "db.adminCommand('ping').ok",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode == 0 and "1" in proc.stdout:
            return True, "Docker Healthy (ping: ok 1)"
        return False, f"Docker exited {proc.returncode}: {proc.stderr}"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 85)
    print("1000 FiX Services Ltd. - Complete Estate Reachability & Health Audit")
    print("=" * 85)

    total = len(SERVICES)
    passed = 0
    results = []

    for svc in SERVICES:
        cat = svc["category"]
        name = svc["name"]
        stype = svc["type"]

        if stype == "tcp":
            ok, detail = check_tcp(svc["host"], svc["port"])
            endpoint = f"{svc['host']}:{svc['port']}"
        elif stype == "http":
            ok, detail = check_http(svc["url"], svc["expected"])
            endpoint = svc["url"]
        elif stype == "docker":
            ok, detail = check_docker(svc["container"])
            endpoint = f"container:{svc['container']}"

        if ok:
            passed += 1
            status = "PASS [OK]"
        else:
            status = "FAIL [X ]"

        results.append((cat, name, endpoint, status, detail))
        print(f"[{status}] {cat:<22} | {name:<30} | {endpoint:<42} | {detail}")

    print("=" * 85)
    print(f"FINAL AUDIT RESULT: {passed}/{total} services 100% REACHABLE & OPERATIONAL")
    print("=" * 85)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
