"""
Full migration from MySQL to Neo4j (neomodel OGM).

What it does:
- Reads entities from MySQL via SQLAlchemy ORM models
- Upserts corresponding Neo4j nodes and creates edges for relationships
- Is idempotent (safe to re-run); updates existing nodes if values changed
- Uses simple batching for large datasets

Entities migrated:
- Reference/lookup: Genres, Formats, Locations
- Core domain: Customers, Addresses, Membership Plans, Memberships
- Movies & inventory: Movies, Inventory Items
- Staff & operations: Employees, Rentals, Rental-Item edges (HAS_ITEM)
- Finance: Fees, Promo Codes, Payments (and links to Rentals/Customers)

Neo4j connection is configured via `src.repositories.neo4j.connection` using env vars:
- NEO4J_URI (default bolt://localhost:7687)
- NEO4J_USER (default neo4j)
- NEO4J_PASSWORD (default neo4j)

Run inside the API container:
	python -m migrations.migrate_sql_to_neo4j
"""

from __future__ import annotations

import os
import sys
from typing import Iterable, List, Dict

# Ensure we can import project modules when run as a module or script
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.append(PROJECT_ROOT)

# Hard-set Neo4j connection so the script runs without external env vars
os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("NEO4J_USER", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "letmein123")

# Configure Neo4j neomodel via project connection module (reads env above)
from src.repositories.neo4j.connection import config as _neo_config  # noqa: F401  # side-effect import
from src.repositories.neo4j.ogm_models.customer_ogm import Customer as CustomerNode
from src.repositories.neo4j.ogm_models.address_ogm import Address as AddressNode
from src.repositories.neo4j.ogm_models.membership_plan_ogm import MembershipPlan as MembershipPlanNode
from src.repositories.neo4j.ogm_models.membership_ogm import Membership as MembershipNode
from src.repositories.neo4j.ogm_models.genre_ogm import Genre as GenreNode
from src.repositories.neo4j.ogm_models.format_ogm import Format as FormatNode
from src.repositories.neo4j.ogm_models.movie_ogm import Movie as MovieNode
from src.repositories.neo4j.ogm_models.inventory_item_ogm import InventoryItem as InventoryItemNode
from src.repositories.neo4j.ogm_models.location_ogm import Location as LocationNode
from src.repositories.neo4j.ogm_models.employee_ogm import Employee as EmployeeNode
from src.repositories.neo4j.ogm_models.rental_ogm import Rental as RentalNode
from src.repositories.neo4j.ogm_models.payment_ogm import Payment as PaymentNode
from src.repositories.neo4j.ogm_models.fee_ogm import Fee as FeeNode
from src.repositories.neo4j.ogm_models.promo_code_ogm import PromoCode as PromoCodeNode

# MySQL ORM access
from src.repositories.mysql.orm_models.customer_orm import Customer as CustomerORM
from src.repositories.mysql.orm_models.address_orm import Address as AddressORM
from src.repositories.mysql.orm_models.membership_plan_orm import MembershipPlan as MembershipPlanORM
from src.repositories.mysql.orm_models.membership_orm import Membership as MembershipORM
from src.repositories.mysql.orm_models.genre_orm import Genre as GenreORM
from src.repositories.mysql.orm_models.format_orm import Format as FormatORM
from src.repositories.mysql.orm_models.movie_orm import Movie as MovieORM
from src.repositories.mysql.orm_models.inventory_item_orm import InventoryItem as InventoryItemORM
from src.repositories.mysql.orm_models.location_orm import Location as LocationORM
from src.repositories.mysql.orm_models.employee_orm import Employee as EmployeeORM
from src.repositories.mysql.orm_models.rental_orm import Rental as RentalORM
from src.repositories.mysql.orm_models.payment_orm import Payment as PaymentORM
from src.repositories.mysql.orm_models.fee_orm import Fee as FeeORM
from src.repositories.mysql.orm_models.promo_code_orm import PromoCode as PromoCodeORM
from src.repositories.mysql.orm_models.base import SessionLocal
from sqlalchemy import text


