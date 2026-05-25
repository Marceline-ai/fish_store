"""
Sales registration widget.
Implements requirements from section 3.1.3 (Sales registration).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QComboBox, QDoubleSpinBox, QSpinBox,
                             QMessageBox, QFormLayout, QDialog, QDialogButtonBox,
                             QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from dal.database import DatabasePool
from dal.repositories import StockRepository, ProductRepository, SaleRepository
from core.validators import validate_quantity, validate_price
from core.logger import get_logger

logger = get_logger()


class SalesWidget(QWidget):
    """Widget for registering and viewing sales."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.stock_repo = StockRepository(db_pool)
        self.product_repo = ProductRepository(db_pool)
        self.sale_repo = SaleRepository(db_pool)
        
        self._init_ui()
        self._load_sales_history()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("💰 Регистрация продаж")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        new_sale_btn = QPushButton("➕ Новая продажа")
        new_sale_btn.clicked.connect(self._new_sale)
        action_layout.addWidget(new_sale_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._load_sales_history)
        action_layout.addWidget(refresh_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Sales history table
        history_group = QGroupBox("История продаж")
        history_layout = QVBoxLayout()
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels([
            "Дата/Время", "Товар", "Партия", "Кол-во", "Цена за ед.", "Сумма"
        ])
        
        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        history_layout.addWidget(self.sales_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        self.setLayout(layout)
    
    def _load_sales_history(self):
        try:
            self.sales_table.setRowCount(0)
            
            # Get last 100 sales
            query = """
                SELECT s.sale_id, s.sale_date, s.quantity, s.sale_price,
                       p.name AS product_name, b.batch_number
                FROM fish_store.sales s
                JOIN fish_store.products p ON s.product_id = p.product_id
                JOIN fish_store.batches b ON s.batch_id = b.batch_id
                ORDER BY s.sale_date DESC
                LIMIT 100
            """
            sales = self.db_pool.execute_query(query)
            
            for sale in sales:
                row = self.sales_table.rowCount()
                self.sales_table.insertRow(row)
                
                date_str = sale['sale_date'].strftime("%d.%m.%Y %H:%M")
                self.sales_table.setItem(row, 0, QTableWidgetItem(date_str))
                self.sales_table.setItem(row, 1, QTableWidgetItem(sale['product_name']))
                self.sales_table.setItem(row, 2, QTableWidgetItem(sale['batch_number'] or 'Б/Н'))
                
                qty_item = QTableWidgetItem(f"{float(sale['quantity']):.3f}")
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(row, 3, qty_item)
                
                price_item = QTableWidgetItem(f"{float(sale['sale_price']):.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(row, 4, price_item)
                
                total = float(sale['quantity']) * float(sale['sale_price'])
                total_item = QTableWidgetItem(f"{total:.2f}")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                total_item.setFont(QFont("Arial", 10, QFont.Bold))
                self.sales_table.setItem(row, 5, total_item)
            
            logger.info(f"Loaded {len(sales)} sales records")
            
        except Exception as e:
            logger.error(f"Error loading sales: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю продаж:\n{str(e)}")
    
    def _new_sale(self):
        dialog = SaleDialog(self.db_pool, self.user_data)
        if dialog.exec_() == QDialog.Accepted:
            self._load_sales_history()


class SaleDialog(QDialog):
    """Dialog for registering a new sale."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.stock_repo = StockRepository(db_pool)
        self.product_repo = ProductRepository(db_pool)
        self.sale_repo = SaleRepository(db_pool)
        
        self.setWindowTitle("Новая продажа")
        self.setFixedSize(500, 450)
        self.setModal(True)
        
        self._init_ui()
        self._load_products()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Product selection
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self._on_product_changed)
        form_layout.addRow("Товар:", self.product_combo)
        
        # Batch selection
        self.batch_combo = QComboBox()
        self.batch_combo.currentIndexChanged.connect(self._on_batch_changed)
        form_layout.addRow("Партия:", self.batch_combo)
        
        # Available quantity label
        self.avail_label = QLabel("Доступно: -")
        self.avail_label.setStyleSheet("color: green; font-weight: bold;")
        form_layout.addRow("", self.avail_label)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.001, 9999.999)
        self.quantity_spin.setDecimals(3)
        self.quantity_spin.setSuffix(" кг")
        form_layout.addRow("Количество:", self.quantity_spin)
        
        # Price
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 99999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("₽ ")
        form_layout.addRow("Цена за ед.:", self.price_spin)
        
        layout.addLayout(form_layout)
        
        # Total label
        self.total_label = QLabel("Итого: 0.00 ₽")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.total_label)
        
        self.quantity_spin.valueChanged.connect(self._update_total)
        self.price_spin.valueChanged.connect(self._update_total)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _load_products(self):
        products = self.product_repo.get_all()
        for product in products:
            self.product_combo.addItem(f"{product['name']} ({product['category']})", product['product_id'])
    
    def _on_product_changed(self, index):
        self.batch_combo.clear()
        self.avail_label.setText("Доступно: -")
        
        if index < 0:
            return
        
        product_id = self.product_combo.itemData(index)
        stock_items = self.stock_repo.get_product_stock(product_id)
        
        for item in stock_items:
            remaining = float(item['remaining_qty'])
            batch_text = f"{item['batch_number'] or 'Б/Н'} (остаток: {remaining:.3f}, до: {item['expiry_date']})"
            self.batch_combo.addItem(batch_text, item['batch_id'] if 'batch_id' in item else None)
        
        if self.batch_combo.count() > 0:
            self._on_batch_changed(0)
    
    def _on_batch_changed(self, index):
        if index >= 0 and self.batch_combo.count() > 0:
            # Parse available quantity from text
            batch_text = self.batch_combo.currentText()
            try:
                # Extract quantity from text like "Batch123 (остаток: 5.500, до: 01.01.2025)"
                start = batch_text.find("остаток: ") + 9
                end = batch_text.find(",", start)
                if start > 8 and end > start:
                    avail_qty = float(batch_text[start:end])
                    self.avail_label.setText(f"Доступно: {avail_qty:.3f} кг")
                    self.quantity_spin.setMaximum(avail_qty)
            except:
                pass
    
    def _update_total(self):
        qty = self.quantity_spin.value()
        price = self.price_spin.value()
        total = qty * price
        self.total_label.setText(f"Итого: {total:.2f} ₽")
    
    def _on_accept(self):
        if self.product_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка ввода", "Выберите товар")
            return
        
        if self.batch_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка ввода", "Выберите партию")
            return
        
        qty = self.quantity_spin.value()
        if not validate_quantity(qty):
            QMessageBox.warning(self, "Ошибка ввода", "Неверное количество")
            return
        
        price = self.price_spin.value()
        if not validate_price(price):
            QMessageBox.warning(self, "Ошибка ввода", "Неверная цена")
            return
        
        # Check available quantity
        avail_text = self.avail_label.text()
        try:
            start = avail_text.find(": ") + 2
            end = avail_text.find(" ", start)
            avail_qty = float(avail_text[start:end])
            if qty > avail_qty:
                QMessageBox.warning(self, "Ошибка", f"Недостаточно товара. Доступно: {avail_qty:.3f}")
                return
        except:
            pass
        
        try:
            product_id = self.product_combo.itemData(self.product_combo.currentIndex())
            batch_item = self.batch_combo.currentData()
            
            # If batch_id is stored differently, we need to get it
            # For now, use first available batch
            stock_items = self.stock_repo.get_product_stock(product_id)
            if stock_items:
                batch_id = stock_items[self.batch_combo.currentIndex()]['batch_id'] if 'batch_id' in stock_items[0] else None
                
                if batch_id:
                    self.sale_repo.create(
                        batch_id=batch_id,
                        product_id=product_id,
                        user_id=self.user_data['user_id'],
                        quantity=qty,
                        sale_price=price
                    )
                    QMessageBox.information(self, "Успех", "Продажа успешно зарегистрирована")
                    logger.info(f"Sale registered: product={product_id}, qty={qty}")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось определить партию")
            else:
                QMessageBox.warning(self, "Ошибка", "Нет доступных остатков")
                
        except Exception as e:
            logger.error(f"Error registering sale: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось оформить продажу:\n{str(e)}")
