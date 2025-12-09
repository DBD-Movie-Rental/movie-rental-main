from flask import Blueprint, jsonify, request

from .crud_blueprint import make_crud_blueprint

from src.repositories.neo4j.customer_repository import CustomerRepository
from src.repositories.neo4j.address_repository import AddressRepository
from src.repositories.neo4j.location_repository import LocationRepository
from src.repositories.neo4j.employee_repository import EmployeeRepository
from src.repositories.neo4j.genre_repository import GenreRepository
from src.repositories.neo4j.format_repository import FormatRepository
from src.repositories.neo4j.movie_repository import MovieRepository
from src.repositories.neo4j.inventory_item_repository import InventoryItemRepository
from src.repositories.neo4j.rental_repository import RentalRepository
from src.repositories.neo4j.payment_repository import PaymentRepository
from src.repositories.neo4j.fee_repository import FeeRepository
from src.repositories.neo4j.promo_code_repository import PromoCodeRepository
from src.repositories.neo4j.membership_repository import MembershipRepository
from src.repositories.neo4j.membership_plan_repository import MembershipPlanRepository

# Parent blueprint for Neo4j routes
bp = Blueprint("neo4j", __name__)

# Initialize repositories
customer_repo = CustomerRepository()
address_repo = AddressRepository()
location_repo = LocationRepository()
employee_repo = EmployeeRepository()
genre_repo = GenreRepository()
format_repo = FormatRepository()
movie_repo = MovieRepository()
inventory_item_repo = InventoryItemRepository()
rental_repo = RentalRepository()
payment_repo = PaymentRepository()
fee_repo = FeeRepository()
promo_code_repo = PromoCodeRepository()
membership_repo = MembershipRepository()
membership_plan_repo = MembershipPlanRepository()