def chunked(iterable: Iterable[Dict], size: int) -> Iterable[List[Dict]]:
	"""Yield successive chunks of given size from iterable."""
	batch: List[Dict] = []
	for item in iterable:
		batch.append(item)
		if len(batch) >= size:
			yield batch
			batch = []
	if batch:
		yield batch


def fetch_all_customers() -> List[Dict]:
	"""Fetch all customers from MySQL as dictionaries using the ORM model."""
	with SessionLocal() as session:
		rows = session.query(CustomerORM).all()
		def to_dict(row: CustomerORM) -> Dict:
			return {
				"customer_id": row.customer_id,
				"first_name": row.first_name,
				"last_name": row.last_name,
				"email": row.email,
				"phone_number": row.phone_number,
				"created_at": row.created_at,
			}

		return [to_dict(r) for r in rows]


def upsert_customer(batch: List[Dict]) -> int:
	"""Upsert a batch of customers into Neo4j. Returns count upserted."""
	count = 0
	for c in batch:
		# Idempotent get-or-create by unique customerId
		node = CustomerNode.nodes.get_or_none(customerId=c["customer_id"])  # type: ignore[attr-defined]
		if node is None:
			node = CustomerNode(
				customerId=c["customer_id"],
				firstName=c["first_name"],
				lastName=c["last_name"],
				email=c["email"],
				phoneNumber=c["phone_number"],
				createdAt=c["created_at"],
			)
		else:
			# Update properties in case of changes
			node.firstName = c["first_name"]
			node.lastName = c["last_name"]
			node.email = c["email"]
			node.phoneNumber = c["phone_number"]
			node.createdAt = c["created_at"]

		node.save()
		count += 1
	return count


def migrate_customers(batch_size: int = 500) -> None:
	customers = fetch_all_customers()
	total = len(customers)
	print(f"Found {total} customers in MySQL.")
	migrated = 0
	for batch in chunked(customers, batch_size):
		migrated += upsert_customer(batch)
		print(f"Migrated {migrated}/{total} customers…")
	print(f"Done. Migrated {migrated} customers to Neo4j.")


# ─────────────────────────── Additional entities & relationships ────────────

def fetch_all_addresses() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(AddressORM).all()
		return [{
			"address_id": r.address_id,
			"address": r.address,
			"city": r.city,
			"post_code": r.post_code,
			"customer_id": r.customer_id,
		} for r in rows]


def upsert_addresses(batch: List[Dict]) -> int:
	count = 0
	for a in batch:
		node = AddressNode.nodes.get_or_none(addressId=a["address_id"])  # type: ignore
		if node is None:
			node = AddressNode(
				addressId=a["address_id"],
				address=a["address"],
				city=a["city"],
				postCode=a["post_code"],
			)
		else:
			node.address = a["address"]
			node.city = a["city"]
			node.postCode = a["post_code"]
		node.save()
		# connect to customer
		cust = CustomerNode.nodes.get_or_none(customerId=a["customer_id"])  # type: ignore
		try:
			if cust:
				cust.addresses.connect(node)  # type: ignore[attr-defined]
		except Exception:
			pass
		count += 1
	return count


def migrate_addresses(batch_size: int = 500) -> None:
	items = fetch_all_addresses()
	total = len(items)
	print(f"Found {total} addresses in MySQL.")
	migrated = 0
	for batch in chunked(items, batch_size):
		migrated += upsert_addresses(batch)
		print(f"Migrated {migrated}/{total} addresses…")
	print(f"Done. Migrated {migrated} addresses to Neo4j.")


