"""Character management service."""

from typing import List, Optional

from ..database.connection import DatabaseConnection
from ..database.models import Character, CharacterFact, CharacterRelation
from ..schemas.models import (
    CharacterCreateRequest,
    FactCreateRequest,
    RelationCreateRequest,
    SearchRequest,
    SearchResult
)
from ..utils.logger import get_logger


logger = get_logger(__name__)


class CharacterService:
    """Service for managing characters and their data."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    async def create_character(self, request: CharacterCreateRequest) -> Character:
        """Create a new character.
        
        Args:
            request: Character creation request
            
        Returns:
            Created character
            
        Raises:
            Exception: If character creation fails
        """
        try:
            logger.info(f"Creating character: {request.name}")
            
            character = await Character.create(
                self.db,
                name=request.name,
                description=request.description,
                tags=request.tags
            )
            
            logger.info(f"Character created successfully: {character.id}")
            return character
            
        except Exception as e:
            logger.error(f"Failed to create character {request.name}: {e}")
            raise
    
    async def get_character(self, character_id: int) -> Optional[Character]:
        """Get a character by ID.
        
        Args:
            character_id: Character ID
            
        Returns:
            Character if found, None otherwise
        """
        try:
            return await Character.get_by_id(self.db, character_id)
        except Exception as e:
            logger.error(f"Failed to get character {character_id}: {e}")
            return None
    
    async def search_characters(self, request: SearchRequest) -> List[SearchResult]:
        """Search for characters.
        
        Args:
            request: Search request
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"Searching characters: {request.query}")
            
            characters = await Character.search(
                self.db,
                query=request.query,
                limit=request.limit
            )
            
            results = [
                SearchResult(
                    id=char.id,
                    content=f"{char.name}: {char.description}",
                    score=1.0,  # TODO: Implement proper scoring
                    metadata={
                        "type": "character",
                        "name": char.name,
                        "tags": char.tags
                    }
                )
                for char in characters
            ]
            
            logger.info(f"Found {len(results)} characters")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search characters: {e}")
            return []
    
    async def add_character_fact(self, request: FactCreateRequest) -> CharacterFact:
        """Add a fact about a character.
        
        Args:
            request: Fact creation request
            
        Returns:
            Created fact
            
        Raises:
            Exception: If fact creation fails
        """
        try:
            logger.info(f"Adding fact to character {request.character_id}: {request.fact_type}")
            
            # TODO: Generate embedding for the fact content
            embedding = None
            
            fact = await CharacterFact.create(
                self.db,
                character_id=request.character_id,
                fact_type=request.fact_type,
                content=request.content,
                embedding=embedding
            )
            
            logger.info(f"Fact added successfully: {fact.id}")
            return fact
            
        except Exception as e:
            logger.error(f"Failed to add fact to character {request.character_id}: {e}")
            raise
    
    async def search_facts(self, request: SearchRequest) -> List[SearchResult]:
        """Search for character facts.
        
        Args:
            request: Search request
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"Searching facts: {request.query}")
            
            facts = await CharacterFact.search_by_content(
                self.db,
                query=request.query,
                character_id=request.character_id,
                fact_type=request.fact_type,
                limit=request.limit
            )
            
            results = [
                SearchResult(
                    id=fact.id,
                    content=fact.content,
                    score=1.0,  # TODO: Implement proper scoring
                    metadata={
                        "type": "fact",
                        "character_id": fact.character_id,
                        "fact_type": fact.fact_type
                    }
                )
                for fact in facts
            ]
            
            logger.info(f"Found {len(results)} facts")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search facts: {e}")
            return []
    
    async def create_relationship(
        self, 
        request: RelationCreateRequest
    ) -> CharacterRelation:
        """Create a relationship between characters.
        
        Args:
            request: Relationship creation request
            
        Returns:
            Created relationship
            
        Raises:
            Exception: If relationship creation fails
        """
        try:
            logger.info(
                f"Creating relationship between {request.character_a_id} and {request.character_b_id}: {request.relation_type}"
            )
            
            relation = await CharacterRelation.create(
                self.db,
                character_a_id=request.character_a_id,
                character_b_id=request.character_b_id,
                relation_type=request.relation_type,
                description=request.description,
                strength=request.strength
            )
            
            logger.info(f"Relationship created successfully: {relation.id}")
            return relation
            
        except Exception as e:
            logger.error(
                f"Failed to create relationship between {request.character_a_id} and {request.character_b_id}: {e}"
            )
            raise
    
    async def get_character_relationships(
        self, 
        character_ids: List[int]
    ) -> List[CharacterRelation]:
        """Get relationships between specific characters.
        
        Args:
            character_ids: List of character IDs
            
        Returns:
            List of relationships
        """
        try:
            logger.info(f"Getting relationships for characters: {character_ids}")
            
            relations = await CharacterRelation.get_by_characters(
                self.db,
                character_ids
            )
            
            logger.info(f"Found {len(relations)} relationships")
            return relations
            
        except Exception as e:
            logger.error(f"Failed to get relationships: {e}")
            return []