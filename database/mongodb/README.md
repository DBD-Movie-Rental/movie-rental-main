# MongoDB Data Model – `movieRental`

## 1. Purpose & Context

- **Domain:** Physical movie rental chain (multiple stores, physical inventory, memberships, fees, promo codes).
- **Origin:** Migration target for an existing **MySQL** schema.
- **Goals with MongoDB design:**
  - Optimize for **read-heavy** operations (browse movies, see customer history, see store inventory).
  - Reduce join-heavy logic from SQL by **embedding** related data.
  - Preserve important relational **constraints and enums** through JSON Schema validation.
  - Keep the model easy to query from an api.

---

## 2. Collections Overview

**Core / transactional collections**

- `customers`
  - Customer identity, **single primary address**, current membership plan, and **recent rentals snapshot**.
- `movies`
  - Movie catalog, genres, and **embedded reviews**.
- `locations`
  - Physical stores with **embedded employees** and **embedded inventory items**.
- `rentals`
  - Rental “contracts” with items, payments, applied fees, and promo info.

**Lookup / configuration collections**

- `membershipTypes`
- `feeTypes`
- `promoCodes`
- `genres`
- `formats`

These are used as **authoritative sources** for allowed values, default amounts and prices, but referenced from main documents by **string codes**, not ObjectIds.

---

## 3. SQL → MongoDB Mapping (High Level)

| SQL Table             | MongoDB Collection / Fields                                       |
|-----------------------|-------------------------------------------------------------------|
| `customer`            | `customers` (root fields)                                        |
| `address`             | `customers.address` (embedded object)                            |
| `membership`          | `membershipTypes` (lookup)                                       |
| `membership_plan`     | `customers.membershipPlan` (embedded)                            |
| `movie`               | `movies`                                                         |
| `genre`, `movie_genre`| `genres` (lookup) + `movies.genres` (string array)               |
| `review`              | `movies.reviews` (embedded array)                                |
| `location`            | `locations`                                                      |
| `employee`            | `locations.employees` (embedded array)                           |
| `format`              | `formats` (lookup) + `locations.inventory.format` / rentals.items.format |
| `inventory_item`      | `locations.inventory` (embedded array)                           |
| `promo_code`          | `promoCodes` + `rentals.promo` snapshot                          |
| `rental`              | `rentals` (root document)                                        |
| `rental_item`         | `rentals.items` (embedded array)                                 |
| `payment`             | `rentals.payments` (embedded array)                              |
| `fee`                 | `feeTypes` (lookup) + `rentals.fees` snapshot                    |

---

## 4. Key Design Patterns

### 4.1 Embedding vs Referencing

**Embedded (one-to-few, always read together):**

- Customer address, membership plan, and recent rentals.
- Movie reviews.
- Store employees and inventory.
- Rental items, payments, fees, and promo info.

**Referenced (separate aggregate roots):**

- `rentals.customerId` → `customers._id`
- `rentals.locationId` → `locations._id`
- `rentals.employeeId` → `locations.employees._id`
- `locations.inventory.movieId` → `movies._id`
- `rentals.items.inventoryItemId` → `locations.inventory._id`
- `rentals.items.movieId` → `movies._id`

**Reasoning:**  
If data is **owned by** and usually read together with one parent (e.g. reviews of a movie), it is embedded. If it is a separate “thing” with its own lifecycle (customers, movies, stores), it is referenced.

---

### 4.2 Lookups as String Codes

Lookup collections:

- `membershipTypes`:
  - `{ type: "GOLD" | "SILVER" | "BRONZE", monthlyCostDkk: Decimal }`
- `feeTypes`:
  - `{ type: "LATE" | "DAMAGED" | "OTHER", defaultAmountDkk: Decimal/null }`
- `genres`:
  - `{ name: <string> }`
- `formats`:
  - `{ type: "DVD" | "BLU-RAY" | "VHS" }`
- `promoCodes`:
  - `{ code, description, percentOff, amountOffDkk, startsAt, endsAt }`

Usage in other collections:

- `customers.membershipPlan.membershipType` ↔ `membershipTypes.type`
- `rentals.fees.feeType` ↔ `feeTypes.type`
- `movies.genres[]` ↔ `genres.name`
- `locations.inventory.format` and `rentals.items.format` ↔ `formats.type`
- `rentals.promo.code` ↔ `promoCodes.code`

