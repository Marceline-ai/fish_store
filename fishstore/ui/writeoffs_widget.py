"""
Write-offs registration widget.
Implements requirements from section 3.1.4 (Write-offs registration).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QComboBox, QDoubleSpinBox,
                             QMessageBox, QFormLayout, QDialog, QDialogButtonBox,
                             QGroupBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from dal.database import DatabasePool
from dal.repositories import StockRepository, ProductRepository, WriteOffRepository
from core.validators import validate_quantity, validate_write_off_reason
from core.logger import get_logger

logger = get_logger()

REASON_CHOICES = [
    ('expired', 'Истечение срока годности'),
    ('damaged', 'Порча/Бой'),
    ('quality_check', 'Контроль качества'),
    ('other', 'Прочее')
]


class WriteOffsWidget(QWidget):
    """Widget for registering and viewing write-offs."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.stock_repo = StockRepository(db_pool)
        self.product_repo = ProductRepository(db_pool)
        self.writeoff_repo = WriteOffRepository(db_pool)
        
        self._init_ui()
        self._load_writeoffs_history()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("📋 Регистрация списаний")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        action_layout = QHBoxLayout()
        
        new_writeoff_btn = QPushButton("➕ Новое списание")
        new_writeoff_btn.clicked.connect(self._new_writeoff)
        action_layout.addWidget(new_writeoff_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._load_writeoffs_history)
        action_layout.addWidget(refresh_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        history_group = QGroupBox("История списаний")
        history_layout = QVBoxLayout()
        
        self.writeoffs_table = QTableWidget()
        self.writeoffs_table.setColumnCount(5)
        self.writeoffs_table.setHorizontalHeaderLabels([
            "Дата", "Товар", "Кол-во", "Причина", "Ответственный"
        ])
        
        header = self.writeoffs_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.writeoffs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.writeoffs_table.setAlternatingRowColors(True)
        self.writeoffs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        history_layout.addWidget(self.writeoffs_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        self.setLayout(layout)
    
    def _load_writeoffs_history(self):
        try:
            self.writeoffs_table.setRowCount(0)
            
            query = """
                SELECT w.write_off_id, w.write_off_date, w.quantity, w.reason,
                       p.name AS product_name, u.full_name AS user_name
                FROM fish_store.write_offs w
                JOIN fish_store.products p ON w.product_id = p.product_id
                JOIN fish_store.users u ON w.user_id = u.user_id
                ORDER BY w.write_off_date DESC
                LIMIT 100
            """
            writeoffs = self.db_pool.execute_query(query)
            
            reason_names = {r[0]: r[1] for r in REASON_CHOICES}
            
            for wo in writeoffs:
                row = self.writeoffs_table.rowCount()
                self.writeoffs_table.insertRow(row)
                
                date_str = wo['write_off_date'].strftime("%d.%m.%Y")
                self.writeoffs_table.setItem(row, 0, QTableWidgetItem(date_str))
                self.writeoffs_table.setItem(row, 1, QTableWidgetItem(wo['product_name']))
                
                qty_item = QTableWidgetItem(f"{float(wo['quantity']):.3f}")
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.writeoffs_table.setItem(row, 2, qty_item)
                
                reason_name = reason_names.get(wo['reason'], wo['reason'])
                self.writeoffs_table.setItem(row, 3, QTableWidgetItem(reason_name))
                self.writeoffs_table.setItem(row, 4, QTableWidgetItem(wo['user_name']))
            
            logger.info(f"Loaded {len(writeoffs)} write-off records")
            
        except Exception as e:
            logger.error(f"Error loading write-offs: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю списаний:\n{str(e)}")
    
    def _new_writeoff(self):
        dialog = WriteOffDialog(self.db_pool, self.user_data)
        if dialog.exec_() == QDialog.Accepted:
            self._load_writeoffs_history()


class WriteOffDialog(QDialog):
    """Dialog for registering a new write-off."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.stock_repo = StockRepository(db_pool)
        self.product_repo = ProductRepository(db_pool)
        self.writeoff_repo = WriteOffRepository(db_pool)
        
        self.setWindowTitle("Новое списание")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self._init_ui()
        self._load_products()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self._on_product_changed)
        form_layout.addRow("Товар:", self.product_combo)
        
        self.batch_combo = QComboBox()
        form_layout.addRow("Партия:", self.batch_combo)
        
        self.avail_label = QLabel("Доступно: -")
        self.avail_label.setStyleSheet("color: green; font-weight: bold;")
        form_layout.addRow("", self.avail_label)
        
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.001, 9999.999)
        self.quantity_spin.setDecimals(3)
        self.quantity_spin.setSuffix(" кг")
        form_layout.addRow("Количество:", self.quantity_spin)
        
        self.reason_combo = QComboBox()
        for code, name in REASON_CHOICES:
            self.reason_combo.addItem(name, code)
        form_layout.addRow("Причина:", self.reason_combo)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Дата:", self.date_edit)
        
        layout.addLayout(form_layout)
        
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
            batch_text = f"{item['batch_number'] or 'Б/Н'} (остаток: {remaining:.3f})"
            self.batch_combo.addItem(batch_text, item.get('batch_id'))
        
        if self.batch_combo.count() > 0:
            self._update_avail_label()
    
    def _update_avail_label(self):
        if self.batch_combo.count() > 0:
            batch_text = self.batch_combo.currentText()
            try:
                start = batch_text.find("остаток: ") + 9
                end = batch_text.find(")", start)
                if start > 8 and end > start:
                    avail_qty = float(batch_text[start:end])
                    self.avail_label.setText(f"Доступно: {avail_qty:.3f} кг")
                    self.quantity_spin.setMaximum(avail_qty)
            except:
                pass
    
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
        
        reason = self.reason_combo.itemData(self.reason_combo.currentIndex())
        if not validate_write_off_reason(reason):
            QMessageBox.warning(self, "Ошибка ввода", "Неверная причина списания")
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
            batch_id = self.batch_combo.currentData()
            write_off_date = self.date_edit.date().toPyDate()
            
            if batch_id:
                self.writeoff_repo.create(
                    batch_id=batch_id,
                    product_id=product_id,
                    user_id=self.user_data['user_id'],
                    quantity=qty,
                    reason=reason,
                    write_off_date=write_off_date
                )
                QMessageBox.information(self, "Успех", "Списание успешно зарегистрировано")
                logger.info(f"Write-off registered: product={product_id}, qty={qty}, reason={reason}")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить партию")
                
        except Exception as e:
            logger.error(f"Error registering write-off: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось оформить списание:\n{str(e)}")
