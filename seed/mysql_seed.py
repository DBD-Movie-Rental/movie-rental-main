"""
MySQL seeding script.

Run this from the project root, for example:

    python -m seed.mysql_seed

This script assumes:

- The MySQL schema is already created (e.g. via 001_movie_rental_create.sql).
- Stored procedures (add_customer_with_address, create_rental, create_reservation)
  are already present (004_movie_rental_stored_procedures.sql).
- Optional base data may have been inserted by 999_movie_rental_insert_data.sql,
  but this script is designed to be safe to run on a fresh schema as well.

It will:

1. Seed static lookup tables (format, membership, fee, some genres).
2. Seed employees from employees.csv.
3. Seed customers (and their addresses) from customers.csv via CustomerRepository.
4. Seed locations from locations.csv.
5. Seed movies + movie_genre from movies.csv.
6. Seed promo codes from promo_codes.csv (optional).
7. Seed inventory_item rows (copies of movies at each location in each format).
8. Seed a handful of rentals and reservations via RentalRepository, using the
   stored procedures create_rental and create_reservation.
"""

from __future__ import annotations

import random
from typing import Optional

from sqlalchemy import text

from src.repositories.mysql.customer_repository import CustomerRepository
from src.repositories.mysql.rental_repository import RentalRepository

from .mysql_seed_helpers import get_session, load_csv, load_lines


# ─────────────────────────────────────────────────────────────────────────────
# Static lookups
# ─────────────────────────────────────────────────────────────────────────────

def seed_static_lookups() -> None:
    """Seed format, membership, fee, and some base genres.

    This uses INSERT ... ON DUPLICATE KEY UPDATE so it is safe to run multiple
    times without breaking unique constraints.
    """
    session = get_session()
    try:
        # Formats
        session.execute(
            text(
                """
                INSERT INTO format (format) VALUES
                ('DVD'), ('BLU-RAY'), ('VHS')
                ON DUPLICATE KEY UPDATE format = VALUES(format)
                """
            )
        )

        # Memberships
        session.execute(
            text(
                """
                INSERT INTO membership (membership) VALUES
                ('GOLD'), ('SILVER'), ('BRONZE')
                ON DUPLICATE KEY UPDATE membership = VALUES(membership)
                """
            )
        )

        # Fees
        session.execute(
            text(
                """
                INSERT INTO fee (fee_type, amount_dkk) VALUES
                ('LATE', 25.00),
                ('DAMAGED', 100.00),
                ('OTHER', 50.00)
                ON DUPLICATE KEY UPDATE amount_dkk = VALUES(amount_dkk)
                """
            )
        )

        # Some common genres; movies.csv may add more
        session.execute(
            text(
                """
                INSERT INTO genre (name) VALUES
                ('Action'), ('Comedy'), ('Drama'), ('Horror'), ('Sci-Fi')
                ON DUPLICATE KEY UPDATE name = VALUES(name)
                """
            )
        )

        session.commit()
        print("[seed] Static lookups seeded.")
    finally:
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Employees
# ─────────────────────────────────────────────────────────────────────────────

def seed_employees() -> None:
    """Seed employees from employees.csv if present.

    Expected columns in employees.csv:

        first_name,last_name,email,phone_number

    Example row:

        Eva,Eriksen,eva@example.com,55555555
    """
    try:
        rows = load_csv("employees.csv")
    except FileNotFoundError:
        print("[seed] employees.csv not found, skipping employees.")
        return

    if not rows:
        print("[seed] employees.csv is empty, skipping employees.")
        return

    session = get_session()
    try:
        for row in rows:
            session.execute(
                text(
                    """
                    INSERT INTO employee (first_name, last_name, email, phone_number, is_active)
                    VALUES (:first_name, :last_name, :email, :phone_number, 1)
                    ON DUPLICATE KEY UPDATE
                        first_name = VALUES(first_name),
                        last_name = VALUES(last_name),
                        phone_number = VALUES(phone_number),
                        is_active = VALUES(is_active)
                    """
                ),
                {
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "phone_number": row["phone_number"],
                },
            )
        session.commit()
        print(f"[seed] Seeded {len(rows)} employees.")
    finally:
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Customers (via repository + stored procedure)
# ─────────────────────────────────────────────────────────────────────────────

