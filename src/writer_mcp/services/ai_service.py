"""AI service for generating content and analysis."""

from typing import List, Optional, Dict, Any
import openai
import json

from ..config import settings
from ..utils.logger import get_logger
from ..database.models import Character, CharacterFact, CharacterRelation


logger = get_logger(__name__)


class AIService:
    """Service for AI-powered content generation and analysis."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_character_tags(
        self, 
        character: Character, 
        facts: Optional[List[CharacterFact]] = None
    ) -> List[str]:
        """Generate tags for a character using AI.
        
        Args:
            character: Character to generate tags for
            facts: Optional list of character facts for context
            
        Returns:
            List of generated tags
        """
        try:
            logger.info(f"Generating tags for character: {character.name}")
            
            # Build context from character and facts
            context = f"Character: {character.name}\nDescription: {character.description}"
            
            if facts:
                context += "\n\nFacts:"
                for fact in facts:
                    context += f"\n- {fact.fact_type}: {fact.content}"
            
            prompt = f"""
Analyze the following character information and generate relevant tags that describe their key attributes, personality traits, roles, and characteristics.

{context}

Generate 5-10 concise, relevant tags for this character. Return only a JSON array of strings.

Example format: ["warrior", "brave", "loyal", "leader", "noble"]
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates character tags for creative writing. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                tags = json.loads(content)
                if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
                    logger.info(f"Generated {len(tags)} tags for character {character.name}")
                    return tags
                else:
                    logger.warning(f"Invalid tag format received: {content}")
                    return []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {content}")
                return []
            
        except Exception as e:
            logger.error(f"Failed to generate tags for character {character.name}: {e}")
            return []
    
    async def analyze_character_relationships(
        self, 
        characters: List[Character], 
        existing_relations: Optional[List[CharacterRelation]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze relationships between characters using AI.
        
        Args:
            characters: List of characters to analyze
            existing_relations: Optional list of existing relationships
            
        Returns:
            List of relationship analysis results
        """
        try:
            logger.info(f"Analyzing relationships between {len(characters)} characters")
            
            if len(characters) < 2:
                logger.warning("Need at least 2 characters for relationship analysis")
                return []
            
            # Build character context
            character_info = []
            for char in characters:
                character_info.append(f"ID {char.id}: {char.name} - {char.description}")
            
            context = "\n".join(character_info)
            
            # Include existing relationships if available
            existing_context = ""
            if existing_relations:
                existing_context = "\n\nExisting relationships:"
                for rel in existing_relations:
                    existing_context += f"\n- Character {rel.character_a_id} and {rel.character_b_id}: {rel.relation_type} ({rel.description})"
            
            prompt = f"""
Analyze the relationships between these characters and suggest potential new relationships or improvements to existing ones:

{context}{existing_context}

For each potential relationship, provide:
1. The two character IDs involved
2. The type of relationship (e.g., "friend", "rival", "mentor", "family", "romantic", etc.)
3. A brief description of the relationship
4. A strength score from 0.0 to 1.0 (how strong/important the relationship is)

Return the results as a JSON array of objects with the following structure:
[
  {{
    "character_a_id": 1,
    "character_b_id": 2,
    "relation_type": "friend",
    "description": "Close childhood friends who trust each other completely",
    "strength": 0.8
  }}
]

Only suggest meaningful relationships that make sense based on the character descriptions.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes character relationships for creative writing. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                relationships = json.loads(content)
                if isinstance(relationships, list):
                    # Validate each relationship object
                    valid_relationships = []
                    for rel in relationships:
                        if (
                            isinstance(rel, dict) and
                            "character_a_id" in rel and
                            "character_b_id" in rel and
                            "relation_type" in rel and
                            "description" in rel and
                            "strength" in rel
                        ):
                            valid_relationships.append(rel)
                    
                    logger.info(f"Generated {len(valid_relationships)} relationship suggestions")
                    return valid_relationships
                else:
                    logger.warning(f"Invalid relationship format received: {content}")
                    return []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {content}")
                return []
            
        except Exception as e:
            logger.error(f"Failed to analyze character relationships: {e}")
            return []
    
    async def generate_character_summary(
        self, 
        character: Character, 
        facts: Optional[List[CharacterFact]] = None,
        relations: Optional[List[CharacterRelation]] = None
    ) -> Optional[str]:
        """Generate a comprehensive summary of a character.
        
        Args:
            character: Character to summarize
            facts: Optional list of character facts
            relations: Optional list of character relationships
            
        Returns:
            Generated character summary or None if generation fails
        """
        try:
            logger.info(f"Generating summary for character: {character.name}")
            
            # Build context
            context = f"Character: {character.name}\nDescription: {character.description}"
            
            if character.tags:
                context += f"\nTags: {', '.join(character.tags)}"
            
            if facts:
                context += "\n\nFacts:"
                for fact in facts:
                    context += f"\n- {fact.fact_type}: {fact.content}"
            
            if relations:
                context += "\n\nRelationships:"
                for rel in relations:
                    context += f"\n- {rel.relation_type}: {rel.description}"
            
            prompt = f"""
Create a comprehensive character summary based on the following information:

{context}

Write a well-structured summary that captures the character's essence, key traits, background, and relationships. The summary should be engaging and useful for creative writing purposes.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates character summaries for creative writing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"Generated summary for character {character.name}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary for character {character.name}: {e}")
            return None
    
    async def suggest_character_development(
        self, 
        character: Character, 
        context: Optional[str] = None
    ) -> List[str]:
        """Suggest character development ideas.
        
        Args:
            character: Character to develop
            context: Optional story context
            
        Returns:
            List of development suggestions
        """
        try:
            logger.info(f"Generating development suggestions for character: {character.name}")
            
            character_context = f"Character: {character.name}\nDescription: {character.description}"
            
            if character.tags:
                character_context += f"\nTags: {', '.join(character.tags)}"
            
            story_context = f"\n\nStory context: {context}" if context else ""
            
            prompt = f"""
Suggest character development ideas for the following character:

{character_context}{story_context}

Provide 5-8 specific, actionable development suggestions that could help deepen this character. Consider:
- Character growth arcs
- Potential conflicts or challenges
- Skill development
- Relationship dynamics
- Backstory elements to explore

Return the suggestions as a JSON array of strings.

Example format: ["Explore their fear of commitment through a romantic subplot", "Develop their magical abilities through training with a mentor"]
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides character development suggestions for creative writing. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                suggestions = json.loads(content)
                if isinstance(suggestions, list) and all(isinstance(s, str) for s in suggestions):
                    logger.info(f"Generated {len(suggestions)} development suggestions")
                    return suggestions
                else:
                    logger.warning(f"Invalid suggestion format received: {content}")
                    return []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {content}")
                return []
            
        except Exception as e:
            logger.error(f"Failed to generate development suggestions: {e}")
            return []