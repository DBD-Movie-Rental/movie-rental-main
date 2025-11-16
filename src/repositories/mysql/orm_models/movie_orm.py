from sqlalchemy import Column, Integer, String, SmallInteger, DECIMAL, Text
from .base import Base


class Movie(Base):
    __tablename__ = "movie"

    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    release_year = Column(Integer, nullable=False)  # YEAR
    runtime_min = Column(SmallInteger, nullable=False)
    rating = Column(DECIMAL(3, 1), nullable=True)
    summary = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.movie_id,
            "title": self.title,
            "release_year": self.release_year,
            "runtime_min": self.runtime_min,
            "rating": float(self.rating) if self.rating is not None else None,
            "summary": self.summary,
        }
