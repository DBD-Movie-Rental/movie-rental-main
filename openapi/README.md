# OpenAPI Folder Structure

This folder contains the OpenAPI specification for the Movie Rental API, split by database technology for clarity and maintainability.

## Files and Separation of Concerns (SoC)

- **openapi.yaml**
  - Main entry point. References all database-specific specs using `$ref`.
- **openapi-mysql.yaml**
  - Contains all MySQL endpoints, tags, and components (schemas, parameters, responses) relevant to MySQL operations.
- **openapi-mongodb.yaml**
  - Contains all MongoDB endpoints, tags, and components relevant to MongoDB operations.
- **openapi-neo4j.yaml**
  - Contains all Neo4j endpoints, tags, and components relevant to Neo4j operations.

## How to Use

Edit each database-specific file to update or add endpoints, schemas, or other OpenAPI components for that technology. The main `openapi.yaml` will aggregate them for documentation and tooling.

## Notes
- Use `$ref` to keep specs modular and DRY.
- Each file should only contain endpoints and components for its respective database.
