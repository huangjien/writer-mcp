"""Database initialization and schema setup."""

from typing import Optional

from .connection import DatabaseConnection
from ..utils.logger import get_logger
from ..config import settings


logger = get_logger(__name__)


# Database schema SQL
CREATE_TABLES_SQL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Characters table
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Character facts table with vector embeddings
CREATE TABLE IF NOT EXISTS character_facts (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    fact_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    embedding vector({vector_dimension}),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Character relationships table
CREATE TABLE IF NOT EXISTS character_relations (
    id SERIAL PRIMARY KEY,
    character_a_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    character_b_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    relation_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    strength FLOAT DEFAULT 0.5 CHECK (strength >= 0.0 AND strength <= 1.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_relation UNIQUE (character_a_id, character_b_id, relation_type)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS idx_characters_tags ON characters USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_character_facts_character_id ON character_facts(character_id);
CREATE INDEX IF NOT EXISTS idx_character_facts_type ON character_facts(fact_type);
CREATE INDEX IF NOT EXISTS idx_character_facts_content ON character_facts USING GIN(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_character_facts_embedding ON character_facts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_character_relations_a ON character_relations(character_a_id);
CREATE INDEX IF NOT EXISTS idx_character_relations_b ON character_relations(character_b_id);
CREATE INDEX IF NOT EXISTS idx_character_relations_type ON character_relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_character_relations_strength ON character_relations(strength);

-- Triggers for updating updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_characters_updated_at ON characters;
CREATE TRIGGER update_characters_updated_at
    BEFORE UPDATE ON characters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_character_facts_updated_at ON character_facts;
CREATE TRIGGER update_character_facts_updated_at
    BEFORE UPDATE ON character_facts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_character_relations_updated_at ON character_relations;
CREATE TRIGGER update_character_relations_updated_at
    BEFORE UPDATE ON character_relations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""


DROP_TABLES_SQL = """
-- Drop tables in reverse order due to foreign key constraints
DROP TABLE IF EXISTS character_relations CASCADE;
DROP TABLE IF EXISTS character_facts CASCADE;
DROP TABLE IF EXISTS characters CASCADE;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
"""


async def init_database(db: Optional[DatabaseConnection] = None) -> bool:
    """Initialize the database with required tables and indexes.
    
    Args:
        db: Optional database connection. If not provided, creates a new one.
        
    Returns:
        True if initialization was successful, False otherwise.
    """
    connection = db
    should_close = False
    
    try:
        if not connection:
            connection = DatabaseConnection(settings.database_url)
            await connection.connect()
            should_close = True
        
        logger.info("Initializing database schema...")
        
        # Format SQL with vector dimension
        formatted_sql = CREATE_TABLES_SQL.format(
            vector_dimension=settings.vector_dimension
        )
        
        # Execute schema creation
        await connection.execute_script(formatted_sql)
        
        logger.info("Database schema initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False
        
    finally:
        if should_close and connection:
            await connection.close()


async def drop_database(db: Optional[DatabaseConnection] = None) -> bool:
    """Drop all database tables and related objects.
    
    Args:
        db: Optional database connection. If not provided, creates a new one.
        
    Returns:
        True if drop was successful, False otherwise.
    """
    connection = db
    should_close = False
    
    try:
        if not connection:
            connection = DatabaseConnection(settings.database_url)
            await connection.connect()
            should_close = True
        
        logger.warning("Dropping database schema...")
        
        # Execute schema drop
        await connection.execute_script(DROP_TABLES_SQL)
        
        logger.warning("Database schema dropped successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to drop database: {e}")
        return False
        
    finally:
        if should_close and connection:
            await connection.close()


async def reset_database(db: Optional[DatabaseConnection] = None) -> bool:
    """Reset the database by dropping and recreating all tables.
    
    Args:
        db: Optional database connection. If not provided, creates a new one.
        
    Returns:
        True if reset was successful, False otherwise.
    """
    connection = db
    should_close = False
    
    try:
        if not connection:
            connection = DatabaseConnection(settings.database_url)
            await connection.connect()
            should_close = True
        
        logger.warning("Resetting database...")
        
        # Drop existing schema
        if not await drop_database(connection):
            return False
        
        # Recreate schema
        if not await init_database(connection):
            return False
        
        logger.info("Database reset completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False
        
    finally:
        if should_close and connection:
            await connection.close()


async def check_database_health(db: Optional[DatabaseConnection] = None) -> bool:
    """Check if the database is properly initialized and accessible.
    
    Args:
        db: Optional database connection. If not provided, creates a new one.
        
    Returns:
        True if database is healthy, False otherwise.
    """
    connection = db
    should_close = False
    
    try:
        if not connection:
            connection = DatabaseConnection(settings.database_url)
            await connection.connect()
            should_close = True
        
        # Check if required tables exist
        check_sql = """
            SELECT COUNT(*) as table_count
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('characters', 'character_facts', 'character_relations')
        """
        
        result = await connection.fetch_one(check_sql)
        
        if result and result['table_count'] == 3:
            logger.info("Database health check passed")
            return True
        else:
            logger.warning(f"Database health check failed: found {result['table_count'] if result else 0}/3 required tables")
            return False
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
        
    finally:
        if should_close and connection:
            await connection.close()