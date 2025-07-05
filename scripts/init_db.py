#!/usr/bin/env python3
"""Database initialization script for Writer MCP."""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from writer_mcp.config import settings
from writer_mcp.database.init import init_database, check_database_health
from writer_mcp.utils.logger import get_logger, setup_logging


logger = get_logger(__name__)


async def main():
    """Initialize the database."""
    setup_logging()
    
    logger.info("Starting database initialization...")
    
    try:
        # Check if database is accessible
        logger.info("Checking database connection...")
        health_status = await check_database_health()
        
        if not health_status["healthy"]:
            logger.error(f"Database health check failed: {health_status['error']}")
            return False
        
        logger.info("Database connection successful")
        
        # Initialize database
        logger.info("Initializing database schema...")
        await init_database()
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)