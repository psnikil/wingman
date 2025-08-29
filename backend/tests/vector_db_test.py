import asyncio
import sys
import chromadb

sys.path.append("..")

from app.infrastructure.database import chroma_impl
from app.infrastructure.database.vector_db_interface import VectorDBConfig,VectorDBFactory,VectorDBType

class TestVectorDB:
    
    async def test_vector_db(self,db_type:VectorDBType=VectorDBType.CHROMA,host:str=None,port:int=None):
        vector_db_config = VectorDBConfig(
            db_type=db_type,
            host=host,
            port=port,
            collection_name="test_collection",
            # Used in Qdrant
            dimensions=768
        )
        print("Vector DB Config:", vector_db_config)
        # Initialize the vector db
        vector_db =VectorDBFactory.create(vector_db_config)
        await vector_db.initialise(vector_db_config)
        await vector_db.create_collection(vector_db_config.collection_name,vector_db_config.dimensions)

        # Inset the vectors
        test_data = {
                    "ids": [
                        "doc_1",
                        "doc_2",
                        "doc_3",
                        "doc_4",
                        "doc_5"
                        ],
                    "documents": [
                        "Chroma is an open-source embedding database designed for LLM applications.",
                        "Docker helps developers package applications and their dependencies into containers.",
                        "Vector databases enable efficient similarity search across high-dimensional data.",
                        "Machine learning models like GPT-5 use embeddings to understand semantic meaning.",
                        "FastAPI is a modern Python framework for building high-performance APIs."
                        ],
                    "metadatas": [
                        {"category": "database", "topic": "chroma"},
                        {"category": "containerization", "topic": "docker"},
                        {"category": "database", "topic": "vector_search"},
                        {"category": "ai", "topic": "embeddings"},
                        {"category": "framework", "topic": "fastapi"}
                        ]
                    }
        
        await vector_db.insert_vectors(
            ids=test_data["ids"],
            documents=test_data["documents"],
            metadatas = test_data["metadatas"]
        )

        result = await vector_db.search_vectors(
            top_k=2,
            query_texts=["What is ChromaDB used for?"]
        )

        print("Search Results:",result)


async def run_vector_db_tests():

    test = TestVectorDB()
    await test.test_vector_db(db_type=VectorDBType.CHROMA,host="localhost",port=6379)

if __name__ == "__main__":
    asyncio.run(run_vector_db_tests())
        



