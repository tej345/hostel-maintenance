CREATE TABLE IF NOT EXISTS repair_logs (
    id SERIAL PRIMARY KEY,
    complaint_id INT NOT NULL UNIQUE REFERENCES complaints(id) ON DELETE CASCADE,
    technician_id INT NOT NULL REFERENCES users(id),
    action_taken TEXT NOT NULL,
    
    parts_replaced TEXT, -- e.g., '1x LED Tube Light Starter, 1x Choke'
    parts_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (parts_cost >= 0),
    labor_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (labor_cost >= 0),
    total_cost NUMERIC(10, 2) GENERATED ALWAYS AS (parts_cost + labor_cost) STORED,
    
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION trg_auto_resolve_complaint()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE complaints
    SET 
        status = 'RESOLVED',
        resolved_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.complaint_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_after_repair_log_insert ON repair_logs;
CREATE TRIGGER trg_after_repair_log_insert
AFTER INSERT ON repair_logs
FOR EACH ROW
EXECUTE FUNCTION trg_auto_resolve_complaint();