# Register CRUD endpoints for core entities
bp.register_blueprint(make_crud_blueprint("customers", customer_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("addresses", address_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("locations", location_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("employees", employee_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("genres", genre_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("formats", format_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("movies", movie_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("inventory_items", inventory_item_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("rentals", rental_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("payments", payment_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("fees", fee_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("promo_codes", promo_code_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("memberships", membership_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("membership_plans", membership_plan_repo, id_converter="int"))

# Health endpoint for Neo4j
@bp.get("/health")
def neo4j_health():
	"""Basic health check for Neo4j connectivity via neomodel."""
	try:
		# lightweight query: count any node label likely to exist (Movie preferred)
		from neomodel import db
		result, _ = db.cypher_query("MATCH (n) RETURN count(n) AS cnt LIMIT 1")
		count = int(result[0][0]) if len(result) else 0
		return jsonify({"status": "ok", "nodeCountSample": count}), 200
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)}), 500



# Neo4j: Movies by rating
@bp.get("/movies/by-rating")
def neo4j_movies_by_rating():
	try:
		from neomodel import db
		min_rating_param = request.args.get("minRating", default="8")
		try:
			min_rating = float(min_rating_param)
		except ValueError:
			return jsonify({"status": "error", "message": "minRating must be a number"}), 400

		# Support both numeric and string-stored ratings by attempting toFloat
		cypher = (
			"MATCH (m:Movie) "
			"WHERE (m.rating IS NOT NULL AND (m.rating >= $min OR toFloat(m.rating) >= $min)) "
			"RETURN m { .movieId, .title, .rating, .releaseYear, .runtimeMin, .summary } AS movie "
			"ORDER BY coalesce(toFloat(m.rating), -1) DESC"
		)
		results, _ = db.cypher_query(cypher, {"min": min_rating})

		movies = [row[0] for row in results]
		return jsonify(movies), 200
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)}), 500

# Neo4j: Customer rental paths 
@bp.get("/customers/<int:id>/rental-paths")
def neo4j_customer_rental_paths(id: int):
	try:
		from neomodel import db
		cypher = (
			"MATCH (c:Customer {customerId: $cid})-[:RENTED]->(r:Rental)"
			" OPTIONAL MATCH (r)-[:HAS_ITEM]->(:InventoryItem)-[:IS_COPY_OF]->(m:Movie)"
			" WITH r, m"
			" RETURN r.rentalId AS rentalId,"
			"        collect(distinct m { .movieId, .title, .rating, .releaseYear, .runtimeMin }) AS movies"
		)
		results, _ = db.cypher_query(cypher, {"cid": id})
		rentals = [{"rental_id": rentalId, "movies": movies} for rentalId, movies in results]
		if not rentals:
			# Check if customer exists to return 404 vs empty traversal
			check, _ = db.cypher_query("MATCH (c:Customer {customerId: $cid}) RETURN c LIMIT 1", {"cid": id})
			if not check:
				return jsonify({"message": "Customer not found"}), 404
		return jsonify({"customer_id": id, "rentals": rentals}), 200
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)}), 500

# Neo4j: Similar movies by genre
@bp.get("/movies/<int:id>/similar")
def neo4j_movies_similar_by_genre(id: int):
	"""Return movies that share genres with the given movie, ranked by genre overlap.

	Showcase: Graph pattern matching and relationship traversal for similarity.
	"""
	try:
		from neomodel import db
		cypher = (
			"MATCH (m:Movie {movieId: $mid})-[:OF_GENRE]->(g:Genre) "
			"MATCH (other:Movie)-[:OF_GENRE]->(g) "
			"WHERE other.movieId <> m.movieId "
			"WITH other, count(DISTINCT g) AS sharedGenres "
			"ORDER BY sharedGenres DESC, other.title ASC "
			"RETURN other { .movieId, .title, .rating, .releaseYear, .runtimeMin } AS movie, sharedGenres "
			"LIMIT 25"
		)
		results, _ = db.cypher_query(cypher, {"mid": id})
		payload = [
			{"movie": row[0], "shared_genres": int(row[1])}
			for row in results
		]
		return jsonify(payload), 200
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)}), 500

# Neo4j: Movie recommendations via co-rentals and genre affinity
@bp.get("/movies/<int:id>/recommendations")
def neo4j_movie_recommendations(id: int):
	"""Recommend movies based on customers who rented the target movie and their other rentals, weighted by genre overlap.

	Showcase: Multi-hop traversal combining customer→rental→movie paths and genre-based scoring.
	"""
	try:
		from neomodel import db
		# Parameters: control weights and limits via query args
		limit_param = request.args.get("limit", default="25")
		try:
			limit = int(limit_param)
		except ValueError:
			limit = 25

		cypher = (
			# Gather target movie genres once
			"MATCH (target:Movie {movieId: $mid})-[:OF_GENRE]->(tg:Genre) "
			"WITH target, collect(DISTINCT tg) AS targetGenres "
			# Customers who rented the target movie
			"MATCH (c:Customer)-[:RENTED]->(:Rental)-[:HAS_ITEM]->(:InventoryItem)-[:IS_COPY_OF]->(target) "
			# Other movies those customers rented
			"MATCH (c)-[:RENTED]->(:Rental)-[:HAS_ITEM]->(:InventoryItem)-[:IS_COPY_OF]->(m:Movie) "
			"WHERE m.movieId <> target.movieId "
			# Genre overlap count between m and target
			"OPTIONAL MATCH (m)-[:OF_GENRE]->(g:Genre) "
			"WITH m, targetGenres, collect(DISTINCT g) AS mGenres, count(DISTINCT c) AS customerSupport "
			"WITH m, customerSupport, size([x IN mGenres WHERE x IN targetGenres]) AS sharedGenreCount "
			# Score: combine genre overlap and number of distinct customers supporting
			"WITH m, (sharedGenreCount * 2) + customerSupport AS score, sharedGenreCount AS genres, customerSupport AS support "
			"ORDER BY score DESC, m.title ASC "
			"RETURN m { .movieId, .title, .rating, .releaseYear, .runtimeMin } AS movie, score, genres, support "
			"LIMIT $limit"
		)
		results, _ = db.cypher_query(cypher, {"mid": id, "limit": limit})
		payload = [
			{
				"movie": row[0],
				"score": float(row[1]) if row[1] is not None else 0.0,
				"shared_genres": int(row[2]) if row[2] is not None else 0,
				"customer_support": int(row[3]) if row[3] is not None else 0,
			}
			for row in results
		]
		return jsonify(payload), 200
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)}), 500