**Why strings instead of ObjectIds?**

- Queries stay very simple:
  - `db.rentals.find({ "fees.feeType": "LATE" })`
  - `db.customers.find({ "membershipPlan.membershipType": "GOLD" })`
- These values are **small, stable enums**, so the cost of denormalizing as strings is low.
- Lookups still serve as the canonical list of valid values and defaults.

---

### 4.3 Snapshots vs Live Lookups

The model distinguishes between:

- **Live values** (from lookup collections):
  - `membershipTypes.monthlyCostDkk`
  - `feeTypes.defaultAmountDkk`
  - `promoCodes` definitions

- **Snapshots at the time of the transaction**:
  - `customers.membershipPlan.monthlyCostDkk`
    - Captures the price agreed with the customer at the time of membership creation.
  - `rentals.fees[].snapshot.defaultAmountDkk`
    - Captures the default fee amount that was used when calculating `amountDkk`.
  - `rentals.promo` object
    - Copies `code`, `percentOff`, `amountOffDkk`, `startsAt`, `endsAt` from `promoCodes` at rental time.

**Why?**

- If business rules or base prices change later, historic rentals and memberships **remain consistent** with what actually happened at that time.

---

## 5. Collection Design Details

### 5.1 `customers`

**Purpose:** Single document per customer.

**Key fields:**

- Identity:
  - `firstName`, `lastName`, `email`, `phoneNumber`, `createdAt`
- Address (embedded):
  - `address.address`, `address.city`, `address.postCode`
- Membership plan (embedded):
  - `membershipPlan.membershipType` → `"GOLD"|"SILVER"|"BRONZE"`
  - `membershipPlan.startsOn`, `membershipPlan.endsOn`
  - `membershipPlan.monthlyCostDkk` (snapshot of agreed price)
- Recent rentals (embedded summary):
  - `recentRentals[]` (max 5 items)
    - `rentalId` (ObjectId → rentals)
    - `status` (`"RESERVED"|"OPEN"|"RETURNED"|"LATE"|"CANCELLED"`)
    - `rentedAtDatetime` (Date)

**Indexing:**

- Unique email (case-insensitive) via collation on `{ email: 1 }`.

**Exam points:**

- Embeds membershipPlan because it is **1:1** and always needed when showing a customer.
- `recentRentals` acts as a **denormalized cache** of the last few rentals for quick profile views.

---

### 5.2 `movies`

**Purpose:** Movie catalog + reviews.

**Key fields:**

- Main:
  - `title`, `releaseYear`, `runtimeMin`, `rating` (int 1–10), `summary`
- Genres:
  - `genres: [ "Sci-Fi", "Action", ... ]` as strings
- Reviews (embedded):
  - `reviews[]`:
    - `_id` (ObjectId)
    - `customerId` (ObjectId or null)
    - `rating` (1–10)
    - `body` (optional)
    - `createdAt` (Date)

**Indexes:**

- `{ title: 1 }` – search by title.
- `{ genres: 1, releaseYear: -1 }` – filter by genre and sort by recency.

**Exam points:**

- Reviews are embedded because they are **owned by a single movie** and read together.
- Rating changed from SQL `DECIMAL(3,1)` to MongoDB **integer 1–10** (intentional simplification).

---

### 5.3 `locations`

**Purpose:** Physical video rental stores.

**Key fields:**

- Basic:
  - `address`, `city`
- Employees (embedded):
  - `employees[]` with `_id`, name, email, `isActive`
- Inventory (embedded):
  - `inventory[]`:
    - `_id` (ObjectId for each copy)
    - `movieId` (ref → `movies._id`)
    - `format` (`"DVD"|"BLU-RAY"|"VHS"`)
    - `status` (`"AVAILABLE"|"RENTED"|"DAMAGED"|"RETIRED"`)

**Indexes:**

- `{ "inventory.movieId": 1, "inventory.status": 1 }` – find stock for a movie by status.
- `{ "employees.email": 1 }` – identify employees by email.

**Exam points:**

