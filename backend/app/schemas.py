from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = Field(default="📁", max_length=10)
    sort_order: int = Field(default=0)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=10)
    sort_order: Optional[int] = None


class CategoryOut(CategoryBase):
    id: int
    phrase_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class PhraseBase(BaseModel):
    chinese: str = Field(..., min_length=1)
    pinyin: str = Field(..., min_length=1)
    thai: str = Field(..., min_length=1)
    category_id: int
    sort_order: int = Field(default=0)


class PhraseCreate(PhraseBase):
    pass


class PhraseUpdate(BaseModel):
    chinese: Optional[str] = Field(None, min_length=1)
    pinyin: Optional[str] = Field(None, min_length=1)
    thai: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None
    sort_order: Optional[int] = None


class PhraseOut(PhraseBase):
    id: int
    audio_file: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TTSSettingsBase(BaseModel):
    voice: str = Field(default="zh-CN-XiaoxiaoNeural", max_length=100)
    rate: str = Field(default="-10%", max_length=20)
    pitch: str = Field(default="+0Hz", max_length=20)


class TTSSettingsOut(TTSSettingsBase):
    id: int

    model_config = {"from_attributes": True}


class AnalyticsOut(BaseModel):
    date: str
    page_views: int
    unique_visitors: int

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_phrases: int
    total_categories: int
    total_page_views: int
    today_views: int
    phrases_with_audio: int
    phrases_missing_audio: int
