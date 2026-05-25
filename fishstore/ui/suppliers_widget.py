"""
Suppliers management widget (CRUD for suppliers).
Implements requirements from section 3.1.1 (Directory management).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QLineEdit, QTextEdit, QMessageBox,
                             QFormLayout, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from dal.database import DatabasePool
from dal.repositories import SupplierRepository
from core.validators import validate_inn, validate_email, validate_phone, validate_string_not_empty
from core.logger import get_logger

logger = get_logger()


class SuppliersWidget(QWidget):
    """Widget for managing suppliers directory."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self.supplier_repo = SupplierRepository(db_pool)
        
        self._init_ui()
        self._load_suppliers()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("🚚 Справочник поставщиков")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск поставщика...")
        self.search_edit.textChanged.connect(self._filter_suppliers)
        search_layout.addWidget(self.search_edit)
        
        add_btn = QPushButton("➕ Добавить")
        add_btn.clicked.connect(self._add_supplier)
        search_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Изменить")
        edit_btn.clicked.connect(self._edit_supplier)
        search_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self._delete_supplier)
        search_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._load_suppliers)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(6)
        self.suppliers_table.setHorizontalHeaderLabels([
            "ID", "Наименование", "ИНН", "Телефон", "Email", "Адрес"
        ])
        
        header = self.suppliers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        self.suppliers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.suppliers_table.doubleClicked.connect(self._edit_supplier)
        
        layout.addWidget(self.suppliers_table)
        self.setLayout(layout)
    
    def _load_suppliers(self):
        try:
            self.suppliers_table.setRowCount(0)
            suppliers = self.supplier_repo.get_all()
            
            for supplier in suppliers:
                row = self.suppliers_table.rowCount()
                self.suppliers_table.insertRow(row)
                
                self.suppliers_table.setItem(row, 0, QTableWidgetItem(str(supplier['supplier_id'])))
                self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier['name']))
                self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier['inn'] or ''))
                self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier['phone'] or ''))
                self.suppliers_table.setItem(row, 4, QTableWidgetItem(supplier['email'] or ''))
                self.suppliers_table.setItem(row, 5, QTableWidgetItem(supplier['address'] or ''))
            
            logger.info(f"Loaded {len(suppliers)} suppliers")
        except Exception as e:
            logger.error(f"Error loading suppliers: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить поставщиков:\n{str(e)}")
    
    def _filter_suppliers(self, text: str):
        for row in range(self.suppliers_table.rowCount()):
            match = False
            for col in range(1, 6):
                item = self.suppliers_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.suppliers_table.setRowHidden(row, not match)
    
    def _get_selected_supplier(self):
        selected_rows = self.suppliers_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        return {
            'supplier_id': int(self.suppliers_table.item(row, 0).text()),
            'name': self.suppliers_table.item(row, 1).text(),
            'inn': self.suppliers_table.item(row, 2).text(),
            'phone': self.suppliers_table.item(row, 3).text(),
            'email': self.suppliers_table.item(row, 4).text(),
            'address': self.suppliers_table.item(row, 5).text()
        }
    
    def _add_supplier(self):
        dialog = SupplierDialog(self, None)
        if dialog.exec_() == QDialog.Accepted:
            supplier_data = dialog.get_supplier_data()
            try:
                self.supplier_repo.create(**supplier_data)
                QMessageBox.information(self, "Успех", "Поставщик успешно добавлен")
                self._load_suppliers()
                logger.info(f"Supplier created: {supplier_data['name']}")
            except Exception as e:
                logger.error(f"Error creating supplier: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить поставщика:\n{str(e)}")
    
    def _edit_supplier(self):
        supplier = self._get_selected_supplier()
        if not supplier:
            QMessageBox.warning(self, "Предупреждение", "Выберите поставщика для редактирования")
            return
        
        dialog = SupplierDialog(self, supplier)
        if dialog.exec_() == QDialog.Accepted:
            supplier_data = dialog.get_supplier_data()
            try:
                self.supplier_repo.update(supplier['supplier_id'], **supplier_data)
                QMessageBox.information(self, "Успех", "Поставщик успешно обновлен")
                self._load_suppliers()
                logger.info(f"Supplier updated: {supplier['supplier_id']}")
            except Exception as e:
                logger.error(f"Error updating supplier: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить поставщика:\n{str(e)}")
    
    def _delete_supplier(self):
        supplier = self._get_selected_supplier()
        if not supplier:
            QMessageBox.warning(self, "Предупреждение", "Выберите поставщика для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы действительно хотите удалить поставщика '{supplier['name']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.supplier_repo.delete(supplier['supplier_id']):
                    QMessageBox.information(self, "Успех", "Поставщик успешно удален")
                    self._load_suppliers()
                    logger.info(f"Supplier deleted: {supplier['supplier_id']}")
                else:
                    QMessageBox.warning(self, "Предупреждение",
                        "Не удалось удалить поставщика.\nВозможно, он используется в других записях.")
            except Exception as e:
                logger.error(f"Error deleting supplier: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить поставщика:\n{str(e)}")


class SupplierDialog(QDialog):
    def __init__(self, parent, supplier_data: dict = None):
        super().__init__(parent)
        self.supplier_data = supplier_data
        self.setWindowTitle("Добавление поставщика" if supplier_data is None else "Редактирование поставщика")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(150)
        form_layout.addRow("Наименование:", self.name_edit)
        
        self.inn_edit = QLineEdit()
        self.inn_edit.setMaxLength(12)
        form_layout.addRow("ИНН:", self.inn_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setMaxLength(20)
        form_layout.addRow("Телефон:", self.phone_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setMaxLength(100)
        form_layout.addRow("Email:", self.email_edit)
        
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(80)
        form_layout.addRow("Адрес:", self.address_edit)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        if self.supplier_data:
            self._load_data()
    
    def _load_data(self):
        self.name_edit.setText(self.supplier_data['name'])
        self.inn_edit.setText(self.supplier_data['inn'] or '')
        self.phone_edit.setText(self.supplier_data['phone'] or '')
        self.email_edit.setText(self.supplier_data['email'] or '')
        self.address_edit.setText(self.supplier_data['address'] or '')
    
    def _on_accept(self):
        name = self.name_edit.text().strip()
        valid, msg = validate_string_not_empty(name, "Наименование")
        if not valid:
            QMessageBox.warning(self, "Ошибка ввода", msg)
            return
        
        inn = self.inn_edit.text().strip()
        if inn and not validate_inn(inn):
            QMessageBox.warning(self, "Ошибка ввода", "Неверный формат ИНН (10 или 12 цифр)")
            return
        
        email = self.email_edit.text().strip()
        if email and not validate_email(email):
            QMessageBox.warning(self, "Ошибка ввода", "Неверный формат Email")
            return
        
        phone = self.phone_edit.text().strip()
        if phone and not validate_phone(phone):
            QMessageBox.warning(self, "Ошибка ввода", "Неверный формат телефона")
            return
        
        self.accept()
    
    def get_supplier_data(self) -> dict:
        return {
            'name': self.name_edit.text().strip(),
            'inn': self.inn_edit.text().strip() or None,
            'phone': self.phone_edit.text().strip() or None,
            'email': self.email_edit.text().strip() or None,
            'address': self.address_edit.toPlainText().strip() or None
        }