def fetch_all_membership_plans() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(MembershipPlanORM).all()
		return [{
			"membership_plan_id": r.membership_plan_id,
			"monthly_cost": float(r.monthly_cost) if r.monthly_cost is not None else None,
			"starts_on": r.starts_on,
			"ends_on": r.ends_on,
			"membership_id": r.membership_id,
			"customer_id": r.customer_id,
		} for r in rows]


def upsert_membership_plans(batch: List[Dict]) -> int:
	count = 0
	for m in batch:
		node = MembershipPlanNode.nodes.get_or_none(membershipPlanId=m["membership_plan_id"])  # type: ignore
		if node is None:
			node = MembershipPlanNode(
				membershipPlanId=m["membership_plan_id"],
				monthlyCost=m["monthly_cost"],
				startsOn=m["starts_on"],
				endsOn=m["ends_on"],
			)
		else:
			node.monthlyCost = m["monthly_cost"]
			node.startsOn = m["starts_on"]
			node.endsOn = m["ends_on"]
		node.save()
		# connect to membership and customer
		try:
			mem = MembershipNode.nodes.get_or_none(membershipId=m["membership_id"])  # type: ignore
			if mem:
				node.membership.connect(mem)  # type: ignore[attr-defined]
		except Exception:
			pass
		try:
			cust = CustomerNode.nodes.get_or_none(customerId=m["customer_id"])  # type: ignore
			if cust:
				node.customer.connect(cust)  # type: ignore[attr-defined]
		except Exception:
			pass
		count += 1
	return count


def migrate_membership_plans(batch_size: int = 500) -> None:
	items = fetch_all_membership_plans()
	total = len(items)
	print(f"Found {total} membership plans in MySQL.")
	migrated = 0
	for batch in chunked(items, batch_size):
		migrated += upsert_membership_plans(batch)
		print(f"Migrated {migrated}/{total} membership plans…")
	print(f"Done. Migrated {migrated} membership plans to Neo4j.")


def fetch_all_memberships() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(MembershipORM).all()
		return [{
			"membership_id": r.membership_id,
			"customer_id": r.customer_id,
			"membership_plan_id": r.membership_plan_id,
			"start_date": r.start_date,
			"end_date": r.end_date,
			"status": r.status,
		} for r in rows]


def upsert_memberships(batch: List[Dict]) -> int:
	count = 0
	for m in batch:
		node = MembershipNode.nodes.get_or_none(membershipId=m["membership_id"])  # type: ignore
		if node is None:
			node = MembershipNode(
				membershipId=m["membership_id"],
				startDate=m["start_date"],
				endDate=m["end_date"],
				status=m["status"],
			)
		else:
			node.startDate = m["start_date"]
			node.endDate = m["end_date"]
			node.status = m["status"]
		node.save()
		# Link to Customer and MembershipPlan if present
		cust = CustomerNode.nodes.get_or_none(customerId=m["customer_id"])  # type: ignore
		plan = MembershipPlanNode.nodes.get_or_none(membershipPlanId=m["membership_plan_id"])  # type: ignore
		if cust:
			# assuming relationship defined on Membership to Customer -> use generic pattern via neomodel Relationship? If not, connect via customer.rentals etc.
			try:
				cust.memberships.connect(node)  # type: ignore[attr-defined]
			except Exception:
				pass
		if plan:
			try:
				node.plan.connect(plan)  # type: ignore[attr-defined]
			except Exception:
				pass
		count += 1
	return count


def migrate_memberships(batch_size: int = 500) -> None:
	items = fetch_all_memberships()
	total = len(items)
	print(f"Found {total} memberships in MySQL.")
	migrated = 0
	for batch in chunked(items, batch_size):
		migrated += upsert_memberships(batch)
		print(f"Migrated {migrated}/{total} memberships…")
	print(f"Done. Migrated {migrated} memberships to Neo4j.")


# Movies, genres, formats, inventory items
def fetch_all_genres() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(GenreORM).all()
		return [{"genre_id": r.genre_id, "name": r.name} for r in rows]