def seed_customers() -> None:
    """Seed customers from customers.csv using CustomerRepository.create().

    This will call the stored procedure add_customer_with_address() under the hood.

    Expected columns in customers.csv:

        first_name,last_name,email,phone_number,address,city,post_code

    Example row:

        Alice,Andersen,alice@example.com,11111111,Testvej 1,Copenhagen,2100
    """
    try:
        rows = load_csv("customers.csv")
    except FileNotFoundError:
        print("[seed] customers.csv not found, skipping customers.")
        return

    if not rows:
        print("[seed] customers.csv is empty, skipping customers.")
        return

    repo = CustomerRepository()
    created = 0
    for row in rows:
        try:
            repo.create(
                {
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "phone_number": row["phone_number"],
                    "address": row["address"],
                    "city": row["city"],
                    "post_code": row["post_code"],
                }
            )
            created += 1
        except Exception as e:  # safety; don't die on one bad row
            print(f"[seed] Skipping customer {row.get('email')}: {e}")

    print(f"[seed] Seeded {created} customers via stored procedure.")


# ─────────────────────────────────────────────────────────────────────────────
# Locations
# ─────────────────────────────────────────────────────────────────────────────

def seed_locations() -> None:
    """Seed locations from locations.csv.

    Expected columns in locations.csv:

        address,city

    Example row:

        Main Street 1,Copenhagen
    """
    try:
        rows = load_csv("locations.csv")
    except FileNotFoundError:
        print("[seed] locations.csv not found, skipping locations.")
        return

    if not rows:
        print("[seed] locations.csv is empty, skipping locations.")
        return

    session = get_session()
    try:
        for row in rows:
            session.execute(
                text(
                    """
                    INSERT INTO location (address, city)
                    VALUES (:address, :city)
                    """
                ),
                {
                    "address": row["address"],
                    "city": row["city"],
                },
            )
        session.commit()
        print(f"[seed] Seeded {len(rows)} locations.")
    finally:
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Movies and genres
# ─────────────────────────────────────────────────────────────────────────────

def seed_movies_and_genres() -> None:
    """Seed movies and their genre mappings from movies.csv.

    Expected columns in movies.csv:

        title,release_year,runtime_min,rating,summary,genres

    - release_year: integer year (e.g. 1999)
    - runtime_min: integer minutes
    - rating: float or empty
    - genres: semicolon-separated list of genre names, e.g. "Sci-Fi;Action"
    """
    try:
        rows = load_csv("movies.csv")
    except FileNotFoundError:
        print("[seed] movies.csv not found, skipping movies.")
        return

    if not rows:
        print("[seed] movies.csv is empty, skipping movies.")
        return

    session = get_session()
    try:
        for row in rows:
            title = row["title"]
            release_year = int(row["release_year"])
            runtime_min = int(row["runtime_min"])
            rating_str = row.get("rating") or ""
            rating: Optional[float] = float(rating_str) if rating_str else None
            summary = row.get("summary", "")

            genres_raw = row.get("genres") or ""
            genres = [g.strip() for g in genres_raw.split(";") if g.strip()]

            # Ensure each genre exists
            for g in genres:
                session.execute(
                    text(
                        """
                        INSERT INTO genre (name) VALUES (:name)
                        ON DUPLICATE KEY UPDATE name = VALUES(name)
                        """
                    ),
                    {"name": g},
                )

            # Insert or update movie
            session.execute(
                text(
                    """
                    INSERT INTO movie (title, release_year, runtime_min, rating, summary)
                    VALUES (:title, :release_year, :runtime_min, :rating, :summary)
                    ON DUPLICATE KEY UPDATE
                        release_year = VALUES(release_year),
                        runtime_min = VALUES(runtime_min),
                        rating = VALUES(rating),
                        summary = VALUES(summary)
                    """
                ),
                {
                    "title": title,
                    "release_year": release_year,
                    "runtime_min": runtime_min,
                    "rating": rating,
                    "summary": summary,
                },
            )

            # Look up movie_id
            movie_row = session.execute(
                text("SELECT movie_id FROM movie WHERE title = :title"),
                {"title": title},
            ).fetchone()
            if not movie_row:
                print(f"[seed] Warning: movie '{title}' not found after insert.")
                continue
            movie_id = movie_row.movie_id

            # Link movie to genres
            # Link movie to genres
            for g in genres:
                session.execute(
                    text(
                        """
                        INSERT IGNORE INTO movie_genre (movie_id, genre_id)
                        SELECT :movie_id, g.genre_id
                        FROM genre AS g
                        WHERE g.name = :genre
                        """
                    ),
                    {"movie_id": movie_id, "genre": g},
                )

        session.commit()
        print(f"[seed] Seeded {len(rows)} movies (and genres).")
    finally:
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Promo codes
# ─────────────────────────────────────────────────────────────────────────────

