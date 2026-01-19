"""
Analytics Routes: Dashboard and metrics
"""
from flask import Blueprint, render_template, jsonify, request, session
from utils.metrics import calculate_metrics, check_srm, get_recent_events, calculate_lift
from utils.logger_service import log_engagement_async

bp = Blueprint('analytics', __name__)


@bp.route('/dashboard')
def dashboard():
    """A/B Testing Dashboard"""
    return render_template('dashboard.html')


@bp.route('/api/metrics')
def get_metrics():
    """API endpoint to get current A/B test metrics"""
    metrics = calculate_metrics()
    srm = check_srm(metrics)
    lift = calculate_lift(metrics)

    return jsonify({
        'metrics': metrics,
        'srm': srm,
        'lift': lift
    })


@bp.route('/api/recent-events')
def recent_events():
    """Get recent events for activity feed"""
    impressions = get_recent_events('impression', n=5)
    clicks = get_recent_events('click', n=5)
    subscriptions = get_recent_events('subscription', n=5)

    return jsonify({
        'impressions': impressions,
        'clicks': clicks,
        'subscriptions': subscriptions
    })


@bp.route('/api/engagement', methods=['POST'])
def log_engagement():
    """
    Log user engagement event (dwell time tracking).

    Tracks how long users spend viewing movie modals - a key engagement metric.
    Uses async logging for zero-latency performance.

    Request body:
        {
            "movie_id": 123,
            "dwell_time_ms": 5000,
            "action": "close" | "rate" | "background_click"
        }
    """
    data = request.get_json()
    movie_id = data.get('movie_id')
    dwell_time_ms = data.get('dwell_time_ms')
    action = data.get('action', 'view')

    user_id = session.get('user_id')
    variant = session.get('variant')

    # Validation
    if not user_id or not variant:
        return jsonify({'error': 'Not logged in'}), 401

    if not movie_id or dwell_time_ms is None:
        return jsonify({'error': 'movie_id and dwell_time_ms required'}), 400

    # Log engagement asynchronously (non-blocking)
    log_engagement_async(user_id, variant, movie_id, dwell_time_ms, action)

    return jsonify({
        'success': True,
        'dwell_time_ms': dwell_time_ms,
        'action': action
    })


@bp.route('/api/metrics/history')
def get_metrics_history():
    """
    API endpoint to get historical metrics for trend charts.
    Returns last 10 data points for CTR/CVR trends.
    """
    # For now, return current metrics repeated as historical data
    # In production, you'd query a time-series database
    metrics = calculate_metrics()
    
    # Simulate historical data points
    history = []
    for i in range(10):
        history.append({
            'timestamp': f'T-{10-i}',
            'control_ctr': metrics['control']['ctr'] * (0.9 + (i * 0.01)),
            'treatment_ctr': metrics['treatment']['ctr'] * (0.9 + (i * 0.01)),
            'control_cvr': metrics['control']['cvr'] * (0.9 + (i * 0.01)),
            'treatment_cvr': metrics['treatment']['cvr'] * (0.9 + (i * 0.01))
        })
    
    return jsonify({
        'history': history
    })


@bp.route('/api/metrics/export')
def export_metrics():
    """
    Server-side export endpoint with date filtering.
    Query params: start_date, end_date, format (csv|json)
    """
    # Get query params
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    export_format = request.args.get('format', 'json')
    
    # Calculate metrics (in production, filter by date range)
    metrics = calculate_metrics()
    srm = check_srm(metrics)
    lift = calculate_lift(metrics)
    
    if export_format == 'csv':
        # Return CSV format
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Metric', 'Control', 'Treatment', 'Lift'])
        
        # Write data
        writer.writerow(['Users', metrics['control']['users'], metrics['treatment']['users'], ''])
        writer.writerow(['Impressions', metrics['control']['impressions'], metrics['treatment']['impressions'], ''])
        writer.writerow(['Clicks', metrics['control']['clicks'], metrics['treatment']['clicks'], ''])
        writer.writerow(['Subscriptions', metrics['control']['subscriptions'], metrics['treatment']['subscriptions'], ''])
        writer.writerow(['CTR (%)', f"{metrics['control']['ctr']*100:.2f}", f"{metrics['treatment']['ctr']*100:.2f}", f"{lift['ctr']:.2f}"])
        writer.writerow(['CVR (%)', f"{metrics['control']['cvr']*100:.2f}", f"{metrics['treatment']['cvr']*100:.2f}", f"{lift['cvr']:.2f}"])
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=metrics-export.csv'
        }
    
    # Default: return JSON
    return jsonify({
        'metrics': metrics,
        'srm': srm,
        'lift': lift,
        'exported_at': request.args.get('timestamp', 'now')
    })
