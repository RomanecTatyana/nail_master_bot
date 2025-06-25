-- Таблиця клієнтів
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    full_name VARCHAR(100),
    phone VARCHAR(20)
);

-- Таблиця послуг
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(60) NOT NULL,
    duration_minutes INTEGER NOT NULL
);

-- Таблиця майстрів
CREATE TABLE IF NOT EXISTS masters (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    full_name VARCHAR(100),
    start_work_time TIME NOT NULL,
    end_work_time TIME NOT NULL
);

-- Таблиця блокування часу майстром
CREATE TABLE IF NOT EXISTS blocked_time (
    id SERIAL PRIMARY KEY,
    master_id INTEGER NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
    blocked_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    reason TEXT
);

-- Таблиця з записами до майстра
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services(id),
    master_id INTEGER NOT NULL REFERENCES masters(id),
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    stat TEXT
);

-- Таблиця з відгуками клієнтів
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    master_id INTEGER NOT NULL REFERENCES masters(id),
    appointment_id INTEGER NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблиця з помітками майстра
CREATE TABLE IF NOT EXISTS client_notes (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    master_id INTEGER NOT NULL REFERENCES masters(id),
    note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
