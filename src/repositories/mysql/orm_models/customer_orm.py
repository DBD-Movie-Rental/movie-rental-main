from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()
engine = create_engine("mysql+pymysql://app:app@127.0.0.1:3307/movie_rental", pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp()) 

    def to_dict(self):
        return {
            "id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
