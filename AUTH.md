# API Authentication

This project exposes protected write operations via JWT-based authentication. Read (GET) endpoints are public; POST/PUT/DELETE require a valid access token.

## Components
- Table `api_user`: stores API usernames, bcrypt password hashes, and roles.
- JWT (access & refresh): Access tokens expire after 30 minutes; refresh tokens after 7 days.
- In-memory blocklist for logout (clears on application restart).

## Endpoints
Base prefix: `/api/v1`

### Register
POST `/api/v1/auth/register`
Body:
```
{ "username": "alice", "password": "S3cretPwd", "role": "USER" }
```
Response 201:
```
{ "id": 1, "username": "alice", "role": "USER", "created_at": "..." }
```

### Login
POST `/api/v1/auth/login`
Body:
```
{ "username": "alice", "password": "S3cretPwd" }
```
Response 200:
```
{ "access_token": "...", "refresh_token": "..." }
```

### Refresh
POST `/api/v1/auth/refresh` (send refresh token in Authorization header)
Header: `Authorization: Bearer <refresh_token>`
Response 200:
```
{ "access_token": "..." }
```

### Logout
POST `/api/v1/auth/logout`
Header: `Authorization: Bearer <access_token>`
Response 200:
```
{ "message": "logged out" }
```

## Using Tokens
Include the access token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

## Curl Examples
```
# Register
curl -X POST http://localhost:5004/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"S3cretPwd"}'

# Login
curl -X POST http://localhost:5004/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"S3cretPwd"}'

# Refresh
curl -X POST http://localhost:5004/api/v1/auth/refresh \
  -H 'Authorization: Bearer <refresh_token>'

# Create a genre (protected)
curl -X POST http://localhost:5004/api/v1/mysql/genres \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name":"Action"}'
```

## Environment Variables
- `JWT_SECRET_KEY` (default: `dev-secret-change-me`) – change in production.

## Future Improvements
- Persistent token revocation (Redis / DB)
- Role-based route restrictions
- Rate limiting
- Password complexity & account lockout

docker exec -i mysql_database sh -c "mysql -u root -proot movie_rental < /docker-entrypoint-initdb.d/010_movie_rental_api_users.sql"
docker exec -i mysql_database sh -c "mysql -u root -proot -e 'SHOW TABLES FROM movie_rental LIKE "api_user";'"