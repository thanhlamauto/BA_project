"""
BentoML Service for Movie Recommendations
Exposes the recommender system as a REST API
"""
import bentoml
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Optional
from pathlib import Path

from recommender_logic import MovieDataset, get_recommendations


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    user_id: str
    variant: str
    rated_movies: Dict[str, int] = {}
    n: int = 12


class MovieResponse(BaseModel):
    """Single movie in response"""
    movieId: int
    title: str
    genres: str
    avg_rating: float
    poster_url: str


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    recommendations: List[dict]
    variant: str
    personalized: bool
    user_id: str


@bentoml.service(
    name="movie-recommender",
    resources={"cpu": "1", "memory": "512Mi"},
    traffic={"timeout": 10},
)
class MovieRecommender:
    """BentoML Service for Movie Recommendations"""

    def __init__(self):
        """Initialize the service with movie dataset"""
        # Try to load from data directory
        data_dir = Path(__file__).parent / 'data'
        movies_file = data_dir / 'movies.csv'

        if movies_file.exists():
            movies_df = pd.read_csv(movies_file)
            self.dataset = MovieDataset(movies_df)
            print(f"[MovieRecommender] Loaded {len(movies_df)} movies from {movies_file}")
        else:
            self.dataset = MovieDataset()
            print(f"[MovieRecommender] Using sample data ({len(self.dataset.movies)} movies)")

    @bentoml.api
    def predict(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Generate movie recommendations based on user variant and ratings.

        Args:
            request: RecommendationRequest with user_id, variant, rated_movies, n

        Returns:
            RecommendationResponse with recommendations list
        """
        recs = get_recommendations(
            user_id=request.user_id,
            variant=request.variant,
            n=request.n,
            rated_movies=request.rated_movies,
            dataset=self.dataset
        )

        return RecommendationResponse(
            recommendations=recs,
            variant=request.variant,
            personalized=len(request.rated_movies) > 0,
            user_id=request.user_id
        )

    @bentoml.api
    def healthz(self) -> dict:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "movies_loaded": len(self.dataset.movies) if self.dataset.movies is not None else 0
        }
