"""Text processing utilities for Writer MCP."""

import re
from typing import List, Optional, Set
from collections import Counter

from ..utils.logger import get_logger


logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
    """Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    if not isinstance(text, str) or not text.strip():
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    
    # Filter by length and remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
        'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    filtered_words = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Count word frequency
    word_counts = Counter(filtered_words)
    
    # Return most common words
    keywords = [word for word, _ in word_counts.most_common(max_keywords)]
    
    return keywords


def generate_summary(text: str, max_sentences: int = 3) -> str:
    """Generate a simple extractive summary of text.
    
    Args:
        text: Text to summarize
        max_sentences: Maximum number of sentences in summary
        
    Returns:
        Generated summary
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return text
    
    # Simple scoring based on sentence length and position
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        # Score based on length (prefer medium-length sentences)
        length_score = min(len(sentence.split()) / 20.0, 1.0)
        
        # Score based on position (prefer earlier sentences)
        position_score = 1.0 - (i / len(sentences))
        
        total_score = length_score * 0.7 + position_score * 0.3
        scored_sentences.append((sentence, total_score))
    
    # Sort by score and take top sentences
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    top_sentences = [s[0] for s in scored_sentences[:max_sentences]]
    
    # Maintain original order
    summary_sentences = []
    for sentence in sentences:
        if sentence in top_sentences:
            summary_sentences.append(sentence)
            if len(summary_sentences) >= max_sentences:
                break
    
    return '. '.join(summary_sentences) + '.'


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using Jaccard similarity.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not isinstance(text1, str) or not isinstance(text2, str):
        return 0.0
    
    # Extract keywords from both texts
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 and not keywords2:
        return 1.0 if text1.strip() == text2.strip() else 0.0
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1.union(keywords2))
    
    return intersection / union if union > 0 else 0.0


def extract_character_mentions(text: str, character_names: List[str]) -> List[str]:
    """Extract mentions of character names from text.
    
    Args:
        text: Text to search
        character_names: List of character names to look for
        
    Returns:
        List of mentioned character names
    """
    if not isinstance(text, str) or not character_names:
        return []
    
    mentioned = []
    text_lower = text.lower()
    
    for name in character_names:
        if isinstance(name, str) and name.strip():
            # Create regex pattern for whole word matching
            pattern = r'\b' + re.escape(name.lower()) + r'\b'
            if re.search(pattern, text_lower):
                mentioned.append(name)
    
    return mentioned


def tokenize_text(text: str) -> List[str]:
    """Tokenize text into words.
    
    Args:
        text: Text to tokenize
        
    Returns:
        List of tokens
    """
    if not isinstance(text, str):
        return []
    
    # Extract words (letters only)
    tokens = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    return tokens


def calculate_readability_score(text: str) -> float:
    """Calculate a simple readability score for text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Readability score (higher = more readable)
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0
    
    # Split into sentences and words
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    words = tokenize_text(text)
    
    if not sentences or not words:
        return 0.0
    
    # Calculate metrics
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Simple readability score (lower sentence length and word length = higher score)
    # Normalize to 0-1 range
    sentence_score = max(0, 1 - (avg_sentence_length - 10) / 20)
    word_score = max(0, 1 - (avg_word_length - 4) / 6)
    
    return (sentence_score + word_score) / 2


def find_text_patterns(text: str, patterns: List[str]) -> List[tuple[str, List[str]]]:
    """Find specific patterns in text.
    
    Args:
        text: Text to search
        patterns: List of regex patterns to find
        
    Returns:
        List of (pattern, matches) tuples
    """
    if not isinstance(text, str) or not patterns:
        return []
    
    results = []
    
    for pattern in patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                results.append((pattern, matches))
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
    
    return results


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not isinstance(text, str):
        return ""
    
    # Replace multiple whitespace characters with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not isinstance(text, str):
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.7:  # If we can find a reasonable word boundary
        truncated = truncated[:last_space]
    
    return truncated + suffix


def extract_quoted_text(text: str) -> List[str]:
    """Extract quoted text from a string.
    
    Args:
        text: Text to search
        
    Returns:
        List of quoted strings
    """
    if not isinstance(text, str):
        return []
    
    # Find text in double quotes
    double_quoted = re.findall(r'"([^"]+)"', text)
    
    # Find text in single quotes
    single_quoted = re.findall(r"'([^']+)'", text)
    
    return double_quoted + single_quoted