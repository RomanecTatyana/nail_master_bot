-- Вставим одного мастера
INSERT INTO masters (telegram_id, full_name, start_work_time, end_work_time)
VALUES (111000222, 'Олена Майстер', '09:00', '18:00');

-- Вставим 5 клиентов
INSERT INTO clients (telegram_id, full_name, phone)
VALUES 
(100000001, 'Марина Іваненко', '+380501112233'),
(100000002, 'Анна Петрівна', '+380501234567'),
(100000003, 'Ірина Коваленко', '+380509876543'),
(100000004, 'Катерина Шевченко', '+380508888888'),
(100000005, 'Ольга Довженко', '+380507777777');

-- Вставим 3 услуги
INSERT INTO services (service_name, duration_minutes)
VALUES 
('Манікюр класичний', 60),
('Манікюр + гель-лак', 90),
('Зняття + нове покриття', 120);

-- Вставим несколько записей к мастеру
INSERT INTO appointments (client_id, service_id, master_id, appointment_date, start_time, end_time)
VALUES 
(1, 1, 1, '2025-05-22', '10:00', '11:00'),
(2, 2, 1, '2025-05-22', '11:30', '13:00'),
(3, 3, 1, '2025-05-23', '09:00', '11:00');

-- Добавим пару отзывов
INSERT INTO reviews (client_id, master_id, appointment_id, rating, comment)
VALUES 
(1, 1, 1, 5, 'Дуже задоволена результатом!'),
(2, 1, 2, 4, 'Все добре, але довго чекала.');

-- Добавим заметку мастера о клиенте
INSERT INTO client_notes (client_id, master_id, note)
VALUES 
(3, 1, 'Не любить червоний колір');