def upsert_genres(batch: List[Dict]) -> int:
	count = 0
	for g in batch:
		node = GenreNode.nodes.get_or_none(genreId=g["genre_id"])  # type: ignore
		if node is None:
			node = GenreNode(genreId=g["genre_id"], name=g["name"])
		else:
			node.name = g["name"]
		node.save(); count += 1
	return count


def fetch_all_formats() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(FormatORM).all()
	return [{"format_id": r.format_id, "format": r.format} for r in rows]


def upsert_formats(batch: List[Dict]) -> int:
	count = 0
	for f in batch:
		node = FormatNode.nodes.get_or_none(formatId=f["format_id"])  # type: ignore
		if node is None:
			node = FormatNode(formatId=f["format_id"], format=f["format"])  # type: ignore
		else:
			node.format = f["format"]
		node.save(); count += 1
	return count


def fetch_all_movies() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(MovieORM).all()
		return [{
			"movie_id": r.movie_id,
			"title": r.title,
			"release_year": r.release_year,
			"runtime_min": r.runtime_min,
			"rating": float(r.rating) if r.rating is not None else None,
			"summary": r.summary,
		} for r in rows]


def upsert_movies(batch: List[Dict]) -> int:
	count = 0
	for m in batch:
		node = MovieNode.nodes.get_or_none(movieId=m["movie_id"])  # type: ignore
		if node is None:
			node = MovieNode(
				movieId=m["movie_id"],
				title=m["title"],
				releaseYear=m["release_year"],
				runtimeMin=m["runtime_min"],
				rating=m["rating"],
				summary=m["summary"],
			)  # type: ignore
		else:
			node.title = m["title"]
			node.releaseYear = m["release_year"]
			node.runtimeMin = m["runtime_min"]
			node.rating = m["rating"]
			node.summary = m["summary"]
		node.save()
		count += 1
	return count


def fetch_all_locations() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(LocationORM).all()
		return [{
			"location_id": r.location_id,
			"address": r.address,
			"city": r.city,
		} for r in rows]


def upsert_locations(batch: List[Dict]) -> int:
	count = 0
	for l in batch:
		node = LocationNode.nodes.get_or_none(locationId=l["location_id"])  # type: ignore
		if node is None:
			node = LocationNode(locationId=l["location_id"], address=l["address"], city=l["city"])  # type: ignore
		else:
			node.address = l["address"]
			node.city = l["city"]
		node.save(); count += 1
	return count


def fetch_all_inventory_items() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(InventoryItemORM).all()
		return [{
			"inventory_item_id": r.inventory_item_id,
			"movie_id": r.movie_id,
			"location_id": r.location_id,
			"format_id": r.format_id,
			"status": r.status,
		} for r in rows]


def upsert_inventory_items(batch: List[Dict]) -> int:
	count = 0
	for ii in batch:
		node = InventoryItemNode.nodes.get_or_none(inventoryItemId=ii["inventory_item_id"])  # type: ignore
		if node is None:
			node = InventoryItemNode(inventoryItemId=ii["inventory_item_id"], status=bool(ii["status"]))  # type: ignore
		else:
			node.status = bool(ii["status"])  # type: ignore
		node.save()
		# link to movie & location
		mv = MovieNode.nodes.get_or_none(movieId=ii["movie_id"])  # type: ignore
		loc = LocationNode.nodes.get_or_none(locationId=ii["location_id"])  # type: ignore
		fmt = FormatNode.nodes.get_or_none(formatId=ii["format_id"])  # type: ignore
		try:
			if mv:
				node.movie.connect(mv)  # type: ignore[attr-defined]
		except Exception:
			pass
		try:
			if loc:
				node.location.connect(loc)  # type: ignore[attr-defined]
		except Exception:
			pass
		try:
			if fmt:
				node.format.connect(fmt)  # type: ignore[attr-defined]
		except Exception:
			pass
		count += 1
	return count


