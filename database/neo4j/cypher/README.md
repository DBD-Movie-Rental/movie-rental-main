# Neo4j Cypher Schema (Movie Rental)

This folder contains `init.cypher`, a corrected Neo4j schema aligned to the MySQL model.

Highlights:
- Labeled nodes and consistent properties.
- Many-to-many relations modeled explicitly:
  - Rental has multiple items via `(:Rental)-[:HAS_ITEM]->(:InventoryItem)` (from `rental_item`).
  - Movie genres via `(:Movie)-[:OF_GENRE]->(:Genre)` (from `movie_genre`).
- Payment linked to rental and customer.
- Review linked only to movie (SQL lacks review.customer_id).
- Employee-to-location relation is commented (no SQL FK).

## How to use

1. Optionally create uniqueness constraints (see commented section in `init.cypher`).
2. Use MERGE with actual IDs and properties when loading from MySQL export.
3. For derived convenience edges (e.g., `(:Customer)-[:RENTED]->(:InventoryItem)`), generate them after importing rentals and rental items.

## Notes

- Property naming uses camelCase for graph nodes; MySQL uses snake_case. Map consistently during ETL.
- Ensure date/time strings are in ISO-8601 when loading into Neo4j.
