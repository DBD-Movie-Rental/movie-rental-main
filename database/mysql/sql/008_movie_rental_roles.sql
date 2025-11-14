-- 010_movie_rental_roles.sql
-- Purpose: Define reusable roles for the movie_rental database
--   r_admin      : full control on schema
--   r_superuser  : application-level power user (no DELETE, no DDL)
--   r_user       : read-only, plus can execute read-only procedures

USE movie_rental;

-- ----------------------------------------
-- 1) Create roles (if not already present)
-- ----------------------------------------
CREATE ROLE IF NOT EXISTS 'r_admin';
CREATE ROLE IF NOT EXISTS 'r_superuser';
CREATE ROLE IF NOT EXISTS 'r_user';

-- ---------------------------------------------------------
-- 2) Grant privileges to roles (Role-Based Access Control)
-- ---------------------------------------------------------

-- r_admin:
GRANT
    ALL PRIVILEGES
ON movie_rental.* 
TO 'r_admin';


-- r_superuser:
GRANT
    SELECT,
    INSERT,
    UPDATE,
    EXECUTE -- allow executing stored procedures
ON movie_rental.*
TO 'r_superuser';


-- r_user:
GRANT
    SELECT,
    EXECUTE -- allow executing stored procedures
ON movie_rental.*
TO 'r_user';