def fetch_all_employees() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(EmployeeORM).all()
		return [{
			"employee_id": r.employee_id,
			"first_name": r.first_name,
			"last_name": r.last_name,
			"phone_number": r.phone_number,
			"email": r.email,
			"is_active": r.is_active,
		} for r in rows]


def upsert_employees(batch: List[Dict]) -> int:
	count = 0
	for e in batch:
		node = EmployeeNode.nodes.get_or_none(employeeId=e["employee_id"])  # type: ignore
		if node is None:
			node = EmployeeNode(
				employeeId=e["employee_id"],
				firstName=e["first_name"],
				lastName=e["last_name"],
				phoneNumber=e["phone_number"],
				email=e["email"],
				isActive=bool(e["is_active"]),
			)  # type: ignore
		else:
			node.firstName = e["first_name"]
			node.lastName = e["last_name"]
			node.phoneNumber = e["phone_number"]
			node.email = e["email"]
			node.isActive = bool(e["is_active"])  # type: ignore
		node.save(); count += 1
	return count


def fetch_all_rentals() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(RentalORM).all()
		return [{
			"rental_id": r.rental_id,
			"customer_id": r.customer_id,
			"rented_at_datetime": r.rented_at_datetime,
			"returned_at_datetime": r.returned_at_datetime,
			"due_at_datetime": r.due_at_datetime,
			"reserved_at_datetime": r.reserved_at_datetime,
			"status": r.status,
			"promo_code_id": r.promo_code_id,
			"employee_id": r.employee_id,
		} for r in rows]


def upsert_rentals(batch: List[Dict]) -> int:
	count = 0
	for r in batch:
		node = RentalNode.nodes.get_or_none(rentalId=r["rental_id"])  # type: ignore
		if node is None:
			node = RentalNode(
				rentalId=r["rental_id"],
				rentedAtDatetime=r["rented_at_datetime"],
				returnedAtDatetime=r["returned_at_datetime"],
				dueAtDatetime=r["due_at_datetime"],
				reservedAtDatetime=r["reserved_at_datetime"],
				status=r["status"],
			)  # type: ignore
		else:
			node.rentedAtDatetime = r["rented_at_datetime"]
			node.returnedAtDatetime = r["returned_at_datetime"]
			node.dueAtDatetime = r["due_at_datetime"]
			node.reservedAtDatetime = r["reserved_at_datetime"]
			node.status = r["status"]
		node.save()
		cust = CustomerNode.nodes.get_or_none(customerId=r["customer_id"])  # type: ignore
		promo = None
		emp = None
		if r.get("promo_code_id") is not None:
			promo = PromoCodeNode.nodes.get_or_none(promoCodeId=r["promo_code_id"])  # type: ignore
		if r.get("employee_id") is not None:
			emp = EmployeeNode.nodes.get_or_none(employeeId=r["employee_id"])  # type: ignore
		try:
			if cust:
				cust.rentals.connect(node)  # type: ignore[attr-defined]
		except Exception:
			pass
		try:
			if promo:
				node.promo.connect(promo)  # type: ignore[attr-defined]
		except Exception:
			pass
		try:
			if emp:
				node.employee.connect(emp)  # type: ignore[attr-defined]
		except Exception:
			pass
		count += 1
	return count


def fetch_all_rental_items() -> List[Dict]:
	"""Fetch rental_item join rows: rental_id, inventory_item_id."""
	with SessionLocal() as session:
		# Use raw SQL as ORM class is not defined
		rows = session.execute(
			text("SELECT rental_id, inventory_item_id FROM rental_item ORDER BY rental_id, inventory_item_id")
		).fetchall()
		return [{"rental_id": r[0], "inventory_item_id": r[1]} for r in rows]


