import threading
import time

_start_monotonic = time.monotonic()
_lock = threading.Lock()

_counters = {
    "request_count": 0,
    "status_2xx": 0,
    "status_4xx": 0,
    "status_5xx": 0,
}

def inc_total():
    with _lock:
        _counters["request_count"] += 1

def inc_status(code: int):
    with _lock:
        if 200 <= code <= 299:
            _counters["status_2xx"] += 1
        elif 400 <= code <= 499:
            _counters["status_4xx"] += 1
        elif 500 <= code <= 599:
            _counters["status_5xx"] += 1

def snapshot() -> dict:
    uptime_seconds = time.monotonic() - _start_monotonic
    with _lock:
        data = dict(_counters)
    data["uptime_seconds"] = round(uptime_seconds, 3)
    return data
