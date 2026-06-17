"""
Main application window.
Implements the main UI with menu, toolbar, and workspace.
"""

from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QAction,
                             QToolBar, QStatusBar, QTabWidget, QWidget,
                             QVBoxLayout, QMessageBox, QLabel)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from dal.database import DatabasePool
from core.logger import get_logger

logger = get_logger()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        
        self.setWindowTitle("FishStore Manager")
        self.setMinimumSize(1366, 768)
        
        # Store role-based permissions
        self.role = user_data['role']
        self._setup_permissions()
        
        self._init_ui()
        logger.info(f"Main window initialized for user: {user_data['full_name']} ({self.role})")
    
    def _setup_permissions(self):
        """Setup role-based permissions."""
        # Role hierarchy: admin > manager > cashier
        self.can_manage_users = self.role == 'admin'
        self.can_manage_products = self.role in ('admin', 'manager')
        self.can_manage_suppliers = self.role in ('admin', 'manager')
        self.can_manage_batches = self.role in ('admin', 'manager')
        self.can_register_sales = True  # All roles can register sales
        self.can_register_write_offs = self.role in ('admin', 'manager')
        self.can_view_reports = True  # All roles can view reports
        self.can_export_data = self.role in ('admin', 'manager')
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Central widget with tabbed interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs based on permissions
        self._create_tabs()
        
        # Setup menu bar
        self._create_menu_bar()
        
        # Setup toolbar
        self._create_toolbar()
        
        # Setup status bar
        self._create_status_bar()
    
    def _create_tabs(self):
        """Create tab pages based on user permissions."""
        # Dashboard (always available)
        dashboard = QLabel("Панель управления\n\nДобро пожаловать, " + 
                          f"{self.user_data['full_name']}!\nРоль: {self._get_role_name()}")
        dashboard.setAlignment(Qt.AlignCenter)
        dashboard.setFont(QFont("Arial", 14))
        self.tab_widget.addTab(dashboard, "📊 Главная")
        
        # Stock/Inventory (always available)
        from ui.stock_widget import StockWidget
        stock_widget = StockWidget(self.db_pool, self.user_data)
        self.tab_widget.addTab(stock_widget, "📦 Остатки")
        
        # Products (admin, manager)
        if self.can_manage_products:
            from ui.products_widget import ProductsWidget
            products_widget = ProductsWidget(self.db_pool, self.user_data)
            self.tab_widget.addTab(products_widget, "🐟 Товары")
        
        # Suppliers (admin, manager)
        if self.can_manage_suppliers:
            from ui.suppliers_widget import SuppliersWidget
            suppliers_widget = SuppliersWidget(self.db_pool, self.user_data)
            self.tab_widget.addTab(suppliers_widget, "🚚 Поставщики")
        
        # Sales (all roles)
        if self.can_register_sales:
            from ui.sales_widget import SalesWidget
            sales_widget = SalesWidget(self.db_pool, self.user_data)
            self.tab_widget.addTab(sales_widget, "💰 Продажи")
        
        # Write-offs (admin, manager)
        if self.can_register_write_offs:
            from ui.writeoffs_widget import WriteOffsWidget
            writeoffs_widget = WriteOffsWidget(self.db_pool, self.user_data)
            self.tab_widget.addTab(writeoffs_widget, "📋 Списания")
        
        # Reports (all roles)
        if self.can_view_reports:
            from ui.reports_widget import ReportsWidget
            reports_widget = ReportsWidget(self.db_pool, self.user_data)
            self.tab_widget.addTab(reports_widget, "📈 Отчёты")
        
        # Users (admin only)
        if self.can_manage_users:
            from ui.users_widget import UsersWidget
            users_widget = UsersWidget(self.db_pool, self.user_data)
            self.tab_widget.addTab(users_widget, "👥 Пользователи")
    
    def _get_role_name(self) -> str:
        """Get human-readable role name."""
        role_names = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'cashier': 'Кассир'
        }
        return role_names.get(self.role, self.role)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Файл")
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Operations menu (based on permissions)
        ops_menu = menubar.addMenu("Операции")
        
        if self.can_register_sales:
            new_sale_action = QAction("Новая продажа", self)
            new_sale_action.setShortcut("Ctrl+S")
            new_sale_action.triggered.connect(lambda: self._switch_to_tab(4))
            ops_menu.addAction(new_sale_action)
        
        if self.can_register_write_offs:
            new_writeoff_action = QAction("Новое списание", self)
            new_writeoff_action.setShortcut("Ctrl+W")
            new_writeoff_action.triggered.connect(lambda: self._switch_to_tab(5))
            ops_menu.addAction(new_writeoff_action)
        
        # Reports menu
        reports_menu = menubar.addMenu("Отчёты")
        
        stock_report_action = QAction("Остатки товаров", self)
        stock_report_action.triggered.connect(lambda: self._switch_to_tab(1))
        reports_menu.addAction(stock_report_action)
        
        sales_report_action = QAction("Продажи", self)
        sales_report_action.triggered.connect(lambda: self._switch_to_tab(6))
        reports_menu.addAction(sales_report_action)
        
        # Help menu
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Главная панель")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Quick access buttons based on permissions
        if self.can_register_sales:
            sale_btn = toolbar.addAction("💰 Продажа")
            sale_btn.triggered.connect(lambda: self._switch_to_tab(4))
        
        if self.can_register_write_offs:
            writeoff_btn = toolbar.addAction("📋 Списание")
            writeoff_btn.triggered.connect(lambda: self._switch_to_tab(5))
        
        toolbar.addSeparator()
        
        stock_btn = toolbar.addAction("📦 Остатки")
        stock_btn.triggered.connect(lambda: self._switch_to_tab(1))
        
        report_btn = toolbar.addAction("📈 Отчёты")
        report_btn.triggered.connect(lambda: self._switch_to_tab(6))
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # User info
        user_info = f"{self.user_data['full_name']} | {self._get_role_name()}"
        self.statusbar.showMessage(user_info)
        
        # Connection status
        if self.db_pool.test_connection():
            self.statusbar.addPermanentWidget(QLabel("✓ БД подключена"))
        else:
            self.statusbar.addPermanentWidget(QLabel("✗ Нет подключения к БД"))
    
    def _switch_to_tab(self, index: int):
        """Switch to a specific tab."""
        if index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "О программе FishStore Manager",
            "<h2>FishStore Manager v1.0</h2>"
            "<p>Система автоматизации учёта товародвижения</p>"
            "<p><b>Заказчик:</b> ИП «Горлов Никита Сергеевич»</p>"
            "<p><b>Разработчик:</b> Студент гр. [номер]</p>"
            "<p>Специальность 09.02.07 «Информационные системы и программирование»</p>"
            "<p>© 2024 Все права защищены</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self, "Выход из программы",
            "Вы действительно хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("User closing application")
            event.accept()
        else:
            event.ignore()
