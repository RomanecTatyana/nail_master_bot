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

SELECT a.appointment_date::date, a.start_time, a.end_time, 
               m.start_work_time, m.end_work_time
        FROM appointments a
        JOIN masters m ON a.master_id = m.id
        WHERE EXTRACT(YEAR FROM a.appointment_date) = %s
          AND EXTRACT(MONTH FROM a.appointment_date) = %s


SELECT a.appointment_date::date, a.start_time, a.end_time, 
               m.start_work_time, m.end_work_time
        FROM appointments a
        JOIN masters m ON a.master_id = m.id
        WHERE EXTRACT(YEAR FROM a.appointment_date) = $1
          AND EXTRACT(MONTH FROM a.appointment_date) = $2
          ANd a.stat = $3


SELECT a.id, a.service_id, a.appointment_date, a.start_time,
                                           s.service_name
                                    FROM appointments a
                                    JOIN services s ON a.service_id=s.id

SELECT full_name, comment, rating, DATE(created_at) AS created_date 
FROM reviews 
JOIN clients ON reviews.client_id = clients.id 
ORDER BY created_date 
LIMIT 5


SELECT a.id, a.appointment_date, a.start_time, a.service_id, a.client_id,
                                             s.service_name,
                                             c.full_name,
                                             cn.note
                                    FROM appointments a
                                    JOIN services s ON a.service_id = s.id
                                    JOIN clients c ON a.client_id = c.id
                                    LEFT JOIN client_notes cn ON a.client_id = cn.client_id
                                    WHERE a.appointment_date = $1
                                        AND a.start_time > $2
                                        AND a.stat = $3
                                    ORDER BY a.start_time


SELECT DISTINCT ON (c.id) 
    c.id, 
    c.full_name,
    a.appointment_date,
    a.end_time
FROM clients c
JOIN appointments a ON c.id = a.client_id
WHERE a.stat = $1
ORDER BY c.id, a.appointment_date DESC, a.end_time DESC;
