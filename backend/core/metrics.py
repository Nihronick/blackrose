import time
import math
import collections

class MetricsRegistry:
    def __init__(self, max_samples: int = 1000):
        self.start_time = time.time()
        self.request_counts = collections.defaultdict(int)
        self.status_counts = collections.defaultdict(int)
        self.endpoint_counts = collections.defaultdict(int)
        self.latencies = collections.deque(maxlen=max_samples)
        self.total_requests = 0
        self.total_errors = 0

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        self.total_requests += 1
        self.request_counts[method] += 1
        self.status_counts[status_code] += 1
        
        # Aggregate path template to avoid cardinality explosion
        clean_path = path.split("?")[0]
        if clean_path.startswith("/api/guide/"):
            clean_path = "/api/guide/{key}"
        elif clean_path.startswith("/api/category/"):
            clean_path = "/api/category/{key}"
        elif clean_path.startswith("/api/media/"):
            clean_path = "/api/media/{hash}"
            
        self.endpoint_counts[clean_path] += 1
        self.latencies.append(duration_ms)

        if status_code >= 500:
            self.total_errors += 1

    def get_percentile(self, p: float) -> float:
        if not self.latencies:
            return 0.0
        sorted_lat = sorted(self.latencies)
        k = (len(sorted_lat) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return round(sorted_lat[int(k)], 2)
        d0 = sorted_lat[int(f)] * (c - k)
        d1 = sorted_lat[int(c)] * (k - f)
        return round(d0 + d1, 2)

    def get_summary(self) -> dict:
        uptime_sec = time.time() - self.start_time
        rps = round(self.total_requests / max(uptime_sec, 1.0), 2)
        error_rate_pct = round((self.total_errors / max(self.total_requests, 1)) * 100, 2)

        return {
            "uptime_seconds": round(uptime_sec, 1),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate_pct": error_rate_pct,
            "requests_per_second": rps,
            "latency_ms": {
                "p50": self.get_percentile(50),
                "p90": self.get_percentile(90),
                "p95": self.get_percentile(95),
                "p99": self.get_percentile(99),
                "samples_tracked": len(self.latencies),
            },
            "status_distribution": dict(self.status_counts),
            "methods_distribution": dict(self.request_counts),
            "top_endpoints": dict(sorted(self.endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        }

    def to_prometheus(self) -> str:
        summary = self.get_summary()
        lines = [
            "# HELP http_requests_total Total HTTP Requests",
            "# TYPE http_requests_total counter",
            f"http_requests_total {summary['total_requests']}",
            "# HELP http_errors_total Total 5xx HTTP Errors",
            "# TYPE http_errors_total counter",
            f"http_errors_total {summary['total_errors']}",
            "# HELP http_latency_p50_ms 50th Percentile Latency",
            "# TYPE http_latency_p50_ms gauge",
            f"http_latency_p50_ms {summary['latency_ms']['p50']}",
            "# HELP http_latency_p90_ms 90th Percentile Latency",
            "# TYPE http_latency_p90_ms gauge",
            f"http_latency_p90_ms {summary['latency_ms']['p90']}",
            "# HELP http_latency_p99_ms 99th Percentile Latency",
            "# TYPE http_latency_p99_ms gauge",
            f"http_latency_p99_ms {summary['latency_ms']['p99']}",
            "# HELP app_uptime_seconds Application Uptime in Seconds",
            "# TYPE app_uptime_seconds counter",
            f"app_uptime_seconds {summary['uptime_seconds']}",
        ]
        return "\n".join(lines) + "\n"

    def get_slo_report(self) -> dict:
        """
        Service Level Objectives report.
        SLO Targets:
          - Availability: 99.5%
          - Latency P99: < 800ms
        """
        total = max(self.total_requests, 1)
        availability_pct = round(((total - self.total_errors) / total) * 100, 3)
        p99 = self.get_percentile(99)
        
        # SLO definitions
        slo_availability = 99.5
        slo_latency_p99_ms = 800.0
        
        # Error budget: how many errors we can still afford
        error_budget_total = (1 - slo_availability / 100) * total
        error_budget_remaining = round(error_budget_total - self.total_errors, 1)
        error_budget_pct = round((error_budget_remaining / max(error_budget_total, 0.01)) * 100, 1)

        return {
            "sli": {
                "availability_pct": availability_pct,
                "latency_p99_ms": p99,
            },
            "slo": {
                "availability_target_pct": slo_availability,
                "latency_p99_target_ms": slo_latency_p99_ms,
            },
            "status": {
                "availability_met": availability_pct >= slo_availability,
                "latency_met": p99 <= slo_latency_p99_ms,
                "overall": availability_pct >= slo_availability and p99 <= slo_latency_p99_ms,
            },
            "error_budget": {
                "total_budget": round(error_budget_total, 1),
                "consumed": self.total_errors,
                "remaining": max(error_budget_remaining, 0),
                "remaining_pct": max(error_budget_pct, 0),
                "exhausted": error_budget_remaining <= 0,
            },
            "total_requests": total,
        }

metrics_registry = MetricsRegistry()
