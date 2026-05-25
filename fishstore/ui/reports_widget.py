"""
Reports widget for generating various reports.
Implements requirements from section 3.1.7 (Reporting) and 3.1.8 (Export).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QDateEdit, QGroupBox,
                             QMessageBox, QTabWidget, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from dal.database import DatabasePool
from core.logger import get_logger

logger = get_logger()


class ReportsWidget(QWidget):
    """Widget for viewing and exporting reports."""
    
    def __init__(self, db_pool: DatabasePool, user_data: dict, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.user_data = user_data
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("Отчёты и аналитика")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_sales_report_tab(), "Продажи")
        self.tabs.addTab(self._create_writeoffs_report_tab(), "Списания")
        self.tabs.addTab(self._create_inventory_report_tab(), "Инвентаризация")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def _create_sales_report_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Период с:"))
        self.sales_start_date = QDateEdit()
        self.sales_start_date.setDate(QDate.currentDate().addDays(-30))
        self.sales_start_date.setCalendarPopup(True)
        date_layout.addWidget(self.sales_start_date)
        
        date_layout.addWidget(QLabel("по:"))
        self.sales_end_date = QDateEdit()
        self.sales_end_date.setDate(QDate.currentDate())
        self.sales_end_date.setCalendarPopup(True)
        date_layout.addWidget(self.sales_end_date)
        
        generate_btn = QPushButton("Сформировать")
        generate_btn.clicked.connect(self._generate_sales_report)
        date_layout.addWidget(generate_btn)
        
        export_btn = QPushButton("Экспорт CSV")
        export_btn.clicked.connect(lambda: self._export_table_to_csv(self.sales_table, "sales_report.csv"))
        date_layout.addWidget(export_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        self.sales_summary_group = QGroupBox("Итого за период")
        summary_layout = QHBoxLayout()
        self.sales_total_qty_label = QLabel("Кол-во: 0 кг")
        summary_layout.addWidget(self.sales_total_qty_label)
        self.sales_total_revenue_label = QLabel("Выручка: 0 руб")
        self.sales_total_revenue_label.setStyleSheet("color: green; font-weight: bold;")
        summary_layout.addWidget(self.sales_total_revenue_label)
        self.sales_transactions_label = QLabel("Транзакций: 0")
        summary_layout.addWidget(self.sales_transactions_label)
        summary_layout.addStretch()
        self.sales_summary_group.setLayout(summary_layout)
        layout.addWidget(self.sales_summary_group)
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Дата", "Товар", "Категория", "Кол-во", "Сумма"])
        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.sales_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_writeoffs_report_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Период с:"))
        self.writeoffs_start_date = QDateEdit()
        self.writeoffs_start_date.setDate(QDate.currentDate().addDays(-30))
        self.writeoffs_start_date.setCalendarPopup(True)
        date_layout.addWidget(self.writeoffs_start_date)
        
        date_layout.addWidget(QLabel("по:"))
        self.writeoffs_end_date = QDateEdit()
        self.writeoffs_end_date.setDate(QDate.currentDate())
        self.writeoffs_end_date.setCalendarPopup(True)
        date_layout.addWidget(self.writeoffs_end_date)
        
        generate_btn = QPushButton("Сформировать")
        generate_btn.clicked.connect(self._generate_writeoffs_report)
        date_layout.addWidget(generate_btn)
        
        export_btn = QPushButton("Экспорт CSV")
        export_btn.clicked.connect(lambda: self._export_table_to_csv(self.writeoffs_table, "writeoffs_report.csv"))
        date_layout.addWidget(export_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        self.writeoffs_table = QTableWidget()
        self.writeoffs_table.setColumnCount(5)
        self.writeoffs_table.setHorizontalHeaderLabels(["Дата", "Товар", "Кол-во", "Причина", "Ответственный"])
        header = self.writeoffs_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.writeoffs_table.setAlternatingRowColors(True)
        self.writeoffs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.writeoffs_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_inventory_report_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        action_layout = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self._generate_inventory_report)
        action_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("Экспорт CSV")
        export_btn.clicked.connect(lambda: self._export_table_to_csv(self.inventory_table, "inventory_report.csv"))
        action_layout.addWidget(export_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(["Товар", "Категория", "Партия", "Остаток", "Срок годности"])
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.inventory_table)
        
        widget.setLayout(layout)
        return widget
    
    def _generate_sales_report(self):
        try:
            start_date = self.sales_start_date.date().toPyDate()
            end_date = self.sales_end_date.date().toPyDate()
            
            query = """
                SELECT DATE(s.sale_date) AS sale_date, p.name AS product_name,
                       p.category, SUM(s.quantity) AS total_qty,
                       SUM(s.sale_price * s.quantity) AS total_amount
                FROM fish_store.sales s
                JOIN fish_store.products p ON s.product_id = p.product_id
                WHERE DATE(s.sale_date) BETWEEN %s AND %s
                GROUP BY DATE(s.sale_date), p.name, p.category
                ORDER BY sale_date DESC, total_amount DESC
            """
            results = self.db_pool.execute_query(query, (start_date, end_date))
            
            self.sales_table.setRowCount(0)
            total_qty = 0
            total_revenue = 0
            transactions = 0
            
            for row_data in results:
                row = self.sales_table.rowCount()
                self.sales_table.insertRow(row)
                self.sales_table.setItem(row, 0, QTableWidgetItem(row_data['sale_date'].strftime("%d.%m.%Y")))
                self.sales_table.setItem(row, 1, QTableWidgetItem(row_data['product_name']))
                self.sales_table.setItem(row, 2, QTableWidgetItem(row_data['category']))
                
                qty = float(row_data['total_qty'])
                total_qty += qty
                qty_item = QTableWidgetItem(f"{qty:.3f}")
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(row, 3, qty_item)
                
                amount = float(row_data['total_amount'])
                total_revenue += amount
                transactions += 1
                amount_item = QTableWidgetItem(f"{amount:.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(row, 4, amount_item)
            
            self.sales_total_qty_label.setText(f"Кол-во: {total_qty:.3f} кг")
            self.sales_total_revenue_label.setText(f"Выручка: {total_revenue:.2f} руб")
            self.sales_transactions_label.setText(f"Транзакций: {transactions}")
            logger.info(f"Sales report generated: {transactions} records")
            
        except Exception as e:
            logger.error(f"Error generating sales report: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчёт:\n{str(e)}")
    
    def _generate_writeoffs_report(self):
        try:
            start_date = self.writeoffs_start_date.date().toPyDate()
            end_date = self.writeoffs_end_date.date().toPyDate()
            
            query = """
                SELECT w.write_off_date, p.name AS product_name, w.quantity,
                       w.reason, u.full_name AS user_name
                FROM fish_store.write_offs w
                JOIN fish_store.products p ON w.product_id = p.product_id
                JOIN fish_store.users u ON w.user_id = u.user_id
                WHERE w.write_off_date BETWEEN %s AND %s
                ORDER BY w.write_off_date DESC
            """
            results = self.db_pool.execute_query(query, (start_date, end_date))
            
            self.writeoffs_table.setRowCount(0)
            reason_names = {'expired': 'Истечение срока', 'damaged': 'Порча', 
                          'quality_check': 'Контроль качества', 'other': 'Прочее'}
            
            for row_data in results:
                row = self.writeoffs_table.rowCount()
                self.writeoffs_table.insertRow(row)
                self.writeoffs_table.setItem(row, 0, QTableWidgetItem(row_data['write_off_date'].strftime("%d.%m.%Y")))
                self.writeoffs_table.setItem(row, 1, QTableWidgetItem(row_data['product_name']))
                
                qty_item = QTableWidgetItem(f"{float(row_data['quantity']):.3f}")
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.writeoffs_table.setItem(row, 2, qty_item)
                
                reason = reason_names.get(row_data['reason'], row_data['reason'])
                self.writeoffs_table.setItem(row, 3, QTableWidgetItem(reason))
                self.writeoffs_table.setItem(row, 4, QTableWidgetItem(row_data['user_name']))
            
            logger.info(f"Write-offs report generated: {len(results)} records")
            
        except Exception as e:
            logger.error(f"Error generating write-offs report: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчёт:\n{str(e)}")
    
    def _generate_inventory_report(self):
        try:
            query = """
                SELECT product_name, category, batch_number, remaining_qty, expiry_date
                FROM fish_store.current_stock
                WHERE remaining_qty > 0
                ORDER BY category, product_name, expiry_date
            """
            results = self.db_pool.execute_query(query)
            
            self.inventory_table.setRowCount(0)
            
            for row_data in results:
                row = self.inventory_table.rowCount()
                self.inventory_table.insertRow(row)
                self.inventory_table.setItem(row, 0, QTableWidgetItem(row_data['product_name']))
                self.inventory_table.setItem(row, 1, QTableWidgetItem(row_data['category']))
                self.inventory_table.setItem(row, 2, QTableWidgetItem(row_data['batch_number'] or 'Б/Н'))
                
                qty_item = QTableWidgetItem(f"{float(row_data['remaining_qty']):.3f}")
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.inventory_table.setItem(row, 3, qty_item)
                
                expiry = row_data['expiry_date'].strftime("%d.%m.%Y")
                self.inventory_table.setItem(row, 4, QTableWidgetItem(expiry))
            
            logger.info(f"Inventory report generated: {len(results)} records")
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчёт:\n{str(e)}")
    
    def _export_table_to_csv(self, table: QTableWidget, default_filename: str):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт", default_filename, "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    headers = []
                    for col in range(table.columnCount()):
                        header = table.horizontalHeaderItem(col)
                        headers.append(header.text() if header else '')
                    f.write(';'.join(headers) + '\n')
                    
                    for row in range(table.rowCount()):
                        row_data = []
                        for col in range(table.columnCount()):
                            item = table.item(row, col)
                            row_data.append(item.text() if item else '')
                        f.write(';'.join(row_data) + '\n')
                
                QMessageBox.information(self, "Успех", f"Отчёт сохранён в файл:\n{file_path}")
                logger.info(f"Report exported to: {file_path}")
                
            except Exception as e:
                logger.error(f"Error exporting report: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчёт:\n{str(e)}")
