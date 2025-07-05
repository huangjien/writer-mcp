"""Database connection management for Writer MCP."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from ..config import settings
from ..utils.logger import get_logger


logger = get_logger(__name__)


class DatabaseConnection:
    """Database connection manager."""
    
    def __init__(self) -> None:
        """Initialize database connection manager."""
        self.pool: Optional[ThreadedConnectionPool] = None
        
    async def connect(self) -> None:
        """Establish database connection pool."""
        try:
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=settings.database_pool_size,
                dsn=settings.database_url,
                cursor_factory=RealDictCursor
            )
            
            # Test connection
            await self._test_connection()
            logger.info("Database connection pool created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
            
    async def _test_connection(self) -> None:
        """Test database connection."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] != 1:
                    raise RuntimeError("Database connection test failed")
        finally:
            self.pool.putconn(conn)
            
    async def close(self) -> None:
        """Close database connection pool."""
        if self.pool:
            self.pool.closeall()
            self.pool = None
            logger.info("Database connection pool closed")
            
    async def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            self.pool.putconn(conn)
            
    async def execute_command(
        self, 
        command: str, 
        params: Optional[tuple] = None
    ) -> int:
        """Execute an INSERT/UPDATE/DELETE command and return affected rows."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(command, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Command execution failed: {e}")
            raise
        finally:
            self.pool.putconn(conn)
            
    async def execute_script(self, script: str) -> None:
        """Execute a SQL script (for migrations)."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(script)
                conn.commit()
                logger.info("SQL script executed successfully")
        except Exception as e:
            conn.rollback()
            logger.error(f"Script execution failed: {e}")
            raise
        finally:
            self.pool.putconn(conn)