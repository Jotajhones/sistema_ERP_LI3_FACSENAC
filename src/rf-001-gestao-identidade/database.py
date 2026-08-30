import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/iam_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)