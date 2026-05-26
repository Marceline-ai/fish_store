"""
FishStore Manager - Main Application Entry Point
ИП «Горлов Н.С.» - Автоматизация учёта товародвижения
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTranslator, QLocale
from PyQt5.QtGui import QIcon
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup_logger
from dal.database import DatabasePool
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog


def main():
    """Main application entry point."""
    
    # Setup logging
    logger = setup_logger()
    logger.info("=== FishStore Manager Starting ===")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("FishStore Manager")
    app.setOrganizationName("ИП Горлов Н.С.")
    
    # Set application icon
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, 'resources', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        logger.info(f"Application icon loaded from: {icon_path}")
    else:
        logger.warning(f"Application icon not found at: {icon_path}")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Setup translator for Russian language
    translator = QTranslator()
    if translator.load(QLocale.system(), "", "", ":/translations"):
        app.installTranslator(translator)
    
    try:
        # Initialize database connection pool
        db_pool = DatabasePool.get_instance()
        
        # Test database connection
        if not db_pool.test_connection():
            QMessageBox.critical(
                None,
                "Ошибка подключения",
                "Не удалось подключиться к базе данных.\n"
                "Проверьте настройки подключения в файле .env"
            )
            logger.error("Database connection test failed")
            return 1
        
        logger.info("Database connection established successfully")
        
        # Show login dialog
        login_dialog = LoginDialog(db_pool)
        if login_dialog.exec_() != LoginDialog.Accepted:
            logger.info("Login cancelled by user")
            return 0
        
        user_data = login_dialog.get_user_data()
        logger.info(f"User logged in: {user_data['login']} ({user_data['role']})")
        
        # Create and show main window
        main_window = MainWindow(db_pool, user_data)
        main_window.show()
        
        # Run application event loop
        exit_code = app.exec_()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.exception(f"Critical error during application startup: {e}")
        QMessageBox.critical(
            None,
            "Критическая ошибка",
            f"Произошла критическая ошибка при запуске:\n{str(e)}"
        )
        return 1
    finally:
        # Cleanup database connections
        if 'db_pool' in locals():
            db_pool.close_all()
        logger.info("=== FishStore Manager Shutdown Complete ===")


if __name__ == "__main__":
    sys.exit(main())
