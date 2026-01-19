"""
MongoDB Migration Script - Complete Edition
============================================
Migrates all CSV logs, creates user profiles, and sets up collections

Features:
- ✅ Upload all logs from CSV to MongoDB
- ✅ Extract and create user profiles
- ✅ Clear existing data (optional)
- ✅ Create indexes for performance
- ✅ Verify data integrity
- ✅ Progress tracking

Run: python scripts/migrate_to_mongodb.py [--clear]
"""
import os
import sys
import csv
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    print("❌ Please install pymongo: pip install pymongo")
    sys.exit(1)

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ba_project')
LOG_DIR = Path(__file__).parent.parent / 'data' / 'logs'

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def get_client():
    """Get MongoDB client"""
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    return client


def clear_collection(db, collection_name):
    """Clear existing collection"""
    collection = db[collection_name]
    count = collection.count_documents({})
    if count > 0:
        collection.delete_many({})
        print(f"  🗑️ Cleared {count} documents from {collection_name}")
    return count


def upload_csv_to_collection(db, collection_name, csv_file, show_progress=True):
    """Upload CSV file to MongoDB collection with progress tracking"""
    if not csv_file.exists():
        print(f"  ⚠️  {csv_file.name} not found, skipping...")
        return 0

    collection = db[collection_name]

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        documents = []
        
        print(f"  📄 Reading {csv_file.name}...", end='', flush=True)

        for row in reader:
            # Convert timestamp string to datetime
            if 'timestamp' in row and row['timestamp']:
                try:
                    row['timestamp'] = datetime.fromisoformat(row['timestamp'])
                except:
                    pass

            # Convert rating to int if present
            if 'rating' in row and row['rating']:
                try:
                    row['rating'] = int(row['rating'])
                except:
                    row['rating'] = None

            # Clean empty strings
            row = {k: v if v != '' else None for k, v in row.items()}
            
            documents.append(row)

        if documents:
            # Insert in batches for better performance
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                collection.insert_many(batch)
                if show_progress:
                    print('.', end='', flush=True)
            
            print(f" {Colors.GREEN}✅ {len(documents):,} docs{Colors.ENDC}")
            return len(documents)
        else:
            print(f" {Colors.YELLOW}⚠️  Empty{Colors.ENDC}")

    return 0


def extract_users_from_logs(db):
    """Extract unique users from logs and create user profiles"""
    print("\n👥 Extracting user profiles...")
    
    users = {}
    
    # Get all unique users from impressions (main interaction log)
    impressions = db['impressions'].find({}, {'user_id': 1, 'variant': 1, 'timestamp': 1})
    
    for record in impressions:
        user_id = record.get('user_id')
        if user_id and user_id not in users:
            variant = record.get('variant', 'unknown')
            first_seen = record.get('timestamp', datetime.now())
            
            users[user_id] = {
                'user_id': user_id,
                'variant': variant,
                'first_seen': first_seen,
                'created_at': datetime.now(),
                'metadata': {}
            }
    
    # Get interaction counts
    print("  📊 Calculating user metrics...")
    for user_id in users:
        # Count impressions
        impressions_count = db['impressions'].count_documents({'user_id': user_id})
        # Count clicks
        clicks_count = db['clicks'].count_documents({'user_id': user_id})
        # Count subscriptions
        subscriptions_count = db['subscriptions'].count_documents({'user_id': user_id})
        
        users[user_id]['total_impressions'] = impressions_count
        users[user_id]['total_clicks'] = clicks_count
        users[user_id]['total_subscriptions'] = subscriptions_count
        users[user_id]['ctr'] = (clicks_count / impressions_count * 100) if impressions_count > 0 else 0
        users[user_id]['converted'] = subscriptions_count > 0
    
    # Insert users into collection
    if users:
        db['users'].delete_many({})  # Clear existing
        db['users'].insert_many(list(users.values()))
        print(f"  {Colors.GREEN}✅ Created {len(users):,} user profiles{Colors.ENDC}")
        
        # Show statistics
        control_users = len([u for u in users.values() if u['variant'] == 'control'])
        treatment_users = len([u for u in users.values() if u['variant'] == 'treatment'])
        converted_users = len([u for u in users.values() if u['converted']])
        
        print(f"     • Control: {control_users}")
        print(f"     • Treatment: {treatment_users}")
        print(f"     • Converted: {converted_users}")
        
        return len(users)
    
    return 0


