"""
Login dialog for user authentication.
Implements requirements from section 3.1.9 (Authorization and roles).
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from dal.database import DatabasePool
from dal.repositories import UserRepository
from core.validators import validate_login


class LoginDialog(QDialog):
    """Login dialog for user authentication."""
    
    def __init__(self, db_pool: DatabasePool, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_repo = UserRepository(db_pool)
        self._user_data = None
        
        self.setWindowTitle("FishStore Manager - Вход в систему")
        self.setFixedSize(400, 250)
        self.setModal(True)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("FishStore Manager")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Вход в систему")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(20)
        
        # Login field
        login_layout = QHBoxLayout()
        login_label = QLabel("Логин:")
        login_label.setFixedWidth(80)
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите логин")
        self.login_edit.setMaxLength(50)
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_edit)
        layout.addLayout(login_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Пароль:")
        password_label.setFixedWidth(80)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.login_button = QPushButton("Войти")
        self.login_button.setFixedWidth(100)
        self.login_button.clicked.connect(self._on_login)
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect Enter key to login
        self.password_edit.returnPressed.connect(self._on_login)
    
    def _on_login(self):
        """Handle login button click."""
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        
        # Validate login format
        if not validate_login(login):
            QMessageBox.warning(
                self, "Ошибка ввода",
                "Логин должен содержать от 3 до 50 символов\n"
                "(буквы, цифры, подчеркивание)"
            )
            return
        
        if not password:
            QMessageBox.warning(self, "Ошибка ввода", "Введите пароль")
            return
        
        try:
            # Get user from database
            user = self.user_repo.get_by_login(login)
            
            if user is None:
                QMessageBox.warning(
                    self, "Ошибка входа",
                    "Неверный логин или пароль"
                )
                return
            
            # Verify password (plain text for educational project)
            if password != user['password_hash']:
                QMessageBox.warning(
                    self, "Ошибка входа",
                    "Неверный логин или пароль"
                )
                return
            
            # Login successful
            self._user_data = {
                'user_id': user['user_id'],
                'full_name': user['full_name'],
                'position': user['position'],
                'login': user['login'],
                'role': user['role']
            }
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Произошла ошибка при входе:\n{str(e)}"
            )
    
    def get_user_data(self) -> dict:
        """Get authenticated user data."""
        return self._user_data
