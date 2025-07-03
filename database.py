from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ Update this if needed
DATABASE_URL = "mysql+pymysql://root:HsKrEZzYTGNIymDGLgHlHxlSzOefsZcm@tramway.proxy.rlwy.net:45052/railway"


engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
