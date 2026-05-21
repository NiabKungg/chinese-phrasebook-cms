from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from .database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(10), nullable=False, default="📁")
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())

    phrases = relationship("Phrase", back_populates="category", cascade="all, delete-orphan",
                           order_by="Phrase.sort_order")


class Phrase(Base):
    __tablename__ = "phrases"
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    chinese = Column(Text, nullable=False)
    pinyin = Column(Text, nullable=False)
    thai = Column(Text, nullable=False)
    audio_file = Column(String(255), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())

    category = relationship("Category", back_populates="phrases")


class TTSSettings(Base):
    __tablename__ = "tts_settings"

    id = Column(Integer, primary_key=True, index=True)
    voice = Column(String(100), nullable=False, default="zh-CN-XiaoxiaoNeural")
    rate = Column(String(20), nullable=False, default="-10%")
    pitch = Column(String(20), nullable=False, default="+0Hz")


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, unique=True, index=True)
    page_views = Column(Integer, nullable=False, default=1)
    unique_visitors = Column(Integer, nullable=False, default=1)
