from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from pathlib import Path

# .envファイルを明示的に読み込み（インポートより先に実行）
# Docker環境では/app/.env、ローカルでは相対パス
if os.path.exists("/app/.env"):
    env_path = Path("/app/.env")
else:
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(f"[Main] Loading .env from: {env_path}")
print(f"[Main] AWS_ACCESS_KEY_ID loaded: {os.getenv('AWS_ACCESS_KEY_ID')}")
print(f"[Main] AWS_S3_BUCKET loaded: {os.getenv('AWS_S3_BUCKET')}")

# 環境変数読み込み後にインポート
from app.api import pet_license, admin, events, licenses
from app.database import engine, Base, SessionLocal
from app.models.database_models import Admin, Event, License
from app.services.auth_service import create_initial_admin
from sqlalchemy import text, inspect

# データベーステーブル作成
Base.metadata.create_all(bind=engine)

# マイグレーション: 既存テーブルに新しいカラムを追加
def run_migrations():
    """既存データベースに不足しているカラムを追加"""
    inspector = inspect(engine)

    # licensesテーブルの既存カラムを取得
    if 'licenses' in inspector.get_table_names():
        existing_columns = {col['name'] for col in inspector.get_columns('licenses')}

        # receipt_numberカラムを追加
        if 'receipt_number' not in existing_columns:
            print("[Migration] Adding receipt_number column to licenses table")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE licenses ADD COLUMN receipt_number VARCHAR(20)"))
                conn.commit()
            print("[Migration] receipt_number column added successfully")

run_migrations()

# 初期管理者アカウント作成
db = SessionLocal()
try:
    create_initial_admin(db)
finally:
    db.close()

app = FastAPI(
    title="Pet License API",
    description="ペット健康免許証生成API",
    version="1.0.0"
)

# CORS設定
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ストレージディレクトリをマウント（開発モード用）
storage_path = Path("./storage")
storage_path.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# ルーター登録
app.include_router(pet_license.router, prefix="/api", tags=["pet_license"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(licenses.router, prefix="/api/licenses", tags=["licenses"])

@app.get("/")
async def root():
    return {"message": "Pet License API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
