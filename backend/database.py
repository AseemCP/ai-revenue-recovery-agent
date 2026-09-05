from sqlalchemy import URL, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="I@seemcppostgressql",
    host="localhost",
    port=5432,
    database="revenue_recovery",
)

engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush=False,
    bind=engine,
)