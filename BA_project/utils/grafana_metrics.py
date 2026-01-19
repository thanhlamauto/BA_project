"""
Grafana Cloud Metrics Exporter
Pushes A/B testing metrics to Grafana Cloud Prometheus

Setup:
1. Sign up at grafana.com
2. Get Prometheus remote write credentials
3. Set environment variables:
   - GRAFANA_CLOUD_URL
   - GRAFANA_CLOUD_USER
   - GRAFANA_CLOUD_API_KEY
"""
import os
import time
import threading
import requests
from requests.auth import HTTPBasicAuth

# Grafana Cloud configuration
GRAFANA_CLOUD_URL = os.getenv('GRAFANA_CLOUD_URL', '')
GRAFANA_CLOUD_USER = os.getenv('GRAFANA_CLOUD_USER', '')
GRAFANA_CLOUD_API_KEY = os.getenv('GRAFANA_CLOUD_API_KEY', '')

# Push interval (seconds)
PUSH_INTERVAL = 60

# Background thread reference
_push_thread = None
_running = False


def is_configured():
    """Check if Grafana Cloud is configured"""
    return bool(GRAFANA_CLOUD_URL and GRAFANA_CLOUD_USER and GRAFANA_CLOUD_API_KEY)


def format_prometheus_metrics(metrics):
    """
    Format metrics as Prometheus text format.

    Args:
        metrics: Dictionary with control/treatment metrics

    Returns:
        String in Prometheus exposition format
    """
    lines = []
    timestamp_ms = int(time.time() * 1000)

    # App info
    lines.append(f'# HELP ba_app_info Application information')
    lines.append(f'# TYPE ba_app_info gauge')
    lines.append(f'ba_app_info{{version="1.0.0",app="movie-recommender"}} 1')

    # Impressions
    lines.append(f'# HELP ba_ab_impressions_total Total impressions by variant')
    lines.append(f'# TYPE ba_ab_impressions_total counter')
    lines.append(f'ba_ab_impressions_total{{variant="control"}} {metrics.get("control", {}).get("impressions", 0)}')
    lines.append(f'ba_ab_impressions_total{{variant="treatment"}} {metrics.get("treatment", {}).get("impressions", 0)}')

    # Clicks
    lines.append(f'# HELP ba_ab_clicks_total Total clicks by variant')
    lines.append(f'# TYPE ba_ab_clicks_total counter')
    lines.append(f'ba_ab_clicks_total{{variant="control"}} {metrics.get("control", {}).get("clicks", 0)}')
    lines.append(f'ba_ab_clicks_total{{variant="treatment"}} {metrics.get("treatment", {}).get("clicks", 0)}')

    # Subscriptions
    lines.append(f'# HELP ba_ab_subscriptions_total Total subscriptions by variant')
    lines.append(f'# TYPE ba_ab_subscriptions_total counter')
    lines.append(f'ba_ab_subscriptions_total{{variant="control"}} {metrics.get("control", {}).get("subscriptions", 0)}')
    lines.append(f'ba_ab_subscriptions_total{{variant="treatment"}} {metrics.get("treatment", {}).get("subscriptions", 0)}')

    # Users
    lines.append(f'# HELP ba_ab_users_total Total users by variant')
    lines.append(f'# TYPE ba_ab_users_total counter')
    lines.append(f'ba_ab_users_total{{variant="control"}} {metrics.get("control", {}).get("users", 0)}')
    lines.append(f'ba_ab_users_total{{variant="treatment"}} {metrics.get("treatment", {}).get("users", 0)}')

    # CTR (as gauge, percentage)
    lines.append(f'# HELP ba_ab_ctr Click-through rate by variant')
    lines.append(f'# TYPE ba_ab_ctr gauge')
    lines.append(f'ba_ab_ctr{{variant="control"}} {metrics.get("control", {}).get("ctr", 0) * 100:.4f}')
    lines.append(f'ba_ab_ctr{{variant="treatment"}} {metrics.get("treatment", {}).get("ctr", 0) * 100:.4f}')

    # CVR (as gauge, percentage)
    lines.append(f'# HELP ba_ab_cvr Conversion rate by variant')
    lines.append(f'# TYPE ba_ab_cvr gauge')
    lines.append(f'ba_ab_cvr{{variant="control"}} {metrics.get("control", {}).get("cvr", 0) * 100:.4f}')
    lines.append(f'ba_ab_cvr{{variant="treatment"}} {metrics.get("treatment", {}).get("cvr", 0) * 100:.4f}')

    return '\n'.join(lines)


def push_metrics_to_grafana():
    """Push current metrics to Grafana Cloud"""
    if not is_configured():
        return False

    try:
        from utils.metrics import calculate_metrics
        metrics = calculate_metrics()

        # Format as Prometheus text
        prometheus_data = format_prometheus_metrics(metrics)

        # Push to Grafana Cloud
        response = requests.post(
            GRAFANA_CLOUD_URL,
            data=prometheus_data,
            auth=HTTPBasicAuth(GRAFANA_CLOUD_USER, GRAFANA_CLOUD_API_KEY),
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )

        if response.status_code in [200, 204]:
            print(f"[Grafana] Metrics pushed successfully")
            return True
        else:
            print(f"[Grafana] Push failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"[Grafana] Error pushing metrics: {e}")
        return False


def _push_loop():
    """Background loop to push metrics periodically"""
    global _running

    print(f"[Grafana] Starting metrics push loop (interval: {PUSH_INTERVAL}s)")

    while _running:
        push_metrics_to_grafana()
        time.sleep(PUSH_INTERVAL)

    print("[Grafana] Metrics push loop stopped")


def start_metrics_push():
    """Start background metrics push to Grafana Cloud"""
    global _push_thread, _running

    if not is_configured():
        print("[Grafana] Not configured, skipping metrics push")
        return False

    if _push_thread is not None and _push_thread.is_alive():
        print("[Grafana] Already running")
        return True

    _running = True
    _push_thread = threading.Thread(target=_push_loop, daemon=True, name="GrafanaMetricsPush")
    _push_thread.start()

    print("[Grafana] Metrics push started")
    return True


def stop_metrics_push():
    """Stop background metrics push"""
    global _running
    _running = False
    print("[Grafana] Stopping metrics push...")


# Auto-start if configured
if is_configured():
    start_metrics_push()
