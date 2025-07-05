"""Data models for Writer MCP."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Character(BaseModel):
    """Character model."""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Fact(BaseModel):
    """Character fact model."""
    id: Optional[int] = None
    character_id: int
    fact_type: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Relation(BaseModel):
    """Character relationship model."""
    id: Optional[int] = None
    character_a_id: int
    character_b_id: int
    relation_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    character_id: Optional[int] = None
    fact_type: Optional[str] = None
    

class SearchResult(BaseModel):
    """Search result model."""
    id: int
    content: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)
    

class CharacterCreateRequest(BaseModel):
    """Character creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    

class FactCreateRequest(BaseModel):
    """Fact creation request."""
    character_id: int
    fact_type: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    

class RelationCreateRequest(BaseModel):
    """Relation creation request."""
    character_a_id: int
    character_b_id: int
    relation_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    

class TagGenerationRequest(BaseModel):
    """Tag generation request."""
    character_id: int
    

class RelationshipAnalysisRequest(BaseModel):
    """Relationship analysis request."""
    character_ids: List[int] = Field(..., min_items=2)