"""
This is for the manual startup of db
"""

from sqlalchemy import create_engine
from db_models import Base

DATABASE_URL = "postgresql://nikilps:Admin123@localhost:6969/wingman_db"

engine = create_engine(DATABASE_URL)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    print("Database and tables created")