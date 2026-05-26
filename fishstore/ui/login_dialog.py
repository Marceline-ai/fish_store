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
        self.setMinimumSize(500, 450)
        self.resize(500, 450)
        self.setModal(True)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(60, 60, 60, 60)
        
        # Title
        title_label = QLabel("FishStore Manager")
        title_font = QFont("Arial", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Система управления рыбным магазином")
        subtitle_font = QFont("Arial", 12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle_label)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(line)
        
        layout.addSpacing(20)
        
        # Login field
        login_label = QLabel("Логин:")
        login_label.setFont(QFont("Arial", 14))
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите ваш логин")
        self.login_edit.setMaxLength(50)
        self.login_edit.setMinimumHeight(45)
        self.login_edit.setFont(QFont("Arial", 14))
        self.login_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px 15px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(login_label)
        layout.addWidget(self.login_edit)
        
        # Password field
        password_label = QLabel("Пароль:")
        password_label.setFont(QFont("Arial", 14))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите ваш пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(45)
        self.password_edit.setFont(QFont("Arial", 14))
        self.password_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px 15px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(password_label)
        layout.addWidget(self.password_edit)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_button = QPushButton("Войти")
        self.login_button.setMinimumHeight(50)
        self.login_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.login_button.clicked.connect(self._on_login)
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.setFont(QFont("Arial", 14))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #566573;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply styling to the whole window
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
        """)
        
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
