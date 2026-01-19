"""
BA Project: Rung Dong - Recommender System with A/B Testing
Main Flask Application (Enhanced with Performance Monitoring & Async Logging)

MLOps Ready: Supports MongoDB, BentoCloud, Grafana Cloud
"""
from flask import Flask, render_template, session, request, jsonify
import os
from datetime import datetime
import requests

# Import routes
from routes import main, analytics

# Import performance middleware
from utils.middleware import setup_middleware

# Import configuration
from config import get_config

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.secret_key = config.SECRET_KEY
app.config.from_object(config)

# Register blueprints
app.register_blueprint(main.bp)
app.register_blueprint(analytics.bp)

# Setup performance monitoring middleware
# Tracks API latency and adds X-Response-Time-Ms header
setup_middleware(app)

# Create necessary directories
os.makedirs('data/logs', exist_ok=True)
os.makedirs('static/images/posters', exist_ok=True)

@app.before_request
def setup_session():
    """Initialize session variables"""
    if 'user_id' not in session:
        session['user_id'] = None
    if 'variant' not in session:
        session['variant'] = None

@app.context_processor
def inject_now():
    """Inject current datetime into all templates"""
    return {'now': datetime.now()}


# ============================================================
# Health Check Endpoints (Required for Production Deployment)
# ============================================================

@app.route('/health')
def health():
    """
    Basic health check for load balancers (Render, etc.)
    Returns 200 if app is running.
    """
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'environment': os.getenv('ENVIRONMENT', 'development')
    }), 200


@app.route('/ready')
def ready():
    """
    Readiness check - verifies all dependencies are available.
    Used by orchestrators to know when app can receive traffic.
    """
    checks = {
        'app': True,
        'mongodb': False,
        'bentoml': False
    }
    all_ready = True

    # Check MongoDB connection (if enabled)
    if os.getenv('USE_MONGODB_LOGGING', 'false').lower() == 'true':
        try:
            from utils.logger_service import get_db
            db = get_db()
            if db is not None:
                db.command('ping')
                checks['mongodb'] = True
            else:
                all_ready = False
        except Exception as e:
            checks['mongodb'] = False
            checks['mongodb_error'] = str(e)
            all_ready = False
    else:
        checks['mongodb'] = 'skipped (CSV mode)'

    # Check BentoML endpoint (optional)
    bentoml_endpoint = os.getenv('BENTOML_ENDPOINT', '')
    if bentoml_endpoint and bentoml_endpoint != 'http://localhost:3000':
        try:
            response = requests.get(f"{bentoml_endpoint}/healthz", timeout=2)
            checks['bentoml'] = response.status_code == 200
            if not checks['bentoml']:
                all_ready = False
        except Exception as e:
            checks['bentoml'] = False
            checks['bentoml_error'] = str(e)
            # BentoML is optional, don't fail readiness
    else:
        checks['bentoml'] = 'skipped (local mode)'

    status_code = 200 if all_ready else 503
    return jsonify({
        'status': 'ready' if all_ready else 'not ready',
        'checks': checks
    }), status_code


@app.route('/metrics')
def metrics():
    """
    Prometheus-compatible metrics endpoint.
    Returns key application metrics for monitoring.
    """
    from utils.logger_service import get_queue_size
    from utils.metrics import calculate_metrics

    try:
        ab_metrics = calculate_metrics()
    except Exception:
        ab_metrics = {'control': {}, 'treatment': {}}

    # Format as Prometheus metrics
    output = []
    output.append('# HELP app_info Application information')
    output.append('# TYPE app_info gauge')
    output.append(f'app_info{{version="1.0.0",environment="{os.getenv("ENVIRONMENT", "development")}"}} 1')

    output.append('# HELP logger_queue_size Current size of the async logging queue')
    output.append('# TYPE logger_queue_size gauge')
    output.append(f'logger_queue_size {get_queue_size()}')

    output.append('# HELP ab_test_impressions_total Total impressions by variant')
    output.append('# TYPE ab_test_impressions_total counter')
    output.append(f'ab_test_impressions_total{{variant="control"}} {ab_metrics.get("control", {}).get("impressions", 0)}')
    output.append(f'ab_test_impressions_total{{variant="treatment"}} {ab_metrics.get("treatment", {}).get("impressions", 0)}')

    output.append('# HELP ab_test_clicks_total Total clicks by variant')
    output.append('# TYPE ab_test_clicks_total counter')
    output.append(f'ab_test_clicks_total{{variant="control"}} {ab_metrics.get("control", {}).get("clicks", 0)}')
    output.append(f'ab_test_clicks_total{{variant="treatment"}} {ab_metrics.get("treatment", {}).get("clicks", 0)}')

    output.append('# HELP ab_test_subscriptions_total Total subscriptions by variant')
    output.append('# TYPE ab_test_subscriptions_total counter')
    output.append(f'ab_test_subscriptions_total{{variant="control"}} {ab_metrics.get("control", {}).get("subscriptions", 0)}')
    output.append(f'ab_test_subscriptions_total{{variant="treatment"}} {ab_metrics.get("treatment", {}).get("subscriptions", 0)}')

    return '\n'.join(output), 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == '__main__':
    print("=" * 60)
    print("  Rung Động - Recommender System with A/B Testing")
    print("  (Enhanced: Async Logging + Performance Monitoring)")
    print("=" * 60)
    print("\n  📍 Running on: http://localhost:5000")
    print("  📊 Dashboard: http://localhost:5000/dashboard")
    print("\n  ⚡ Features:")
    print("    - Zero-latency async logging (<5ms)")
    print("    - API performance tracking")
    print("    - Consistent hashing (sticky sessions)")
    print("\n" + "=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
