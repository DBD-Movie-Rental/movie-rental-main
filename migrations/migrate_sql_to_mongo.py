import time
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from src.repositories.mysql.orm_models.customer_orm import (
    SessionLocal,
    Customer as SqlCustomer,
)
from src.repositories.mongodb.connection import init_mongo
from src.repositories.mongodb.odm_models.customer_document import (
    Customer as MongoCustomer,
    Address,
    MembershipPlan,
)


def get_mysql_session_with_retry(retries: int = 10, delay_seconds: int = 3):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            session = SessionLocal()
            session.execute(text("SELECT 1"))
            return session
        except OperationalError as e:
            last_error = e
            print(
                f"[MySQL] Connection attempt {attempt}/{retries} failed: {e}. "
                f"Retrying in {delay_seconds}s..."
            )
            time.sleep(delay_seconds)
        except Exception as e:
            last_error = e
            print(
                f"[MySQL] Non-operational error on attempt {attempt}/{retries}: {e}. "
                f"Retrying in {delay_seconds}s..."
            )
            time.sleep(delay_seconds)

    raise RuntimeError(f"Could not connect to MySQL after {retries} attempts") from last_error


def migrate_customers():
    # 1) Init Mongo connection (default alias)
    init_mongo()

    # 1b) Reset customers collection so migration is repeatable in dev
    MongoCustomer.drop_collection()

    # 2) Get MySQL session (with retry)
    session = get_mysql_session_with_retry()

    try:
        customers = session.query(SqlCustomer).all()
        print(f"Found {len(customers)} customers in MySQL")

        for c in customers:
            # --- address: pick the first address row for this customer ---
            addr_row = session.execute(
                text(
                    """
                    SELECT address_id, address, city, post_code
                    FROM address
                    WHERE customer_id = :cid
                    ORDER BY address_id
                    LIMIT 1
                    """
                ),
                {"cid": c.customer_id},
            ).fetchone()

            if not addr_row:
                raise RuntimeError(
                    f"No address found for customer_id={c.customer_id}"
                )

            address_embedded = Address(
                address_id=addr_row.address_id,
                address=addr_row.address,
                city=addr_row.city,
                post_code=addr_row.post_code,
            )

            # --- membership plan + membership type (GOLD/SILVER/BRONZE) ---
            mp_row = session.execute(
                text(
                    """
                    SELECT
                        mp.membership_plan_id,
                        mp.monthly_cost,
                        mp.starts_on,
                        mp.ends_on,
                        mp.membership_id,
                        m.membership AS membership_type
                    FROM membership_plan AS mp
                    JOIN membership AS m
                      ON mp.membership_id = m.membership_id
                    WHERE mp.customer_id = :cid
                    LIMIT 1
                    """
                ),
                {"cid": c.customer_id},
            ).fetchone()

            if not mp_row:
                raise RuntimeError(
                    f"No membership_plan found for customer_id={c.customer_id}"
                )

            membership_plan_embedded = MembershipPlan(
                membership_plan_id=mp_row.membership_plan_id,
                membership_type=mp_row.membership_type,
                starts_on=mp_row.starts_on,
                ends_on=mp_row.ends_on,
                monthly_cost_dkk=mp_row.monthly_cost,
                membership_id=mp_row.membership_id,
            )

            # --- create Mongo Customer document ---
            doc = MongoCustomer(
                customer_id=c.customer_id,
                first_name=c.first_name,
                last_name=c.last_name,
                email=c.email,
                phone_number=c.phone_number,
                created_at=c.created_at or datetime.utcnow(),
                address=address_embedded,
                membership_plan=membership_plan_embedded,
            )

            doc.save()

        print("Customer migration completed.")

    finally:
        session.close()


if __name__ == "__main__":
    print("Starting customer migration from MySQL to MongoDB...")
    migrate_customers()
    print("Migration finished.")
