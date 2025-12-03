from typing import Any, Dict, List, Optional
from datetime import datetime
from src.repositories.mongodb.odm_models.movie_document import Movie, ReviewEmbedded

class ReviewRepositoryMongo:
    def get_all(self) -> List[Dict[str, Any]]:
        movies = Movie.objects()
        reviews = []
        for m in movies:
            for r in m.reviews:
                d = r.to_dict()
                d["movie_id"] = m.movie_id
                reviews.append(d)
        return reviews

    def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
        m = Movie.objects(reviews__review_id=id_).first()
        if not m:
            return None
        for r in m.reviews:
            if r.review_id == id_:
                d = r.to_dict()
                d["movie_id"] = m.movie_id
                return d
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        movie_id = data.get("movie_id")
        if not movie_id:
            raise ValueError("movie_id is required to create a review")
        
        m = Movie.objects(movie_id=movie_id).first()
        if not m:
            raise ValueError(f"Movie {movie_id} not found")

        max_id = 0
        all_movies = Movie.objects()
        for mov in all_movies:
            for r in mov.reviews:
                if r.review_id > max_id:
                    max_id = r.review_id
        new_id = max_id + 1

        new_review = ReviewEmbedded(
            review_id=new_id,
            movie_id=movie_id,
            rating=data.get("rating"),
            body=data.get("body"),
            created_at=datetime.utcnow(),
            customer_id=data.get("customer_id")
        )
        
        m.reviews.append(new_review)
        m.save()
        
        return new_review.to_dict()

    def update(self, id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        m = Movie.objects(reviews__review_id=id_).first()
        if not m:
            return None
        
        target_r = None
        for r in m.reviews:
            if r.review_id == id_:
                target_r = r
                break
        
        if not target_r:
            return None

        if "rating" in data: target_r.rating = data["rating"]
        if "body" in data: target_r.body = data["body"]
        if "customer_id" in data: target_r.customer_id = data["customer_id"]

        m.save()
        
        return target_r.to_dict()

    def delete(self, id_: int) -> bool:
        m = Movie.objects(reviews__review_id=id_).first()
        if not m:
            return False
        
        original_len = len(m.reviews)
        m.reviews = [r for r in m.reviews if r.review_id != id_]
        
        if len(m.reviews) < original_len:
            m.save()
            return True
        return False
