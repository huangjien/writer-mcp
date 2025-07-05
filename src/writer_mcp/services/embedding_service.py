"""Embedding service for generating and managing vector embeddings."""

from typing import List, Optional
import openai

from ..config import settings
from ..utils.logger import get_logger


logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating and managing vector embeddings."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        self.dimension = settings.vector_dimension
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector or None if generation fails
        """
        try:
            logger.debug(f"Generating embedding for text: {text[:100]}...")
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            
            # Validate embedding dimension
            if len(embedding) != self.dimension:
                logger.warning(
                    f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}"
                )
                return None
            
            logger.debug(f"Generated embedding with dimension {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    async def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors (None for failed generations)
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # OpenAI API supports batch processing
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
                encoding_format="float"
            )
            
            embeddings = []
            for i, data in enumerate(response.data):
                embedding = data.embedding
                
                # Validate embedding dimension
                if len(embedding) != self.dimension:
                    logger.warning(
                        f"Embedding dimension mismatch for text {i}: expected {self.dimension}, got {len(embedding)}"
                    )
                    embeddings.append(None)
                else:
                    embeddings.append(embedding)
            
            successful_count = sum(1 for emb in embeddings if emb is not None)
            logger.info(f"Generated {successful_count}/{len(texts)} embeddings successfully")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return [None] * len(texts)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        try:
            if len(embedding1) != len(embedding2):
                logger.warning("Embedding dimension mismatch for similarity calculation")
                return 0.0
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            
            # Calculate magnitudes
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(b * b for b in embedding2) ** 0.5
            
            # Avoid division by zero
            if magnitude1 == 0.0 or magnitude2 == 0.0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = dot_product / (magnitude1 * magnitude2)
            
            return similarity
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    async def find_similar_embeddings(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        threshold: float = 0.7,
        limit: int = 10
    ) -> List[tuple[int, float]]:
        """Find similar embeddings from a list of candidates.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            threshold: Minimum similarity threshold
            limit: Maximum number of results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate)
                
                if similarity >= threshold:
                    similarities.append((i, similarity))
            
            # Sort by similarity score (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Apply limit
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar embeddings: {e}")
            return []
    
    async def semantic_search(
        self,
        query: str,
        documents: List[str],
        threshold: float = 0.7,
        limit: int = 10
    ) -> List[tuple[int, str, float]]:
        """Perform semantic search on a list of documents.
        
        Args:
            query: Search query
            documents: List of documents to search
            threshold: Minimum similarity threshold
            limit: Maximum number of results to return
            
        Returns:
            List of (index, document, similarity_score) tuples
        """
        try:
            logger.info(f"Performing semantic search: {query}")
            
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Generate document embeddings
            document_embeddings = await self.generate_embeddings(documents)
            
            # Filter out failed embeddings
            valid_embeddings = []
            valid_indices = []
            
            for i, embedding in enumerate(document_embeddings):
                if embedding is not None:
                    valid_embeddings.append(embedding)
                    valid_indices.append(i)
            
            if not valid_embeddings:
                logger.warning("No valid document embeddings generated")
                return []
            
            # Find similar embeddings
            similar_indices = await self.find_similar_embeddings(
                query_embedding,
                valid_embeddings,
                threshold,
                limit
            )
            
            # Map back to original document indices
            results = []
            for embedding_idx, similarity in similar_indices:
                original_idx = valid_indices[embedding_idx]
                document = documents[original_idx]
                results.append((original_idx, document, similarity))
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            return []