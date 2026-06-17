"""
Users management widget (admin only).
Implements requirements from section 3.1.1 (Directory management) and 3.1.9 (Authorization).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QLineEdit, QComboBox, QMessageBox,
                             QFormLayout, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from dal.database import DatabasePool
from dal.repositories import UserRepository
from core.validators import validate_login, validate_password, validate_string_not_empty, validate_role
from core.logger import get_logger

logger = get_logger()

ROLE_CHOICES = [
    ('admin', 'Администратор'),
    ('manager', 'Менеджер'),
    ('cashier', 'Кассир')
]


class UsersWidget(QWidget):
    """Widget for managing system users (admin only)."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.user_repo = UserRepository(db_pool)
        
        self._init_ui()
        self._load_users()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("👥 Пользователи системы")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Добавить")
        add_btn.clicked.connect(self._add_user)
        action_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Изменить")
        edit_btn.clicked.connect(self._edit_user)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self._delete_user)
        action_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._load_users)
        action_layout.addWidget(refresh_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Должность", "Логин", "Роль"
        ])
        
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.doubleClicked.connect(self._edit_user)
        
        layout.addWidget(self.users_table)
        self.setLayout(layout)
    
    def _load_users(self):
        try:
            self.users_table.setRowCount(0)
            users = self.user_repo.get_all()
            
            role_names = {r[0]: r[1] for r in ROLE_CHOICES}
            
            for user in users:
                row = self.users_table.rowCount()
                self.users_table.insertRow(row)
                
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user['user_id'])))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['full_name']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user['position']))
                self.users_table.setItem(row, 3, QTableWidgetItem(user['login']))
                
                role_name = role_names.get(user['role'], user['role'])
                self.users_table.setItem(row, 4, QTableWidgetItem(role_name))
            
            logger.info(f"Loaded {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить пользователей:\n{str(e)}")
    
    def _get_selected_user(self):
        selected_rows = self.users_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        return {
            'user_id': int(self.users_table.item(row, 0).text()),
            'full_name': self.users_table.item(row, 1).text(),
            'position': self.users_table.item(row, 2).text(),
            'login': self.users_table.item(row, 3).text(),
            'role': self.users_table.item(row, 4).text()
        }
    
    def _add_user(self):
        dialog = UserDialog(self, None)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            try:
                # Store password in plain text (for educational project)
                password_hash = user_data.pop('password')
                
                self.user_repo.create(password_hash=password_hash, **user_data)
                QMessageBox.information(self, "Успех", "Пользователь успешно добавлен")
                self._load_users()
                logger.info(f"User created: {user_data['login']}")
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить пользователя:\n{str(e)}")
    
    def _edit_user(self):
        user = self._get_selected_user()
        if not user:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для редактирования")
            return
        
        dialog = UserDialog(self, user)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            try:
                # Update password if changed (plain text for educational project)
                if 'password' in user_data and user_data['password']:
                    password_hash = user_data.pop('password')
                    self.user_repo.update_password(user['user_id'], password_hash)
                
                self.user_repo.update(user['user_id'], **user_data)
                QMessageBox.information(self, "Успех", "Пользователь успешно обновлен")
                self._load_users()
                logger.info(f"User updated: {user['user_id']}")
            except Exception as e:
                logger.error(f"Error updating user: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить пользователя:\n{str(e)}")
    
    def _delete_user(self):
        user = self._get_selected_user()
        if not user:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для удаления")
            return
        
        # Prevent deleting yourself
        if user['user_id'] == self.user_data['user_id']:
            QMessageBox.warning(self, "Предупреждение", "Нельзя удалить свою собственную учётную запись")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы действительно хотите удалить пользователя '{user['full_name']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.user_repo.delete(user['user_id']):
                    QMessageBox.information(self, "Успех", "Пользователь успешно удален")
                    self._load_users()
                    logger.info(f"User deleted: {user['user_id']}")
                else:
                    QMessageBox.warning(self, "Предупреждение",
                        "Не удалось удалить пользователя.\nВозможно, он используется в других записях.")
            except Exception as e:
                logger.error(f"Error deleting user: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить пользователя:\n{str(e)}")


class UserDialog(QDialog):
    """Dialog for adding/editing users."""
    
    def __init__(self, parent, user_data: dict = None):
        super().__init__(parent)
        self.user_data = user_data
        
        self.setWindowTitle("Добавление пользователя" if user_data is None else "Редактирование пользователя")
        self.setFixedSize(450, 400)
        self.setModal(True)
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setMaxLength(100)
        form_layout.addRow("ФИО:", self.full_name_edit)
        
        self.position_edit = QLineEdit()
        self.position_edit.setMaxLength(50)
        form_layout.addRow("Должность:", self.position_edit)
        
        self.login_edit = QLineEdit()
        self.login_edit.setMaxLength(50)
        if self.user_data:
            self.login_edit.setEnabled(False)  # Can't change login
        form_layout.addRow("Логин:", self.login_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        placeholder = "Новый пароль" if self.user_data else "Пароль"
        self.password_edit.setPlaceholderText(placeholder)
        form_layout.addRow("Пароль:", self.password_edit)
        
        self.role_combo = QComboBox()
        for code, name in ROLE_CHOICES:
            self.role_combo.addItem(name, code)
        form_layout.addRow("Роль:", self.role_combo)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        if self.user_data:
            self._load_data()
    
    def _load_data(self):
        self.full_name_edit.setText(self.user_data['full_name'])
        self.position_edit.setText(self.user_data['position'])
        self.login_edit.setText(self.user_data['login'])
        
        # Find and select role
        role_code = self.user_data.get('role', 'cashier')
        # Parse role from Russian name
        role_map = {'Администратор': 'admin', 'Менеджер': 'manager', 'Кассир': 'cashier'}
        actual_code = role_map.get(role_code, role_code)
        
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == actual_code:
                self.role_combo.setCurrentIndex(i)
                break
    
    def _on_accept(self):
        full_name = self.full_name_edit.text().strip()
        valid, msg = validate_string_not_empty(full_name, "ФИО")
        if not valid:
            QMessageBox.warning(self, "Ошибка ввода", msg)
            return
        
        position = self.position_edit.text().strip()
        valid, msg = validate_string_not_empty(position, "Должность")
        if not valid:
            QMessageBox.warning(self, "Ошибка ввода", msg)
            return
        
        login = self.login_edit.text().strip()
        if not self.user_data:  # Only validate login for new users
            if not validate_login(login):
                QMessageBox.warning(self, "Ошибка ввода", "Неверный формат логина")
                return
        
        password = self.password_edit.text()
        if not self.user_data or password:  # Password required for new, optional for edit
            valid, msg = validate_password(password)
            if not valid:
                QMessageBox.warning(self, "Ошибка ввода", msg)
                return
        
        self.accept()
    
    def get_user_data(self) -> dict:
        data = {
            'full_name': self.full_name_edit.text().strip(),
            'position': self.position_edit.text().strip(),
            'role': self.role_combo.itemData(self.role_combo.currentIndex())
        }
        
        if not self.user_data:
            data['login'] = self.login_edit.text().strip()
        
        password = self.password_edit.text()
        if password:
            data['password'] = password
        
        return data
