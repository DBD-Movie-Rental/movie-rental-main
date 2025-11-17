from .base_repository import MongoBaseRepository
from .odm_models.movie_document import Movie


class MovieRepositoryMongo(MongoBaseRepository[Movie]):
    def __init__(self) -> None:
        super().__init__(Movie, id_field="movie_id")

    def get_details(self, item_id: int) -> dict | None:
        movie = self.model.objects(movie_id=item_id).first()
        if movie:
            return movie.to_detailed_dict()
        return None
    
    def get_all_details(self) -> list[dict]:
        return [m.to_detailed_dict() for m in self.model.objects()]