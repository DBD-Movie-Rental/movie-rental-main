from mongoengine import Document, IntField, StringField


class GenreDocument(Document):
    meta = {
        "collection": "genres",
        "auto_create_index": False,
    }

    genre_id = IntField(required=True, unique=True, db_field="genreId")
    name = StringField(required=True, db_field="name")

    def to_dict(self) -> dict:
        return {
            "id": self.genre_id,
            "name": self.name,
        }