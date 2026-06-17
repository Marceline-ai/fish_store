"""
Repository for Products (Справочник товаров).
Implements CRUD operations for the products table.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dal.database import DatabasePool


class ProductRepository:
    """Repository for product operations."""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all products."""
        query = """
            SELECT product_id, name, category, unit, shelf_life_days, temp_storage
            FROM fish_store.products
            ORDER BY category, name
        """
        return self.db_pool.execute_query(query)
    
    def get_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        query = """
            SELECT product_id, name, category, unit, shelf_life_days, temp_storage
            FROM fish_store.products
            WHERE product_id = %s
        """
        return self.db_pool.execute_single(query, (product_id,))
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category."""
        query = """
            SELECT product_id, name, category, unit, shelf_life_days, temp_storage
            FROM fish_store.products
            WHERE category = %s
            ORDER BY name
        """
        return self.db_pool.execute_query(query, (category,))
    
    def create(self, name: str, category: str, unit: str, 
               shelf_life_days: int, temp_storage: str) -> Dict[str, Any]:
        """Create a new product."""
        query = """
            INSERT INTO fish_store.products (name, category, unit, shelf_life_days, temp_storage)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING product_id, name, category, unit, shelf_life_days, temp_storage
        """
        return self.db_pool.execute_returning(query, 
            (name, category, unit, shelf_life_days, temp_storage))
    
    def update(self, product_id: int, name: str, category: str, unit: str,
               shelf_life_days: int, temp_storage: str) -> Dict[str, Any]:
        """Update an existing product."""
        query = """
            UPDATE fish_store.products
            SET name = %s, category = %s, unit = %s, 
                shelf_life_days = %s, temp_storage = %s
            WHERE product_id = %s
            RETURNING product_id, name, category, unit, shelf_life_days, temp_storage
        """
        return self.db_pool.execute_returning(query,
            (name, category, unit, shelf_life_days, temp_storage, product_id))
    
    def delete(self, product_id: int) -> bool:
        """Delete a product. Returns True if successful."""
        query = "DELETE FROM fish_store.products WHERE product_id = %s"
        return self.db_pool.execute_command(query, (product_id,)) > 0
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """Search products by name or category."""
        query = """
            SELECT product_id, name, category, unit, shelf_life_days, temp_storage
            FROM fish_store.products
            WHERE name ILIKE %s OR category ILIKE %s
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        return self.db_pool.execute_query(query, (search_pattern, search_pattern))
    
    def get_categories(self) -> List[str]:
        """Get distinct product categories."""
        query = """
            SELECT DISTINCT category
            FROM fish_store.products
            ORDER BY category
        """
        results = self.db_pool.execute_query(query)
        return [row['category'] for row in results]