def seed_promo_codes() -> None:
    """Seed promo codes from promo_codes.csv (optional).

    Expected columns in promo_codes.csv:

        code,description,percent_off,amount_off_dkk,starts_at,ends_at

    - percent_off: 0–100 or empty (for NULL)
    - amount_off_dkk: decimal number or empty (for NULL)
    - starts_at / ends_at: DATETIME strings that MySQL can parse, e.g.
      '2025-01-01 00:00:00'
    """
    try:
        rows = load_csv("promo_codes.csv")
    except FileNotFoundError:
        print("[seed] promo_codes.csv not found, skipping promo codes.")
        return

    if not rows:
        print("[seed] promo_codes.csv is empty, skipping promo codes.")
        return

    session = get_session()
    try:
        for row in rows:
            percent_off_str = row.get("percent_off") or ""
            amount_off_str = row.get("amount_off_dkk") or ""

            percent_off = float(percent_off_str) if percent_off_str else None
            amount_off = float(amount_off_str) if amount_off_str else None

            session.execute(
                text(
                    """
                    INSERT INTO promo_code
                        (code, description, percent_off, amount_off_dkk, starts_at, ends_at)
                    VALUES
                        (:code, :description, :percent_off, :amount_off_dkk, :starts_at, :ends_at)
                    ON DUPLICATE KEY UPDATE
                        description = VALUES(description),
                        percent_off = VALUES(percent_off),
                        amount_off_dkk = VALUES(amount_off_dkk),
                        starts_at = VALUES(starts_at),
                        ends_at = VALUES(ends_at)
                    """
                ),
                {
                    "code": row["code"],
                    "description": row.get("description", ""),
                    "percent_off": percent_off,
                    "amount_off_dkk": amount_off,
                    "starts_at": row["starts_at"],
                    "ends_at": row["ends_at"],
                },
            )
        session.commit()
        print(f"[seed] Seeded {len(rows)} promo codes.")
    finally:
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Inventory items
# ─────────────────────────────────────────────────────────────────────────────

def seed_inventory_items() -> None:
    """Create inventory_item copies of each movie at each location in each format.

    This function does *not* use CSV; it uses existing movies/locations/formats.

    Strategy:
      - SELECT all movie_id, location_id, format_id combinations.
      - For each combination, insert 1–3 copies with status = 1 (available).
    """
    session = get_session()
    try:
        movies = session.execute(text("SELECT movie_id FROM movie")).fetchall()
        locations = session.execute(text("SELECT location_id FROM location")).fetchall()
        formats = session.execute(text("SELECT format_id FROM format")).fetchall()

        if not movies or not locations or not formats:
            print("[seed] Not enough data to seed inventory items (movies/locations/formats missing).")
            return

        inserted = 0
        for m in movies:
            for loc in locations:
                for f in formats:
                    copies = random.randint(1, 3)
                    for _ in range(copies):
                        session.execute(
                            text(
                                """
                                INSERT INTO inventory_item (movie_id, location_id, format_id, status)
                                VALUES (:movie_id, :location_id, :format_id, 1)
                                """
                            ),
                            {
                                "movie_id": m.movie_id,
                                "location_id": loc.location_id,
                                "format_id": f.format_id,
                            },
                        )
                        inserted += 1

        session.commit()
        print(f"[seed] Seeded {inserted} inventory items.")
    finally:
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Rentals and reservations
# ─────────────────────────────────────────────────────────────────────────────

