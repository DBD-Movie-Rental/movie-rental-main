from .base_repository import MongoBaseRepository
from .odm_models.genre_document import GenreDocument


class GenreRepositoryMongo(MongoBaseRepository[GenreDocument]):
    def __init__(self) -> None:
        super().__init__(GenreDocument, id_field="genre_id")
