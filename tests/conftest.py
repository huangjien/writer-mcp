"""Pytest configuration and fixtures for Writer MCP tests."""

import asyncio
import os
import pytest
import pytest_asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

# Add src to path
src_path = Path(__file__).parent.parent / "src"
import sys
sys.path.insert(0, str(src_path))

from writer_mcp.config import Settings
from writer_mcp.database.connection import DatabaseConnection
from writer_mcp.database.init import init_database, drop_database
from writer_mcp.services.character_service import CharacterService
from writer_mcp.services.embedding_service import EmbeddingService
from writer_mcp.services.ai_service import AIService


# Test database URL
TEST_DATABASE_URL = "postgresql://localhost:5432/writer_mcp_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        openai_api_key="test-key",
        app_name="Writer MCP Test",
        debug=True,
        vector_dimension=1536,
        embedding_model="text-embedding-3-small",
        chat_model="gpt-4",
        mcp_server_name="writer-mcp-test",
        mcp_server_version="0.1.0"
    )


@pytest_asyncio.fixture(scope="session")
async def test_db_connection(test_settings: Settings) -> AsyncGenerator[DatabaseConnection, None]:
    """Create a test database connection."""
    db = DatabaseConnection(test_settings.database_url)
    
    try:
        await db.connect()
        yield db
    finally:
        await db.close()


@pytest_asyncio.fixture(scope="function")
async def clean_database(test_db_connection: DatabaseConnection) -> AsyncGenerator[DatabaseConnection, None]:
    """Provide a clean database for each test."""
    # Drop and recreate database schema
    await drop_database(test_db_connection)
    await init_database(test_db_connection)
    
    yield test_db_connection
    
    # Clean up after test
    await drop_database(test_db_connection)


@pytest_asyncio.fixture
async def character_service(clean_database: DatabaseConnection, test_settings: Settings) -> CharacterService:
    """Create a character service instance."""
    embedding_service = EmbeddingService(test_settings)
    return CharacterService(clean_database, embedding_service)


@pytest_asyncio.fixture
async def embedding_service(test_settings: Settings) -> EmbeddingService:
    """Create an embedding service instance."""
    return EmbeddingService(test_settings)


@pytest_asyncio.fixture
async def ai_service(test_settings: Settings) -> AIService:
    """Create an AI service instance."""
    return AIService(test_settings)


@pytest.fixture
def sample_character_data() -> dict:
    """Sample character data for testing."""
    return {
        "name": "John Doe",
        "description": "A mysterious detective with a troubled past",
        "background": "Former police officer turned private investigator",
        "personality": "Cynical but caring, intelligent and observant",
        "tags": ["detective", "mysterious", "troubled"]
    }


@pytest.fixture
def sample_fact_data() -> dict:
    """Sample fact data for testing."""
    return {
        "fact_type": "background",
        "content": "John served in the military before joining the police force",
        "importance": 0.8,
        "tags": ["military", "background"]
    }


@pytest.fixture
def sample_relation_data() -> dict:
    """Sample relation data for testing."""
    return {
        "relation_type": "friend",
        "description": "Close friends since childhood",
        "strength": 0.9,
        "tags": ["friendship", "childhood"]
    }


# Skip tests that require OpenAI API if no key is provided
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "requires_openai: mark test as requiring OpenAI API key"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip OpenAI tests if no API key."""
    if not os.getenv("OPENAI_API_KEY"):
        skip_openai = pytest.mark.skip(reason="OpenAI API key not provided")
        for item in items:
            if "requires_openai" in item.keywords:
                item.add_marker(skip_openai)