"""
PC Web API endpoints for public access
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db, Post
from models import R, PostResponse, PostListResponse, SearchRequest, SearchResponse
from knowledge_base_agent import search_knowledge_base, _knowledge_base

router = APIRouter(prefix="/api/web", tags=["Web"])


# ==================== Post Endpoints ====================

@router.get("/posts")
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List active posts (public access)"""
    posts = db.query(Post).filter(Post.is_active == True).offset(skip).limit(limit).all()
    total = db.query(Post).filter(Post.is_active == True).count()

    post_list = []
    for post in posts:
        tags = post.tags.split(",") if post.tags else []
        post_list.append(PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            tags=tags,
            created_at=post.created_at,
            updated_at=post.updated_at,
            is_active=post.is_active
        ))

    resp = PostListResponse(posts=post_list, total=total, page=skip // limit + 1, page_size=limit)
    return R.ok(resp.model_dump())


@router.get("/posts/{post_id}")
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """Get post by ID (public access)"""
    post = db.query(Post).filter(Post.id == post_id, Post.is_active == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    tags = post.tags.split(",") if post.tags else []
    resp = PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        tags=tags,
        created_at=post.created_at,
        updated_at=post.updated_at,
        is_active=post.is_active
    )
    return R.ok(resp.model_dump())


# ==================== Search Endpoints ====================

@router.post("/search")
async def search_posts(search_request: SearchRequest):
    """Search posts using RAG (public access)"""
    try:
        result = search_knowledge_base(search_request.query, search_request.top_k)
        return R.ok(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search")
async def search_posts_get(
    query: str = Query(..., min_length=1),
    top_k: int = Query(3, ge=1, le=20)
):
    """Search posts using RAG (GET method, public access)"""
    try:
        result = search_knowledge_base(query, top_k)
        return R.ok(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
