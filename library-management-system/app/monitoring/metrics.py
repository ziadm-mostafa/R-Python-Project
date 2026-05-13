from datetime import datetime, timezone


_start_time = datetime.now(timezone.utc)

_total_requests = 0
_failed_requests = 0


def record_request(status_code: int) -> None:
    global _total_requests, _failed_requests

    _total_requests += 1

    if status_code >= 400:
        _failed_requests += 1


def get_stats() -> dict:
    uptime_seconds = (
        datetime.now(timezone.utc) - _start_time
    ).total_seconds()

    if _total_requests > 0:
        error_rate = round((_failed_requests / _total_requests) * 100, 2)
    else:
        error_rate = 0.0

    return {
        "uptime_seconds": uptime_seconds,
        "total_requests": _total_requests,
        "failed_requests": _failed_requests,
        "error_rate_percent": error_rate
    }