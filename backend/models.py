"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ==================== Post Models ====================

class PostCreate(BaseModel):
    """Create post request model"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = Field(default_factory=list)


class PostUpdate(BaseModel):
    """Update post request model"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class PostResponse(BaseModel):
    """Post response model"""
    id: str
    title: str
    content: str
    tags: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Post list response model"""
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int


# ==================== API Key Models ====================

class APIKeyCreate(BaseModel):
    """Create API key request model"""
    key_type: str = Field(..., pattern="^(openai|google)$")
    key_name: str = Field(..., min_length=1, max_length=100)
    key_value: str = Field(..., min_length=1)
    description: Optional[str] = None


class APIKeyUpdate(BaseModel):
    """Update API key request model"""
    key_name: Optional[str] = Field(None, min_length=1, max_length=100)
    key_value: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None
    description: Optional[str] = None


class APIKeyResponse(BaseModel):
    """API key response model (key_value is masked)"""
    id: int
    key_type: str
    key_name: str
    key_value: str  # Masked value
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """API key list response model"""
    api_keys: List[APIKeyResponse]
    total: int


# ==================== Admin Models ====================

class AdminLogin(BaseModel):
    """Admin login request model"""
    username: str
    password: str


class AdminCreate(BaseModel):
    """Create admin user request model"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_super_admin: bool = False


class AdminResponse(BaseModel):
    """Admin user response model"""
    id: int
    username: str
    email: str
    is_active: bool
    is_super_admin: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== Search Models ====================

class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)


class SearchResult(BaseModel):
    """Search result model"""
    post_id: str
    title: str
    relevance_score: float
    matched_content: str
    reason: str


class SearchResponse(BaseModel):
    """Search response model"""
    status: str
    query: str
    results_count: int
    results: List[SearchResult]
    message: Optional[str] = None

