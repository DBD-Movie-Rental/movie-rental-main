import time
from datetime import datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# MySQL ORM imports
from src.repositories.mysql.orm_models.base import SessionLocal
from src.repositories.mysql.orm_models.customer_orm import Customer as SqlCustomer
from src.repositories.mysql.orm_models.movie_orm import Movie as SqlMovie
from src.repositories.mysql.orm_models.review_orm import Review as SqlReview
from src.repositories.mysql.orm_models.genre_orm import Genre as SqlGenre
from src.repositories.mysql.orm_models.format_orm import Format as SqlFormat
from src.repositories.mysql.orm_models.location_orm import Location as SqlLocation
from src.repositories.mysql.orm_models.inventory_item_orm import (
    InventoryItem as SqlInventoryItem,
)
from src.repositories.mysql.orm_models.employee_orm import Employee as SqlEmployee
from src.repositories.mysql.orm_models.fee_orm import Fee as SqlFee
from src.repositories.mysql.orm_models.membership_orm import (
    Membership as SqlMembership,
)
from src.repositories.mysql.orm_models.promo_code_orm import (
    PromoCode as SqlPromoCode,
)
from src.repositories.mysql.orm_models.rental_orm import Rental as SqlRental
from src.repositories.mysql.orm_models.payment_orm import Payment as SqlPayment

