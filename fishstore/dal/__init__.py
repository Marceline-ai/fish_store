"""
Data Access Layer for FishStore Manager.
Contains repository classes for all database entities.
"""

from .database import DatabasePool, get_db_pool

__all__ = ['DatabasePool', 'get_db_pool']
