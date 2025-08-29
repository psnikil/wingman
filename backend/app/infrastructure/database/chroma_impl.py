import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import numpy as np
import uuid
from app.infrastructure.database.vector_db_interface import VectorDBInterface,VectorDBConfig,VectorDBFactory,VectorDBType,SearchResult


class ChromaVectorDB(VectorDBInterface):
    def __init__(self):
        self.client = None
        self.collection = None
        self.config = None

    async def initialise(self, config: VectorDBConfig):
        """Initialise the ChromaDB database"""
        self.config = config

        if config.host == 'Ephemeral':
            # Local instance
            self.client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False)
            )
        elif config.host == 'Persistent':
            # Local instance with persistence
            self.client = chromadb.PersistentClient(
                path='./chroma_db_data',
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            # Remote instance either self-hosted or Chroma Cloud
            print('the config here is',config.host, config.port)
            self.client = chromadb.HttpClient(
                host=config.host,
                port=config.port,
                # settings=Settings(
                #     # chroma_api_impl="rest",
                #     # chroma_server_host=config.host,
                #     # chroma_server_http_port=config.port,
                #     anonymized_telemetry=False
                # )
            )

    async def create_collection(self, name:str, dimensions:int, **kwargs):
        """Create new chroma collection"""
        try:
            self.collection = self.client.create_collection(
                name=name,
                embedding_function=None,
                metadata={"dimensions": dimensions, **kwargs}
            )
        except Exception:
            # collection already exists
            self.collection = self.client.get_collection(name=name)
    
    async def insert_vectors(self,metadatas: List[Dict[str, Any]], 
                             vectors: List[np.ndarray] = None, 
                             ids: Optional[List[str]] = None,
                             **kwargs):
        """Insert vectors into the ChromaDB collection."""
        print("The collection is",self.collection)
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))] #check logic if the id is really unique
        # if self.collection._embedding_function:
        #     # TODO: do something with the embedding function
        #     embeddings = [vec.tolist() for vec in vectors]  # Convert numpy arrays to lists

        self.collection.add(
            embeddings=None,
            metadatas=metadatas,
            ids=ids,
            **kwargs
        )   

    async def search_vectors(self, query_vector: np.ndarray = None, top_k: int = 10, 
                             filter: Optional[Dict[str, Any]] = None,
                             include_content: bool = False,
                             **kwargs) -> List[SearchResult]:
        """  Search chroma db """
        print('the search paranms ars',top_k,kwargs)
        results =self.collection.query(
            query_embeddings= None,
            n_results=top_k,
            where=filter,
            **kwargs
        )
        print("Raw search results:", results)
        search_results = []
        for i in range(len(results['ids'][0])):
            search_results.append(SearchResult(
                id=results['ids'][0][i],
                score=1.0 - results['distances'][0][i],  # Convert distance to similarity
                metadata=results['metadatas'][0][i],
                content=results['documents'][0][i] if results['documents'] else None
            ))
        
        return search_results
    
    async def delete_vectors(self, ids: List[str]):
        """Delete vectors by IDs"""
        self.collection.delete(ids=ids)
    
    async def close(self):
        """Close Chroma client"""
        # Chroma doesn't require explicit closing
        pass

# Register implementation
VectorDBFactory.register(VectorDBType.CHROMA, ChromaVectorDB)
