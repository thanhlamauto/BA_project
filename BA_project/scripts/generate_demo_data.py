#!/usr/bin/env python3
"""
Generate Demo Data for A/B Testing Dashboard
Creates fake users, impressions, clicks, and subscriptions for visualization
"""
import sys
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ab_testing import assign_variant

LOG_DIR = Path(__file__).parent.parent / 'data' / 'logs'


def generate_user_id(index):
    """Generate unique user ID"""
    timestamp = int(datetime.now().timestamp() * 1000) + index
    random_num = random.randint(1000, 9999)
    return f"demo_user_{timestamp}_{random_num}"


def write_to_csv(filename, rows, fieldnames):
    """Write rows to CSV file"""
    filepath = LOG_DIR / filename
    
    # Check if file exists
    file_exists = filepath.exists()
    
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(rows)


def generate_demo_data(num_users=50):
    """
    Generate demo data for A/B testing
    
    Args:
        num_users: Number of users to generate (default 50)
    """
    print("="*60)
    print("Generating Demo Data for A/B Testing Dashboard")
    print("="*60)
    print(f"\nGenerating {num_users} users...")
    
    # Create log directory if not exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Track statistics
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
            
            # Small timestamp increment for next impression
            timestamp += timedelta(minutes=random.randint(5, 30))
        
        # User clicks on 0-3 movies (CTR ~30-40%)
        num_clicks = random.randint(0, 3)
        
        for _ in range(num_clicks):
            clicked_movie_id = random.randint(1, 120)
            
            clicks_data.append({
                'timestamp': timestamp.isoformat(),
                'user_id': user_id,
                'variant': variant,
                'movie_id': clicked_movie_id,
                'rating': '',
                'metadata': ''
            })
            
            stats[variant]['clicks'] += 1
            
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
            
            timestamp += timedelta(minutes=random.randint(1, 10))
        
        # User subscribes (CVR ~20-25% of users)
        if random.random() < 0.22:
            subscriptions_data.append({
                'timestamp': timestamp.isoformat(),
                'user_id': user_id,
                'variant': variant,
                'movie_id': '',
                'rating': '',
                'metadata': ''
            })
            
            stats[variant]['subscriptions'] += 1
    
    # Write data to CSV files
    print("\n📝 Writing data to CSV files...")
    
    fieldnames = ['timestamp', 'user_id', 'variant', 'movie_id', 'rating', 'metadata']
    
    if impressions_data:
        write_to_csv('impressions.csv', impressions_data, fieldnames)
        print(f"  ✅ impressions.csv: {len(impressions_data)} events")
    
    if clicks_data:
        write_to_csv('clicks.csv', clicks_data, fieldnames)
        print(f"  ✅ clicks.csv: {len(clicks_data)} events")
    
    if subscriptions_data:
        write_to_csv('subscriptions.csv', subscriptions_data, fieldnames)
        print(f"  ✅ subscriptions.csv: {len(subscriptions_data)} events")
    
    if engagements_data:
        write_to_csv('engagements.csv', engagements_data, fieldnames)
        print(f"  ✅ engagements.csv: {len(engagements_data)} events")
    
    # Calculate and display statistics
    print("\n📊 Generated Data Statistics:")
    print("="*60)
    
    for variant in ['control', 'treatment']:
        v_stats = stats[variant]
        
        print(f"\n{variant.upper()}:")
        print(f"  Users:        {v_stats['users']:4d}")
        print(f"  Impressions:  {v_stats['impressions']:4d}")
        print(f"  Clicks:       {v_stats['clicks']:4d}")
        print(f"  Subscriptions:{v_stats['subscriptions']:4d}")
        
        if v_stats['impressions'] > 0:
            ctr = (v_stats['clicks'] / v_stats['impressions']) * 100
            print(f"  CTR:          {ctr:5.2f}%")
        
        if v_stats['clicks'] > 0:
            cvr = (v_stats['subscriptions'] / v_stats['clicks']) * 100
            print(f"  CVR:          {cvr:5.2f}%")
    
    # Check variant distribution
    total_users = stats['control']['users'] + stats['treatment']['users']
    control_pct = (stats['control']['users'] / total_users) * 100
    treatment_pct = (stats['treatment']['users'] / total_users) * 100
    
    print(f"\n{'='*60}")
    print("Variant Distribution:")
    print(f"  Control:   {stats['control']['users']:3d} users ({control_pct:5.2f}%)")
    print(f"  Treatment: {stats['treatment']['users']:3d} users ({treatment_pct:5.2f}%)")
    
    if 45 <= control_pct <= 55:
        print("  ✅ Balanced (within 45-55% range)")
    else:
        print("  ⚠️  Imbalanced (outside 45-55% range)")
    
    print("\n" + "="*60)
    print("✅ Demo data generated successfully!")
    print("="*60)
    print("\n📍 Next Steps:")
    print("  1. Restart your Flask app: python app.py")
    print("  2. Visit dashboard: http://localhost:5000/dashboard")
    print("  3. You should see metrics for both variants")
    print("  4. Login with new user to test recommendations")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate demo data for A/B testing')
    parser.add_argument('--users', type=int, default=50, help='Number of users to generate (default: 50)')
    parser.add_argument('--clear', action='store_true', help='Clear existing data first')
    
    args = parser.parse_args()
    
    if args.clear:
        print("\n🗑️  Clearing existing CSV files...")
        for filename in ['impressions.csv', 'clicks.csv', 'subscriptions.csv', 'engagements.csv']:
            filepath = LOG_DIR / filename
            if filepath.exists():
                filepath.unlink()
                print(f"  Deleted {filename}")
    
    generate_demo_data(num_users=args.users)
