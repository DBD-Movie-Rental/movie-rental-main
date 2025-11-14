# 🎬 Movie Rental Database

![MySQL](https://img.shields.io/badge/MySQL-8.x-blue?logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7.x-green?logo=mongodb&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-latest-blue?logo=neo4j&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.2-black?logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.44-red?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue?logo=docker&logoColor=white)

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

> Python/virtualenv are only needed if you want to run the API directly on your host.  
> For the Docker setup below, everything runs in containers.

## Setup (local)

Run the Flask API on your machine, and MySQL in Docker.

```bash
# 1. Clone the repository
git clone https://github.com/DBD-Movie-Rental/movie-rental-main.git
cd movie-rental-main

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start only the MySQL container
docker compose -f compose/docker-compose.dev.yml up -d mysql

# 5. Run the Flask API locally
python -m src.app
```

API will be available at: `http://localhost:5004`  
MySQL will be available at: `localhost:3307` (user: `app`, password: `app`, db: `movie_rental`)


## Setup (Docker – API + MySQL)

Run both the API and MySQL inside Docker.

```bash
# 1. Clone the repository
git clone https://github.com/DBD-Movie-Rental/movie-rental-main.git
cd movie-rental-main

# 2. Built docker compose and run
docker compose -f compose/docker-compose.dev.yml up --build -d

# 3. Run mysql --> mongodb migration
docker compose -f compose/docker-compose.dev.yml exec api python -m migrations.migrate_sql_to_mongo

# 3. (Optional) Check running containers
docker ps
```

API: `http://localhost:5004/api/v1/health`  
MySQL: `localhost:3307`


## Docker build only

If you just want to (re)build images without starting containers:

```bash
docker compose -f compose/docker-compose.dev.yml build
```

---

## 👥 Authors

- **Christian B. Thellefsen**  
  [![GitHub](https://img.shields.io/badge/GitHub-ChristianBT96-black?logo=github)](https://github.com/ChristianBT96)

- **Marcus R. Kjærsgaard**  
  [![GitHub](https://img.shields.io/badge/GitHub-marcus--rk-black?logo=github)](https://github.com/marcus-rk)