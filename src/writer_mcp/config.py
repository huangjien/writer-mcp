"""Configuration management for Writer MCP."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # 应用配置
    app_name: str = Field("Writer MCP", description="Application name")
    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Logging level")
    
    # 数据库配置
    database_url: str = Field(..., description="PostgreSQL database URL")
    test_database_url: Optional[str] = Field(None, description="Test database URL")
    database_pool_size: int = Field(10, description="Database connection pool size")
    
    # OpenAI 配置
    openai_api_key: str = Field(..., description="OpenAI API key")
    chat_model: str = Field("gpt-4o-mini", description="OpenAI model for text generation")
    embedding_model: str = Field(
        "text-embedding-3-small", description="OpenAI model for embeddings"
    )
    
    # 向量配置
    vector_dimension: int = Field(1536, description="Vector embedding dimension")
    
    # 搜索配置
    default_search_limit: int = Field(10, description="Default search result limit")
    max_search_limit: int = Field(100, description="Maximum search result limit")
    
    # MCP 服务器配置
    mcp_server_name: str = Field("writer-mcp", description="MCP server name")
    mcp_server_version: str = Field("0.1.0", description="MCP server version")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
        
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug
        
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


# Global settings instance
settings = Settings()