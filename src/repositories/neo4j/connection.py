import os
from neomodel import config

# Configure Neo4j OGM (neomodel) using environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

# neomodel expects bolt URL with auth in URI form
config.DATABASE_URL = f"bolt://{NEO4J_USER}:{NEO4J_PASSWORD}@{NEO4J_URI.split('://')[-1]}"

# Optional: enable auto-install labels (useful during development)
config.AUTO_INSTALL_LABELS = True
