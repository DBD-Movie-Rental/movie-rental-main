from .base_repository import MongoBaseRepository
from .odm_models.movie_document import Movie


class MovieRepositoryMongo(MongoBaseRepository[Movie]):
    def __init__(self) -> None:
        super().__init__(Movie, id_field="movie_id")
