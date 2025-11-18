USE movie_rental;

-- users:
--   marcus_rk, ChristianBT96 -> r_admin
--   superuser                -> r_superuser
--   app_user                 -> r_user (read-only)

-- 1) Create users (demo passwords = 'password')
CREATE USER IF NOT EXISTS 'marcus_rk'@'%'
    IDENTIFIED BY 'password';

CREATE USER IF NOT EXISTS 'ChristianBT96'@'%'
    IDENTIFIED BY 'password';

CREATE USER IF NOT EXISTS 'superuser'@'%'
    IDENTIFIED BY 'password';

CREATE USER IF NOT EXISTS 'app_user'@'%'
    IDENTIFIED BY 'password';


-- 2) Grant roles
GRANT 'r_admin'     TO 'marcus_rk'@'%';
GRANT 'r_admin'     TO 'ChristianBT96'@'%';
GRANT 'r_superuser' TO 'superuser'@'%';
GRANT 'r_user'      TO 'app_user'@'%';


-- 3) Default roles
SET DEFAULT ROLE 'r_admin'     TO 'marcus_rk'@'%';
SET DEFAULT ROLE 'r_admin'     TO 'ChristianBT96'@'%';
SET DEFAULT ROLE 'r_superuser' TO 'superuser'@'%';
SET DEFAULT ROLE 'r_user'      TO 'app_user'@'%';


-- 4) Flask API DB user:
--    created by Docker from MYSQL_USER=app / MYSQL_PASSWORD=app
--    here we just attach the r_superuser role.
GRANT 'r_superuser' TO 'app'@'%';
SET DEFAULT ROLE 'r_superuser' TO 'app'@'%';
