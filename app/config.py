from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Qdrant Configuration
    QDRANT_URL: Optional[str] = None
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "documents"
    QDRANT_API_KEY: Optional[str] = None

    # Embedding Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Chunking Configuration
    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_CHUNK_OVERLAP: int = 50

    # RAG Configuration
    TOP_K_RETRIEVAL: int = 5
    MAX_CONTEXT_LENGTH: int = 2000

    # Application Configuration
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
