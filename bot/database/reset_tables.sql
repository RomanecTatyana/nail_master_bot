DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS client_notes;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS blocked_time;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS masters;

SELECT full_name, comment, rating, DATE(created_at)
FROM reviews 
JOIN clients
ON reviews.client_id = clients.id

SELECT appointment_date
FROM appointments
WHERE month = $1 AND
    year = $2

INSERT INTO appointments (client_id, service_id, master_id, appointment_date, start_time, end_time)
VALUES 
(1, 1, 1, '2025-05-30', '09:00', '11:13');


INSERT INTO appointments (client_id, service_id, master_id, appointment_date, start_time, end_time)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING id

ALTER TABLE appointments
ADD COLUMN stat text;


UPDATE appointments
SET stat = 'active'
WHERE true;