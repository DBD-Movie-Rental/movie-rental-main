from sqlalchemy import Column, Integer, SmallInteger, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Review(Base):
    __tablename__ = "review"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    rating = Column(SmallInteger, nullable=True)  # CHECK 1..10 in DB
    body = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    movie_id = Column(Integer, ForeignKey("movie.movie_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.review_id,
            "rating": self.rating,
            "body": self.body,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "movie_id": self.movie_id,
        }
