#!/usr/bin/env python3
"""
Скрипт инициализации первого пользователя (Администратора).
Запускается один раз перед первым входом в приложение.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь, чтобы работали импорты
sys.path.insert(0, str(Path(__file__).parent))

from dal.database import DatabasePool
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

def create_admin_user():
    print("=== Инициализация первого пользователя FishStore ===\n")
    
    # Ввод данных
    full_name = input("Введите ФИО администратора: ").strip()
    if not full_name:
        print("❌ ФИО не может быть пустым.")
        return

    position = input("Введите должность (например, Администратор): ").strip() or "Администратор"
    
    login = input("Введите логин (латиницей): ").strip()
    if not login:
        print("❌ Логин не может быть пустым.")
        return

    while True:
        password = input("Введите пароль: ").strip()
        if len(password) < 4:
            print("❌ Пароль должен быть не менее 4 символов.")
            continue
        confirm_password = input("Подтвердите пароль: ").strip()
        if password != confirm_password:
            print("❌ Пароли не совпадают.")
            continue
        break

    # Хранение пароля в открытом виде (для учебного проекта)
    password_hash = password

    # Подключение к БД и вставка
    print("💾 Сохранение в базу данных...")
    
    try:
        db_pool = DatabasePool()
        with db_pool.get_connection() as conn:
            with conn.cursor() as cur:
                # Проверка существования логина
                cur.execute("SELECT user_id FROM fish_store.users WHERE login = %s", (login,))
                if cur.fetchone():
                    print(f"❌ Пользователь с логином '{login}' уже существует!")
                    return

                # Вставка нового пользователя
                query = """
                    INSERT INTO fish_store.users (full_name, position, login, password_hash, role)
                    VALUES (%s, %s, %s, %s, 'admin')
                    RETURNING user_id;
                """
                cur.execute(query, (full_name, position, login, password_hash))
                user_id = cur.fetchone()[0]
                conn.commit()
                
        print("\n✅ Успешно!")
        print(f"   Пользователь '{login}' (ID: {user_id}) создан с ролью 'admin'.")
        print(f"   Теперь вы можете войти в приложение, используя этот логин и пароль.")
        
    except Exception as e:
        print(f"\n❌ Ошибка при работе с базой данных: {e}")
        print("   Проверьте настройки подключения в файле .env")

if __name__ == "__main__":
    create_admin_user()
