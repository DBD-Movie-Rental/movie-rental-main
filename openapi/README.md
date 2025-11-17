# Movie Rental API – OpenAPI Files

This project uses **OpenAPI 3.0.3** to describe a Movie Rental API.  
The spec is split into files to keep things readable and separated by responsibility.

---

## Files

```text
.
├── openapi.yaml
├── openapi-mysql.yaml
├── openapi-mongodb.yaml
└── openapi-neo4j.yaml
```

### `openapi.yaml` (main file)

- Full API in one file.
- Includes **all** paths:
  - `/api/v1/mysql/...`
  - `/api/v1/mongodb/...`
  - `/api/v1/neo4j/...`
- Also contains shared `components` (schemas, parameters, responses).

---

### `openapi-mysql.yaml`

- Only MySQL endpoints:

  ```yaml
  paths:
    /api/v1/mysql/...: ...
  ```

- Still has the same `info`, `servers`, `tags`, and `components` as the main file.

**Purpose:** Relational CRUD API (tables like customers, movies, rentals).

---

### `openapi-mongodb.yaml`

- Only MongoDB endpoints:

  ```yaml
  paths:
    /api/v1/mongodb/...: ...
  ```

- Same shared `components`.

**Purpose:** Read models and “detailed”/embedded views (documents with nested data).

---

### `openapi-neo4j.yaml`

- Only Neo4j endpoints:

  ```yaml
  paths:
    /api/v1/neo4j/...: ...
  ```

- Same shared `components`.

**Purpose:** Graph-related API (currently health, future relationship queries).

---

## Why split the files?

- Easier to read and work on one backend at a time.
- Clear **Separation of Concerns (SoC)**:
  - MySQL = relational CRUD
  - MongoDB = document read models
  - Neo4j = graph
- Each file is a **valid OpenAPI spec**, so you can:
  - Load it in Swagger UI
  - Generate clients
  - Use it in tests

Pick the file that matches the part of the system you’re working on, or use `openapi.yaml` for everything.
