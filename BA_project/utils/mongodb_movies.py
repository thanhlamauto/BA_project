"""
MongoDB Movie Dataset Handler
Loads movies from sample_mflix.movies collection (21,000+ real movies!)

Usage:
    from utils.mongodb_movies import MongoMovieDataset
    dataset = MongoMovieDataset()
    movies = dataset.get_all_movies()
"""
import os
import random

# Try to import pymongo
try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

# MongoDB connection
_client = None
_movies_collection = None


def get_movies_collection():
    """Get MongoDB movies collection (lazy initialization)"""
    global _client, _movies_collection

    if not PYMONGO_AVAILABLE:
        return None

    if _movies_collection is None:
        try:
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ba_project')
            _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            _client.admin.command('ping')

            # Use sample_mflix database for movies
            db = _client['sample_mflix']
            _movies_collection = db['movies']

            # Verify collection exists
            count = _movies_collection.count_documents({})
            if count > 0:
                print(f"[MongoDB Movies] Connected: {count:,} movies available")
            else:
                _movies_collection = None

        except Exception as e:
            print(f"[MongoDB Movies] Connection failed: {e}")
            _movies_collection = None

    return _movies_collection


class MongoMovieDataset:
    """Movie dataset from MongoDB sample_mflix"""

    def __init__(self, limit=500):
        """
        Initialize dataset.
        Args:
            limit: Max number of movies to load (for performance)
        """
        self.limit = limit
        self.movies = []
        self._movies_dict = {}
        self.load_data()

    def load_data(self):
        """Load movies from MongoDB"""
        collection = get_movies_collection()

        if collection is None:
            print("[MongoDB Movies] Using fallback sample data")
            self.movies = self._create_fallback_data()
            return

        # Query movies with posters and ratings
        # Only get movies with poster images for better UI
        cursor = collection.find(
            {
                'poster': {'$exists': True, '$ne': None, '$ne': ''},
                'imdb.rating': {'$exists': True, '$gt': 0}
            },
            {
                '_id': 1,
                'title': 1,
                'year': 1,
                'genres': 1,
                'poster': 1,
                'plot': 1,
                'imdb': 1,
                'runtime': 1
            }
        ).sort('imdb.rating', -1).limit(self.limit)

        for doc in cursor:
            movie = self._transform_movie(doc)
            self.movies.append(movie)
            self._movies_dict[movie['movieId']] = movie

        print(f"[MongoDB Movies] Loaded {len(self.movies)} movies")

    def _transform_movie(self, doc):
        """Transform MongoDB document to standard format"""
        # Convert genres list to pipe-separated string
        genres = doc.get('genres', [])
        if isinstance(genres, list):
            genres_str = '|'.join(genres)
        else:
            genres_str = str(genres)

        # Get IMDB rating
        imdb = doc.get('imdb', {})
        rating = imdb.get('rating', 3.0) if isinstance(imdb, dict) else 3.0

        # Normalize rating to 5-star scale (IMDB is 10-point)
        avg_rating = round(rating / 2, 1) if rating else 3.0

        return {
            'movieId': str(doc['_id']),
            'title': doc.get('title', 'Unknown'),
            'year': doc.get('year', ''),
            'genres': genres_str,
            'avg_rating': avg_rating,
            'poster_url': doc.get('poster', ''),
            'plot': doc.get('plot', ''),
            'runtime': doc.get('runtime', 0)
        }

    def _create_fallback_data(self):
        """Fallback sample data if MongoDB not available"""
        return [
            {'movieId': '1', 'title': 'The Shawshank Redemption', 'year': 1994, 'genres': 'Drama',
             'avg_rating': 4.5, 'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg'},
            {'movieId': '2', 'title': 'The Godfather', 'year': 1972, 'genres': 'Crime|Drama',
             'avg_rating': 4.4, 'poster_url': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg'},
            {'movieId': '3', 'title': 'The Dark Knight', 'year': 2008, 'genres': 'Action|Crime|Drama',
             'avg_rating': 4.3, 'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg'},
            {'movieId': '4', 'title': 'Pulp Fiction', 'year': 1994, 'genres': 'Crime|Drama|Thriller',
             'avg_rating': 4.3, 'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'},
            {'movieId': '5', 'title': 'Inception', 'year': 2010, 'genres': 'Action|Mystery|Sci-Fi',
             'avg_rating': 4.2, 'poster_url': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg'},
        ]

    def get_all_movies(self):
        """Return all movies as list of dicts"""
        return self.movies

    def get_movie_by_id(self, movie_id):
        """Get movie by ID"""
        return self._movies_dict.get(str(movie_id))

    def get_random_movies(self, n=12):
        """Get n random movies"""
        return random.sample(self.movies, min(n, len(self.movies)))

    def get_top_rated(self, n=12):
        """Get top rated movies"""
        sorted_movies = sorted(self.movies, key=lambda m: m['avg_rating'], reverse=True)
        return sorted_movies[:n]

    def search_by_genre(self, genre, n=12):
        """Search movies by genre"""
        matches = [m for m in self.movies if genre.lower() in m['genres'].lower()]
        return matches[:n]


# Singleton instance
_dataset = None


def get_mongo_dataset():
    """Get singleton MongoMovieDataset instance"""
    global _dataset
    if _dataset is None:
        _dataset = MongoMovieDataset()
    return _dataset


# Quick test
if __name__ == '__main__':
    print("Testing MongoDB Movie Dataset...")
    dataset = MongoMovieDataset(limit=10)

    print(f"\nLoaded {len(dataset.movies)} movies:")
    for movie in dataset.movies[:5]:
        print(f"  - {movie['title']} ({movie['year']}) - {movie['avg_rating']}★")
        print(f"    Genres: {movie['genres']}")
        print(f"    Poster: {movie['poster_url'][:50]}...")
