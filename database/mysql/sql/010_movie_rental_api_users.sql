USE movie_rental;

-- -----------------------------------------------------
-- Table api_user (for API authentication)
-- -----------------------------------------------------
-- Separate from domain 'customer' to focus only on API access
-- Roles here are application-level, not MySQL server roles.
-- Passwords stored as bcrypt hashes.

DROP TABLE IF EXISTS api_user;
CREATE TABLE api_user (
  api_user_id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('ADMIN','SUPERUSER','USER') NOT NULL DEFAULT 'USER',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (api_user_id)
);

CREATE INDEX idx_api_user_username ON api_user(username);
