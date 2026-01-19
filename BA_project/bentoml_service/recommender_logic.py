"""
Recommender Logic for BentoML Service
Standalone version of the recommendation algorithms (Control: MF, Treatment: LightGCN)
"""
import random
import pandas as pd
from pathlib import Path

# Data directory (relative to service)
DATA_DIR = Path(__file__).parent / 'data'


class MovieDataset:
    """Simple movie dataset handler"""

    def __init__(self, movies_df=None):
        self.movies = movies_df
        if self.movies is None:
            self.load_data()

    def load_data(self):
        """Load movie metadata"""
        movies_file = DATA_DIR / 'movies.csv'

        if movies_file.exists():
            self.movies = pd.read_csv(movies_file)
        else:
            # Create sample data if file doesn't exist
            self.movies = self._create_sample_data()

    def _create_sample_data(self):
        """Create sample movie data for demo"""
        sample_movies = [
            {'movieId': 1, 'title': 'The Shawshank Redemption (1994)', 'genres': 'Drama', 'avg_rating': 4.5,
             'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg'},
            {'movieId': 2, 'title': 'The Godfather (1972)', 'genres': 'Crime|Drama', 'avg_rating': 4.4,
             'poster_url': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg'},
            {'movieId': 3, 'title': 'The Dark Knight (2008)', 'genres': 'Action|Crime|Drama', 'avg_rating': 4.3,
             'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg'},
            {'movieId': 4, 'title': 'Pulp Fiction (1994)', 'genres': 'Crime|Drama|Thriller', 'avg_rating': 4.3,
             'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'},
            {'movieId': 5, 'title': 'Forrest Gump (1994)', 'genres': 'Comedy|Drama|Romance', 'avg_rating': 4.2,
             'poster_url': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg'},
            {'movieId': 6, 'title': 'Inception (2010)', 'genres': 'Action|Mystery|Sci-Fi', 'avg_rating': 4.2,
             'poster_url': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg'},
            {'movieId': 7, 'title': 'The Matrix (1999)', 'genres': 'Action|Sci-Fi|Thriller', 'avg_rating': 4.1,
             'poster_url': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg'},
            {'movieId': 8, 'title': 'Interstellar (2014)', 'genres': 'Adventure|Drama|Sci-Fi', 'avg_rating': 4.1,
             'poster_url': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg'},
            {'movieId': 9, 'title': 'Fight Club (1999)', 'genres': 'Drama|Thriller', 'avg_rating': 4.0,
             'poster_url': 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'},
            {'movieId': 10, 'title': 'The Lord of the Rings (2001)', 'genres': 'Adventure|Fantasy', 'avg_rating': 4.0,
             'poster_url': 'https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg'},
        ]
        return pd.DataFrame(sample_movies)

    def get_all_movies(self):
        """Return all movies"""
        return self.movies.to_dict('records')

    def get_movie_by_id(self, movie_id):
        """Get movie details by ID"""
        movie = self.movies[self.movies['movieId'] == int(movie_id)]
        if not movie.empty:
            return movie.iloc[0].to_dict()
        return None


def extract_genre_preferences(rated_movies_dict, dataset):
    """Extract genre preferences from user's rated movies."""
    genre_scores = {}

    if not rated_movies_dict:
        return genre_scores

    for movie_id, rating in rated_movies_dict.items():
        movie = dataset.get_movie_by_id(int(movie_id))
        if not movie:
            continue

        genres = movie.get('genres', '').split('|')
        weight = float(rating) / 5.0

        for genre in genres:
            genre = genre.strip()
            if genre:
                genre_scores[genre] = genre_scores.get(genre, 0) + weight

    return genre_scores


def score_movie_by_preference(movie, genre_preferences, variant='control'):
    """Score a movie based on genre preferences and variant type."""
    if not genre_preferences:
        if variant == 'treatment':
            return movie.get('avg_rating', 3.0) / 5.0
        else:
            return random.random()

    genre_match_score = 0
    movie_genres = movie.get('genres', '').split('|')

    for genre in movie_genres:
        genre = genre.strip()
        genre_match_score += genre_preferences.get(genre, 0)

    genre_match_score = min(genre_match_score / 5.0, 1.0)
    popularity_score = movie.get('avg_rating', 3.0) / 5.0

    if variant == 'treatment':
        return (genre_match_score * 0.6) + (popularity_score * 0.4)
    else:
        return (genre_match_score * 0.3) + (random.random() * 0.7)


def get_recommendations(user_id, variant, n=12, rated_movies=None, dataset=None):
    """
    Get recommendations based on assigned variant.

    Args:
        user_id: User identifier
        variant: 'control' or 'treatment'
        n: Number of recommendations
        rated_movies: Dictionary of {movie_id: rating} for personalization
        dataset: MovieDataset instance

    Returns:
        List of movie dictionaries
    """
    if dataset is None:
        dataset = MovieDataset()

    all_movies = dataset.get_all_movies()

    if rated_movies:
        rated_ids = set(int(mid) for mid in rated_movies.keys())
        candidates = [m for m in all_movies if m['movieId'] not in rated_ids]
        genre_prefs = extract_genre_preferences(rated_movies, dataset)

        for movie in candidates:
            movie['_score'] = score_movie_by_preference(movie, genre_prefs, variant=variant)

        candidates.sort(key=lambda m: m['_score'], reverse=True)
        result = candidates[:n]

        for m in result:
            m.pop('_score', None)

        return result
    else:
        if variant == 'treatment':
            movies = dataset.movies.copy()
            if 'avg_rating' in movies.columns:
                movies = movies.sort_values('avg_rating', ascending=False)
            return movies.head(n).to_dict('records')
        else:
            return random.sample(all_movies, min(n, len(all_movies)))
