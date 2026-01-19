"""
Metrics Calculation for A/B Testing
Supports both CSV (development) and MongoDB (production) backends.

- CTR (Click-Through Rate)
- CVR (Conversion Rate)
- Sample sizes
- SRM (Sample Ratio Mismatch) check
"""
import os
import pandas as pd
from pathlib import Path

LOG_DIR = Path('data/logs')

# Try to import pymongo (optional dependency)
try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

# MongoDB connection (lazy initialization)
_mongo_client = None
_db = None


def get_db():
    """Get MongoDB database connection (lazy initialization)"""
    global _mongo_client, _db

    if not PYMONGO_AVAILABLE:
        return None

    if _db is None:
        try:
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ba_project')
            _mongo_client = MongoClient(
                mongo_uri,
                maxPoolSize=10,
                serverSelectionTimeoutMS=5000
            )
            _mongo_client.admin.command('ping')
            _db = _mongo_client.get_database()
        except Exception as e:
            print(f"[Metrics] MongoDB connection failed: {e}")
            _db = None

    return _db


def use_mongodb():
    """Check if MongoDB should be used for querying"""
    use_mongo = os.getenv('USE_MONGODB_LOGGING', 'false').lower() == 'true'
    return use_mongo and PYMONGO_AVAILABLE and get_db() is not None


def read_log_file(event_type):
    """Read log file and return as DataFrame (CSV backend)"""
    log_file = LOG_DIR / f'{event_type}s.csv'

    if not log_file.exists():
        return pd.DataFrame()

    return pd.read_csv(log_file)


def calculate_metrics():
    """
    Calculate A/B test metrics from log storage.
    Uses MongoDB in production, CSV in development.

    Returns:
        Dictionary with metrics by variant
    """
    if use_mongodb():
        return _calculate_metrics_mongodb()
    else:
        return _calculate_metrics_csv()


def _calculate_metrics_mongodb():
    """Calculate metrics from MongoDB"""
    db = get_db()

    metrics = {
        'control': {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'subscriptions': 0,
            'ctr': 0.0,
            'cvr': 0.0,
            'users': 0
        },
        'treatment': {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'subscriptions': 0,
            'ctr': 0.0,
            'cvr': 0.0,
            'users': 0
        }
    }

    for variant in ['control', 'treatment']:
        # Count impressions
        metrics[variant]['impressions'] = db.impressions.count_documents({'variant': variant})
        metrics[variant]['users'] = len(db.impressions.distinct('user_id', {'variant': variant}))

        # Count clicks
        metrics[variant]['clicks'] = db.clicks.count_documents({'variant': variant})

        # Count conversions
        metrics[variant]['conversions'] = db.conversions.count_documents({'variant': variant})

        # Count subscriptions
        metrics[variant]['subscriptions'] = db.subscriptions.count_documents({'variant': variant})

        # Calculate rates
        if metrics[variant]['impressions'] > 0:
            metrics[variant]['ctr'] = metrics[variant]['clicks'] / metrics[variant]['impressions']
        if metrics[variant]['clicks'] > 0:
            metrics[variant]['cvr'] = metrics[variant]['subscriptions'] / metrics[variant]['clicks']

    return metrics


