"""
Admin API endpoints for managing API keys and posts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import (
    get_db, APIKey, Post, AdminUser, sync_api_keys_to_env,
    get_current_model, set_current_model, AVAILABLE_MODELS,
)
from models import (
    R,
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyListResponse,
    PostCreate, PostUpdate, PostResponse, PostListResponse,
    AdminLogin, AdminCreate, AdminResponse
)
from auth import get_current_admin, require_super_admin, create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ==================== Authentication ====================

@router.post("/login")
async def admin_login(login_data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login"""
    admin = db.query(AdminUser).filter(AdminUser.username == login_data.username).first()

    if not admin or not verify_password(login_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    access_token = create_access_token(data={"sub": admin.username})
    return R.ok({
        "access_token": access_token,
        "token_type": "bearer",
        "admin": AdminResponse.model_validate(admin).model_dump()
    })


@router.get("/me")
async def get_current_admin_info(
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Get current logged-in admin info"""
    return R.ok(AdminResponse.model_validate(current_admin).model_dump())


@router.post("/logout")
async def admin_logout(
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Admin logout"""
    return R.ok(message="Logged out successfully")


@router.post("/users")
async def create_admin_user(
    admin_data: AdminCreate,
    current_admin: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Create admin user (super admin only)"""
    existing = db.query(AdminUser).filter(
        (AdminUser.username == admin_data.username) | (AdminUser.email == admin_data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    admin = AdminUser(
        username=admin_data.username,
        email=admin_data.email,
        password_hash=get_password_hash(admin_data.password),
        is_super_admin=admin_data.is_super_admin
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return R.ok(AdminResponse.model_validate(admin).model_dump())


# ==================== API Key Management ====================

@router.get("/api-keys/effective")
async def get_effective_api_keys(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get currently effective API key settings (masked values)"""
    import os
    env_map = {"openai": "OPENAI_API_KEY", "google": "GOOGLE_API_KEY"}
    result = {}
    for key_type, env_name in env_map.items():
        # Check database first
        db_key = db.query(APIKey).filter(
            APIKey.key_type == key_type, APIKey.is_active == True
        ).first()
        if db_key and db_key.key_value:
            result[key_type] = {
                "configured": True,
                "masked_value": mask_api_key(db_key.key_value),
                "source": "database",
                "key_name": db_key.key_name,
            }
        elif os.getenv(env_name):
            result[key_type] = {
                "configured": True,
                "masked_value": mask_api_key(os.getenv(env_name)),
                "source": "env",
                "key_name": env_name,
            }
        else:
            result[key_type] = {
                "configured": False,
                "masked_value": None,
                "source": None,
                "key_name": None,
            }
    return R.ok(result)


@router.get("/api-keys")
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all API keys"""
    api_keys = db.query(APIKey).offset(skip).limit(limit).all()
    total = db.query(APIKey).count()

    masked_keys = []
    for key in api_keys:
        masked_keys.append(APIKeyResponse(
            id=key.id,
            key_type=key.key_type,
            key_name=key.key_name,
            key_value=mask_api_key(key.key_value),
            is_active=key.is_active,
            created_at=key.created_at,
            updated_at=key.updated_at,
            created_by=key.created_by,
            description=key.description
        ))

    return R.ok(APIKeyListResponse(api_keys=masked_keys, total=total).model_dump())


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new API key"""
    api_key = APIKey(
        key_type=api_key_data.key_type,
        key_name=api_key_data.key_name,
        key_value=api_key_data.key_value,
        description=api_key_data.description,
        created_by=current_admin.username
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    sync_api_keys_to_env()

    resp = APIKeyResponse(
        id=api_key.id,
        key_type=api_key.key_type,
        key_name=api_key.key_name,
        key_value=mask_api_key(api_key.key_value),
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
        created_by=api_key.created_by,
        description=api_key.description
    )
    return R.ok(resp.model_dump())


@router.get("/api-keys/{key_id}")
async def get_api_key(
    key_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get API key by ID"""
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    resp = APIKeyResponse(
        id=api_key.id,
        key_type=api_key.key_type,
        key_name=api_key.key_name,
        key_value=mask_api_key(api_key.key_value),
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
        created_by=api_key.created_by,
        description=api_key.description
    )
    return R.ok(resp.model_dump())


@router.put("/api-keys/{key_id}")
async def update_api_key(
    key_id: int,
    api_key_data: APIKeyUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update API key"""
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key_data.key_name is not None:
        api_key.key_name = api_key_data.key_name
    if api_key_data.key_value is not None:
        api_key.key_value = api_key_data.key_value
    if api_key_data.is_active is not None:
        api_key.is_active = api_key_data.is_active
    if api_key_data.description is not None:
        api_key.description = api_key_data.description

    api_key.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(api_key)
    sync_api_keys_to_env()

    resp = APIKeyResponse(
        id=api_key.id,
        key_type=api_key.key_type,
        key_name=api_key.key_name,
        key_value=mask_api_key(api_key.key_value),
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
        created_by=api_key.created_by,
        description=api_key.description
    )
    return R.ok(resp.model_dump())


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete API key"""
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()
    sync_api_keys_to_env()
    return R.ok()


def mask_api_key(key_value: str) -> str:
    """Mask API key for display (show first 4 and last 4 characters)"""
    if len(key_value) <= 8:
        return "****"
    return f"{key_value[:4]}...{key_value[-4:]}"


# ==================== Model Management ====================

@router.get("/models")
async def list_models(
    current_admin: AdminUser = Depends(get_current_admin),
):
    """List available AI models"""
    current = get_current_model()
    return R.ok({
        "models": AVAILABLE_MODELS,
        "current": current,
    })


@router.get("/models/current")
async def get_model(
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Get current AI model"""
    return R.ok({"model": get_current_model()})


@router.put("/models/current")
async def update_model(
    payload: dict,
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Set current AI model"""
    model_id = payload.get("model")
    if not model_id:
        raise HTTPException(status_code=400, detail="model is required")

    valid_ids = [m["id"] for m in AVAILABLE_MODELS]
    if model_id not in valid_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model. Available: {', '.join(valid_ids)}"
        )

    set_current_model(model_id)

    # Rebuild agents with new model
    from adk_agents import rebuild_agents
    rebuild_agents()

    return R.ok({"model": model_id})


# ==================== Post Management ====================

@router.get("/posts")
async def list_posts(
    skip: int = 0,
    limit: int = 20,
    language: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all posts, optionally filtered by language"""
    query = db.query(Post)
    if language:
        query = query.filter(Post.language == language)
    posts = query.offset(skip).limit(limit).all()
    total = query.count()

    post_list = []
    for post in posts:
        tags = post.tags.split(",") if post.tags else []
        post_list.append(PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            tags=tags,
            language=post.language or "zh-CN",
            created_at=post.created_at,
            updated_at=post.updated_at,
            is_active=post.is_active
        ))

    resp = PostListResponse(posts=post_list, total=total, page=skip // limit + 1, page_size=limit)
    return R.ok(resp.model_dump())


@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new post"""
    post = Post(
        id=str(uuid.uuid4()),
        title=post_data.title,
        content=post_data.content,
        tags=",".join(post_data.tags) if post_data.tags else None,
        language=post_data.language,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    # Trigger RAG update
    from knowledge_base_agent import _knowledge_base
    try:
        from knowledge_base_agent import Post as KBPost
        kb_post = KBPost(
            id=post.id,
            title=post.title,
            content=post.content,
            tags=post_data.tags,
            language=post_data.language,
        )
        _knowledge_base.add_post(kb_post)
    except Exception as e:
        print(f"Warning: Failed to update RAG vector store: {e}")

    resp = PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        tags=post_data.tags,
        language=post.language or "zh-CN",
        created_at=post.created_at,
        updated_at=post.updated_at,
        is_active=post.is_active
    )
    return R.ok(resp.model_dump())


@router.get("/posts/{post_id}")
async def get_post(
    post_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get post by ID"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    tags = post.tags.split(",") if post.tags else []
    resp = PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        tags=tags,
        language=post.language or "zh-CN",
        created_at=post.created_at,
        updated_at=post.updated_at,
        is_active=post.is_active
    )
    return R.ok(resp.model_dump())


@router.put("/posts/{post_id}")
async def update_post(
    post_id: str,
    post_data: PostUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.tags is not None:
        post.tags = ",".join(post_data.tags) if post_data.tags else None
    if post_data.is_active is not None:
        post.is_active = post_data.is_active
    if post_data.language is not None:
        post.language = post_data.language

    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)

    # Trigger RAG update: reload posts from MySQL first, then rebuild vectors
    from knowledge_base_agent import _knowledge_base
    try:
        _knowledge_base.load_posts()
        _knowledge_base._generate_all_embeddings()
    except Exception as e:
        print(f"Warning: Failed to update RAG vector store: {e}")

    tags = post.tags.split(",") if post.tags else []
    resp = PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        tags=tags,
        language=post.language or "zh-CN",
        created_at=post.created_at,
        updated_at=post.updated_at,
        is_active=post.is_active
    )
    return R.ok(resp.model_dump())


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    # Trigger RAG update: reload posts and rebuild vectors
    from knowledge_base_agent import _knowledge_base
    try:
        _knowledge_base.load_posts()
        _knowledge_base._generate_all_embeddings()
    except Exception as e:
        print(f"Warning: Failed to update RAG vector store: {e}")

    return R.ok()
