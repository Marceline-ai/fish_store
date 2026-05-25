"""
Stock/Inventory widget showing current stock levels.
Implements requirements from section 3.1.5 (Stock calculation) and 3.1.6 (Expiry control).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont

from dal.database import DatabasePool
from dal.repositories import StockRepository, BatchRepository
from core.logger import get_logger

logger = get_logger()


class StockWidget(QWidget):
    """Widget for viewing current stock levels."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.stock_repo = StockRepository(db_pool)
        self.batch_repo = BatchRepository(db_pool)
        
        self._init_ui()
        self._load_stock_data()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("📦 Текущие остатки товаров")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Info group
        info_group = QGroupBox("Информация")
        info_layout = QHBoxLayout()
        
        self.total_items_label = QLabel("Всего позиций: 0")
        info_layout.addWidget(self.total_items_label)
        
        self.expiring_soon_label = QLabel("Истекает скоро: 0")
        self.expiring_soon_label.setStyleSheet("color: orange; font-weight: bold;")
        info_layout.addWidget(self.expiring_soon_label)
        
        self.expired_label = QLabel("Просрочено: 0")
        self.expired_label.setStyleSheet("color: red; font-weight: bold;")
        info_layout.addWidget(self.expired_label)
        
        info_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._load_stock_data)
        info_layout.addWidget(refresh_btn)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Stock table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels([
            "Товар", "Категория", "Партия", "Остаток", "Ед.изм.", "Срок годности"
        ])
        
        header = self.stock_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.stock_table)
        
        self.setLayout(layout)
    
    def _load_stock_data(self):
        """Load stock data from database."""
        try:
            self.stock_table.setRowCount(0)
            
            stock_items = self.stock_repo.get_current_stock()
            
            today = QDate.currentDate().toPyDate()
            expiring_count = 0
            expired_count = 0
            
            for item in stock_items:
                row = self.stock_table.rowCount()
                self.stock_table.insertRow(row)
                
                # Product name
                name_item = QTableWidgetItem(item['product_name'])
                name_item.setFont(QFont("Arial", 10, QFont.Bold))
                self.stock_table.setItem(row, 0, name_item)
                
                # Category
                self.stock_table.setItem(row, 1, QTableWidgetItem(item['category']))
                
                # Batch number
                batch_num = item['batch_number'] or 'Б/Н'
                self.stock_table.setItem(row, 2, QTableWidgetItem(batch_num))
                
                # Remaining quantity
                qty = float(item['remaining_qty'])
                qty_item = QTableWidgetItem(f"{qty:.3f}")
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.stock_table.setItem(row, 3, qty_item)
                
                # Unit
                # Get unit from product (need to fetch separately or join)
                self.stock_table.setItem(row, 4, QTableWidgetItem("кг"))  # Default
                
                # Expiry date with color coding
                expiry_date = item['expiry_date']
                expiry_item = QTableWidgetItem(expiry_date.strftime("%d.%m.%Y"))
                
                # Calculate days until expiry
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry < 0:
                    # Expired - red background
                    expiry_item.setBackground(QColor(255, 150, 150))
                    expiry_item.setForeground(QColor(100, 0, 0))
                    expired_count += 1
                elif days_until_expiry <= 3:
                    # Expiring soon - yellow/orange background
                    expiry_item.setBackground(QColor(255, 255, 150))
                    expiry_item.setForeground(QColor(100, 80, 0))
                    expiring_count += 1
                else:
                    # Normal - green text
                    expiry_item.setForeground(QColor(0, 100, 0))
                
                self.stock_table.setItem(row, 5, expiry_item)
            
            # Update info labels
            self.total_items_label.setText(f"Всего позиций: {len(stock_items)}")
            self.expiring_soon_label.setText(f"Истекает скоро: {expiring_count}")
            self.expired_label.setText(f"Просрочено: {expired_count}")
            
            if expired_count > 0:
                QMessageBox.warning(
                    self, "Внимание!",
                    f"Обнаружено {expired_count} просроченных товаров!\n"
                    "Необходимо оформить списание."
                )
            
            logger.info(f"Stock data loaded: {len(stock_items)} items")
            
        except Exception as e:
            logger.error(f"Error loading stock data: {e}")
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось загрузить данные об остатках:\n{str(e)}"
            )