class SupplierRepository:
    """Repository for supplier operations."""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all suppliers."""
        query = """
            SELECT supplier_id, name, inn, phone, email, address
            FROM fish_store.suppliers
            ORDER BY name
        """
        return self.db_pool.execute_query(query)
    
    def get_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """Get supplier by ID."""
        query = """
            SELECT supplier_id, name, inn, phone, email, address
            FROM fish_store.suppliers
            WHERE supplier_id = %s
        """
        return self.db_pool.execute_single(query, (supplier_id,))
    
    def create(self, name: str, inn: str = None, phone: str = None,
               email: str = None, address: str = None) -> Dict[str, Any]:
        """Create a new supplier."""
        query = """
            INSERT INTO fish_store.suppliers (name, inn, phone, email, address)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING supplier_id, name, inn, phone, email, address
        """
        return self.db_pool.execute_returning(query, (name, inn, phone, email, address))
    
    def update(self, supplier_id: int, name: str, inn: str = None, phone: str = None,
               email: str = None, address: str = None) -> Dict[str, Any]:
        """Update an existing supplier."""
        query = """
            UPDATE fish_store.suppliers
            SET name = %s, inn = %s, phone = %s, email = %s, address = %s
            WHERE supplier_id = %s
            RETURNING supplier_id, name, inn, phone, email, address
        """
        return self.db_pool.execute_returning(query,
            (name, inn, phone, email, address, supplier_id))
    
    def delete(self, supplier_id: int) -> bool:
        """Delete a supplier. Returns True if successful."""
        query = "DELETE FROM fish_store.suppliers WHERE supplier_id = %s"
        return self.db_pool.execute_command(query, (supplier_id,)) > 0
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """Search suppliers by name."""
        query = """
            SELECT supplier_id, name, inn, phone, email, address
            FROM fish_store.suppliers
            WHERE name ILIKE %s
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        return self.db_pool.execute_query(query, (search_pattern,))


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all users (without password hash)."""
        query = """
            SELECT user_id, full_name, position, login, role
            FROM fish_store.users
            ORDER BY full_name
        """
        return self.db_pool.execute_query(query)
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID (without password hash)."""
        query = """
            SELECT user_id, full_name, position, login, role
            FROM fish_store.users
            WHERE user_id = %s
        """
        return self.db_pool.execute_single(query, (user_id,))
    
    def get_by_login(self, login: str) -> Optional[Dict[str, Any]]:
        """Get user by login (with password hash for authentication)."""
        query = """
            SELECT user_id, full_name, position, login, password_hash, role
            FROM fish_store.users
            WHERE login = %s
        """
        return self.db_pool.execute_single(query, (login,))
    
    def create(self, full_name: str, position: str, login: str,
               password_hash: str, role: str) -> Dict[str, Any]:
        """Create a new user."""
        query = """
            INSERT INTO fish_store.users (full_name, position, login, password_hash, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id, full_name, position, login, role
        """
        return self.db_pool.execute_returning(query,
            (full_name, position, login, password_hash, role))
    
    def update(self, user_id: int, full_name: str, position: str,
               role: str) -> Dict[str, Any]:
        """Update an existing user (without password)."""
        query = """
            UPDATE fish_store.users
            SET full_name = %s, position = %s, role = %s
            WHERE user_id = %s
            RETURNING user_id, full_name, position, login, role
        """
        return self.db_pool.execute_returning(query,
            (full_name, position, role, user_id))
    
    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Update user password."""
        query = """
            UPDATE fish_store.users
            SET password_hash = %s
            WHERE user_id = %s
        """
        return self.db_pool.execute_command(query, (password_hash, user_id)) > 0
    
    def delete(self, user_id: int) -> bool:
        """Delete a user. Returns True if successful."""
        query = "DELETE FROM fish_store.users WHERE user_id = %s"
        return self.db_pool.execute_command(query, (user_id,)) > 0


class BatchRepository:
    """Repository for batch operations."""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all batches with product and supplier info."""
        query = """
            SELECT b.batch_id, b.batch_number, b.arrival_date, b.quantity,
                   b.purchase_price, b.expiry_date,
                   p.product_id, p.name AS product_name, p.category, p.unit,
                   s.supplier_id, s.name AS supplier_name
            FROM fish_store.batches b
            JOIN fish_store.products p ON b.product_id = p.product_id
            JOIN fish_store.suppliers s ON b.supplier_id = s.supplier_id
            ORDER BY b.arrival_date DESC, b.batch_number
        """
        return self.db_pool.execute_query(query)
    
    def get_by_id(self, batch_id: int) -> Optional[Dict[str, Any]]:
        """Get batch by ID."""
        query = """
            SELECT b.batch_id, b.batch_number, b.arrival_date, b.quantity,
                   b.purchase_price, b.expiry_date,
                   b.supplier_id, b.product_id,
                   p.name AS product_name, p.unit,
                   s.name AS supplier_name
            FROM fish_store.batches b
            JOIN fish_store.products p ON b.product_id = p.product_id
            JOIN fish_store.suppliers s ON b.supplier_id = s.supplier_id
            WHERE b.batch_id = %s
        """
        return self.db_pool.execute_single(query, (batch_id,))
    
    def get_expiring_soon(self, days: int = 3) -> List[Dict[str, Any]]:
        """Get batches expiring within specified days."""
        query = """
            SELECT b.batch_id, b.batch_number, b.expiry_date, b.quantity,
                   p.name AS product_name, p.unit,
                   CURRENT_DATE - b.expiry_date AS days_until_expiry
            FROM fish_store.batches b
            JOIN fish_store.products p ON b.product_id = p.product_id
            WHERE b.expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
            ORDER BY b.expiry_date
        """
        return self.db_pool.execute_query(query, (days,))
    
    def get_expired(self) -> List[Dict[str, Any]]:
        """Get expired batches."""
        query = """
            SELECT b.batch_id, b.batch_number, b.expiry_date, b.quantity,
                   p.name AS product_name, p.unit,
                   b.expiry_date - CURRENT_DATE AS days_overdue
            FROM fish_store.batches b
            JOIN fish_store.products p ON b.product_id = p.product_id
            WHERE b.expiry_date < CURRENT_DATE
            ORDER BY b.expiry_date
        """
        return self.db_pool.execute_query(query)
    
    def create(self, supplier_id: int, product_id: int, quantity: float,
               purchase_price: float, expiry_date, batch_number: str = None,
               arrival_date=None) -> Dict[str, Any]:
        """Create a new batch."""
        if arrival_date is None:
            arrival_date = 'CURRENT_DATE'
            query = """
                INSERT INTO fish_store.batches 
                (supplier_id, product_id, batch_number, arrival_date, quantity, purchase_price, expiry_date)
                VALUES (%s, %s, %s, DEFAULT, %s, %s, %s)
                RETURNING batch_id, batch_number, arrival_date, quantity, purchase_price, expiry_date
            """
            return self.db_pool.execute_returning(query,
                (supplier_id, product_id, batch_number, quantity, purchase_price, expiry_date))
        else:
            query = """
                INSERT INTO fish_store.batches 
                (supplier_id, product_id, batch_number, arrival_date, quantity, purchase_price, expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING batch_id, batch_number, arrival_date, quantity, purchase_price, expiry_date
            """
            return self.db_pool.execute_returning(query,
                (supplier_id, product_id, batch_number, arrival_date, quantity, purchase_price, expiry_date))
    
    def update_quantity(self, batch_id: int, quantity: float) -> bool:
        """Update batch quantity."""
        query = """
            UPDATE fish_store.batches
            SET quantity = %s
            WHERE batch_id = %s
        """
        return self.db_pool.execute_command(query, (quantity, batch_id)) > 0


