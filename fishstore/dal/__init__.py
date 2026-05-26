"""
Data Access Layer for FishStore Manager.
Contains repository classes for all database entities.
"""

from .database import DatabasePool, get_db_pool
from .repositories import (
    ProductRepository,
    SupplierRepository,
    UserRepository,
    BatchRepository,
    StockRepository,
    SaleRepository,
    WriteOffRepository,
)

__all__ = [
    'DatabasePool',
    'get_db_pool',
    'ProductRepository',
    'SupplierRepository',
    'UserRepository',
    'BatchRepository',
    'StockRepository',
    'SaleRepository',
    'WriteOffRepository',
]
