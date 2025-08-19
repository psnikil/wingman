from fastapi import APIRouter, HTTPException
from app.schemas.misc import IsInit
from app.domain.services import IsInitService
from app.infrastructure.ollama.ollama_client import is_ollama_running, start_ollama, list_ollama_models
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.db_models import Base


DATABASE_URL = "postgresql://nikilps:Admin123@localhost:6969/wingman_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

router = APIRouter()
is_init_service = IsInitService()

@router.get("/is_init")
def is_initiated():
    try:
        if not is_ollama_running():
            start_ollama()
            is_init_service.update_init(True)
        
        return IsInit(is_init=True)
    except Exception as e:
        print(f" Error during initialization: {e}")
        is_init_service.update_init(False)
        return IsInit(is_init=False, err_message=str(e))
    
@router.get("/db_startup")
def check_database_started():
    inspector = inspect(engine)

    # check if table Chat exists
    table_exists = 'Chat' in inspector.get_table_names()
    if not table_exists:
        Base.metadata.create_all(bind=engine)

        print("Database and tables created")
    else:
        # this is a print for logs
        print('Database is already initialised')
        
    # status = "initialised " if table_exists else "not initialized"
    return {"db_status":'initialised'}