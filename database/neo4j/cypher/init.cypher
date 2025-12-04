// Neo4j schema and sample creation aligned with MySQL model
// Labels, properties, and relationship directions corrected.
// Use MERGE with unique IDs when loading real data.

// Optional uniqueness constraints (adapt as needed)
CREATE CONSTRAINT customer_id_unique IF NOT EXISTS FOR (c:Customer) REQUIRE c.customerId IS UNIQUE;
CREATE CONSTRAINT employee_id_unique IF NOT EXISTS FOR (e:Employee) REQUIRE e.employeeId IS UNIQUE;
CREATE CONSTRAINT location_id_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.locationId IS UNIQUE;
CREATE CONSTRAINT format_id_unique IF NOT EXISTS FOR (f:Format) REQUIRE f.formatId IS UNIQUE;
CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.movieId IS UNIQUE;
CREATE CONSTRAINT inventory_item_id_unique IF NOT EXISTS FOR (i:InventoryItem) REQUIRE i.inventoryItemId IS UNIQUE;
CREATE CONSTRAINT membership_id_unique IF NOT EXISTS FOR (mt:Membership) REQUIRE mt.membershipId IS UNIQUE;
CREATE CONSTRAINT membership_plan_id_unique IF NOT EXISTS FOR (mp:MembershipPlan) REQUIRE mp.membershipPlanId IS UNIQUE;
CREATE CONSTRAINT genre_id_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.genreId IS UNIQUE;
CREATE CONSTRAINT rental_id_unique IF NOT EXISTS FOR (r:Rental) REQUIRE r.rentalId IS UNIQUE;
CREATE CONSTRAINT payment_id_unique IF NOT EXISTS FOR (p:Payment) REQUIRE p.paymentId IS UNIQUE;
CREATE CONSTRAINT fee_id_unique IF NOT EXISTS FOR (f:Fee) REQUIRE f.feeId IS UNIQUE;
CREATE CONSTRAINT promo_code_id_unique IF NOT EXISTS FOR (pc:PromoCode) REQUIRE pc.promoCodeId IS UNIQUE;
CREATE CONSTRAINT review_id_unique IF NOT EXISTS FOR (rv:Review) REQUIRE rv.reviewId IS UNIQUE;

// Example structure with corrected edges and properties.
// Replace empty strings with real values or use parameterized MERGE during ingestion.

CREATE
  (mtype:Membership {membershipId: "", membership: ""})<-[:IS_MEMBERSHIP_TYPE]-
  (mp:MembershipPlan {membershipPlanId: "", monthlyCost: "", startsOn: "", endsOn: ""})-[:HAS_MEMBERSHIP]->
  (c:Customer {customerId: "", firstName: "", lastName: "", email: "", phoneNumber: "", createdAt: ""})-[:HAS_ADDRESS]->
  (addr:Address {addressId: "", address: "", city: "", postCode: ""}),

  (e:Employee {employeeId: "", firstName: "", lastName: "", phoneNumber: "", email: "", isActive: ""}),
  (loc:Location {locationId: "", address: "", city: ""}),
  (e)-[:EMPLOYED_AT]->(loc),

  (item:InventoryItem {inventoryItemId: "", status: ""})-[:LOCATED_AT]->(loc),
  (c)-[:RENTED]->(r:Rental {rentalId: "", rentedAtDatetime: "", returnedAtDatetime: "", dueAtDatetime: "", reservedAtDatetime: "", status: ""}),
  // Rental can include multiple items (from rental_item table)
  (r)-[:HAS_ITEM]->(item),

  (fmt:Format {formatId: "", format: ""})<-[:HAS_FORMAT]-(item),
  (mov:Movie {movieId: "", title: "", summary: "", releaseYear: "", runtimeMin: "", rating: ""}),
  (item)-[:IS_COPY_OF]->(mov),
  (mov)-[:OF_GENRE]->(gen:Genre {genreId: "", name: ""}),

  (pay:Payment {paymentId: "", amountDkk: "", createdAt: ""})-[:FOR_RENTAL]->(r),
  (c)-[:MADE_PAYMENT]->(pay),

  // Review lacks customer_id in SQL; only model Review->Movie unless schema is extended
  (rev:Review {reviewId: "", rating: "", body: "", createdAt: ""})-[:REVIEWS]->(mov),

  (fee:Fee {feeId: "", feeType: "", amountDkk: ""})<-[:HAS_FEE]-(r),
  (promo:PromoCode {promoCodeId: "", code: "", description: "", percentOff: "", amountOffDkk: "", startsAt: "", endsAt: ""}),
  (r)-[:USED_PROMO]->(promo);

// Note: If you want a derived convenience edge (Customer)-[:RENTED]->(InventoryItem),
// create it from rental_item rows after ingest; keep Rental as source of truth.
