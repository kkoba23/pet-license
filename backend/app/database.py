from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# SQLiteデータベースファイルのパス
# Docker環境では/app/dataを使用、それ以外は相対パス
if os.path.exists("/app"):
    DATABASE_PATH = Path("/app/data/pet_license.db")
else:
    DATABASE_PATH = Path(__file__).parent.parent / "data" / "pet_license.db"
DATABASE_PATH.parent.mkdir(exist_ok=True)

print(f"[Database] Using database path: {DATABASE_PATH}")
print(f"[Database] Database exists: {DATABASE_PATH.exists()}")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