class StockRepository:
    """Repository for stock/inventory operations using current_stock view."""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    def get_current_stock(self) -> List[Dict[str, Any]]:
        """Get current stock levels from the view."""
        query = """
            SELECT product_id, product_name, category, batch_number,
                   expiry_date, remaining_qty
            FROM fish_store.current_stock
            WHERE remaining_qty > 0
            ORDER BY expiry_date, product_name, batch_number
        """
        return self.db_pool.execute_query(query)
    
    def get_product_stock(self, product_id: int) -> List[Dict[str, Any]]:
        """Get stock for a specific product."""
        query = """
            SELECT product_id, product_name, category, batch_number,
                   expiry_date, remaining_qty
            FROM fish_store.current_stock
            WHERE product_id = %s AND remaining_qty > 0
            ORDER BY expiry_date
        """
        return self.db_pool.execute_query(query, (product_id,))
    
    def get_available_quantity(self, batch_id: int) -> float:
        """Get available quantity for a specific batch."""
        query = """
            SELECT remaining_qty
            FROM fish_store.current_stock
            WHERE batch_id = %s
        """
        # Note: current_stock view doesn't have batch_id directly
        # We need to join or use a different approach
        result = self.db_pool.execute_single("""
            SELECT b.batch_id, b.quantity - COALESCE(SUM(s.quantity), 0) - COALESCE(SUM(w.quantity), 0) AS remaining_qty
            FROM fish_store.batches b
            LEFT JOIN fish_store.sales s ON b.batch_id = s.batch_id
            LEFT JOIN fish_store.write_offs w ON b.batch_id = w.batch_id
            WHERE b.batch_id = %s
            GROUP BY b.batch_id, b.quantity
        """, (batch_id,))
        return float(result['remaining_qty']) if result else 0.0
    
    def get_low_stock_products(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Get products with low total stock."""
        query = """
            SELECT product_id, product_name, category,
                   SUM(remaining_qty) AS total_remaining
            FROM fish_store.current_stock
            GROUP BY product_id, product_name, category
            HAVING SUM(remaining_qty) <= %s
            ORDER BY total_remaining
        """
        return self.db_pool.execute_query(query, (threshold,))


class SaleRepository:
    """Repository for sales operations."""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    def create(self, batch_id: int, product_id: int, user_id: int,
               quantity: float, sale_price: float,
               sale_date: datetime = None) -> Dict[str, Any]:
        """Create a new sale record."""
        if sale_date is None:
            query = """
                INSERT INTO fish_store.sales 
                (batch_id, product_id, user_id, sale_date, quantity, sale_price)
                VALUES (%s, %s, %s, DEFAULT, %s, %s)
                RETURNING sale_id, sale_date, quantity, sale_price
            """
            return self.db_pool.execute_returning(query,
                (batch_id, product_id, user_id, quantity, sale_price))
        else:
            query = """
                INSERT INTO fish_store.sales 
                (batch_id, product_id, user_id, sale_date, quantity, sale_price)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING sale_id, sale_date, quantity, sale_price
            """
            return self.db_pool.execute_returning(query,
                (batch_id, product_id, user_id, sale_date, quantity, sale_price))
    
    def get_by_batch(self, batch_id: int) -> List[Dict[str, Any]]:
        """Get all sales for a specific batch."""
        query = """
            SELECT s.sale_id, s.sale_date, s.quantity, s.sale_price,
                   u.full_name AS cashier_name
            FROM fish_store.sales s
            JOIN fish_store.users u ON s.user_id = u.user_id
            WHERE s.batch_id = %s
            ORDER BY s.sale_date DESC
        """
        return self.db_pool.execute_query(query, (batch_id,))
    
    def get_sales_report(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get sales report for date range."""
        query = """
            SELECT DATE(s.sale_date) AS sale_day,
                   p.name AS product_name, p.category,
                   SUM(s.quantity) AS total_qty,
                   SUM(s.sale_price * s.quantity) AS total_revenue,
                   COUNT(*) AS transaction_count
            FROM fish_store.sales s
            JOIN fish_store.products p ON s.product_id = p.product_id
            WHERE DATE(s.sale_date) BETWEEN %s AND %s
            GROUP BY DATE(s.sale_date), p.name, p.category
            ORDER BY sale_day DESC, total_revenue DESC
        """
        return self.db_pool.execute_query(query, (start_date, end_date))
    
    def get_revenue_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get revenue summary for date range."""
        query = """
            SELECT 
                SUM(s.quantity) AS total_qty,
                SUM(s.sale_price * s.quantity) AS total_revenue,
                AVG(s.sale_price) AS avg_price,
                COUNT(*) AS transaction_count
            FROM fish_store.sales s
            WHERE DATE(s.sale_date) BETWEEN %s AND %s
        """
        return self.db_pool.execute_single(query, (start_date, end_date))


class WriteOffRepository:
    """Repository for write-off operations."""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    def create(self, batch_id: int, product_id: int, user_id: int,
               quantity: float, reason: str,
               write_off_date: date = None) -> Dict[str, Any]:
        """Create a new write-off record."""
        if write_off_date is None:
            query = """
                INSERT INTO fish_store.write_offs 
                (batch_id, product_id, user_id, write_off_date, quantity, reason)
                VALUES (%s, %s, %s, DEFAULT, %s, %s)
                RETURNING write_off_id, write_off_date, quantity, reason
            """
            return self.db_pool.execute_returning(query,
                (batch_id, product_id, user_id, quantity, reason))
        else:
            query = """
                INSERT INTO fish_store.write_offs 
                (batch_id, product_id, user_id, write_off_date, quantity, reason)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING write_off_id, write_off_date, quantity, reason
            """
            return self.db_pool.execute_returning(query,
                (batch_id, product_id, user_id, write_off_date, quantity, reason))
    
    def get_by_batch(self, batch_id: int) -> List[Dict[str, Any]]:
        """Get all write-offs for a specific batch."""
        query = """
            SELECT w.write_off_id, w.write_off_date, w.quantity, w.reason,
                   u.full_name AS user_name
            FROM fish_store.write_offs w
            JOIN fish_store.users u ON w.user_id = u.user_id
            WHERE w.batch_id = %s
            ORDER BY w.write_off_date DESC
        """
        return self.db_pool.execute_query(query, (batch_id,))
    
    def get_write_offs_report(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get write-offs report for date range."""
        query = """
            SELECT w.write_off_date,
                   p.name AS product_name, p.category,
                   w.quantity, w.reason,
                   u.full_name AS user_name
            FROM fish_store.write_offs w
            JOIN fish_store.products p ON w.product_id = p.product_id
            JOIN fish_store.users u ON w.user_id = u.user_id
            WHERE w.write_off_date BETWEEN %s AND %s
            ORDER BY w.write_off_date DESC, p.name
        """
        return self.db_pool.execute_query(query, (start_date, end_date))
    
    def get_write_offs_summary(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get write-offs summary by reason for date range."""
        query = """
            SELECT w.reason,
                   COUNT(*) AS count,
                   SUM(w.quantity) AS total_qty,
                   p.category
            FROM fish_store.write_offs w
            JOIN fish_store.products p ON w.product_id = p.product_id
            WHERE w.write_off_date BETWEEN %s AND %s
            GROUP BY w.reason, p.category
            ORDER BY total_qty DESC
        """
        return self.db_pool.execute_query(query, (start_date, end_date))
