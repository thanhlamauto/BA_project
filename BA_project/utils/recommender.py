"""
Mock Recommender Systems
- Control: Matrix Factorization
- Treatment: LightGCN

Supports two data sources:
- Local CSV/sample data (default)
- MongoDB sample_mflix (set USE_MONGODB_MOVIES=true)
"""
import os
import random
import pandas as pd
from pathlib import Path

DATA_DIR = Path('data')

# Check if we should use MongoDB movies
USE_MONGODB_MOVIES = os.getenv('USE_MONGODB_MOVIES', 'false').lower() == 'true'


class MovieDataset:
    """Simple movie dataset handler"""

    def __init__(self):
        self.movies = None
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
        """Create sample movie data for demo with real TMDB poster URLs"""
        sample_movies = [
            {
                'movieId': 1,
                'title': 'The Shawshank Redemption (1994)',
                'genres': 'Drama',
                'avg_rating': 4.5,
                'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg'
            },
            {
                'movieId': 2,
                'title': 'The Godfather (1972)',
                'genres': 'Crime|Drama',
                'avg_rating': 4.4,
                'poster_url': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg'
            },
            {
                'movieId': 3,
                'title': 'The Dark Knight (2008)',
                'genres': 'Action|Crime|Drama',
                'avg_rating': 4.3,
                'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg'
            },
            {
                'movieId': 4,
                'title': 'Pulp Fiction (1994)',
                'genres': 'Crime|Drama|Thriller',
                'avg_rating': 4.3,
                'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'
            },
            {
                'movieId': 5,
                'title': 'Forrest Gump (1994)',
                'genres': 'Comedy|Drama|Romance',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg'
            },
            {
                'movieId': 6,
                'title': 'Inception (2010)',
                'genres': 'Action|Mystery|Sci-Fi',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg'
            },
            {
                'movieId': 7,
                'title': 'The Matrix (1999)',
                'genres': 'Action|Sci-Fi|Thriller',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg'
            },
            {
                'movieId': 8,
                'title': 'Interstellar (2014)',
                'genres': 'Adventure|Drama|Sci-Fi',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg'
            },
            {
                'movieId': 9,
                'title': 'Fight Club (1999)',
                'genres': 'Drama|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'
            },
            {
                'movieId': 10,
                'title': 'The Lord of the Rings (2001)',
                'genres': 'Adventure|Fantasy',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg'
            },
            {
                'movieId': 11,
                'title': 'Parasite (2019)',
                'genres': 'Comedy|Drama|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg'
            },
            {
                'movieId': 12,
                'title': 'Avengers: Endgame (2019)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg'
            },
            {
                'movieId': 13,
                'title': 'Joker (2019)',
                'genres': 'Crime|Drama|Thriller',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg'
            },
            {
                'movieId': 14,
                'title': 'Spider-Man: No Way Home (2021)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg'
            },
            {
                'movieId': 15,
                'title': 'Dune (2021)',
                'genres': 'Action|Adventure|Drama|Sci-Fi',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg'
            },
            {
                'movieId': 16,
                'title': 'Everything Everywhere All at Once (2022)',
                'genres': 'Action|Comedy|Sci-Fi',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg'
            },
            {
                'movieId': 17,
                'title': 'The Grand Budapest Hotel (2014)',
                'genres': 'Comedy|Drama',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg'
            },
            {
                'movieId': 18,
                'title': 'Whiplash (2014)',
                'genres': 'Drama|Music',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg'
            },
            {
                'movieId': 19,
                'title': 'Her (2013)',
                'genres': 'Drama|Romance|Sci-Fi',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/eCOtqtfvn7mxGl6nfmq4b1exJRc.jpg'
            },
            {
                'movieId': 20,
                'title': 'La La Land (2016)',
                'genres': 'Comedy|Drama|Musical|Romance',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg'
            },
            {
                'movieId': 21,
                'title': 'Spirited Away (2001)',
                'genres': 'Animation|Adventure|Fantasy',
                'avg_rating': 4.3,
                'poster_url': 'https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg'
            },
            {
                'movieId': 22,
                'title': 'The Silence of the Lambs (1991)',
                'genres': 'Crime|Drama|Thriller',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg'
            },
            {
                'movieId': 23,
                'title': 'Get Out (2017)',
                'genres': 'Horror|Mystery|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg'
            },
            {
                'movieId': 24,
                'title': 'The Prestige (2006)',
                'genres': 'Drama|Mystery|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/bdN3gXuIZYaJP7ftKK2sU0nPtEA.jpg'
            },
            {
                'movieId': 25,
                'title': 'Toy Story (1995)',
                'genres': 'Animation|Comedy|Family',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg'
            },
            {
                'movieId': 26,
                'title': 'The Social Network (2010)',
                'genres': 'Drama',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg'
            },
            {
                'movieId': 27,
                'title': 'Blade Runner 2049 (2017)',
                'genres': 'Sci-Fi|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg'
            },
            {
                'movieId': 28,
                'title': 'Arrival (2016)',
                'genres': 'Drama|Sci-Fi',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg'
            },
            {
                'movieId': 29,
                'title': 'Mad Max: Fury Road (2015)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/hA2ple9q4qnwxp3hKVNhroipsir.jpg'
            },
            {
                'movieId': 30,
                'title': 'The Truman Show (1998)',
                'genres': 'Comedy|Drama|Sci-Fi',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/vuza0WqY239yBXOadKlGwJsZJFE.jpg'
            },
            {
                'movieId': 31,
                'title': 'Coco (2017)',
                'genres': 'Animation|Family|Fantasy',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg'
            },
            {
                'movieId': 32,
                'title': 'A Quiet Place (2018)',
                'genres': 'Drama|Horror|Sci-Fi',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/nAU74GmpUk7t5iklEp3bufwDq4n.jpg'
            },
            {
                'movieId': 33,
                'title': 'Eternal Sunshine of the Spotless Mind (2004)',
                'genres': 'Drama|Romance|Sci-Fi',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg'
            },
            {
                'movieId': 34,
                'title': 'The Wolf of Wall Street (2013)',
                'genres': 'Comedy|Crime|Drama',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/34m2tygAYBGqA9MXKhRDtzYd4MrX.jpg'
            },
            {
                'movieId': 35,
                'title': 'Shutter Island (2010)',
                'genres': 'Drama|Mystery|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/4GDy0PHYX3VRXUtwK5ysFbg3kEx.jpg'
            },
            {
                'movieId': 36,
                'title': 'Knives Out (2019)',
                'genres': 'Comedy|Crime|Mystery',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/pThyQovXQrw2m0s9x82twj48Jq4.jpg'
            },
            {
                'movieId': 37,
                'title': 'The Conjuring (2013)',
                'genres': 'Horror|Mystery|Thriller',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/wVYREutTvI2tmxr6ujrHT704wGF.jpg'
            },
            {
                'movieId': 38,
                'title': 'Hereditary (2018)',
                'genres': 'Drama|Horror|Mystery',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/p4gPDs7MbJa5Wi3TMqbhA76xIVT.jpg'
            },
            {
                'movieId': 39,
                'title': 'The Lighthouse (2019)',
                'genres': 'Drama|Horror|Mystery',
                'avg_rating': 3.5,
                'poster_url': 'https://image.tmdb.org/t/p/w500/3nk9UoepYmv1G9oP18q6JJCeYwN.jpg'
            },
            {
                'movieId': 40,
                'title': 'Soul (2020)',
                'genres': 'Animation|Comedy|Drama|Fantasy',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/hm58Jw4Lw8OIeECIq5qyPYhAeRJ.jpg'
            },
            {
                'movieId': 41,
                'title': 'Gladiator (2000)',
                'genres': 'Action|Adventure|Drama',
                'avg_rating': 4.3,
                'poster_url': 'https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg'
            },
            {
                'movieId': 42,
                'title': 'The Departed (2006)',
                'genres': 'Crime|Drama|Thriller',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq20Qblg61T.jpg'
            },
            {
                'movieId': 43,
                'title': 'Goodfellas (1990)',
                'genres': 'Crime|Drama',
                'avg_rating': 4.3,
                'poster_url': 'https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg'
            },
            {
                'movieId': 44,
                'title': 'Saving Private Ryan (1998)',
                'genres': 'Drama|War',
                'avg_rating': 4.4,
                'poster_url': 'https://image.tmdb.org/t/p/w500/1wY4psJ5NVEhCuOYROwLH2XExM2.jpg'
            },
            {
                'movieId': 45,
                'title': 'Schindler\'s List (1993)',
                'genres': 'Drama|History|War',
                'avg_rating': 4.5,
                'poster_url': 'https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg'
            },
            {
                'movieId': 46,
                'title': 'Se7en (1995)',
                'genres': 'Crime|Drama|Mystery|Thriller',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/6yoghtyTpznpBik8ber3cFSEvlC.jpg'
            },
            {
                'movieId': 47,
                'title': 'The Green Mile (1999)',
                'genres': 'Crime|Drama|Fantasy',
                'avg_rating': 4.3,
                'poster_url': 'https://image.tmdb.org/t/p/w500/velWPhVMQeQKcxggNEU8YmIo52R.jpg'
            },
            {
                'movieId': 48,
                'title': 'Django Unchained (2012)',
                'genres': 'Drama|Western',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/7oWY8VDWW7thTzWh3OKYRkWUlD5.jpg'
            },
            {
                'movieId': 49,
                'title': 'The Lion King (1994)',
                'genres': 'Animation|Adventure|Drama|Family',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg'
            },
            {
                'movieId': 50,
                'title': 'Alien (1979)',
                'genres': 'Horror|Sci-Fi',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/vfrQk5IPloGg1v9Rzbh2Eg3VGyM.jpg'
            },
            {
                'movieId': 51,
                'title': 'Terminator 2: Judgment Day (1991)',
                'genres': 'Action|Sci-Fi',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/5M0j0B18abtBI5gi2RhfjjurTqb.jpg'
            },
            {
                'movieId': 52,
                'title': 'Back to the Future (1985)',
                'genres': 'Adventure|Comedy|Sci-Fi',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg'
            },
            {
                'movieId': 53,
                'title': 'WALL·E (2008)',
                'genres': 'Animation|Family|Sci-Fi',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg'
            },
            {
                'movieId': 54,
                'title': 'Up (2009)',
                'genres': 'Animation|Adventure|Comedy|Family',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/vpbaStTMt8qqXaEgnOR2EE4DNJk.jpg'
            },
            {
                'movieId': 55,
                'title': 'Finding Nemo (2003)',
                'genres': 'Animation|Adventure|Comedy|Family',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/eHuGQ10FUzK1mdOY69wF5pGgEf5.jpg'
            },
            {
                'movieId': 56,
                'title': 'Inside Out (2015)',
                'genres': 'Animation|Comedy|Drama|Family',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg'
            },
            {
                'movieId': 57,
                'title': 'The Incredibles (2004)',
                'genres': 'Action|Animation|Family',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/2LqaLgk4Z226KkgPJuiOQ58wvrm.jpg'
            },
            {
                'movieId': 58,
                'title': 'Ratatouille (2007)',
                'genres': 'Animation|Comedy|Family',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/t3vaWRPSf6WjDSamIkKDs1iQWna.jpg'
            },
            {
                'movieId': 59,
                'title': 'Monsters, Inc. (2001)',
                'genres': 'Animation|Comedy|Family',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/sgheSKxZkttIe8ONsf2sKu62t2X.jpg'
            },
            {
                'movieId': 60,
                'title': 'Jurassic Park (1993)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/oU7Oez2fVVfnpqoHdBSfpKLgb.jpg'
            },
            {
                'movieId': 61,
                'title': 'Avatar (2009)',
                'genres': 'Action|Adventure|Fantasy|Sci-Fi',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg'
            },
            {
                'movieId': 62,
                'title': 'Titanic (1997)',
                'genres': 'Drama|Romance',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg'
            },
            {
                'movieId': 63,
                'title': 'The Avengers (2012)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg'
            },
            {
                'movieId': 64,
                'title': 'Iron Man (2008)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/78lPtwv72eTNqFW9COBYI0dWDJa.jpg'
            },
            {
                'movieId': 65,
                'title': 'Captain America: Civil War (2016)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/rAGiXaUfPzY7CDEyNKUofk3Kw2e.jpg'
            },
            {
                'movieId': 66,
                'title': 'Thor: Ragnarok (2017)',
                'genres': 'Action|Adventure|Comedy',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/rzRwTcFvttcN1ZpX2xv4j3tSdJu.jpg'
            },
            {
                'movieId': 67,
                'title': 'Guardians of the Galaxy (2014)',
                'genres': 'Action|Adventure|Comedy|Sci-Fi',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg'
            },
            {
                'movieId': 68,
                'title': 'Black Panther (2018)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uxzzxijgPIY7slzFvMotPv8wjKA.jpg'
            },
            {
                'movieId': 69,
                'title': 'Doctor Strange (2016)',
                'genres': 'Action|Adventure|Fantasy',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uGBVj3bEbCoZbDjjl9wTxcygko1.jpg'
            },
            {
                'movieId': 70,
                'title': 'Ant-Man (2015)',
                'genres': 'Action|Adventure|Comedy|Sci-Fi',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/rQRnQfUl3kfp78nCWq8Ks04SKW.jpg'
            },
            {
                'movieId': 71,
                'title': 'Logan (2017)',
                'genres': 'Action|Drama|Sci-Fi',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/fnbjcRDYn6YviCcePDnGdyAkYsB.jpg'
            },
            {
                'movieId': 72,
                'title': 'Deadpool (2016)',
                'genres': 'Action|Comedy',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/3E53WEZJqP6aM84D8CckXx4pIHw.jpg'
            },
            {
                'movieId': 73,
                'title': 'X-Men: Days of Future Past (2014)',
                'genres': 'Action|Adventure|Sci-Fi',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/tYfijzolzgoMOtegh1Y7j2Enorg.jpg'
            },
            {
                'movieId': 74,
                'title': 'Wonder Woman (2017)',
                'genres': 'Action|Adventure|Fantasy',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/gfJGlDaHuWimErCr5Ql0I8x9QSy.jpg'
            },
            {
                'movieId': 75,
                'title': 'The Batman (2022)',
                'genres': 'Action|Crime|Drama',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg'
            },
            {
                'movieId': 76,
                'title': 'Aquaman (2018)',
                'genres': 'Action|Adventure|Fantasy',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/xLPffWMhMj1l50ND3KchMjYoKmE.jpg'
            },
            {
                'movieId': 77,
                'title': 'Shazam! (2019)',
                'genres': 'Action|Adventure|Comedy',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/xnopI5Xtky18MPhK40cZAGAOVeV.jpg'
            },
            {
                'movieId': 78,
                'title': 'John Wick (2014)',
                'genres': 'Action|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg'
            },
            {
                'movieId': 79,
                'title': 'John Wick: Chapter 2 (2017)',
                'genres': 'Action|Crime|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/hXWBc0ioZP3cN4zCu6SN3YHXZVO.jpg'
            },
            {
                'movieId': 80,
                'title': 'John Wick: Chapter 3 (2019)',
                'genres': 'Action|Crime|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/ziEuG1essDuWuC5lpWUaw1uXY2O.jpg'
            },
            {
                'movieId': 81,
                'title': 'Mission: Impossible - Fallout (2018)',
                'genres': 'Action|Adventure|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/AkJQpZp9WoNdj7pLYSj1L0RcMMN.jpg'
            },
            {
                'movieId': 82,
                'title': 'Top Gun: Maverick (2022)',
                'genres': 'Action|Drama',
                'avg_rating': 4.2,
                'poster_url': 'https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg'
            },
            {
                'movieId': 83,
                'title': 'The Bourne Identity (2002)',
                'genres': 'Action|Mystery|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/bXQIL36VQdzJ69lcjQR1WQzJqQR.jpg'
            },
            {
                'movieId': 84,
                'title': 'Casino Royale (2006)',
                'genres': 'Action|Adventure|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/l0kWrWoJhPQ0uSRkxJzEb31Jg6D.jpg'
            },
            {
                'movieId': 85,
                'title': 'Skyfall (2012)',
                'genres': 'Action|Adventure|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/nrtHvN0ZHMW96xKvNrfTYmr7XK.jpg'
            },
            {
                'movieId': 86,
                'title': 'No Time to Die (2021)',
                'genres': 'Action|Adventure|Thriller',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/iUgygt3fscRoKWCV1d0C7FbM9TP.jpg'
            },
            {
                'movieId': 87,
                'title': 'Fast & Furious 7 (2015)',
                'genres': 'Action|Crime|Thriller',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/dCgm7efXDmiABSdvR4PwlgkZ7Td.jpg'
            },
            {
                'movieId': 88,
                'title': 'The Hangover (2009)',
                'genres': 'Comedy',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uluhlXubGu1VxU63X9VHCLWDAYP.jpg'
            },
            {
                'movieId': 89,
                'title': 'Superbad (2007)',
                'genres': 'Comedy',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/ek8e8txUyUwd2BNqj6lFEerJfbq.jpg'
            },
            {
                'movieId': 90,
                'title': 'Step Brothers (2008)',
                'genres': 'Comedy',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/yXqUxI0qguKaMRs6UlMFMQ5l4dN.jpg'
            },
            {
                'movieId': 91,
                'title': 'Bridesmaids (2011)',
                'genres': 'Comedy|Romance',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/8uXFGH0kPRgQp1UupJ6mVqKWb2O.jpg'
            },
            {
                'movieId': 92,
                'title': 'The 40-Year-Old Virgin (2005)',
                'genres': 'Comedy|Romance',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/mVeoqL37gMEgkSD9NlqdNsWgTb.jpg'
            },
            {
                'movieId': 93,
                'title': 'Zombieland (2009)',
                'genres': 'Comedy|Horror',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/dUzaKja1pGL9qiHlmVTfPKLbk9V.jpg'
            },
            {
                'movieId': 94,
                'title': 'Shaun of the Dead (2004)',
                'genres': 'Comedy|Horror',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/lq87fTPOPvETv3qAYcHTEpmWQKV.jpg'
            },
            {
                'movieId': 95,
                'title': 'Hot Fuzz (2007)',
                'genres': 'Action|Comedy|Mystery',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/zPib4ukTSdXvHP9pxGkFCe34fl3.jpg'
            },
            {
                'movieId': 96,
                'title': 'Scott Pilgrim vs. the World (2010)',
                'genres': 'Action|Comedy|Romance',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/g5IoYeudx9XBEfwNL0fHvSckLBz.jpg'
            },
            {
                'movieId': 97,
                'title': 'The Notebook (2004)',
                'genres': 'Drama|Romance',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/rNzQyW4f8B8cQeg7Dgj3n6eT5k9.jpg'
            },
            {
                'movieId': 98,
                'title': 'Pride & Prejudice (2005)',
                'genres': 'Drama|Romance',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/l5HwfTN3VXEhk7X5x7jHDI3Nvmm.jpg'
            },
            {
                'movieId': 99,
                'title': 'Crazy Rich Asians (2018)',
                'genres': 'Comedy|Drama|Romance',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/1XxL4LJ5WHdrcYcihEZUCgNCpAW.jpg'
            },
            {
                'movieId': 100,
                'title': 'The Fault in Our Stars (2014)',
                'genres': 'Drama|Romance',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/qU8Q3FVQK66Y0h3QnW4Ak9pX4kE.jpg'
            },
            {
                'movieId': 101,
                'title': 'A Star Is Born (2018)',
                'genres': 'Drama|Music|Romance',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/wrFpXMNBRj2PBiN4Z5kix51XaIZ.jpg'
            },
            {
                'movieId': 102,
                'title': 'Bohemian Rhapsody (2018)',
                'genres': 'Drama|Music',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/lHu1wtNaczFPGFDTrjCSzeLPTKN.jpg'
            },
            {
                'movieId': 103,
                'title': 'The Greatest Showman (2017)',
                'genres': 'Drama|Musical',
                'avg_rating': 3.8,
                'poster_url': 'https://image.tmdb.org/t/p/w500/b9CeobiihCx1uG1tpw8hXmpi7nm.jpg'
            },
            {
                'movieId': 104,
                'title': 'Mamma Mia! (2008)',
                'genres': 'Comedy|Musical|Romance',
                'avg_rating': 3.5,
                'poster_url': 'https://image.tmdb.org/t/p/w500/qCkknHNWXQ8ClxrPJMOI6Pk45yB.jpg'
            },
            {
                'movieId': 105,
                'title': 'Sing Street (2016)',
                'genres': 'Comedy|Drama|Music|Romance',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/ik0BT1t0UxG5KJbGr0j8IKB4LLm.jpg'
            },
            {
                'movieId': 106,
                'title': 'It (2017)',
                'genres': 'Horror|Thriller',
                'avg_rating': 3.7,
                'poster_url': 'https://image.tmdb.org/t/p/w500/9E2y5Q7WlCVNEhP5GiVTjhEhx1o.jpg'
            },
            {
                'movieId': 107,
                'title': 'The Exorcist (1973)',
                'genres': 'Horror',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/4ucLGcXVVSVnsfkGtbLY4XAius8.jpg'
            },
            {
                'movieId': 108,
                'title': 'The Shining (1980)',
                'genres': 'Drama|Horror',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/nRj5511mZdTl4saWEPoj9QroTIu.jpg'
            },
            {
                'movieId': 109,
                'title': 'Psycho (1960)',
                'genres': 'Horror|Mystery|Thriller',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/yz4QVqPx3h1hD1DfqqQkCq3rmxW.jpg'
            },
            {
                'movieId': 110,
                'title': 'Midsommar (2019)',
                'genres': 'Drama|Horror|Mystery',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/7LEI8ulZzO5gy9Ww2NVCrKmHeDt.jpg'
            },
            {
                'movieId': 111,
                'title': 'Us (2019)',
                'genres': 'Horror|Thriller',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/ux2dU1jQ2ACIMShzB3yP93Udpzc.jpg'
            },
            {
                'movieId': 112,
                'title': 'Train to Busan (2016)',
                'genres': 'Action|Horror|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/9kz6s4It1C95PotqbldIE5O0yaX.jpg'
            },
            {
                'movieId': 113,
                'title': 'The Witch (2015)',
                'genres': 'Drama|Horror|Mystery',
                'avg_rating': 3.6,
                'poster_url': 'https://image.tmdb.org/t/p/w500/zap5hGUKmJcLqVtX4RmCzN46M0K.jpg'
            },
            {
                'movieId': 114,
                'title': 'Gone Girl (2014)',
                'genres': 'Drama|Mystery|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/lv5xShBIDPe7m4ufdlV1lZqjlhE.jpg'
            },
            {
                'movieId': 115,
                'title': 'Zodiac (2007)',
                'genres': 'Crime|Drama|Mystery|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/eGFf7Wr6cDWiLpNFnGfKo8tbEJ.jpg'
            },
            {
                'movieId': 116,
                'title': 'Prisoners (2013)',
                'genres': 'Crime|Drama|Mystery|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uhvJKGFn1wqkcvJlnPt6SPhRkW4.jpg'
            },
            {
                'movieId': 117,
                'title': 'Sicario (2015)',
                'genres': 'Action|Crime|Drama|Thriller',
                'avg_rating': 3.9,
                'poster_url': 'https://image.tmdb.org/t/p/w500/ufbqN8lCFjnWVwLt40S0Ls6H7yl.jpg'
            },
            {
                'movieId': 118,
                'title': 'Nightcrawler (2014)',
                'genres': 'Crime|Drama|Thriller',
                'avg_rating': 4.0,
                'poster_url': 'https://image.tmdb.org/t/p/w500/j9HrX8f7GbZQm1BrBiR40uFQaoV.jpg'
            },
            {
                'movieId': 119,
                'title': 'No Country for Old Men (2007)',
                'genres': 'Crime|Drama|Thriller',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/6d5XOczc226jECq1GMfSP7Zwmpu.jpg'
            },
            {
                'movieId': 120,
                'title': 'There Will Be Blood (2007)',
                'genres': 'Drama',
                'avg_rating': 4.1,
                'poster_url': 'https://image.tmdb.org/t/p/w500/fa0RDkAlCec0STeMNAhPaF89q6U.jpg'
            },
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


# Global dataset instance
# Use MongoDB movies if enabled, otherwise use local sample data
if USE_MONGODB_MOVIES:
    try:
        from utils.mongodb_movies import MongoMovieDataset
        dataset = MongoMovieDataset(limit=500)
        print("[Recommender] Using MongoDB sample_mflix movies")
    except Exception as e:
        print(f"[Recommender] MongoDB failed ({e}), using local data")
        dataset = MovieDataset()
else:
    dataset = MovieDataset()
    print("[Recommender] Using local sample data")


def extract_genre_preferences(rated_movies_dict):
    """
    Extract genre preferences from user's rated movies.

    Args:
        rated_movies_dict: {movie_id: rating} dictionary

    Returns:
        Dictionary of {genre: preference_score}
    """
    genre_scores = {}

    if not rated_movies_dict:
        return genre_scores

    for movie_id, rating in rated_movies_dict.items():
        # Support both string and int movie IDs
        movie = dataset.get_movie_by_id(movie_id)
        if not movie:
            continue

        genres = movie.get('genres', '').split('|')

        # Weight by rating (5★ = 1.0, 1★ = 0.2)
        weight = float(rating) / 5.0

        for genre in genres:
            genre = genre.strip()
            if genre:
                genre_scores[genre] = genre_scores.get(genre, 0) + weight

    return genre_scores


def score_movie_by_preference(movie, genre_preferences, variant='control'):
    """
    Score a movie based on genre preferences and variant type.

    Args:
        movie: Movie dictionary
        genre_preferences: Genre preference scores from extract_genre_preferences()
        variant: 'control' or 'treatment'

    Returns:
        Float score (0.0 to 1.0)
    """
    if not genre_preferences:
        # No preferences yet - use default scoring
        if variant == 'treatment':
            return movie.get('avg_rating', 3.0) / 5.0
        else:
            return random.random()

    # Calculate genre match score
    genre_match_score = 0
    movie_genres = movie.get('genres', '').split('|')

    for genre in movie_genres:
        genre = genre.strip()
        genre_match_score += genre_preferences.get(genre, 0)

    # Normalize (max score ~5.0 if all genres match highly)
    genre_match_score = min(genre_match_score / 5.0, 1.0)

    # Combine with popularity
    popularity_score = movie.get('avg_rating', 3.0) / 5.0

    if variant == 'treatment':
        # LightGCN: More weight on genre matching (60%) + popularity (40%)
        return (genre_match_score * 0.6) + (popularity_score * 0.4)
    else:
        # Matrix Factorization: Less weight on genre matching (30%) + randomness (70%)
        return (genre_match_score * 0.3) + (random.random() * 0.7)


def get_control_recommendations(user_id, n=12, rated_movies=None):
    """
    Control: Matrix Factorization (with pseudo-personalization if user has ratings)

    Args:
        user_id: User identifier
        n: Number of recommendations
        rated_movies: Dictionary of {movie_id: rating} for personalization

    Returns:
        List of movie dictionaries
    """
    all_movies = dataset.get_all_movies()

    # Filter out already-rated movies
    if rated_movies:
        rated_ids = set(int(mid) for mid in rated_movies.keys())
        candidates = [m for m in all_movies if m['movieId'] not in rated_ids]

        # Extract genre preferences
        genre_prefs = extract_genre_preferences(rated_movies)

        # Score movies with slight genre bias
        for movie in candidates:
            movie['_score'] = score_movie_by_preference(movie, genre_prefs, variant='control')

        # Sort by score and return top N
        candidates.sort(key=lambda m: m['_score'], reverse=True)
        result = candidates[:n]

        # Clean up temporary score field
        for m in result:
            m.pop('_score', None)

        return result
    else:
        # No ratings yet - pure random
        return random.sample(all_movies, min(n, len(all_movies)))


def get_treatment_recommendations(user_id, n=12, rated_movies=None):
    """
    Treatment: LightGCN (with genre personalization)

    Args:
        user_id: User identifier
        n: Number of recommendations
        rated_movies: Dictionary of {movie_id: rating} for personalization

    Returns:
        List of movie dictionaries
    """
    all_movies = dataset.get_all_movies()

    # Filter out already-rated movies
    if rated_movies:
        rated_ids = set(int(mid) for mid in rated_movies.keys())
        candidates = [m for m in all_movies if m['movieId'] not in rated_ids]

        # Extract genre preferences
        genre_prefs = extract_genre_preferences(rated_movies)

        # Score movies with genre + popularity
        for movie in candidates:
            movie['_score'] = score_movie_by_preference(movie, genre_prefs, variant='treatment')

        # Sort by score and return top N
        candidates.sort(key=lambda m: m['_score'], reverse=True)
        result = candidates[:n]

        # Clean up temporary score field
        for m in result:
            m.pop('_score', None)

        return result
    else:
        # No ratings yet - pure popularity
        movies = dataset.movies.copy()
        if 'avg_rating' in movies.columns:
            movies = movies.sort_values('avg_rating', ascending=False)
        return movies.head(n).to_dict('records')


def get_recommendations(user_id, variant, n=12, rated_movies=None):
    """
    Get recommendations based on assigned variant (with personalization)

    Args:
        user_id: User identifier
        variant: 'control' or 'treatment'
        n: Number of recommendations
        rated_movies: Dictionary of {movie_id: rating} for personalization

    Returns:
        List of movie dictionaries
    """
    if variant == 'treatment':
        return get_treatment_recommendations(user_id, n, rated_movies)
    else:
        return get_control_recommendations(user_id, n, rated_movies)