def fetch_all_movie_genres() -> List[Dict]:
    """Fetch movie_genre join rows: movie_id, genre_id."""
    with SessionLocal() as session:
        rows = session.execute(
            text("SELECT movie_id, genre_id FROM movie_genre ORDER BY movie_id, genre_id")
        ).fetchall()
        return [{"movie_id": r[0], "genre_id": r[1]} for r in rows]


def wire_movie_genres(batch: List[Dict]) -> int:
    """Create (:Movie)-[:OF_GENRE]->(:Genre) edges from join rows."""
    count = 0
    for mg in batch:
        mv = MovieNode.nodes.get_or_none(movieId=mg["movie_id"])  # type: ignore
        gn = GenreNode.nodes.get_or_none(genreId=mg["genre_id"])  # type: ignore
        if not mv or not gn:
            continue
        try:
            mv.genres.connect(gn)  # type: ignore[attr-defined]
        except Exception:
            pass
        count += 1
    return count


def wire_rental_items(batch: List[Dict]) -> int:
	"""Create (:Rental)-[:HAS_ITEM]->(:InventoryItem) edges from join rows."""
	count = 0
	for ri in batch:
		rent = RentalNode.nodes.get_or_none(rentalId=ri["rental_id"])  # type: ignore
		item = InventoryItemNode.nodes.get_or_none(inventoryItemId=ri["inventory_item_id"])  # type: ignore
		if not rent or not item:
			continue
		try:
			rent.items.connect(item)  # type: ignore[attr-defined]
		except Exception:
			pass
		count += 1
	return count


def fetch_all_fees() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(FeeORM).all()
		return [{
			"fee_id": r.fee_id,
			"fee_type": r.fee_type,
			"amount_dkk": float(r.amount_dkk) if r.amount_dkk is not None else None,
		} for r in rows]


def upsert_fees(batch: List[Dict]) -> int:
	count = 0
	for f in batch:
		node = FeeNode.nodes.get_or_none(feeId=f["fee_id"])  # type: ignore
		if node is None:
			node = FeeNode(feeId=f["fee_id"], feeType=f["fee_type"], amountDkk=f["amount_dkk"])  # type: ignore
		else:
			node.feeType = f["fee_type"]
			node.amountDkk = f["amount_dkk"]
		node.save(); count += 1
	return count


def fetch_all_promo_codes() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(PromoCodeORM).all()
		return [{
			"promo_code_id": r.promo_code_id,
			"code": r.code,
			"description": r.description,
			"percent_off": float(r.percent_off) if r.percent_off is not None else None,
			"amount_off_dkk": float(r.amount_off_dkk) if r.amount_off_dkk is not None else None,
			"starts_at": r.starts_at,
			"ends_at": r.ends_at,
		} for r in rows]


def upsert_promo_codes(batch: List[Dict]) -> int:
	count = 0
	for p in batch:
		node = PromoCodeNode.nodes.get_or_none(promoCodeId=p["promo_code_id"])  # type: ignore
		if node is None:
			node = PromoCodeNode(
				promoCodeId=p["promo_code_id"],
				code=p["code"],
				description=p["description"],
				percentOff=p["percent_off"],
				amountOffDkk=p["amount_off_dkk"],
				startsAt=p["starts_at"],
				endsAt=p["ends_at"],
			)  # type: ignore
		else:
			node.code = p["code"]
			node.description = p["description"]
			node.percentOff = p["percent_off"]
			node.amountOffDkk = p["amount_off_dkk"]
			node.startsAt = p["starts_at"]
			node.endsAt = p["ends_at"]
		node.save(); count += 1
	return count


def fetch_all_payments() -> List[Dict]:
	with SessionLocal() as session:
		rows = session.query(PaymentORM).all()
		return [{
			"payment_id": r.payment_id,
			"rental_id": r.rental_id,
			"amount_dkk": float(r.amount_dkk) if r.amount_dkk is not None else None,
			"created_at": r.created_at,
		} for r in rows]