- Inventory is embedded to model a **store-centric view**: “show me this store and everything it has.”
- String statuses (`"AVAILABLE"`, etc.) are self-documenting compared to numeric codes.

---

### 5.4 `rentals`

**Purpose:** Rental contracts / transactions.

**Key fields:**

- References:
  - `customerId` → `customers._id`
  - `locationId` → `locations._id`
  - `employeeId` → `locations.employees._id` (who handled it, optional)
- Status & timing:
  - `status`: `"RESERVED"|"OPEN"|"RETURNED"|"LATE"|"CANCELLED"`
  - `rentedAtDatetime`, `returnedAtDatetime`, `dueAtDatetime`, `reservedAtDatetime`
- Items (embedded):
  - `items[]`:
    - `inventoryItemId` → `locations.inventory._id` (specific physical copy)
    - `movieId` → `movies._id` (logical movie)
    - `format` (`"DVD"|"BLU-RAY"|"VHS"|"DIGITAL"`) – snapshot; supports future digital rentals.
- Payments (embedded):
  - `payments[]`:
    - `_id`, `amountDkk`, `createdAt`, plus optional fields (e.g. method)
- Fees (embedded):
  - `fees[]`:
    - `_id`
    - `feeType` (`"LATE"|"DAMAGED"|"OTHER"`)
    - `amountDkk`
    - `snapshot.defaultAmountDkk` – captures `feeTypes.defaultAmountDkk` at the time
- Promo (embedded snapshot):
  - `promo` (optional):
    - `code`, `percentOff`, `amountOffDkk`, `startsAt`, `endsAt`

**Indexes:**

- `{ customerId: 1, status: 1, rentedAtDatetime: -1 }` – customer history queries.
- `{ status: 1 }` – operational dashboards by status.
- `{ "items.inventoryItemId": 1 }` – see full rental history for a specific copy.
- `{ locationId: 1, status: 1, rentedAtDatetime: -1 }` – per-store reporting.

**Exam points:**

- `items` keeps **both** `inventoryItemId` and `movieId`:
  - granular physical tracking **and** easy movie-based analytics.
- `format` is denormalized per item to preserve the **rented format** even if the inventory record changes later.
- Everything needed for a rental is stored in **one document**, avoiding joins.

---

### 5.5 Lookup Collections

**`membershipTypes`**

- Defines valid membership types and their standard monthly price.
- Used to:
  - validate `membershipPlan.membershipType`
  - provide defaults for new memberships.

**`feeTypes`**

- Defines valid fee types and default amounts.
- Used in:
  - validation for `fees.feeType`
  - snapshotting `defaultAmountDkk` when applying a fee.

**`promoCodes`**

- Business-side definitions (marketing).
- Rental documents copy the relevant fields into `promo` for history.

**`genres` and `formats`**

- Simple canonical lists for UI and validation.
- Main collections use **strings** for ease of querying.

---

## 6. Index Strategy

- `customers`:
  - Unique, case-insensitive email index.
- `movies`:
  - Title and `(genres, releaseYear)` for searching and filtering.
- `locations`:
  - Inventory index for stock queries by movie and status.
  - Employees index by email.
- `rentals`:
  - Combined index for customer history.
  - Combined store + status + date index for reports.
  - Index for `items.inventoryItemId` for copy-level tracking.

**Exam angle:**  
Indexes reflect **real query patterns**: “last rentals per customer”, “current open rentals per store”, “inventory availability”, etc.

---

## 7. Summary of Design Choices (Exam-Friendly)

- **Embedding** used for:
  - Structures with clear ownership and “always together” access patterns.
- **String enums** used instead of ObjectId references:
  - Simpler queries, human-readable values, still backed by lookup collections.
- **Snapshots** used only where values can change afterwards:
  - Membership cost, fees, and promo details at the time of the rental.
- **Validation** via JSON Schema:
  - Enforces enum constraints and required fields, partially replacing SQL constraints.
- **Migration-aware:**
  - Each MongoDB structure can be directly traced back to the original MySQL tables and relationships.
  - The model is denormalized where it removes typical SQL joins, but still keeps **relational intent** (customers, movies, locations, rentals) clear.

This gives you a MongoDB model that is:

- faithful to the original relational domain,
- optimized for common read patterns,
- and easy to explain and justify in an exam report.