def _calculate_metrics_csv():
    """Calculate metrics from CSV files"""
    impressions = read_log_file('impression')
    clicks = read_log_file('click')
    conversions = read_log_file('conversion')
    subscriptions = read_log_file('subscription')

    metrics = {
        'control': {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'subscriptions': 0,
            'ctr': 0.0,
            'cvr': 0.0,
            'users': 0
        },
        'treatment': {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'subscriptions': 0,
            'ctr': 0.0,
            'cvr': 0.0,
            'users': 0
        }
    }

    # Count impressions by variant
    if not impressions.empty:
        impression_counts = impressions.groupby('variant').size()
        user_counts = impressions.groupby('variant')['user_id'].nunique()

        for variant in ['control', 'treatment']:
            if variant in impression_counts.index:
                metrics[variant]['impressions'] = int(impression_counts[variant])
                metrics[variant]['users'] = int(user_counts[variant])

    # Count clicks by variant
    if not clicks.empty:
        click_counts = clicks.groupby('variant').size()

        for variant in ['control', 'treatment']:
            if variant in click_counts.index:
                metrics[variant]['clicks'] = int(click_counts[variant])

    # Count conversions by variant (ratings - kept for reference)
    if not conversions.empty:
        conversion_counts = conversions.groupby('variant').size()

        for variant in ['control', 'treatment']:
            if variant in conversion_counts.index:
                metrics[variant]['conversions'] = int(conversion_counts[variant])

    # Count subscriptions by variant
    if not subscriptions.empty:
        subscription_counts = subscriptions.groupby('variant').size()

        for variant in ['control', 'treatment']:
            if variant in subscription_counts.index:
                metrics[variant]['subscriptions'] = int(subscription_counts[variant])

    # Calculate rates
    for variant in ['control', 'treatment']:
        # CTR = clicks / impressions
        if metrics[variant]['impressions'] > 0:
            metrics[variant]['ctr'] = metrics[variant]['clicks'] / metrics[variant]['impressions']

        # CVR = subscriptions / clicks (changed from conversions to subscriptions)
        if metrics[variant]['clicks'] > 0:
            metrics[variant]['cvr'] = metrics[variant]['subscriptions'] / metrics[variant]['clicks']

    return metrics


def check_srm(metrics):
    """
    Check for Sample Ratio Mismatch (SRM)

    Expected ratio: 50/50 (due to hash-based assignment)

    Returns:
        Dictionary with SRM check results
    """
    control_users = metrics['control']['users']
    treatment_users = metrics['treatment']['users']
    total_users = control_users + treatment_users

    if total_users == 0:
        return {
            'has_srm': False,
            'message': 'No users yet',
            'control_ratio': 0,
            'treatment_ratio': 0
        }

    control_ratio = control_users / total_users
    treatment_ratio = treatment_users / total_users

    # Flag SRM if ratio deviates more than 5% from expected 50/50
    expected_ratio = 0.5
    tolerance = 0.05

    has_srm = (abs(control_ratio - expected_ratio) > tolerance or
               abs(treatment_ratio - expected_ratio) > tolerance)

    return {
        'has_srm': has_srm,
        'message': 'SRM detected! Check assignment logic.' if has_srm else 'No SRM detected',
        'control_ratio': round(control_ratio, 3),
        'treatment_ratio': round(treatment_ratio, 3),
        'expected_ratio': expected_ratio
    }


def get_recent_events(event_type, n=10):
    """Get recent events for display"""
    if use_mongodb():
        return _get_recent_events_mongodb(event_type, n)
    else:
        return _get_recent_events_csv(event_type, n)


def _get_recent_events_mongodb(event_type, n=10):
    """Get recent events from MongoDB"""
    db = get_db()
    collection_name = f"{event_type}s"

    events = list(db[collection_name].find().sort('timestamp', -1).limit(n))

    # Convert ObjectId to string for JSON serialization
    for event in events:
        event['_id'] = str(event['_id'])
        if 'timestamp' in event:
            event['timestamp'] = event['timestamp'].isoformat() if hasattr(event['timestamp'], 'isoformat') else str(event['timestamp'])

    return events


def _get_recent_events_csv(event_type, n=10):
    """Get recent events from CSV"""
    log_file = LOG_DIR / f'{event_type}s.csv'

    if not log_file.exists():
        return []

    df = pd.read_csv(log_file)
    return df.tail(n).to_dict('records')


def calculate_lift(metrics):
    """
    Calculate lift: (Treatment - Control) / Control

    Returns:
        Dictionary with lift percentages
    """
    lift = {}

    # CTR lift
    if metrics['control']['ctr'] > 0:
        lift['ctr'] = ((metrics['treatment']['ctr'] - metrics['control']['ctr']) /
                       metrics['control']['ctr']) * 100
    else:
        lift['ctr'] = 0

    # CVR lift
    if metrics['control']['cvr'] > 0:
        lift['cvr'] = ((metrics['treatment']['cvr'] - metrics['control']['cvr']) /
                       metrics['control']['cvr']) * 100
    else:
        lift['cvr'] = 0

    return lift
