docker compose -f compose/docker-compose.dev.yml down -v
docker compose -f compose/docker-compose.dev.yml up -d

python3 -m src.app