def create_indexes(db):
    """Create indexes for fast A/B testing queries"""
    print("\n📊 Creating indexes for performance...")

    indexes = {
        'impressions': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)],
            [("movie_id", 1)]
        ],
        'clicks': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)],
            [("movie_id", 1)]
        ],
        'conversions': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)]
        ],
        'subscriptions': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)]
        ],
        'engagements': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1)]
        ],
        'performances': [
            [("endpoint", 1), ("timestamp", -1)],
            [("status_code", 1)]
        ],
        'users': [
            [("user_id", 1)],
            [("variant", 1)],
            [("converted", 1)]
        ]
    }

    total_indexes = 0
    for collection_name, index_list in indexes.items():
        if db[collection_name].count_documents({}) > 0:  # Only if collection has data
            collection = db[collection_name]
            for index in index_list:
                try:
                    collection.create_index(index)
                    total_indexes += 1
                except Exception as e:
                    print(f"  ⚠️  Error creating index on {collection_name}: {e}")
            print(f"  ✅ {collection_name}: {len(index_list)} indexes")
    
    print(f"\n  {Colors.GREEN}✓ Total {total_indexes} indexes created{Colors.ENDC}")


def verify_data(db):
    """Verify uploaded data integrity"""
    print("\n🔍 Verifying data integrity...")
    
    collections_to_check = ['impressions', 'clicks', 'subscriptions', 'engagements', 'performances', 'users']
    all_good = True
    
    for coll_name in collections_to_check:
        count = db[coll_name].count_documents({})
        
        if count > 0:
            # Check for timestamps
            with_timestamp = db[coll_name].count_documents({'timestamp': {'$exists': True}})
            
            # Check for required fields
            if coll_name in ['impressions', 'clicks', 'subscriptions']:
                with_user_id = db[coll_name].count_documents({'user_id': {'$exists': True}})
                with_variant = db[coll_name].count_documents({'variant': {'$exists': True}})
                
                if with_user_id == count and with_variant == count:
                    print(f"  {Colors.GREEN}✅ {coll_name}: {count:,} docs (all valid){Colors.ENDC}")
                else:
                    print(f"  {Colors.YELLOW}⚠️  {coll_name}: {count:,} docs (some missing fields){Colors.ENDC}")
                    all_good = False
            else:
                print(f"  {Colors.GREEN}✅ {coll_name}: {count:,} docs{Colors.ENDC}")
        else:
            print(f"  {Colors.YELLOW}⚠️  {coll_name}: empty{Colors.ENDC}")
    
    return all_good


def check_sample_mflix(client):
    """Check if sample_mflix database exists and has movies with posters"""
    print("\n🎬 Checking sample_mflix database (for movie posters)...")

    if 'sample_mflix' in client.list_database_names():
        db = client['sample_mflix']
        
        total_movies = db.movies.count_documents({})
        movies_with_posters = db.movies.count_documents({'poster': {'$exists': True, '$ne': None, '$ne': ''}})
        
        print(f"  {Colors.GREEN}✅ sample_mflix.movies: {total_movies:,} movies{Colors.ENDC}")
        print(f"     • With posters: {movies_with_posters:,}")

        # Show sample movies
        samples = db.movies.find(
            {'poster': {'$exists': True, '$ne': ''}, 'imdb.rating': {'$gt': 8}},
            {'title': 1, 'year': 1, 'genres': 1, 'poster': 1, 'imdb.rating': 1}
        ).limit(3)
        
        print(f"\n  📽️  Sample movies:")
        for movie in samples:
            rating = movie.get('imdb', {}).get('rating', 'N/A') if isinstance(movie.get('imdb'), dict) else 'N/A'
            print(f"     • {movie.get('title')} ({movie.get('year')})")
            print(f"       Rating: {rating}/10 | Genres: {', '.join(movie.get('genres', [])[:3])}")
            print(f"       Poster: {Colors.GREEN}✓{Colors.ENDC}")

        return True
    else:
        print(f"  {Colors.YELLOW}⚠️  sample_mflix not found{Colors.ENDC}")
        print(f"     To add 21,000+ real movies with posters:")
        print(f"     1. Go to MongoDB Atlas Dashboard")
        print(f"     2. Click 'Browse Collections'")
        print(f"     3. Click '...' → Load Sample Dataset")
        print(f"     4. Wait 5-10 minutes for loading")
        return False


