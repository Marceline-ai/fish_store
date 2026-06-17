"""
Products management widget (CRUD for products).
Implements requirements from section 3.1.1 (Directory management).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QLineEdit, QComboBox, QSpinBox,
                             QMessageBox, QFormLayout, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from dal.database import DatabasePool
from dal.repositories import ProductRepository
from core.validators import (validate_string_not_empty, validate_unit,
                            validate_positive_number)
from core.logger import get_logger

logger = get_logger()


class ProductsWidget(QWidget):
    """Widget for managing products directory."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.product_repo = ProductRepository(db_pool)
        
        self._init_ui()
        self._load_products()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("🐟 Справочник товаров")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Search and actions
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск товара...")
        self.search_edit.textChanged.connect(self._filter_products)
        search_layout.addWidget(self.search_edit)
        
        add_btn = QPushButton("➕ Добавить")
        add_btn.clicked.connect(self._add_product)
        search_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Изменить")
        edit_btn.clicked.connect(self._edit_product)
        search_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self._delete_product)
        search_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._load_products)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Наименование", "Категория", "Ед.изм.", "Срок годности (дн.)", "Условия хранения"
        ])
        
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.doubleClicked.connect(self._edit_product)
        
        layout.addWidget(self.products_table)
        
        self.setLayout(layout)
    
    def _load_products(self):
        """Load products from database."""
        try:
            self.products_table.setRowCount(0)
            products = self.product_repo.get_all()
            
            for product in products:
                row = self.products_table.rowCount()
                self.products_table.insertRow(row)
                
                self.products_table.setItem(row, 0, QTableWidgetItem(str(product['product_id'])))
                self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
                self.products_table.setItem(row, 2, QTableWidgetItem(product['category']))
                self.products_table.setItem(row, 3, QTableWidgetItem(product['unit']))
                self.products_table.setItem(row, 4, QTableWidgetItem(str(product['shelf_life_days'])))
                self.products_table.setItem(row, 5, QTableWidgetItem(product['temp_storage']))
            
            logger.info(f"Loaded {len(products)} products")
            
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить товары:\n{str(e)}")
    
    def _filter_products(self, text: str):
        """Filter products by search text."""
        for row in range(self.products_table.rowCount()):
            match = False
            for col in range(1, 6):  # Skip ID column
                item = self.products_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.products_table.setRowHidden(row, not match)
    
    def _get_selected_product(self):
        """Get selected product data."""
        selected_rows = self.products_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        return {
            'product_id': int(self.products_table.item(row, 0).text()),
            'name': self.products_table.item(row, 1).text(),
            'category': self.products_table.item(row, 2).text(),
            'unit': self.products_table.item(row, 3).text(),
            'shelf_life_days': int(self.products_table.item(row, 4).text()),
            'temp_storage': self.products_table.item(row, 5).text()
        }
    
    def _add_product(self):
        """Add new product."""
        dialog = ProductDialog(self, None)
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_product_data()
            try:
                self.product_repo.create(**product_data)
                QMessageBox.information(self, "Успех", "Товар успешно добавлен")
                self._load_products()
                logger.info(f"Product created: {product_data['name']}")
            except Exception as e:
                logger.error(f"Error creating product: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить товар:\n{str(e)}")
    
    def _edit_product(self):
        """Edit selected product."""
        product = self._get_selected_product()
        if not product:
            QMessageBox.warning(self, "Предупреждение", "Выберите товар для редактирования")
            return
        
        dialog = ProductDialog(self, product)
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_product_data()
            try:
                self.product_repo.update(product['product_id'], **product_data)
                QMessageBox.information(self, "Успех", "Товар успешно обновлен")
                self._load_products()
                logger.info(f"Product updated: {product['product_id']}")
            except Exception as e:
                logger.error(f"Error updating product: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить товар:\n{str(e)}")
    
    def _delete_product(self):
        """Delete selected product."""
        product = self._get_selected_product()
        if not product:
            QMessageBox.warning(self, "Предупреждение", "Выберите товар для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы действительно хотите удалить товар '{product['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.product_repo.delete(product['product_id']):
                    QMessageBox.information(self, "Успех", "Товар успешно удален")
                    self._load_products()
                    logger.info(f"Product deleted: {product['product_id']}")
                else:
                    QMessageBox.warning(
                        self, "Предупреждение",
                        "Не удалось удалить товар.\nВозможно, он используется в других записях."
                    )
            except Exception as e:
                logger.error(f"Error deleting product: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить товар:\n{str(e)}")


class ProductDialog(QDialog):
    """Dialog for adding/editing products."""
    
    def __init__(self, parent, product_data: dict = None):
        super().__init__(parent)
        self.product_data = product_data
        
        self.setWindowTitle("Добавление товара" if product_data is None else "Редактирование товара")
        self.setFixedSize(450, 350)
        self.setModal(True)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(100)
        form_layout.addRow("Наименование:", self.name_edit)
        
        # Category
        self.category_edit = QLineEdit()
        self.category_edit.setMaxLength(50)
        form_layout.addRow("Категория:", self.category_edit)
        
        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['кг', 'шт', 'уп'])
        form_layout.addRow("Ед.изм.:", self.unit_combo)
        
        # Shelf life
        self.shelf_life_spin = QSpinBox()
        self.shelf_life_spin.setRange(1, 3650)
        self.shelf_life_spin.setSuffix(" дн.")
        form_layout.addRow("Срок годности:", self.shelf_life_spin)
        
        # Storage conditions
        self.storage_edit = QLineEdit()
        self.storage_edit.setMaxLength(100)
        form_layout.addRow("Условия хранения:", self.storage_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Load existing data if editing
        if self.product_data:
            self._load_data()
    
    def _load_data(self):
        """Load existing product data into form."""
        self.name_edit.setText(self.product_data['name'])
        self.category_edit.setText(self.product_data['category'])
        self.unit_combo.setCurrentText(self.product_data['unit'])
        self.shelf_life_spin.setValue(self.product_data['shelf_life_days'])
        self.storage_edit.setText(self.product_data['temp_storage'])
    
    def _on_accept(self):
        """Validate and accept dialog."""
        name = self.name_edit.text().strip()
        valid, msg = validate_string_not_empty(name, "Наименование")
        if not valid:
            QMessageBox.warning(self, "Ошибка ввода", msg)
            return
        
        category = self.category_edit.text().strip()
        valid, msg = validate_string_not_empty(category, "Категория")
        if not valid:
            QMessageBox.warning(self, "Ошибка ввода", msg)
            return
        
        unit = self.unit_combo.currentText()
        if not validate_unit(unit):
            QMessageBox.warning(self, "Ошибка ввода", "Неверная единица измерения")
            return
        
        self.accept()
    
    def get_product_data(self) -> dict:
        """Get product data from form."""
        return {
            'name': self.name_edit.text().strip(),
            'category': self.category_edit.text().strip(),
            'unit': self.unit_combo.currentText(),
            'shelf_life_days': self.shelf_life_spin.value(),
            'temp_storage': self.storage_edit.text().strip() or "Стандартные"
        }
