from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database file path
DATABASE_URL = "sqlite:///./converted_data.sqlite"

# Setup SQLite Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
