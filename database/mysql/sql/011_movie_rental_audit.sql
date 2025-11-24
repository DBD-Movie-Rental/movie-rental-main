USE movie_rental;

-- -----------------------------------------------------
-- Audit tables for critical entities
-- -----------------------------------------------------
-- Pattern: Application sets SET @app_user = 'username' per session.
-- Triggers fall back to CURRENT_USER() if @app_user is NULL.
-- -----------------------------------------------------
-- Usage example from application connection:
--   SET @app_user = 'api_user_123';
--   INSERT INTO rental (...);
-- The trigger will record 'api_user_123' in changed_by.
-- For bulk operations, you can set a correlation id similarly:
--   SET @correlation_id = UUID();  (extend tables to store if needed)
-- Consider periodic archiving of audit rows older than retention window.

-- Drop existing audit tables if recreating
DROP TABLE IF EXISTS rental_status_audit;
CREATE TABLE rental_status_audit (
  audit_id BIGINT NOT NULL AUTO_INCREMENT,
  rental_id INT NOT NULL,
  action ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  old_status ENUM('RESERVED','OPEN','RETURNED','LATE','CANCELLED') NULL,
  new_status ENUM('RESERVED','OPEN','RETURNED','LATE','CANCELLED') NULL,
  old_rented_at_datetime DATETIME NULL,
  new_rented_at_datetime DATETIME NULL,
  old_due_at_datetime DATETIME NULL,
  new_due_at_datetime DATETIME NULL,
  old_returned_at_datetime DATETIME NULL,
  new_returned_at_datetime DATETIME NULL,
  changed_by VARCHAR(128) NOT NULL,
  changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (audit_id),
  INDEX idx_rental_status_audit_rental_id (rental_id),
  INDEX idx_rental_status_audit_changed_at (changed_at)
);

DROP TABLE IF EXISTS payment_audit;
CREATE TABLE payment_audit (
  audit_id BIGINT NOT NULL AUTO_INCREMENT,
  payment_id INT NULL, -- NULL for DELETE when original row reference may be gone or INSERT before id known
  rental_id INT NULL,
  action ENUM('INSERT','UPDATE','DELETE','REFUND') NOT NULL,
  old_amount_dkk DECIMAL(10,2) NULL,
  new_amount_dkk DECIMAL(10,2) NULL,
  changed_by VARCHAR(128) NOT NULL,
  changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (audit_id),
  INDEX idx_payment_audit_payment_id (payment_id),
  INDEX idx_payment_audit_rental_id (rental_id),
  INDEX idx_payment_audit_changed_at (changed_at)
);
