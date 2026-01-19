"""
Script to test MongoDB Atlas connection
Run: python scripts/test_mongodb.py
"""
import os
from pymongo import MongoClient

# Replace with your MongoDB Atlas connection string
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ba_project')


def test_connection():
    print(f"Testing connection to: {MONGODB_URI[:60]}...")

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

        # Test connection
        client.admin.command('ping')
        print("✅ Connection successful!")

        # List all databases
        print("\n📁 Available databases:")
        for db_name in client.list_database_names():
            print(f"   - {db_name}")

        # Check sample_mflix database (movie database)
        print("\n" + "=" * 50)
        print("🎬 Checking sample_mflix database...")
        print("=" * 50)

        if 'sample_mflix' in client.list_database_names():
            db = client['sample_mflix']

            # List collections
            print("\n📂 Collections in sample_mflix:")
            for coll_name in db.list_collection_names():
                count = db[coll_name].count_documents({})
                print(f"   - {coll_name}: {count:,} documents")

            # Show sample movies
            movies_collection = db['movies']
            movies_count = movies_collection.count_documents({})

            print(f"\n🎬 Total movies: {movies_count:,}")

            # Get movies with posters (for the app)
            movies_with_posters = movies_collection.count_documents({
                'poster': {'$exists': True, '$ne': None, '$ne': ''}
            })
            print(f"🖼️ Movies with posters: {movies_with_posters:,}")

            # Show top rated movies
            print("\n⭐ Top 5 rated movies:")
            top_movies = movies_collection.find(
                {'imdb.rating': {'$exists': True}},
                {'title': 1, 'year': 1, 'genres': 1, 'imdb.rating': 1, 'poster': 1}
            ).sort('imdb.rating', -1).limit(5)

            for movie in top_movies:
                title = movie.get('title', 'Unknown')
                year = movie.get('year', 'N/A')
                rating = movie.get('imdb', {}).get('rating', 'N/A')
                genres = movie.get('genres', [])
                has_poster = '✅' if movie.get('poster') else '❌'

                print(f"   {title} ({year})")
                print(f"      IMDB: {rating}/10 | Genres: {genres} | Poster: {has_poster}")

        else:
            print("⚠️ sample_mflix database not found!")
            print("   Go to Atlas → Load Sample Dataset to add it")

        # Check/Create ba_project database for logs
        print("\n" + "=" * 50)
        print("📊 Setting up ba_project database (for A/B test logs)...")
        print("=" * 50)

        db = client['ba_project']

        # Create indexes for A/B testing
        print("\nCreating indexes...")

        db.impressions.create_index([("user_id", 1), ("timestamp", -1)])
        db.impressions.create_index([("variant", 1), ("timestamp", -1)])
        db.clicks.create_index([("user_id", 1), ("timestamp", -1)])
        db.clicks.create_index([("variant", 1), ("timestamp", -1)])
        db.conversions.create_index([("user_id", 1), ("timestamp", -1)])
        db.subscriptions.create_index([("variant", 1), ("timestamp", -1)])

        print("✅ Indexes created for: impressions, clicks, conversions, subscriptions")

        # Summary
        print("\n" + "=" * 50)
        print("🎉 MongoDB Atlas is ready!")
        print("=" * 50)
        print("""
Configuration summary:
  - sample_mflix.movies: Use for movie recommendations
  - ba_project.*: Use for A/B test event logs

Environment variables to set:
  export MONGODB_URI="<your-connection-string>"
  export USE_MONGODB_LOGGING=true
  export USE_MONGODB_MOVIES=true
""")

        client.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    return True


if __name__ == '__main__':
    test_connection()
