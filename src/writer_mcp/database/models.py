"""Database models for Writer MCP."""

from datetime import datetime
from typing import List, Optional

from ..database.connection import DatabaseConnection
from ..utils.logger import get_logger


logger = get_logger(__name__)


class Character:
    """Character database model."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        description: str = "",
        tags: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags or []
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    async def create(
        cls, 
        db: DatabaseConnection, 
        name: str, 
        description: str, 
        tags: Optional[List[str]] = None
    ) -> "Character":
        """Create a new character."""
        query = """
            INSERT INTO characters (name, description, tags, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
            RETURNING id, name, description, tags, created_at, updated_at
        """
        
        results = await db.execute_query(
            query, 
            (name, description, tags or [])
        )
        result = results[0] if results else None
        
        if result:
            return cls(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                tags=result['tags'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        
        raise Exception("Failed to create character")
    
    @classmethod
    async def get_by_id(cls, db: DatabaseConnection, character_id: int) -> Optional["Character"]:
        """Get character by ID."""
        query = """
            SELECT id, name, description, tags, created_at, updated_at
            FROM characters
            WHERE id = $1
        """
        
        results = await db.execute_query(query, (character_id,))
        result = results[0] if results else None
        
        if result:
            return cls(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                tags=result['tags'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        
        return None
    
    @classmethod
    async def search(
        cls, 
        db: DatabaseConnection, 
        query: str, 
        limit: int = 10
    ) -> List["Character"]:
        """Search characters by name or description."""
        sql = """
            SELECT id, name, description, tags, created_at, updated_at
            FROM characters
            WHERE name ILIKE $1 OR description ILIKE $1
            ORDER BY 
                CASE 
                    WHEN name ILIKE $1 THEN 1
                    ELSE 2
                END,
                name
            LIMIT $2
        """
        
        search_pattern = f"%{query}%"
        results = await db.execute_query(sql, (search_pattern, limit))
        
        return [
            cls(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                tags=row['tags'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in results
        ]


class CharacterFact:
    """Character fact database model."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        character_id: int = 0,
        fact_type: str = "",
        content: str = "",
        embedding: Optional[List[float]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.character_id = character_id
        self.fact_type = fact_type
        self.content = content
        self.embedding = embedding
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    async def create(
        cls,
        db: DatabaseConnection,
        character_id: int,
        fact_type: str,
        content: str,
        embedding: Optional[List[float]] = None
    ) -> "CharacterFact":
        """Create a new character fact."""
        query = """
            INSERT INTO character_facts (character_id, fact_type, content, embedding, created_at, updated_at)
            VALUES ($1, $2, $3, $4, NOW(), NOW())
            RETURNING id, character_id, fact_type, content, embedding, created_at, updated_at
        """
        
        results = await db.execute_query(
            query,
            (character_id, fact_type, content, embedding)
        )
        result = results[0] if results else None
        
        if result:
            return cls(
                id=result['id'],
                character_id=result['character_id'],
                fact_type=result['fact_type'],
                content=result['content'],
                embedding=result['embedding'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        
        raise Exception("Failed to create character fact")
    
    @classmethod
    async def search_by_content(
        cls,
        db: DatabaseConnection,
        query: str,
        character_id: Optional[int] = None,
        fact_type: Optional[str] = None,
        limit: int = 10
    ) -> List["CharacterFact"]:
        """Search facts by content."""
        conditions = ["content ILIKE $1"]
        params = [f"%{query}%"]
        param_count = 1
        
        if character_id:
            param_count += 1
            conditions.append(f"character_id = ${param_count}")
            params.append(character_id)
        
        if fact_type:
            param_count += 1
            conditions.append(f"fact_type = ${param_count}")
            params.append(fact_type)
        
        param_count += 1
        params.append(limit)
        
        sql = f"""
            SELECT id, character_id, fact_type, content, embedding, created_at, updated_at
            FROM character_facts
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT ${param_count}
        """
        
        results = await db.execute_query(sql, tuple(params))
        
        return [
            cls(
                id=row['id'],
                character_id=row['character_id'],
                fact_type=row['fact_type'],
                content=row['content'],
                embedding=row['embedding'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in results
        ]


class CharacterRelation:
    """Character relationship database model."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        character_a_id: int = 0,
        character_b_id: int = 0,
        relation_type: str = "",
        description: str = "",
        strength: float = 0.5,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.character_a_id = character_a_id
        self.character_b_id = character_b_id
        self.relation_type = relation_type
        self.description = description
        self.strength = strength
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    async def create(
        cls,
        db: DatabaseConnection,
        character_a_id: int,
        character_b_id: int,
        relation_type: str,
        description: str,
        strength: float = 0.5
    ) -> "CharacterRelation":
        """Create a new character relationship."""
        query = """
            INSERT INTO character_relations 
            (character_a_id, character_b_id, relation_type, description, strength, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            RETURNING id, character_a_id, character_b_id, relation_type, description, strength, created_at, updated_at
        """
        
        results = await db.execute_query(
            query,
            (character_a_id, character_b_id, relation_type, description, strength)
        )
        result = results[0] if results else None
        
        if result:
            return cls(
                id=result['id'],
                character_a_id=result['character_a_id'],
                character_b_id=result['character_b_id'],
                relation_type=result['relation_type'],
                description=result['description'],
                strength=result['strength'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        
        raise Exception("Failed to create character relationship")
    
    @classmethod
    async def get_by_characters(
        cls,
        db: DatabaseConnection,
        character_ids: List[int]
    ) -> List["CharacterRelation"]:
        """Get relationships between specific characters."""
        if len(character_ids) < 2:
            return []
        
        placeholders = ", ".join([f"${i+1}" for i in range(len(character_ids))])
        
        sql = f"""
            SELECT id, character_a_id, character_b_id, relation_type, description, strength, created_at, updated_at
            FROM character_relations
            WHERE character_a_id IN ({placeholders}) AND character_b_id IN ({placeholders})
            ORDER BY strength DESC, created_at DESC
        """
        
        # Duplicate the character_ids for both IN clauses
        params = character_ids + character_ids
        results = await db.execute_query(sql, tuple(params))
        
        return [
            cls(
                id=row['id'],
                character_a_id=row['character_a_id'],
                character_b_id=row['character_b_id'],
                relation_type=row['relation_type'],
                description=row['description'],
                strength=row['strength'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in results
        ]