DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'priority_level') THEN
        CREATE TYPE priority_level AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'EMERGENCY');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'complaint_status') THEN
        CREATE TYPE complaint_status AS ENUM ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'REJECTED');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS complaint_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- e.g., 'Electrical', 'Plumbing', 'Carpentry', 'AC', 'Wi-Fi'
    description TEXT
);

CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    category_id INT NOT NULL REFERENCES complaint_categories(id),
    student_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id INT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    
    priority priority_level NOT NULL DEFAULT 'MEDIUM',
    status complaint_status NOT NULL DEFAULT 'PENDING',
    
    assigned_technician_id INT REFERENCES users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);