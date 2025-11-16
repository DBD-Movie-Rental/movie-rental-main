from sqlalchemy import Column, Integer, SmallInteger, ForeignKey
from .base import Base


class InventoryItem(Base):
    __tablename__ = "inventory_item"

    inventory_item_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("location.location_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    format_id = Column(Integer, ForeignKey("format.format_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movie.movie_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(SmallInteger, nullable=False, default=1)

    def to_dict(self):
        return {
            "id": self.inventory_item_id,
            "location_id": self.location_id,
            "format_id": self.format_id,
            "movie_id": self.movie_id,
            "status": self.status,
        }
