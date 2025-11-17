from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    StringField,
    DateTimeField,
    ListField,
)


class ReviewEmbedded(EmbeddedDocument):
    review_id = IntField(required=True, db_field="reviewId")
    movie_id = IntField(required=True, db_field="movieId")
    rating = IntField(required=True, min_value=1, max_value=10, db_field="rating")
    body = StringField(db_field="body")
    created_at = DateTimeField(required=True, db_field="createdAt")
    customer_id = IntField(db_field="customerId")  # optional link


class Movie(Document):
    meta = {
        "collection": "movies",
        "auto_create_index": False,
    }

    movie_id = IntField(required=True, unique=True, db_field="movieId")
    title = StringField(required=True, db_field="title")
    release_year = IntField(db_field="releaseYear")
    runtime_min = IntField(db_field="runtimeMin")
    rating = IntField(min_value=1, max_value=10, db_field="rating")
    summary = StringField(db_field="summary")

    # denormalized list of genre names
    genres = ListField(StringField(), db_field="genres")

    reviews = EmbeddedDocumentListField(ReviewEmbedded, db_field="reviews")

    def to_dict(self) -> dict:
        return {
            "id": self.movie_id,
            "title": self.title,
            "release_year": self.release_year,
            "runtime_min": self.runtime_min,
            "rating": self.rating,
            "summary": self.summary,
            "genres": self.genres,
        }

    def to_detailed_dict(self) -> dict:
        payload = self.to_dict()
        payload["reviews"] = [
            {
                "review_id": review.review_id,
                "movie_id": review.movie_id,
                "rating": review.rating,
                "body": review.body,
                "created_at": review.created_at.isoformat()
                if review.created_at
                else None,
                "customer_id": review.customer_id,
            }
            for review in self.reviews
        ]
        return payload
    