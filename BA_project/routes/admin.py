"""
Admin Routes - For Demo Data Generation & Management
Supports both CSV and MongoDB backends
"""
from flask import Blueprint, jsonify, request
import os
import sys
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.ab_testing import assign_variant

bp = Blueprint('admin', __name__, url_prefix='/admin')

LOG_DIR = Path('data/logs')

# Check if MongoDB is enabled
USE_MONGODB = os.getenv('USE_MONGODB_LOGGING', 'false').lower() == 'true'

if USE_MONGODB:
    try:
        from utils.logger_service import log_impression, log_click, log_subscription, log_engagement
        print("[Admin] Using MongoDB backend")
    except ImportError:
        print("[Admin] MongoDB import failed, falling back to CSV")
        USE_MONGODB = False


def generate_user_id(index):
    """Generate unique user ID"""
    timestamp = int(datetime.now().timestamp() * 1000) + index
    random_num = random.randint(1000, 9999)
    return f"demo_user_{timestamp}_{random_num}"


def write_to_csv(filename, rows, fieldnames):
    """Write rows to CSV file"""
    filepath = LOG_DIR / filename
    
    # Create directory if not exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if file exists
    file_exists = filepath.exists()
    
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(rows)


@bp.route('/generate-demo-data', methods=['POST'])
def generate_demo_data():
    """
    Generate demo data via API endpoint
    
    POST /admin/generate-demo-data
    Body: {
        "num_users": 100,
        "secret": "your-secret-key"
    }
    """
    # Simple authentication (use environment variable in production)
    secret = request.json.get('secret')
    expected_secret = os.getenv('ADMIN_SECRET', 'demo_secret_2024')
    
    if secret != expected_secret:
        return jsonify({'error': 'Invalid secret key'}), 403
    
    num_users = request.json.get('num_users', 50)
    
    if not isinstance(num_users, int) or num_users < 1 or num_users > 500:
        return jsonify({'error': 'num_users must be between 1 and 500'}), 400
    
    try:
        # Generate demo data
        stats = {
            'control': {'users': 0, 'impressions': 0, 'clicks': 0, 'subscriptions': 0},
            'treatment': {'users': 0, 'impressions': 0, 'clicks': 0, 'subscriptions': 0}
        }
        
        impressions_data = []
        clicks_data = []
        subscriptions_data = []
        engagements_data = []
        
        # Generate data for each user
        for i in range(num_users):
            user_id = generate_user_id(i)
            variant = assign_variant(user_id)
            
            stats[variant]['users'] += 1
            
            # Generate timestamp (last 7 days)
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Each user gets 2-5 impression events
            num_impressions = random.randint(2, 5)
            
            for _ in range(num_impressions):
                # Generate random movie IDs (12 movies per impression)
                movie_ids = random.sample(range(1, 121), 12)
                
                if USE_MONGODB:
                    # MongoDB: log directly
                    log_impression(user_id, variant, movie_ids)
                else:
                    # CSV: collect for batch write
                    movie_ids_str = ','.join(str(m) for m in movie_ids)
                    impressions_data.append({
                        'timestamp': timestamp.isoformat(),
                        'user_id': user_id,
                        'variant': variant,
                        'movie_id': movie_ids_str,
                        'rating': '',
                        'metadata': ''
                    })
                
                stats[variant]['impressions'] += 1
                timestamp += timedelta(minutes=random.randint(5, 30))
            
            # User clicks on 0-3 movies (CTR ~30-40%)
            num_clicks = random.randint(0, 3)
            
            for _ in range(num_clicks):
                clicked_movie_id = random.randint(1, 120)
                
                if USE_MONGODB:
                    # MongoDB: log directly
                    log_click(user_id, variant, clicked_movie_id)
                    
                    # Add engagement event
                    engagement_duration = random.randint(30, 300)
                    log_engagement(user_id, variant, clicked_movie_id, 
                                 metadata={'duration_seconds': engagement_duration})
                else:
                    # CSV: collect for batch write
                    clicks_data.append({
                        'timestamp': timestamp.isoformat(),
                        'user_id': user_id,
                        'variant': variant,
                        'movie_id': clicked_movie_id,
                        'rating': '',
                        'metadata': ''
                    })
                    
                    # Add engagement event
                    engagement_duration = random.randint(30, 300)
                    engagements_data.append({
                        'timestamp': timestamp.isoformat(),
                        'user_id': user_id,
                        'variant': variant,
                        'movie_id': clicked_movie_id,
                        'rating': '',
                        'metadata': f'{{"duration_seconds": {engagement_duration}}}'
                    })
                
                stats[variant]['clicks'] += 1
                timestamp += timedelta(minutes=random.randint(1, 10))
            
            # User subscribes (CVR ~20-25% of users)
            if random.random() < 0.22:
                if USE_MONGODB:
                    # MongoDB: log directly
                    log_subscription(user_id, variant)
                else:
                    # CSV: collect for batch write
                    subscriptions_data.append({
                        'timestamp': timestamp.isoformat(),
                        'user_id': user_id,
                        'variant': variant,
                        'movie_id': '',
                        'rating': '',
                        'metadata': ''
                    })
                
                stats[variant]['subscriptions'] += 1
        
        # Write to CSV if not using MongoDB
        if not USE_MONGODB:
            fieldnames = ['timestamp', 'user_id', 'variant', 'movie_id', 'rating', 'metadata']
            
            write_to_csv('impressions.csv', impressions_data, fieldnames)
            write_to_csv('clicks.csv', clicks_data, fieldnames)
            write_to_csv('subscriptions.csv', subscriptions_data, fieldnames)
            write_to_csv('engagements.csv', engagements_data, fieldnames)
        
        # Calculate CTR/CVR
        for variant in ['control', 'treatment']:
            if stats[variant]['impressions'] > 0:
                stats[variant]['ctr'] = (stats[variant]['clicks'] / stats[variant]['impressions']) * 100
            else:
                stats[variant]['ctr'] = 0
            
            if stats[variant]['clicks'] > 0:
                stats[variant]['cvr'] = (stats[variant]['subscriptions'] / stats[variant]['clicks']) * 100
            else:
                stats[variant]['cvr'] = 0
        
        return jsonify({
            'success': True,
            'message': f'Generated demo data for {num_users} users',
            'backend': 'MongoDB' if USE_MONGODB else 'CSV',
            'stats': stats,
            'events_written': {
                'impressions': stats['control']['impressions'] + stats['treatment']['impressions'],
                'clicks': stats['control']['clicks'] + stats['treatment']['clicks'],
                'subscriptions': stats['control']['subscriptions'] + stats['treatment']['subscriptions'],
                'engagements': stats['control']['clicks'] + stats['treatment']['clicks']  # Same as clicks
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/clear-demo-data', methods=['POST'])
def clear_demo_data():
    """
    Clear all demo data (MongoDB collections or CSV files)
    
    POST /admin/clear-demo-data
    Body: {
        "secret": "your-secret-key"
    }
    """
    secret = request.json.get('secret')
    expected_secret = os.getenv('ADMIN_SECRET', 'demo_secret_2024')
    
    if secret != expected_secret:
        return jsonify({'error': 'Invalid secret key'}), 403
    
    try:
        if USE_MONGODB:
            # Clear MongoDB collections
            from pymongo import MongoClient
            client = MongoClient(os.getenv('MONGODB_URI'))
            db = client.get_database()
            
            cleared_collections = []
            for collection_name in ['impressions', 'clicks', 'subscriptions', 
                                   'conversions', 'engagements', 'performances', 'users']:
                if collection_name in db.list_collection_names():
                    result = db[collection_name].delete_many({})
                    cleared_collections.append({
                        'collection': collection_name,
                        'deleted_count': result.deleted_count
                    })
            
            client.close()
            
            return jsonify({
                'success': True,
                'backend': 'MongoDB',
                'message': f'Cleared {len(cleared_collections)} collections',
                'cleared': cleared_collections
            })
        else:
            # Clear CSV files
            deleted_files = []
            
            for filename in ['impressions.csv', 'clicks.csv', 'subscriptions.csv', 
                            'conversions.csv', 'engagements.csv', 'performances.csv']:
                filepath = LOG_DIR / filename
                if filepath.exists():
                    filepath.unlink()
                    deleted_files.append(filename)
            
            return jsonify({
                'success': True,
                'backend': 'CSV',
                'message': f'Cleared {len(deleted_files)} files',
                'deleted_files': deleted_files
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get current data statistics (MongoDB or CSV)"""
    secret = request.args.get('secret')
    expected_secret = os.getenv('ADMIN_SECRET', 'demo_secret_2024')
    
    if secret != expected_secret:
        return jsonify({'error': 'Invalid secret key'}), 403
    
    try:
        stats = {}
        
        if USE_MONGODB:
            # Get stats from MongoDB
            from pymongo import MongoClient
            client = MongoClient(os.getenv('MONGODB_URI'))
            db = client.get_database()
            
            for collection_name in ['impressions', 'clicks', 'subscriptions', 
                                   'engagements', 'users']:
                if collection_name in db.list_collection_names():
                    stats[collection_name] = db[collection_name].count_documents({})
                else:
                    stats[collection_name] = 0
            
            client.close()
            
            return jsonify({
                'success': True,
                'backend': 'MongoDB',
                'stats': stats
            })
        else:
            # Get stats from CSV files
            for filename in ['impressions', 'clicks', 'subscriptions', 'engagements']:
                filepath = LOG_DIR / f'{filename}.csv'
                if filepath.exists():
                    with open(filepath, 'r') as f:
                        # Count lines (subtract 1 for header)
                        count = sum(1 for line in f) - 1
                        stats[filename] = count
                else:
                    stats[filename] = 0
            
            return jsonify({
                'success': True,
                'backend': 'CSV',
                'stats': stats
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
