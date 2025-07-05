"""Tests for character service."""

import pytest
from unittest.mock import AsyncMock, patch

from writer_mcp.services.character_service import CharacterService
from writer_mcp.schemas.models import Character, Fact


class TestCharacterService:
    """Test cases for CharacterService."""
    
    @pytest.mark.asyncio
    async def test_create_character(self, character_service: CharacterService, sample_character_data: dict):
        """Test character creation."""
        character = await character_service.create_character(
            name=sample_character_data["name"],
            description=sample_character_data["description"],
            background=sample_character_data["background"],
            personality=sample_character_data["personality"],
            tags=sample_character_data["tags"]
        )
        
        assert character is not None
        assert character.name == sample_character_data["name"]
        assert character.description == sample_character_data["description"]
        assert character.background == sample_character_data["background"]
        assert character.personality == sample_character_data["personality"]
        assert character.tags == sample_character_data["tags"]
        assert character.id is not None
    
    @pytest.mark.asyncio
    async def test_get_character(self, character_service: CharacterService, sample_character_data: dict):
        """Test character retrieval."""
        # Create a character first
        created_character = await character_service.create_character(
            name=sample_character_data["name"],
            description=sample_character_data["description"]
        )
        
        # Retrieve the character
        retrieved_character = await character_service.get_character(created_character.id)
        
        assert retrieved_character is not None
        assert retrieved_character.id == created_character.id
        assert retrieved_character.name == created_character.name
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_character(self, character_service: CharacterService):
        """Test retrieval of non-existent character."""
        character = await character_service.get_character("nonexistent-id")
        assert character is None
    
    @pytest.mark.asyncio
    async def test_search_characters(self, character_service: CharacterService, sample_character_data: dict):
        """Test character search."""
        # Create a character first
        await character_service.create_character(
            name=sample_character_data["name"],
            description=sample_character_data["description"]
        )
        
        # Search for characters
        results = await character_service.search_characters(
            query="detective",
            limit=10
        )
        
        assert len(results) > 0
        assert any(char.name == sample_character_data["name"] for char in results)
    
    @pytest.mark.asyncio
    async def test_add_character_fact(self, character_service: CharacterService, sample_character_data: dict, sample_fact_data: dict):
        """Test adding a fact to a character."""
        # Create a character first
        character = await character_service.create_character(
            name=sample_character_data["name"],
            description=sample_character_data["description"]
        )
        
        # Add a fact
        fact = await character_service.add_character_fact(
            character_id=character.id,
            fact_type=sample_fact_data["fact_type"],
            content=sample_fact_data["content"],
            importance=sample_fact_data["importance"],
            tags=sample_fact_data["tags"]
        )
        
        assert fact is not None
        assert fact.character_id == character.id
        assert fact.fact_type == sample_fact_data["fact_type"]
        assert fact.content == sample_fact_data["content"]
        assert fact.importance == sample_fact_data["importance"]
        assert fact.tags == sample_fact_data["tags"]
    
    @pytest.mark.asyncio
    async def test_search_facts(self, character_service: CharacterService, sample_character_data: dict, sample_fact_data: dict):
        """Test searching character facts."""
        # Create a character and add a fact
        character = await character_service.create_character(
            name=sample_character_data["name"],
            description=sample_character_data["description"]
        )
        
        await character_service.add_character_fact(
            character_id=character.id,
            fact_type=sample_fact_data["fact_type"],
            content=sample_fact_data["content"]
        )
        
        # Search for facts
        results = await character_service.search_facts(
            query="military",
            character_id=character.id,
            limit=10
        )
        
        assert len(results) > 0
        assert any(fact.content == sample_fact_data["content"] for fact in results)
    
    @pytest.mark.asyncio
    async def test_create_relationship(self, character_service: CharacterService, sample_character_data: dict, sample_relation_data: dict):
        """Test creating a relationship between characters."""
        # Create two characters
        character1 = await character_service.create_character(
            name="Character 1",
            description="First character"
        )
        
        character2 = await character_service.create_character(
            name="Character 2",
            description="Second character"
        )
        
        # Create relationship
        relation = await character_service.create_relationship(
            character1_id=character1.id,
            character2_id=character2.id,
            relation_type=sample_relation_data["relation_type"],
            description=sample_relation_data["description"],
            strength=sample_relation_data["strength"],
            tags=sample_relation_data["tags"]
        )
        
        assert relation is not None
        assert relation.character1_id == character1.id
        assert relation.character2_id == character2.id
        assert relation.relation_type == sample_relation_data["relation_type"]
        assert relation.description == sample_relation_data["description"]
        assert relation.strength == sample_relation_data["strength"]
    
    @pytest.mark.asyncio
    async def test_get_character_relationships(self, character_service: CharacterService, sample_relation_data: dict):
        """Test retrieving character relationships."""
        # Create two characters and a relationship
        character1 = await character_service.create_character(
            name="Character 1",
            description="First character"
        )
        
        character2 = await character_service.create_character(
            name="Character 2",
            description="Second character"
        )
        
        await character_service.create_relationship(
            character1_id=character1.id,
            character2_id=character2.id,
            relation_type=sample_relation_data["relation_type"],
            description=sample_relation_data["description"]
        )
        
        # Get relationships
        relationships = await character_service.get_character_relationships(character1.id)
        
        assert len(relationships) > 0
        assert any(rel.character2_id == character2.id for rel in relationships)
    
    @pytest.mark.asyncio
    async def test_invalid_character_creation(self, character_service: CharacterService):
        """Test character creation with invalid data."""
        with pytest.raises(ValueError):
            await character_service.create_character(
                name="",  # Empty name should raise error
                description="Valid description"
            )
    
    @pytest.mark.asyncio
    async def test_duplicate_character_name(self, character_service: CharacterService):
        """Test creating characters with duplicate names."""
        # Create first character
        await character_service.create_character(
            name="Duplicate Name",
            description="First character"
        )
        
        # Create second character with same name (should be allowed)
        character2 = await character_service.create_character(
            name="Duplicate Name",
            description="Second character"
        )
        
        assert character2 is not None
        assert character2.name == "Duplicate Name"