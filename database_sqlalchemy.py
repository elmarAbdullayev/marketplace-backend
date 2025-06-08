from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://marketplace_db_23a6_user:J08kKwtV5Aah6HYgnSBVVnjbMsxbQpAM@dpg-d12not3uibrs73fdqgv0-a.oregon-postgres.render.com/marketplace_db_23a6"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
