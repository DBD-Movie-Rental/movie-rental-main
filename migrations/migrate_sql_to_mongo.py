from src.repositories.mysql.orm_models.customer_orm import SessionLocal, Customer as SqlCustomer
from src.repositories.mongodb.connection import init_mongo
from src.repositories.mongodb.odm_models.customer_document import Customer as MongoCustomer
from datetime import datetime

def migrate_customers():
    init_mongo()
    session = SessionLocal()

    for c in session.query(SqlCustomer).all():
        doc = MongoCustomer(
            customer_id=c.customer_id,
            first_name=c.first_name,
            last_name=c.last_name,
            email=c.email,
            phone_number=c.phone_number,
            created_at=c.created_at or datetime.utcnow(),
        )
        doc.save()

    session.close()

if __name__ == "__main__":
    print("Starting customer migration from MySQL to MongoDB...")
    migrate_customers()
    print("Customer migration completed.")
