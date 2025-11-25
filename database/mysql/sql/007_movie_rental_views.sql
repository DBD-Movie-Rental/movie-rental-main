USE movie_rental;


-- ----------------------------------------
-- View of overdue rentals
-- ----------------------------------------
CREATE OR REPLACE VIEW vw_overdue_rentals AS
SELECT
  r.rental_id,
  r.customer_id,
  r.due_at_datetime,
  r.status,
  TIMESTAMPDIFF(HOUR, r.due_at_datetime, NOW()) AS hours_overdue
FROM rental r
WHERE r.status IN ('OPEN','LATE')
  AND r.due_at_datetime IS NOT NULL
  AND NOW() > r.due_at_datetime;

-- ----------------------------------------
-- View of customers with their addresses
-- A customer may have multiple addresses.
-- ----------------------------------------
CREATE OR REPLACE VIEW vw_customer_addresses AS
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  c.email,
  c.phone_number,
  a.address_id,
  a.address,
  a.city,
  a.post_code
FROM customer c
LEFT JOIN address a ON a.customer_id = c.customer_id;

-- ----------------------------------------
-- View of customers, their addresses, and rentals
-- Rentals duplicated per address if multiple addresses exist.
-- ----------------------------------------
CREATE OR REPLACE VIEW vw_customer_address_rentals AS
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  c.email,
  c.phone_number,
  a.address_id,
  a.address,
  a.city,
  a.post_code,
  r.rental_id,
  r.status AS rental_status,
  r.rented_at_datetime,
  r.due_at_datetime,
  r.returned_at_datetime,
  r.reserved_at_datetime,
  r.employee_id,
  r.promo_code_id
FROM customer c
LEFT JOIN address a ON a.customer_id = c.customer_id
LEFT JOIN rental r ON r.customer_id = c.customer_id;

-- ----------------------------------------
-- Aggregated rental summary per customer
-- Includes counts by status, first/last rental timestamps,
-- total payments and total fees (late/damaged/other) aggregated.
-- ----------------------------------------
CREATE OR REPLACE VIEW vw_customer_rental_summary AS
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  c.email,
  c.phone_number,
  COUNT(r.rental_id) AS total_rentals,
  SUM(r.status = 'OPEN') AS open_rentals,
  SUM(r.status = 'LATE') AS late_rentals,
  SUM(r.status = 'RESERVED') AS reserved_rentals,
  SUM(r.status = 'RETURNED') AS returned_rentals,
  MIN(r.rented_at_datetime) AS first_rented_at_datetime,
  MAX(r.rented_at_datetime) AS last_rented_at_datetime,
  COALESCE(SUM(p.amount_dkk), 0) AS total_payments_dkk,
  COALESCE(SUM(CASE f.fee_type WHEN 'LATE' THEN f.amount_dkk ELSE 0 END),0) AS total_late_fees_dkk,
  COALESCE(SUM(CASE f.fee_type WHEN 'DAMAGED' THEN f.amount_dkk ELSE 0 END),0) AS total_damaged_fees_dkk,
  COALESCE(SUM(CASE f.fee_type WHEN 'OTHER' THEN f.amount_dkk ELSE 0 END),0) AS total_other_fees_dkk,
  COALESCE(SUM(f.amount_dkk),0) AS total_all_fees_dkk
FROM customer c
LEFT JOIN rental r ON r.customer_id = c.customer_id
LEFT JOIN payment p ON p.rental_id = r.rental_id
LEFT JOIN rental_fee rf ON rf.rental_id = r.rental_id
LEFT JOIN fee f ON f.fee_id = rf.fee_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.phone_number;

-- ----------------------------------------
-- View of customers with membership info
-- One row per customer (membership_plan.customer_id UNIQUE)
-- ----------------------------------------
CREATE OR REPLACE VIEW vw_customer_membership AS
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  c.email,
  c.phone_number,
  mp.membership_plan_id,
  m.membership AS membership_level,
  mp.monthly_cost,
  mp.starts_on,
  mp.ends_on
FROM customer c
LEFT JOIN membership_plan mp ON mp.customer_id = c.customer_id
LEFT JOIN membership m ON m.membership_id = mp.membership_id;