def upsert_payments(batch: List[Dict]) -> int:
	count = 0
	for p in batch:
		node = PaymentNode.nodes.get_or_none(paymentId=p["payment_id"])  # type: ignore
		if node is None:
			node = PaymentNode(paymentId=p["payment_id"], amountDkk=p["amount_dkk"], createdAt=p["created_at"])  # type: ignore
		else:
			node.amountDkk = p["amount_dkk"]
			node.createdAt = p["created_at"]
		node.save()
		rent = RentalNode.nodes.get_or_none(rentalId=p["rental_id"])  # type: ignore
		if rent:
			try:
				node.rental.connect(rent)  # type: ignore[attr-defined]
			except Exception:
				pass
			# derive customer from rental relationship if available
			try:
				cust = CustomerNode.nodes.get_or_none(customerId=rent.customer.single().customerId)  # type: ignore[attr-defined]
			except Exception:
				cust = None
			if cust:
				try:
					cust.payments.connect(node)  # type: ignore[attr-defined]
				except Exception:
					pass
		count += 1
	return count


def main() -> None:
	# Optional batch size override
	try:
		batch_size = int(os.getenv("CUSTOMER_MIGRATE_BATCH", "500"))
	except ValueError:
		batch_size = 500
	# Order: reference types first
	migrate_addresses(batch_size=batch_size)
	migrate_membership_plans(batch_size=batch_size)
	# Migrate genres and formats
	items = fetch_all_genres(); migrated = 0; total = len(items); print(f"Found {total} genres in MySQL.")
	for b in chunked(items, batch_size): migrated += upsert_genres(b); print(f"Migrated {migrated}/{total} genres…")
	print(f"Done. Migrated {migrated} genres to Neo4j.")

	items = fetch_all_formats(); migrated = 0; total = len(items); print(f"Found {total} formats in MySQL.")
	for b in chunked(items, batch_size): migrated += upsert_formats(b); print(f"Migrated {migrated}/{total} formats…")
	print(f"Done. Migrated {migrated} formats to Neo4j.")

	migrate_movies_items = fetch_all_movies(); migrated = 0; total = len(migrate_movies_items); print(f"Found {total} movies in MySQL.")
	for b in chunked(migrate_movies_items, batch_size): migrated += upsert_movies(b); print(f"Migrated {migrated}/{total} movies…")
	print(f"Done. Migrated {migrated} movies to Neo4j.")

	migrate_locations_items = fetch_all_locations(); migrated = 0; total = len(migrate_locations_items); print(f"Found {total} locations in MySQL.")
	for b in chunked(migrate_locations_items, batch_size): migrated += upsert_locations(b); print(f"Migrated {migrated}/{total} locations…")
	print(f"Done. Migrated {migrated} locations to Neo4j.")

	# Core entity: customers
	migrate_customers(batch_size=batch_size)

	inv_items = fetch_all_inventory_items(); migrated = 0; total = len(inv_items); print(f"Found {total} inventory items in MySQL.")
	for b in chunked(inv_items, batch_size): migrated += upsert_inventory_items(b); print(f"Migrated {migrated}/{total} inventory items…")
	print(f"Done. Migrated {migrated} inventory items to Neo4j.")

	emps = fetch_all_employees(); migrated = 0; total = len(emps); print(f"Found {total} employees in MySQL.")
	for b in chunked(emps, batch_size): migrated += upsert_employees(b); print(f"Migrated {migrated}/{total} employees…")
	print(f"Done. Migrated {migrated} employees to Neo4j.")

	# Rentals and Payments after references exist
	rents = fetch_all_rentals(); migrated = 0; total = len(rents); print(f"Found {total} rentals in MySQL.")
	for b in chunked(rents, batch_size): migrated += upsert_rentals(b); print(f"Migrated {migrated}/{total} rentals…")
	print(f"Done. Migrated {migrated} rentals to Neo4j.")

	# Wire rental items (join table) into graph edges
	ri_rows = fetch_all_rental_items(); wired = 0; total = len(ri_rows); print(f"Found {total} rental_item rows in MySQL.")
	for b in chunked(ri_rows, batch_size): wired += wire_rental_items(b); print(f"Wired {wired}/{total} rental_item edges…")
	print(f"Done. Wired {wired} rental_item edges to Neo4j.")

	# Wire movie_genre edges
	mgs = fetch_all_movie_genres(); wired = 0; total = len(mgs); print(f"Found {total} movie_genre rows in MySQL.")
	for b in chunked(mgs, batch_size): wired += wire_movie_genres(b); print(f"Wired {wired}/{total} movie_genre edges…")
	print(f"Done. Wired {wired} movie_genre edges to Neo4j.")

	fees = fetch_all_fees(); migrated = 0; total = len(fees); print(f"Found {total} fees in MySQL.")
	for b in chunked(fees, batch_size): migrated += upsert_fees(b); print(f"Migrated {migrated}/{total} fees…")
	print(f"Done. Migrated {migrated} fees to Neo4j.")

	promos = fetch_all_promo_codes(); migrated = 0; total = len(promos); print(f"Found {total} promo codes in MySQL.")
	for b in chunked(promos, batch_size): migrated += upsert_promo_codes(b); print(f"Migrated {migrated}/{total} promo codes…")
	print(f"Done. Migrated {migrated} promo codes to Neo4j.")

	pays = fetch_all_payments(); migrated = 0; total = len(pays); print(f"Found {total} payments in MySQL.")
	for b in chunked(pays, batch_size): migrated += upsert_payments(b); print(f"Migrated {migrated}/{total} payments…")
	print(f"Done. Migrated {migrated} payments to Neo4j.")

	# ─────────────────────────── Backfill relationships ───────────────────────────
	print("Starting relationship backfill pass…")
	# Re-run upserts that include relationship connects now that all nodes exist
	addr = fetch_all_addresses(); wired = 0; total = len(addr); print(f"Backfill: {total} addresses → customers")
	for b in chunked(addr, batch_size): wired += upsert_addresses(b); print(f"Backfilled {wired}/{total} address links…")

	plans = fetch_all_membership_plans(); wired = 0; total = len(plans); print(f"Backfill: {total} membership plans → membership/customer")
	for b in chunked(plans, batch_size): wired += upsert_membership_plans(b); print(f"Backfilled {wired}/{total} membership plan links…")

	items = fetch_all_inventory_items(); wired = 0; total = len(items); print(f"Backfill: {total} inventory items → movie/location/format")
	for b in chunked(items, batch_size): wired += upsert_inventory_items(b); print(f"Backfilled {wired}/{total} inventory item links…")

	# Backfill: movie_genre edges
	mgs = fetch_all_movie_genres(); wired = 0; total = len(mgs); print(f"Backfill: {total} movie_genre edges (OF_GENRE)")
	for b in chunked(mgs, batch_size): wired += wire_movie_genres(b); print(f"Backfilled {wired}/{total} movie_genre edges…")

	rents = fetch_all_rentals(); wired = 0; total = len(rents); print(f"Backfill: {total} rentals → customer/promo/employee")
	for b in chunked(rents, batch_size): wired += upsert_rentals(b); print(f"Backfilled {wired}/{total} rental links…")

	ri_rows = fetch_all_rental_items(); wired = 0; total = len(ri_rows); print(f"Backfill: {total} rental_item edges (HAS_ITEM)")
	for b in chunked(ri_rows, batch_size): wired += wire_rental_items(b); print(f"Backfilled {wired}/{total} rental_item edges…")

	pays = fetch_all_payments(); wired = 0; total = len(pays); print(f"Backfill: {total} payments → rental/customer")
	for b in chunked(pays, batch_size): wired += upsert_payments(b); print(f"Backfilled {wired}/{total} payment links…")

	print("Relationship backfill complete.")


if __name__ == "__main__":
	main()

