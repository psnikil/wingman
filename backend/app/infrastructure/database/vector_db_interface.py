from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum



class VectorDBType(Enum):
    CHROMA = "chroma"
    QDRANT = "qdrant"
    # Rest are commeneted out, should test
    # WEAVIATE = "weaviate"
    # PGVECTOR = "pgvector"
    # MILVUS = "milvus"

@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]
    content: Optional[str] = None

@dataclass
class VectorDBConfig:
    db_type: VectorDBType
    host: Optional[str] = None
    port: Optional[int] = None
    dimensions: Optional[int] = None
    api_key: Optional[str] = None
    collection_name: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None

class VectorDBInterface(ABC):
    """Abstract interface for vector database operations."""

    @abstractmethod
    async def initialise(self, config:VectorDBConfig):
        """Initialise the vector database connection."""
        pass
    @abstractmethod
    async def create_collection(self,name:str, dimensions:int, **kwargs):
        """ Create a new collection/index"""
        pass
    @abstractmethod
    async def insert_vectors(self, vectors: List[np.ndarray], 
                             metadata: List[Dict[str, Any]], 
                             ids: Optional[List[str]] = None):
        """Insert vectors into the database."""
        pass

    @abstractmethod
    async def search_vectors(self, query_vector: np.ndarray, top_k: int = 10, 
                             filter: Optional[Dict[str, Any]] = None,
                             include_content: bool = False) -> List[SearchResult]:
        """Search for similar vectors in the database."""
        pass

    @abstractmethod
    async def delete_vectors(self, ids: List[str]):
        """Delete vectors from the database by their IDs."""
        pass

    @abstractmethod
    async def close(self):
        """Close the database connection."""
        pass

class VectorDBFactory:
    """Factory for creating vector database instances."""

    _implementations = {}

    @classmethod
    def register(cls, db_type: VectorDBType, implementation_class):
        """Register a new vector database implementation."""
        cls._implementations[db_type] = implementation_class

    @classmethod
    def create(cls, config: VectorDBConfig) ->  VectorDBInterface:
        """Create a vector database instance"""

        if config.db_type not in cls._implementations:
            print(f'The only supported vector db types are: {list(cls._implementations)}')
            raise ValueError(f"Unsupported vector DB type: {config.db_type},")
        
        return cls._implementations[config.db_type]()
