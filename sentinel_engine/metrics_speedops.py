from prometheus_client import Histogram, Counter, CollectorRegistry

# Reuse main registry by import alias in api
request_latency = Histogram("sentinel_request_latency_seconds", "Request latency", ["path", "method"])
requests_total  = Counter("sentinel_requests_total", "HTTP requests", ["path", "method", "code"])