# Mongo connection + ODM imports
from src.repositories.mongodb.connection import init_mongo
from src.repositories.mongodb.odm_models.customer_document import (
    Customer as MongoCustomer,
    Address as MongoAddress,
    MembershipPlan as MongoMembershipPlan,
)
from src.repositories.mongodb.odm_models.movie_document import (
    Movie as MongoMovie,
    ReviewEmbedded as MongoReviewEmbedded,
)
from src.repositories.mongodb.odm_models.location_document import (
    Location as MongoLocation,
    EmployeeEmbedded as MongoEmployeeEmbedded,
    InventoryItemEmbedded as MongoInventoryEmbedded,
)
from src.repositories.mongodb.odm_models.genre_document import (
    GenreDocument as MongoGenre,
)
from src.repositories.mongodb.odm_models.format_document import (
    FormatDocument as MongoFormat,
)
from src.repositories.mongodb.odm_models.fee_type_document import (
    FeeTypeDocument as MongoFeeType,
)
from src.repositories.mongodb.odm_models.membership_type_document import (
    MembershipTypeDocument as MongoMembershipType,
)
from src.repositories.mongodb.odm_models.promo_code_document import (
    PromoCodeDocument as MongoPromoCode,
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


def migrate_customers(session):
    """Migrate customers with their primary address and current membership plan."""
    MongoCustomer.drop_collection()

    customers = session.query(SqlCustomer).all()
    print(f"[customers] Found {len(customers)} in MySQL")

    for c in customers:
        # address: pick first address row for this customer
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

        address_embedded = MongoAddress(
            address_id=addr_row.address_id,
            address=addr_row.address,
            city=addr_row.city,
            post_code=addr_row.post_code,
        )

        # membership plan + membership type
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
            membership_plan_embedded = MongoMembershipPlan(
                membership_plan_id=c.customer_id,  # fallback ID
                membership_type="BRONZE",
                starts_on=datetime.utcnow(),
                ends_on=None,
                monthly_cost_dkk=0.0,
                membership_id=3,  # Assuming 3=BRONZE
            )
        else:
            membership_plan_embedded = MongoMembershipPlan(
                membership_plan_id=mp_row.membership_plan_id,
                membership_type=mp_row.membership_type,
                starts_on=mp_row.starts_on,
                ends_on=mp_row.ends_on,
                monthly_cost_dkk=mp_row.monthly_cost,
                membership_id=mp_row.membership_id,
            )

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

    print("[customers] Migration completed.")


def migrate_membership_types(session):
    """Migrate membership types (lookup)."""
    MongoMembershipType.drop_collection()
    rows = session.query(SqlMembership).all()
    print(f"[membershipTypes] Found {len(rows)} in MySQL")
    for r in rows:
        MongoMembershipType(membership_id=r.membership_id, type=r.membership).save()
    print("[membershipTypes] Migration completed.")


def migrate_formats(session):
    """Migrate formats (lookup)."""
    MongoFormat.drop_collection()
    rows = session.query(SqlFormat).all()
    print(f"[formats] Found {len(rows)} in MySQL")
    for r in rows:
        MongoFormat(format_id=r.format_id, type=r.format).save()
    print("[formats] Migration completed.")


def migrate_genres(session):
    """Migrate genres (lookup)."""
    MongoGenre.drop_collection()
    rows = session.query(SqlGenre).all()
    print(f"[genres] Found {len(rows)} in MySQL")
    for r in rows:
        MongoGenre(genre_id=r.genre_id, name=r.name).save()
    print("[genres] Migration completed.")


def migrate_fee_types(session):
    """Migrate fee types (lookup)."""
    MongoFeeType.drop_collection()
    rows = session.query(SqlFee).all()
    print(f"[feeTypes] Found {len(rows)} in MySQL")
    for r in rows:
        # ensure Decimal type for Decimal128Field
        amt = r.amount_dkk if isinstance(r.amount_dkk, Decimal) else Decimal(str(r.amount_dkk))
        MongoFeeType(
            fee_id=r.fee_id,
            fee_type=r.fee_type,
            default_amount_dkk=amt,
        ).save()
    print("[feeTypes] Migration completed.")


def migrate_promo_codes(session):
    """Migrate promo codes (lookup)."""
    MongoPromoCode.drop_collection()
    rows = session.query(SqlPromoCode).all()
    print(f"[promoCodes] Found {len(rows)} in MySQL")
    for r in rows:
        percent = None if r.percent_off is None else (r.percent_off if isinstance(r.percent_off, Decimal) else Decimal(str(r.percent_off)))
        amount = None if r.amount_off_dkk is None else (r.amount_off_dkk if isinstance(r.amount_off_dkk, Decimal) else Decimal(str(r.amount_off_dkk)))
        MongoPromoCode(
            promo_code_id=r.promo_code_id,
            code=r.code,
            description=r.description,
            percent_off=percent,
            amount_off_dkk=amount,
            starts_at=r.starts_at,
            ends_at=r.ends_at,
        ).save()
    print("[promoCodes] Migration completed.")


def migrate_movies(session):
    """Migrate movies with denormalized genres and embedded reviews."""
    MongoMovie.drop_collection()
    movies = session.query(SqlMovie).all()
    print(f"[movies] Found {len(movies)} in MySQL")

    for m in movies:
        # genres via movie_genre join
        genre_rows = session.execute(
            text(
                """
                SELECT g.name
                FROM movie_genre mg
                JOIN genre g ON g.genre_id = mg.genre_id
                WHERE mg.movie_id = :mid
                ORDER BY g.name
                """
            ),
            {"mid": m.movie_id},
        ).fetchall()
        genres = [gr.name for gr in genre_rows]

        # embedded reviews
        reviews = (
            session.query(SqlReview)
            .filter(SqlReview.movie_id == m.movie_id)
            .all()
        )
        review_embeds = []
        for rv in reviews:
            review_embeds.append(
                MongoReviewEmbedded(
                    review_id=rv.review_id,
                    movie_id=rv.movie_id,
                    rating=int(rv.rating) if rv.rating is not None else 0,
                    body=rv.body,
                    created_at=rv.created_at or datetime.utcnow(),
                    customer_id=None,  # not present in SQL schema
                )
            )

        # Convert average rating (Decimal) to int within 1..10 if present
        avg_rating = None
        if m.rating is not None:
            try:
                avg_rating = max(1, min(10, int(round(float(m.rating)))))
            except Exception:
                avg_rating = None

        MongoMovie(
            movie_id=m.movie_id,
            title=m.title,
            release_year=m.release_year,
            runtime_min=m.runtime_min,
            rating=avg_rating,
            summary=m.summary,
            genres=genres,
            reviews=review_embeds,
        ).save()

    print("[movies] Migration completed.")


def _status_code_to_string(code: int) -> str:
    # Fallback mapping for inventory_item.status -> string label
    mapping = {
        0: "UNKNOWN",
        1: "AVAILABLE",
        2: "RENTED",
        3: "RESERVED",
    }
    return mapping.get(int(code) if code is not None else 0, "UNKNOWN")


def migrate_locations(session):
    """Migrate locations with embedded employees and inventory items."""
    MongoLocation.drop_collection()

    # employees are not linked to locations in SQL; embed all employees in each location
    employees = session.query(SqlEmployee).all()
    employee_embeds = [
        MongoEmployeeEmbedded(
            employee_id=e.employee_id,
            first_name=e.first_name,
            last_name=e.last_name,
            phone_number=e.phone_number,
            email=e.email,
            is_active=bool(e.is_active),
        )
        for e in employees
    ]

    locations = session.query(SqlLocation).all()
    print(f"[locations] Found {len(locations)} in MySQL")

    for loc in locations:
        # inventory for this location
        inventory_rows = (
            session.query(SqlInventoryItem)
            .filter(SqlInventoryItem.location_id == loc.location_id)
            .all()
        )
        inv_embeds = [
            MongoInventoryEmbedded(
                inventory_item_id=ii.inventory_item_id,
                movie_id=ii.movie_id,
                format_id=ii.format_id,
                status=_status_code_to_string(ii.status),
            )
            for ii in inventory_rows
        ]

        MongoLocation(
            location_id=loc.location_id,
            address=loc.address,
            city=loc.city,
            employees=employee_embeds,
            inventory=inv_embeds,
        ).save()

    print("[locations] Migration completed.")


def migrate_rentals(session):
    """Migrate rentals with embedded items, payments, fees, and promo snapshot."""
    MongoRental = None  # lazy import to avoid circular if any
    from src.repositories.mongodb.odm_models.rental_document import (
        Rental as _MongoRental,
        RentalItemEmbedded as _MongoRentalItem,
        PaymentEmbedded as _MongoPayment,
        RentalFeeEmbedded as _MongoRentalFee,
        FeeSnapshotEmbedded as _MongoFeeSnapshot,
        PromoSnapshotEmbedded as _MongoPromoSnapshot,
    )

    MongoRental = _MongoRental

    MongoRental.drop_collection()

    rentals = session.query(SqlRental).all()
    print(f"[rentals] Found {len(rentals)} in MySQL")

    for r in rentals:
        # derive location_id from first rental_item -> inventory_item
        loc_row = session.execute(
            text(
                """
                SELECT ii.location_id
                FROM rental_item ri
                JOIN inventory_item ii ON ii.inventory_item_id = ri.inventory_item_id
                WHERE ri.rental_id = :rid
                ORDER BY ri.rental_item_id
                LIMIT 1
                """
            ),
            {"rid": r.rental_id},
        ).fetchone()
        location_id = loc_row.location_id if loc_row else None

        # items: join rental_item -> inventory_item for details
        item_rows = session.execute(
            text(
                """
                SELECT ri.rental_item_id, ri.inventory_item_id, ii.movie_id, ii.format_id
                FROM rental_item ri
                JOIN inventory_item ii ON ii.inventory_item_id = ri.inventory_item_id
                WHERE ri.rental_id = :rid
                ORDER BY ri.rental_item_id
                """
            ),
            {"rid": r.rental_id},
        ).fetchall()
        item_embeds = [
            _MongoRentalItem(
                rental_item_id=it.rental_item_id,
                inventory_item_id=it.inventory_item_id,
                movie_id=it.movie_id,
                format_id=it.format_id,
            )
            for it in item_rows
        ]

        # payments
        payments = (
            session.query(SqlPayment)
            .filter(SqlPayment.rental_id == r.rental_id)
            .all()
        )
        pay_embeds = [
            _MongoPayment(
                payment_id=p.payment_id,
                amount_dkk=p.amount_dkk if isinstance(p.amount_dkk, Decimal) else Decimal(str(p.amount_dkk)),
                created_at=p.created_at or datetime.utcnow(),
            )
            for p in payments
        ]

        # fees with snapshot
        fee_rows = session.execute(
            text(
                """
                SELECT rf.rental_fee_id, rf.fee_id, f.fee_type, f.amount_dkk
                FROM rental_fee rf
                JOIN fee f ON f.fee_id = rf.fee_id
                WHERE rf.rental_id = :rid
                ORDER BY rf.rental_fee_id
                """
            ),
            {"rid": r.rental_id},
        ).fetchall()
        fee_embeds = []
        for fr in fee_rows:
            snapshot = _MongoFeeSnapshot(
                fee_type=fr.fee_type,
                default_amount_dkk=fr.amount_dkk if isinstance(fr.amount_dkk, Decimal) else Decimal(str(fr.amount_dkk)),
            )
            fee_embeds.append(
                _MongoRentalFee(
                    rental_fee_id=fr.rental_fee_id,
                    fee_id=fr.fee_id,
                    amount_dkk=snapshot.default_amount_dkk,
                    snapshot=snapshot,
                )
            )

        # promo snapshot (optional)
        promo_embed = None
        if r.promo_code_id is not None:
            promo = session.get(SqlPromoCode, r.promo_code_id)
            if promo:
                promo_embed = _MongoPromoSnapshot(
                    promo_code_id=promo.promo_code_id,
                    code=promo.code,
                    percent_off=None if promo.percent_off is None else (promo.percent_off if isinstance(promo.percent_off, Decimal) else Decimal(str(promo.percent_off))),
                    amount_off_dkk=None if promo.amount_off_dkk is None else (promo.amount_off_dkk if isinstance(promo.amount_off_dkk, Decimal) else Decimal(str(promo.amount_off_dkk))),
                    starts_at=promo.starts_at,
                    ends_at=promo.ends_at,
                )

        MongoRental(
            rental_id=r.rental_id,
            customer_id=r.customer_id,
            location_id=location_id,
            employee_id=r.employee_id,
            status=r.status,
            rented_at=r.rented_at_datetime,
            returned_at=r.returned_at_datetime,
            due_at=r.due_at_datetime,
            reserved_at=r.reserved_at_datetime,
            items=item_embeds,
            payments=pay_embeds,
            fees=fee_embeds,
            promo=promo_embed,
        ).save()

    print("[rentals] Migration completed.")


def migrate_all():
    """Run all migrations in a dependency-safe order."""
    # 1) Init Mongo connection
    init_mongo()

    # 2) MySQL session with retry
    session = get_mysql_session_with_retry()

    try:
        # lookups first
        migrate_membership_types(session)
        migrate_formats(session)
        migrate_genres(session)
        migrate_fee_types(session)
        migrate_promo_codes(session)

        # main entities
        migrate_movies(session)
        migrate_locations(session)
        migrate_customers(session)
        migrate_rentals(session)
    finally:
        session.close()


if __name__ == "__main__":
    print("Starting full migration from MySQL to MongoDB...")
    migrate_all()
    print("Migration finished.")
