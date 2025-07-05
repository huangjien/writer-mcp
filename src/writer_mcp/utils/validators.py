"""Validation utilities for Writer MCP."""

import re
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger


logger = get_logger(__name__)


def validate_character_name(name: str) -> bool:
    """Validate character name.
    
    Args:
        name: Character name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Check length
    if len(name) < 1 or len(name) > 255:
        return False
    
    # Check for valid characters (letters, numbers, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z0-9\s\-']+$", name):
        return False
    
    return True


def validate_description(description: str) -> bool:
    """Validate description text.
    
    Args:
        description: Description to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not description or not isinstance(description, str):
        return False
    
    # Remove leading/trailing whitespace
    description = description.strip()
    
    # Check minimum length
    if len(description) < 1:
        return False
    
    # Check maximum length (reasonable limit for descriptions)
    if len(description) > 10000:
        return False
    
    return True


def validate_tags(tags: List[str]) -> bool:
    """Validate list of tags.
    
    Args:
        tags: List of tags to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(tags, list):
        return False
    
    # Check maximum number of tags
    if len(tags) > 50:
        return False
    
    for tag in tags:
        if not isinstance(tag, str):
            return False
        
        # Remove leading/trailing whitespace
        tag = tag.strip()
        
        # Check tag length
        if len(tag) < 1 or len(tag) > 50:
            return False
        
        # Check for valid characters (letters, numbers, hyphens, underscores)
        if not re.match(r"^[a-zA-Z0-9\-_]+$", tag):
            return False
    
    return True


def validate_fact_type(fact_type: str) -> bool:
    """Validate fact type.
    
    Args:
        fact_type: Fact type to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not fact_type or not isinstance(fact_type, str):
        return False
    
    # Remove leading/trailing whitespace
    fact_type = fact_type.strip()
    
    # Check length
    if len(fact_type) < 1 or len(fact_type) > 100:
        return False
    
    # Check for valid characters (letters, numbers, spaces, hyphens, underscores)
    if not re.match(r"^[a-zA-Z0-9\s\-_]+$", fact_type):
        return False
    
    return True


def validate_relation_type(relation_type: str) -> bool:
    """Validate relationship type.
    
    Args:
        relation_type: Relationship type to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not relation_type or not isinstance(relation_type, str):
        return False
    
    # Remove leading/trailing whitespace
    relation_type = relation_type.strip()
    
    # Check length
    if len(relation_type) < 1 or len(relation_type) > 100:
        return False
    
    # Check for valid characters (letters, numbers, spaces, hyphens, underscores)
    if not re.match(r"^[a-zA-Z0-9\s\-_]+$", relation_type):
        return False
    
    return True


def validate_strength(strength: float) -> bool:
    """Validate relationship strength.
    
    Args:
        strength: Strength value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(strength, (int, float)):
        return False
    
    return 0.0 <= strength <= 1.0


def validate_search_query(query: str) -> bool:
    """Validate search query.
    
    Args:
        query: Search query to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not query or not isinstance(query, str):
        return False
    
    # Remove leading/trailing whitespace
    query = query.strip()
    
    # Check minimum length
    if len(query) < 1:
        return False
    
    # Check maximum length
    if len(query) > 1000:
        return False
    
    return True


def validate_limit(limit: int) -> bool:
    """Validate search/query limit.
    
    Args:
        limit: Limit value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(limit, int):
        return False
    
    return 1 <= limit <= 100


def validate_character_id(character_id: int) -> bool:
    """Validate character ID.
    
    Args:
        character_id: Character ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(character_id, int):
        return False
    
    return character_id > 0


def validate_character_ids(character_ids: List[int]) -> bool:
    """Validate list of character IDs.
    
    Args:
        character_ids: List of character IDs to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(character_ids, list):
        return False
    
    # Check minimum number of IDs
    if len(character_ids) < 1:
        return False
    
    # Check maximum number of IDs
    if len(character_ids) > 100:
        return False
    
    # Validate each ID
    for character_id in character_ids:
        if not validate_character_id(character_id):
            return False
    
    # Check for duplicates
    if len(set(character_ids)) != len(character_ids):
        return False
    
    return True


