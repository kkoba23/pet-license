from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_code = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4())[:8])
    name = Column(String(200), nullable=False)
    issue_location = Column(String(200), nullable=False)
    issue_date = Column(Date, nullable=True)  # Nullの場合は「自動」（アクセス日）
    auto_issue_date = Column(Boolean, default=False)  # 交付日自動設定フラグ
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # リレーション
    licenses = relationship("License", back_populates="event", cascade="all, delete-orphan")


class License(Base):
    """生成された免許証"""
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    receipt_number = Column(String(20), nullable=True, index=True)  # イベント内の受付番号

    # ペット情報
    pet_name = Column(String(100), nullable=False)
    owner_name = Column(String(100), nullable=False)
    animal_type = Column(String(50))
    breed = Column(String(100))
    color = Column(String(50))
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10))

    # その他情報
    favorite_food = Column(String(100))
    favorite_word = Column(String(200))
    microchip_no = Column(String(50))

    # 画像URL
    license_image_url = Column(Text, nullable=False)
    original_image_url = Column(Text, nullable=True)
    s3_license_key = Column(String(500))
    s3_original_key = Column(String(500))

    # タイムスタンプ
    created_at = Column(DateTime, server_default=func.now())

    # リレーション
    event = relationship("Event", back_populates="licenses")
