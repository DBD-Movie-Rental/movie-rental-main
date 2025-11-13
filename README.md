# 🎬 Movie Rental Database

![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue?logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-latest-green?logo=mongodb&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-latest-blue?logo=neo4j&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.2-black?logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.44-red?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10+-blue?logo=docker&logoColor=white)

A movie rental system based on a traditional physical rental store.  
The project models customers, rentals, inventory, staff, payments, and overdue handling.

It is designed to demonstrate how the same domain can be implemented across three databases:

- **MySQL** for the structured, transactional rental workflow  
- **MongoDB** for flexible, document-oriented data  
- **Neo4j** for graph-based relationships such as actors, genres, and connections

Each database has its own API namespace:

- `/api/v1/mysql/*`
- `/api/v1/mongodb/*`
- `/api/v1/neo4j/*`

The goal is to showcase practical, side-by-side implementations using ORM/ODM/OGM patterns, all containerized with Docker.

---

## Quick Start (Docker - Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running  
- Git  
- Python 3.10+ (for the API layer)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/DBD-Movie-Rental/movie-rental-main.git
cd movie-rental-main

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Start containers
docker compose -f compose/docker-compose.dev.yml down -v
docker compose -f compose/docker-compose.dev.yml up -d


# Optional check running containers
docker ps
```

---

## 👥 Authors

- **Christian B. Thellefsen**  
  [![GitHub](https://img.shields.io/badge/GitHub-ChristianBT96-black?logo=github)](https://github.com/ChristianBT96)

- **Marcus R. Kjærsgaard**  
  [![GitHub](https://img.shields.io/badge/GitHub-marcus--rk-black?logo=github)](https://github.com/marcus-rk)