def show_summary(db, total_docs):
    """Show migration summary with statistics"""
    print_header("Migration Summary")
    
    print(f"{Colors.BOLD}📊 Collections:{Colors.ENDC}")
    collections = ['impressions', 'clicks', 'subscriptions', 'conversions', 'engagements', 'performances', 'users']
    for coll_name in collections:
        count = db[coll_name].count_documents({})
        if count > 0:
            print(f"  • {coll_name:20} {count:>8,} documents")
    
    print(f"\n{Colors.GREEN}✓ Total migrated: {total_docs:,} documents{Colors.ENDC}")
    
    # Calculate metrics
    print(f"\n{Colors.BOLD}📈 A/B Test Metrics:{Colors.ENDC}")
    
    for variant in ['control', 'treatment']:
        impressions = db['impressions'].count_documents({'variant': variant})
        clicks = db['clicks'].count_documents({'variant': variant})
        subscriptions = db['subscriptions'].count_documents({'variant': variant})
        users = db['users'].count_documents({'variant': variant})
        
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cvr = (subscriptions / clicks * 100) if clicks > 0 else 0
        
        variant_label = variant.upper()
        print(f"\n  {Colors.BOLD}{variant_label}:{Colors.ENDC}")
        print(f"    Users: {users:,} | Impressions: {impressions:,} | Clicks: {clicks:,} | Subs: {subscriptions:,}")
        print(f"    CTR: {ctr:.2f}% | CVR: {cvr:.2f}%")


def main():
    parser = argparse.ArgumentParser(description='Migrate CSV logs to MongoDB')
    parser.add_argument('--clear', action='store_true', help='Clear existing collections before upload')
    parser.add_argument('--skip-users', action='store_true', help='Skip user profile extraction')
    args = parser.parse_args()

    print_header("MongoDB Migration Script")
    print(f"{Colors.BLUE}🔗 Connecting to MongoDB...{Colors.ENDC}")
    print(f"   URI: {MONGODB_URI[:60]}...")

    try:
        client = get_client()
        print(f"   {Colors.GREEN}✓ Connected!{Colors.ENDC}\n")

        # Get database name from URI
        db_name = MONGODB_URI.split('/')[-1].split('?')[0] or 'ba_project'
        db = client[db_name]
        print(f"📁 Database: {Colors.BOLD}{db_name}{Colors.ENDC}")

        # Clear collections if requested
        if args.clear:
            print_header("Clearing Existing Data")
            collections = ['impressions', 'clicks', 'conversions', 'subscriptions', 
                          'engagements', 'performances', 'users']
            for coll_name in collections:
                clear_collection(db, coll_name)

        # Upload CSV logs
        print_header("Uploading CSV Logs")
        csv_files = {
            'impressions': LOG_DIR / 'impressions.csv',
            'clicks': LOG_DIR / 'clicks.csv',
            'conversions': LOG_DIR / 'conversions.csv',
            'subscriptions': LOG_DIR / 'subscriptions.csv',
            'engagements': LOG_DIR / 'engagements.csv',
            'performances': LOG_DIR / 'performances.csv',
        }

        total_docs = 0
        for collection_name, csv_file in csv_files.items():
            count = upload_csv_to_collection(db, collection_name, csv_file)
            total_docs += count

        # Extract user profiles
        if not args.skip_users:
            user_count = extract_users_from_logs(db)
            total_docs += user_count

        # Create indexes
        create_indexes(db)

        # Verify data
        verify_data(db)

        # Check sample_mflix
        check_sample_mflix(client)

        # Show summary
        show_summary(db, total_docs)

        # Next steps
        print_header("Next Steps")
        print(f"""
{Colors.BOLD}1. Enable MongoDB logging:{Colors.ENDC}
   export USE_MONGODB_LOGGING=true

{Colors.BOLD}2. Use MongoDB for movies (optional):{Colors.ENDC}
   export USE_MONGODB_MOVIES=true
   
   # MongoDB has 21,000+ real movies with posters!
   # Much better than the 20 sample movies in CSV

{Colors.BOLD}3. Start the application:{Colors.ENDC}
   python app.py

{Colors.BOLD}4. View MongoDB data:{Colors.ENDC}
   # Install MongoDB Compass: https://www.mongodb.com/products/compass
   # Or use Atlas web interface

{Colors.BOLD}5. Test Grafana (optional):{Colors.ENDC}
   python scripts/test_grafana.py
""")

        print(f"{Colors.GREEN}{Colors.BOLD}✅ Migration completed successfully!{Colors.ENDC}\n")
        
        client.close()
        return True

    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Migration failed!{Colors.ENDC}")
        print(f"   Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
