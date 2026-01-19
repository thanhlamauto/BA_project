"""
Migration Script: Upload CSV logs and setup MongoDB collections
Run: python scripts/migrate_to_mongodb.py
"""
import os
import sys
import csv
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pymongo import MongoClient
    print("✅ pymongo imported")
except ImportError:
    print("❌ Please install pymongo: pip install pymongo")
    sys.exit(1)

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ba_project')
LOG_DIR = Path(__file__).parent.parent / 'data' / 'logs'


def get_client():
    """Get MongoDB client"""
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    return client


def upload_csv_to_collection(db, collection_name, csv_file):
    """Upload CSV file to MongoDB collection"""
    if not csv_file.exists():
        print(f"  ⚠️ {csv_file.name} not found, skipping...")
        return 0

    collection = db[collection_name]

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        documents = []

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
                    pass

            documents.append(row)

        if documents:
            collection.insert_many(documents)
            return len(documents)

    return 0


def create_indexes(db):
    """Create indexes for A/B testing queries"""
    print("\n📊 Creating indexes...")

    indexes = {
        'impressions': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)]
        ],
        'clicks': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)]
        ],
        'conversions': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)]
        ],
        'subscriptions': [
            [("user_id", 1), ("timestamp", -1)],
            [("variant", 1), ("timestamp", -1)]
        ]
    }

    for collection_name, index_list in indexes.items():
        collection = db[collection_name]
        for index in index_list:
            collection.create_index(index)
        print(f"  ✅ {collection_name}: {len(index_list)} indexes")


def check_sample_mflix(client):
    """Check if sample_mflix database exists and has movies"""
    print("\n🎬 Checking sample_mflix database...")

    if 'sample_mflix' in client.list_database_names():
        db = client['sample_mflix']
        movies_count = db.movies.count_documents({})
        print(f"  ✅ sample_mflix.movies: {movies_count:,} movies available!")

        # Show sample movie
        sample = db.movies.find_one({}, {'title': 1, 'year': 1, 'genres': 1, 'poster': 1})
        if sample:
            print(f"  📽️ Sample: {sample.get('title')} ({sample.get('year')})")
            print(f"     Genres: {sample.get('genres', [])}")
            if sample.get('poster'):
                print(f"     Poster: ✅ Available")

        return True
    else:
        print("  ⚠️ sample_mflix not found")
        print("     Go to Atlas → Browse Collections → Load Sample Dataset")
        return False


def main():
    print("=" * 60)
    print("  MongoDB Migration Script")
    print("=" * 60)

    print(f"\n🔗 Connecting to: {MONGODB_URI[:50]}...")

    try:
        client = get_client()
        print("✅ Connected!")

        # Get database name from URI
        db_name = MONGODB_URI.split('/')[-1].split('?')[0] or 'ba_project'
        db = client[db_name]
        print(f"📁 Database: {db_name}")

        # Upload CSV logs
        print("\n📤 Uploading CSV logs...")
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
            if count > 0:
                print(f"  ✅ {collection_name}: {count} documents")
                total_docs += count

        print(f"\n📊 Total uploaded: {total_docs} documents")

        # Create indexes
        create_indexes(db)

        # Check sample_mflix
        check_sample_mflix(client)

        # Summary
        print("\n" + "=" * 60)
        print("  Migration Complete!")
        print("=" * 60)
        print(f"""
Next steps:
1. Set environment variable:
   export USE_MONGODB_LOGGING=true

2. Use sample_mflix for movies:
   Movies are in: sample_mflix.movies

3. Run the app:
   python app.py
""")

        client.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


if __name__ == '__main__':
    main()
