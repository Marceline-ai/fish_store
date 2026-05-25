#!/usr/bin/env python3
"""
Script to add template users to FishStore database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dal.database import DatabasePool
from dal.repositories import UserRepository
import hashlib


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def main():
    # Инициализация пула соединений
    db_pool = DatabasePool.get_instance()

    # Создание репозитория
    user_repo = UserRepository(db_pool)

    # Данные для создания пользователей
    # Должность | Численность
    # Продавец-консультант | 2
    # Кладовщик-экспедитор | 1
    # Администратор-оператор | 2
    
    users_data = [
        # Продавцы-консультанты (2)
        {
            'full_name': 'Иванов Иван Иванович',
            'position': 'Продавец-консультант',
            'login': 'seller_1',
            'password': 'password123',
            'role': 'seller'
        },
        {
            'full_name': 'Петрова Мария Петровна',
            'position': 'Продавец-консультант',
            'login': 'seller_2',
            'password': 'password123',
            'role': 'seller'
        },
        
        # Кладовщик-экспедитор (1)
        {
            'full_name': 'Сидоров Алексей Владимирович',
            'position': 'Кладовщик-экспедитор',
            'login': 'warehouse_1',
            'password': 'password123',
            'role': 'warehouse'
        },
        
        # Администраторы-операторы (2)
        {
            'full_name': 'Козлов Дмитрий Сергеевич',
            'position': 'Администратор-оператор',
            'login': 'operator_1',
            'password': 'password123',
            'role': 'operator'
        },
        {
            'full_name': 'Новикова Елена Александровна',
            'position': 'Администратор-оператор',
            'login': 'operator_2',
            'password': 'password123',
            'role': 'operator'
        },
    ]

    # Добавление пользователей
    print("Добавление пользователей в базу данных...")
    print("=" * 60)
    
    for user_data in users_data:
        password_hash = hash_password(user_data['password'])
        created_user = user_repo.create(
            full_name=user_data['full_name'],
            position=user_data['position'],
            login=user_data['login'],
            password_hash=password_hash,
            role=user_data['role']
        )
        if created_user:
            print(f"✓ Создан пользователь: {created_user['full_name']}")
            print(f"  Логин: {created_user['login']}, Должность: {created_user['position']}, Роль: {created_user['role']}")
        else:
            print(f"✗ Ошибка создания пользователя: {user_data['login']}")
        print()

    db_pool.close_all()
    print("=" * 60)
    print("Все пользователи успешно созданы!")


if __name__ == '__main__':
    main()
