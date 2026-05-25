"""
Database connection pool and base operations.
Implements requirements from section 3.2 (reliability) and 3.3 (security).
"""

import os
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

from core.logger import get_logger

logger = get_logger()


class DatabasePool:
    """
    Singleton database connection pool with automatic recovery.
    Implements ACID compliance and secure parameterized queries.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._pool: Optional[pool.SimpleConnectionPool] = None
        self._initialize_pool()
        self._initialized = True
    
    def _initialize_pool(self):
        """Initialize the connection pool with settings from environment."""
        try:
            self._pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'fish_store'),
                user=os.getenv('DB_USER', 'fishstore_app'),
                password=os.getenv('DB_PASSWORD', ''),
                cursor_factory=RealDictCursor
            )
            logger.info("Database pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the database pool."""
        return cls()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool.
        Ensures proper connection return even on errors.
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                try:
                    self._pool.putconn(conn)
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        Implements ACID compliance with automatic rollback on errors.
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            if conn:
                conn.rollback()
                logger.warning(f"Transaction rolled back due to error: {e}")
            raise
        finally:
            if conn:
                try:
                    self._pool.putconn(conn)
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def close_all(self):
        """Close all connections in the pool."""
        if self._pool:
            try:
                self._pool.closeall()
                logger.info("All database connections closed")
            except Exception as e:
                logger.error(f"Error closing connections: {e}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries.
        Uses parameterized queries to prevent SQL injection.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
    
    def execute_single(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and return single result or None."""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_command(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE command.
        Returns number of affected rows.
        Automatically commits the transaction.
        """
        with self.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount
    
    def execute_returning(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Execute INSERT/UPDATE with RETURNING clause.
        Returns the inserted/updated row.
        Automatically commits the transaction.
        """
        with self.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()


# Convenience functions using the singleton pool
def get_db_pool() -> DatabasePool:
    """Get the database pool singleton instance."""
    return DatabasePool.get_instance()


@contextmanager
def db_transaction():
    """Convenience function for transactions."""
    pool = get_db_pool()
    with pool.transaction() as conn:
        yield conn


def query(sql_query: str, *params) -> List[Dict[str, Any]]:
    """Convenience function for SELECT queries."""
    return get_db_pool().execute_query(sql_query, params)


def query_one(sql_query: str, *params) -> Optional[Dict[str, Any]]:
    """Convenience function for single-row SELECT queries."""
    return get_db_pool().execute_single(sql_query, params)


def command(sql_query: str, *params) -> int:
    """Convenience function for INSERT/UPDATE/DELETE commands."""
    return get_db_pool().execute_command(sql_query, params)