def seed_rentals_and_reservations(
    num_rentals: int = 10,
    num_reservations: int = 10,
) -> None:
    session = get_session()
    try:
        customers = session.execute(
            text("SELECT customer_id FROM customer ORDER BY customer_id")
        ).fetchall()
        employees = session.execute(
            text("SELECT employee_id FROM employee ORDER BY employee_id")
        ).fetchall()
        items = session.execute(
            text("SELECT inventory_item_id FROM inventory_item WHERE status = 1")
        ).fetchall()
    finally:
        session.close()

    if not customers or not employees or not items:
        print("[seed] Not enough data to seed rentals/reservations (customers/employees/items missing).")
        return

    rental_repo = RentalRepository()

    def random_customer_id() -> int:
        return random.choice(customers).customer_id

    def random_employee_id() -> int:
        return random.choice(employees).employee_id

    def take_item_ids(k: int = 1) -> list[int]:
        nonlocal items
        if len(items) < k:
            return []
        chosen = random.sample(items, k)
        # remove chosen from the pool so we don't reuse them
        remaining = [it for it in items if it not in chosen]
        items = remaining
        return [c.inventory_item_id for c in chosen]

    created_rentals = 0
    for _ in range(num_rentals):
        item_ids = take_item_ids(1)
        if not item_ids:
            print("[seed] No more available items for rentals.")
            break
        try:
            rental_repo.create(
                {
                    "customer_id": random_customer_id(),
                    "employee_id": random_employee_id(),
                    "promo_code_id": None,
                    "inventory_item_ids": item_ids,
                }
            )
            created_rentals += 1
        except Exception as e:
            print(f"[seed] Error creating rental: {e}")

    created_reservations = 0
    for _ in range(num_reservations):
        item_ids = take_item_ids(1)
        if not item_ids:
            print("[seed] No more available items for reservations.")
            break
        try:
            rental_repo.create_reservation(
                {
                    "customer_id": random_customer_id(),
                    "employee_id": random_employee_id(),
                    "promo_code_id": None,
                    "inventory_item_ids": item_ids,
                }
            )
            created_reservations += 1
        except Exception as e:
            print(f"[seed] Error creating reservation: {e}")

    print(f"[seed] Seeded {created_rentals} rentals and {created_reservations} reservations.")

# ─────────────────────────────────────────────────────────────────────────────
# Reviews (optional, using reviews.txt)
# ─────────────────────────────────────────────────────────────────────────────

def seed_reviews(max_reviews_per_movie: int = 3) -> None:
    """Seed reviews for movies using random text lines from reviews.txt.

    Expected file: reviews.txt (optional) with one review per line.

    Strategy:
      - Load all movie_ids.
      - For each movie, create between 0 and max_reviews_per_movie reviews.
      - Ratings are random integers 1–10.
    """
    try:
        texts = load_lines("reviews.txt")
    except FileNotFoundError:
        print("[seed] reviews.txt not found, skipping reviews.")
        return

    if not texts:
        print("[seed] reviews.txt is empty, skipping reviews.")
        return

    session = get_session()
    try:
        movies = session.execute(text("SELECT movie_id FROM movie")).fetchall()
        if not movies:
            print("[seed] No movies found, skipping reviews.")
            return

        inserted = 0
        for movie in movies:
            n = random.randint(0, max_reviews_per_movie)
            for _ in range(n):
                rating = random.randint(1, 10)
                body = random.choice(texts)
                session.execute(
                    text(
                        """
                        INSERT INTO review (rating, body, movie_id)
                        VALUES (:rating, :body, :movie_id)
                        """
                    ),
                    {
                        "rating": rating,
                        "body": body,
                        "movie_id": movie.movie_id,
                    },
                )
                inserted += 1

        session.commit()
        print(f"[seed] Seeded {inserted} reviews.")
    finally:
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Main entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Main entrypoint for seeding MySQL data."""
    print("[seed] Starting MySQL seeding ...")
    seed_static_lookups()
    seed_employees()
    print(f'5% done with seeding.')
    seed_customers()
    seed_locations()
    print(f'50% done with seeding.')
    seed_movies_and_genres()
    seed_promo_codes()
    seed_inventory_items()
    print(f'80% done with seeding.')
    seed_rentals_and_reservations()
    seed_reviews()
    print("[seed] MySQL seeding complete.")


if __name__ == "__main__":
    main()