def validate_tool_params(tool_name: str, params: Dict[str, Any]) -> bool:
    """Validate tool parameters.
    
    Args:
        tool_name: Tool name to validate
        params: Tool parameters to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not tool_name or not isinstance(tool_name, str):
        return False
    
    if not isinstance(params, dict):
        return False
    
    return True


def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate tool arguments based on tool name.
    
    Args:
        tool_name: Name of the tool
        arguments: Tool arguments to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if tool_name == "create_character":
            if "name" not in arguments:
                return False, "Missing required field: name"
            if not validate_character_name(arguments["name"]):
                return False, "Invalid character name"
            
            if "description" not in arguments:
                return False, "Missing required field: description"
            if not validate_description(arguments["description"]):
                return False, "Invalid description"
            
            if "tags" in arguments and not validate_tags(arguments["tags"]):
                return False, "Invalid tags"
        
        elif tool_name == "search_characters":
            if "query" not in arguments:
                return False, "Missing required field: query"
            if not validate_search_query(arguments["query"]):
                return False, "Invalid search query"
            
            if "limit" in arguments and not validate_limit(arguments["limit"]):
                return False, "Invalid limit"
        
        elif tool_name == "add_character_fact":
            if "character_id" not in arguments:
                return False, "Missing required field: character_id"
            if not validate_character_id(arguments["character_id"]):
                return False, "Invalid character_id"
            
            if "fact_type" not in arguments:
                return False, "Missing required field: fact_type"
            if not validate_fact_type(arguments["fact_type"]):
                return False, "Invalid fact_type"
            
            if "content" not in arguments:
                return False, "Missing required field: content"
            if not validate_description(arguments["content"]):
                return False, "Invalid content"
        
        elif tool_name == "search_facts":
            if "query" not in arguments:
                return False, "Missing required field: query"
            if not validate_search_query(arguments["query"]):
                return False, "Invalid search query"
            
            if "character_id" in arguments and arguments["character_id"] is not None:
                if not validate_character_id(arguments["character_id"]):
                    return False, "Invalid character_id"
            
            if "fact_type" in arguments and arguments["fact_type"] is not None:
                if not validate_fact_type(arguments["fact_type"]):
                    return False, "Invalid fact_type"
            
            if "limit" in arguments and not validate_limit(arguments["limit"]):
                return False, "Invalid limit"
        
        elif tool_name == "generate_character_tags":
            if "character_id" not in arguments:
                return False, "Missing required field: character_id"
            if not validate_character_id(arguments["character_id"]):
                return False, "Invalid character_id"
        
        elif tool_name == "analyze_character_relationships":
            if "character_ids" not in arguments:
                return False, "Missing required field: character_ids"
            if not validate_character_ids(arguments["character_ids"]):
                return False, "Invalid character_ids"
        
        else:
            return False, f"Unknown tool: {tool_name}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error validating arguments for tool {tool_name}: {e}")
        return False, f"Validation error: {str(e)}"


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input.
    
    Args:
        text: Text to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Apply length limit if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def sanitize_tags(tags: List[str]) -> List[str]:
    """Sanitize list of tags.
    
    Args:
        tags: List of tags to sanitize
        
    Returns:
        Sanitized list of tags
    """
    if not isinstance(tags, list):
        return []
    
    sanitized = []
    for tag in tags:
        if isinstance(tag, str):
            sanitized_tag = sanitize_string(tag, 50)
            if sanitized_tag and re.match(r"^[a-zA-Z0-9\-_]+$", sanitized_tag):
                sanitized.append(sanitized_tag)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in sanitized:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return unique_tags[:50]  # Limit to 50 tags


def validate_character_data(data: Dict[str, Any]) -> bool:
    """Validate character data.
    
    Args:
        data: Character data to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    # Check required fields
    if "name" not in data or "description" not in data:
        return False
    
    # Validate fields
    if not validate_character_name(data["name"]):
        return False
    
    if not validate_description(data["description"]):
        return False
    
    # Validate optional fields
    if "tags" in data and not validate_tags(data["tags"]):
        return False
    
    return True


def validate_fact_data(data: Dict[str, Any]) -> bool:
    """Validate fact data.
    
    Args:
        data: Fact data to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    # Check required fields
    required_fields = ["character_id", "fact_type", "content"]
    for field in required_fields:
        if field not in data:
            return False
    
    # Validate fields
    if not validate_character_id(data["character_id"]):
        return False
    
    if not validate_fact_type(data["fact_type"]):
        return False
    
    if not data["content"] or not isinstance(data["content"], str):
        return False
    
    return True