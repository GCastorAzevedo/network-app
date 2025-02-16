from sqlalchemy import create_engine

# SQLAlchmeny engine using psycopg3. notice Alembic uses psycopg2.
engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres", echo=True
)
