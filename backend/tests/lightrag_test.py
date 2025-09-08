import asyncio
from app.infrastructure.rag.lightrag_manager import LightRAGManager
from app.infrastructure.database.vector_db_interface import VectorDBConfig,VectorDBFactory,VectorDBType
from app.infrastructure.database import chroma_impl
from lightrag import QueryParam

class TestLightRAG:

    async def test_lightRag_init(self, vector_db_type: VectorDBType = VectorDBType.CHROMA):
        
        rag_manager = LightRAGManager(vector_db_type=vector_db_type)

        try:
            rag = await rag_manager.initialise_rag(work_dir="./test_rag_storage")
            print("LightRAG initialized successfully with vector DB:", vector_db_type)

            await rag.ainsert("This is a test document for LightRAG.")
            print("Document inserted successfully.")

            result =  await rag.aquery(
                "What is this document about?"
                param=QueryParam(mode="naive")
            )

            print(f"✅ Query successful: {result[:100]}...")

        except Exception as e:
            print(f"❌ Error: {e}")
            raise
        finally:
            await rag_manager.cleanup()


async def run_lightRag_tests(self, vector_db_type: VectorDBType = VectorDBType.CHROMA):

    
    lightRag_test = TestLightRAG()
    await lightRag_test.test_lightRag_init(vector_db_type=vector_db_type)


if __name__ == "__main__":

    asyncio.run(run_lightRag_tests())
