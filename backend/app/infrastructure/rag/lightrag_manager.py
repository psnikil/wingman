import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc
from app.infrastructure.database.vector_db_interface import VectorDBFactory,VectorDBConfig,VectorDBType


class LightRAGManager:
    def __init__(self, vector_db_type: VectorDBType = VectorDBType.CHROMA):
        self.vector_db_type = vector_db_type
        self.rag = None
        self.vector_db = None

    #TODO make this location common among database and rag
    async def initialise_rag(self, work_dir:str = "./rag_storage"): 

        vector_db_config = VectorDBConfig(
            db_type=self.vector_db_type,
            host=os.getenv("VECTOR_DB_HOST","localhost") ,
            port=int(os.getenv("VECTOR_DB_PORT", self.get_default_port())),
            collection_name=os.getenv("VECTOR_DB_COLLECTION","documents"),
            # Assuming 768 dimensions for Ollama embeddings
            dimensions=int(os.getenv("EMBEDDING_DIM", 768))  
        )

        self.vector_db = VectorDBFactory.create(vector_db_config)
        await self.vector_db.initialise(vector_db_config)
        await self.vector_db.create_collection(
            vector_db_config.collection_name, 
            vector_db_config.dimensions
            )

        storage_config = self.get_storage_config()

        self.rag = LightRAG(
            working_dir=work_dir,

            # LL config
            llm_model_func= ollama_model_complete,
            llm_model_name= "qwen2.5:7b",
            llm_model_max_async=4,
            llm_model_max_token_size=32768,
            llm_model_kwargs={
                "host": "http://localhost:11434",
                "options": {"num_ctx": 32768}
            },

            embedding_func=EmbeddingFunc(
                embedding_dim=int(os.getenv("EMBEDDING_DIM", 768)),
                max_token_size=8192,
                func= lambda texts: ollama_embed(
                    texts,
                    embed_model=os.getenv("EMBEDDING_MODEL", "bge-m3"),
                    host="http://localhost:11434"
                )
            ),

            **storage_config
        )


        await self.rag.initialize_storages()

        return self.rag
    
    def _get_default_port(self) -> int:
        """Get default port for vector database"""
        port_map = {
            VectorDBType.CHROMA: 6379,
            VectorDBType.QDRANT: 6333,
            VectorDBType.WEAVIATE: 8080,
            VectorDBType.PGVECTOR: 5432,
            VectorDBType.MILVUS: 19530
        }
        return port_map.get(self.vector_db_type, 6379)
    
    def _get_storage_config(self) -> dict:
        """Get storage configuration based on vector database type"""
        if self.vector_db_type == VectorDBType.PGVECTOR:
            return {
                "kv_storage": "PGKVStorage",
                "vector_storage": "PGVectorStorage",
                "graph_storage": "PGGraphStorage",
                "doc_status_storage": "PGDocStatusStorage"
            }
        # TODO add chroma vector db specific storage configs
        else:
            # Default to file-based storage with custom vector DB
            return {
                "kv_storage": "JsonKVStorage",
                "vector_storage": "CustomVectorStorage",
                "graph_storage": "NetworkXStorage",
                "doc_status_storage": "JsonDocStatusStorage"
            }
    async def cleanup(self):
        """Cleanup resources"""
        if self.rag:
            await self.rag.finalize_storages()
        if self.vector_db:
            await self.vector_db.close()