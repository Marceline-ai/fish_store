-- Скрипт инициализации базы данных FishStore
-- Выполняется после создания схемы из ТЗ

SET search_path TO fish_store;

-- Создаём первого администратора (пароль: admin123)
-- Хэш сгенерирован через bcrypt
INSERT INTO users (full_name, position, login, password_hash, role) VALUES
('Администратор', 'Администратор системы', 'admin', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS7MebO2e', 
 'admin')
ON CONFLICT (login) DO NOTHING;

-- Пример данных для тестирования (опционально)
-- Товары
INSERT INTO products (name, category, unit, shelf_life_days, temp_storage) VALUES
('Лосось свежий', 'Рыба свежая', 'кг', 7, 'Холодильник 0..+4°C'),
('Сельдь солёная', 'Рыба солёная', 'кг', 30, 'Холодильник 0..+6°C'),
('Икра красная', 'Икра', 'уп', 120, 'Холодильник -4..-6°C'),
('Креветки тигровые', 'Морепродукты', 'кг', 90, 'Морозильник -18°C')
ON CONFLICT DO NOTHING;

-- Поставщики
INSERT INTO suppliers (name, inn, phone, email, address) VALUES
('ООО "Рыбпром"', '7701234567', '+7(495)123-45-67', 'info@rybprom.ru', 'г. Москва, ул. Рыбная, д. 1'),
('ИП Иванов А.А.', '770123456789', '+7(999)123-45-67', 'ivanov@mail.ru', 'г. Москва, ул. Торговая, д. 5')
ON CONFLICT DO NOTHING;
