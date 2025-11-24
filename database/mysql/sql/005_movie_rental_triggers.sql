USE movie_rental;


-- ---------------------------------------------
-- Automatic trigger checking membership upgrade
-- ---------------------------------------------
DELIMITER $$

DROP TRIGGER IF EXISTS trg_check_membership_upgrade$$
CREATE TRIGGER trg_check_membership_upgrade
AFTER INSERT ON rental
FOR EACH ROW
BEGIN
    DECLARE v_rental_count INT;
    DECLARE v_membership_id INT;

    SET v_rental_count = get_customer_rental_count(NEW.customer_id);

    IF v_rental_count >= 200 THEN
        SELECT membership_id INTO v_membership_id FROM membership WHERE membership = 'GOLD';
    ELSEIF v_rental_count >= 50 THEN
        SELECT membership_id INTO v_membership_id FROM membership WHERE membership = 'SILVER';
    END IF;

    IF v_membership_id IS NOT NULL THEN
        UPDATE membership_plan SET membership_id = v_membership_id WHERE customer_id = NEW.customer_id;
    END IF;
END$$

-- ---------------------------------------------
-- Rental audit triggers
-- ---------------------------------------------
DROP TRIGGER IF EXISTS trg_rental_insert_audit$$
CREATE TRIGGER trg_rental_insert_audit
AFTER INSERT ON rental
FOR EACH ROW
BEGIN
    INSERT INTO rental_status_audit (
        rental_id, action,
        old_status, new_status,
        old_rented_at_datetime, new_rented_at_datetime,
        old_due_at_datetime, new_due_at_datetime,
        old_returned_at_datetime, new_returned_at_datetime,
        changed_by
    ) VALUES (
        NEW.rental_id, 'INSERT',
        NULL, NEW.status,
        NULL, NEW.rented_at_datetime,
        NULL, NEW.due_at_datetime,
        NULL, NEW.returned_at_datetime,
        COALESCE(@app_user, CURRENT_USER())
    );
END$$

DROP TRIGGER IF EXISTS trg_rental_update_audit$$
CREATE TRIGGER trg_rental_update_audit
AFTER UPDATE ON rental
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status
       OR OLD.rented_at_datetime <> NEW.rented_at_datetime
       OR OLD.due_at_datetime <> NEW.due_at_datetime
       OR OLD.returned_at_datetime <> NEW.returned_at_datetime THEN
        INSERT INTO rental_status_audit (
            rental_id, action,
            old_status, new_status,
            old_rented_at_datetime, new_rented_at_datetime,
            old_due_at_datetime, new_due_at_datetime,
            old_returned_at_datetime, new_returned_at_datetime,
            changed_by
        ) VALUES (
            NEW.rental_id, 'UPDATE',
            OLD.status, NEW.status,
            OLD.rented_at_datetime, NEW.rented_at_datetime,
            OLD.due_at_datetime, NEW.due_at_datetime,
            OLD.returned_at_datetime, NEW.returned_at_datetime,
            COALESCE(@app_user, CURRENT_USER())
        );
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_rental_delete_audit$$
CREATE TRIGGER trg_rental_delete_audit
AFTER DELETE ON rental
FOR EACH ROW
BEGIN
    INSERT INTO rental_status_audit (
        rental_id, action,
        old_status, new_status,
        old_rented_at_datetime, new_rented_at_datetime,
        old_due_at_datetime, new_due_at_datetime,
        old_returned_at_datetime, new_returned_at_datetime,
        changed_by
    ) VALUES (
        OLD.rental_id, 'DELETE',
        OLD.status, NULL,
        OLD.rented_at_datetime, NULL,
        OLD.due_at_datetime, NULL,
        OLD.returned_at_datetime, NULL,
        COALESCE(@app_user, CURRENT_USER())
    );
END$$

-- ---------------------------------------------
-- Payment audit triggers
-- ---------------------------------------------
DROP TRIGGER IF EXISTS trg_payment_insert_audit$$
CREATE TRIGGER trg_payment_insert_audit
AFTER INSERT ON payment
FOR EACH ROW
BEGIN
    INSERT INTO payment_audit (
        payment_id, rental_id, action,
        old_amount_dkk, new_amount_dkk,
        changed_by
    ) VALUES (
        NEW.payment_id, NEW.rental_id, 'INSERT',
        NULL, NEW.amount_dkk,
        COALESCE(@app_user, CURRENT_USER())
    );
END$$

DROP TRIGGER IF EXISTS trg_payment_update_audit$$
CREATE TRIGGER trg_payment_update_audit
AFTER UPDATE ON payment
FOR EACH ROW
BEGIN
    IF OLD.amount_dkk <> NEW.amount_dkk THEN
        INSERT INTO payment_audit (
            payment_id, rental_id, action,
            old_amount_dkk, new_amount_dkk,
            changed_by
        ) VALUES (
            NEW.payment_id, NEW.rental_id, 'UPDATE',
            OLD.amount_dkk, NEW.amount_dkk,
            COALESCE(@app_user, CURRENT_USER())
        );
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_payment_delete_audit$$
CREATE TRIGGER trg_payment_delete_audit
AFTER DELETE ON payment
FOR EACH ROW
BEGIN
    INSERT INTO payment_audit (
        payment_id, rental_id, action,
        old_amount_dkk, new_amount_dkk,
        changed_by
    ) VALUES (
        OLD.payment_id, OLD.rental_id, 'DELETE',
        OLD.amount_dkk, NULL,
        COALESCE(@app_user, CURRENT_USER())
    );
END$$

DELIMITER ;
