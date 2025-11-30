"""
Knowledge Base Agent with RAG (Retrieval-Augmented Generation)

This module implements a knowledge base agent that can:
- Search through posts/articles
- Answer questions based on retrieved content
- Show related posts and reasoning
"""

from typing import Dict, List, Optional, Tuple
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Try to import LangChain for RAG with OpenAI embeddings (no torch required)
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    RAG_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import paths
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.schema import Document
        RAG_AVAILABLE = True
    except ImportError:
        RAG_AVAILABLE = False
        print("Warning: LangChain with OpenAI embeddings not installed. RAG functionality will not be available.")

from google.adk.agents import Agent
from google.adk.tools import BaseTool
from pydantic import BaseModel, Field


# ==================== Data Models ====================

class Post(BaseModel):
    """Post/Article model"""
    id: str
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None


class SearchResult(BaseModel):
    """Search result model"""
    post_id: str
    title: str
    relevance_score: float
    matched_content: str
    reason: str  # Why this post is relevant


# ==================== Knowledge Base Storage ====================

class KnowledgeBase:
    """
    RAG-based knowledge base for posts with vector embeddings
    
    This implementation uses:
    1. LangChain with OpenAI embeddings for generating embeddings
    2. FAISS vector store for efficient similarity search
    3. Requires OPENAI_API_KEY environment variable
    
    RAG is mandatory - keyword matching fallback is not used.
    In production, you might want to use a vector database like Chroma, Pinecone, or Vertex AI Vector Search
    """
    
    def __init__(self, use_mysql: bool = True):
        """
        Initialize knowledge base with RAG (mandatory)
        
        Args:
            use_mysql: Whether to load posts from MySQL database (default: True)
        
        Raises:
            RuntimeError: If RAG is not available or OPENAI_API_KEY is not set
        """
        if not RAG_AVAILABLE:
            raise RuntimeError(
                "RAG is required but LangChain with OpenAI embeddings is not installed. "
                "Please install: pip install langchain langchain-openai langchain-community"
            )
        
        self.use_mysql = use_mysql
        self.posts: Dict[str, Post] = {}
        
        # Initialize embedding model and vector store (RAG is mandatory)
        self.embeddings = None
        self.vector_store = None
        
        try:
            # Get OpenAI API key from database or environment
            openai_api_key = self._get_openai_api_key()
            if not openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found. Please set it in the admin panel or environment variable."
                )
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            print("RAG enabled: Using LangChain with OpenAI embeddings for semantic search")
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize RAG: {e}. "
                "RAG is required for this knowledge base. Please ensure OPENAI_API_KEY is set correctly."
            ) from e
        
        self.load_posts()
        
        # Generate embeddings for existing posts
        self._generate_all_embeddings()
    
    def _get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from database or environment"""
        # First try database
        if self.use_mysql:
            try:
                from database import SessionLocal, APIKey
                db = SessionLocal()
                try:
                    api_key = db.query(APIKey).filter(
                        APIKey.key_type == 'openai',
                        APIKey.is_active == True
                    ).first()
                    if api_key:
                        return api_key.key_value
                finally:
                    db.close()
            except Exception as e:
                print(f"Warning: Could not load API key from database: {e}")
        
        # Fallback to environment variable
        return os.getenv('OPENAI_API_KEY')
    
    def load_posts(self):
        """Load posts from MySQL database or JSON file"""
        if self.use_mysql:
            try:
                from database import SessionLocal
                db = SessionLocal()
                try:
                    from database import Post as DBPost
                    db_posts = db.query(DBPost).filter(DBPost.is_active == True).all()
                    for db_post in db_posts:
                        tags = db_post.tags.split(",") if db_post.tags else []
                        post = Post(
                            id=db_post.id,
                            title=db_post.title,
                            content=db_post.content,
                            tags=tags,
                            created_at=db_post.created_at.isoformat() if db_post.created_at else None
                        )
                        self.posts[post.id] = post
                    print(f"Loaded {len(self.posts)} posts from MySQL database")
                finally:
                    db.close()
            except Exception as e:
                print(f"Error loading posts from MySQL: {e}")
                print("Falling back to empty posts list")
        else:
            # Fallback to JSON file (for backward compatibility)
            storage_path = "knowledge_base.json"
            if os.path.exists(storage_path):
                try:
                    with open(storage_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for post_data in data.get('posts', []):
                            post = Post(**post_data)
                            self.posts[post.id] = post
                    print(f"Loaded {len(self.posts)} posts from {storage_path}")
                except Exception as e:
                    print(f"Error loading posts from JSON: {e}")
    
    def save_posts(self):
        """Save posts to MySQL database"""
        if self.use_mysql:
            try:
                from database import SessionLocal
                from database import Post as DBPost
                db = SessionLocal()
                try:
                    # Posts are saved via admin API, this is just for backward compatibility
                    print(f"Posts are managed via MySQL database (current count: {len(self.posts)})")
                finally:
                    db.close()
            except Exception as e:
                print(f"Error saving posts to MySQL: {e}")
        else:
            # Fallback to JSON file (for backward compatibility)
            storage_path = "knowledge_base.json"
            try:
                data = {
                    'posts': [post.model_dump() for post in self.posts.values()]
                }
                with open(storage_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Saved {len(self.posts)} posts to {storage_path}")
            except Exception as e:
                print(f"Error saving posts to JSON: {e}")
    
    def add_post(self, post: Post):
        """Add a new post"""
        self.posts[post.id] = post
        self.save_posts()
        
        # Add to vector store (RAG is mandatory)
        if self.embeddings and self.vector_store:
            self._add_post_to_vector_store(post)
    
    def search_posts(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """
        Search posts using RAG (vector embeddings)
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of search results with relevance scores
        
        Raises:
            RuntimeError: If RAG is not properly initialized
        """
        if not self.vector_store:
            raise RuntimeError(
                "Vector store is not initialized. RAG requires a properly initialized vector store."
            )
        return self._search_with_rag(query, top_k)
    
    def _search_with_rag(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """
        RAG-based search using LangChain FAISS vector store
        
        This is the core RAG implementation:
        1. Use FAISS similarity search to find relevant documents
        2. Extract post information from search results
        3. Return top-k most similar posts
        """
        try:
            # Perform similarity search using FAISS
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            results = []
            for doc, score in docs_with_scores:
                # Extract post_id from document metadata
                post_id = doc.metadata.get('post_id')
                if post_id and post_id in self.posts:
                    post = self.posts[post_id]
                    
                    # Convert distance to similarity score (lower distance = higher similarity)
                    # FAISS returns distance, so we convert it to similarity
                    similarity_score = 1.0 / (1.0 + float(score)) if score > 0 else 1.0
                    
                    # Extract relevant snippet
                    matched_content = self._extract_relevant_snippet_semantic(post.content, query, max_length=200)
                    
                    # Generate reason based on similarity
                    reason = f"Semantic similarity: {similarity_score:.3f}"
                    if post.tags:
                        reason += f"; Tags: {', '.join(post.tags)}"
                    
                    results.append(SearchResult(
                        post_id=post.id,
                        title=post.title,
                        relevance_score=similarity_score,
                        matched_content=matched_content,
                        reason=reason
                    ))
            
            return results
        except Exception as e:
            raise RuntimeError(f"RAG search failed: {e}. Please ensure RAG is properly configured.") from e
    
    
    def _generate_all_embeddings(self):
        """Generate embeddings and create vector store for all posts"""
        if not self.embeddings:
            return
        
        print("Generating embeddings for all posts using LangChain...")
        
        # Create documents from posts
        documents = []
        for post_id, post in self.posts.items():
            # Combine title and content for embedding
            text = f"{post.title}. {post.content}"
            doc = Document(
                page_content=text,
                metadata={
                    'post_id': post.id,
                    'title': post.title,
                    'tags': ', '.join(post.tags) if post.tags else ''
                }
            )
            documents.append(doc)
        
        if documents:
            try:
                # Create FAISS vector store from documents
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                print(f"Created vector store with {len(documents)} posts")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create vector store: {e}. "
                    "RAG is required. Please ensure embeddings are properly initialized."
                ) from e
    
    def _add_post_to_vector_store(self, post: Post):
        """Add a single post to the vector store"""
        if not self.embeddings or not self.vector_store:
            return
        
        try:
            # Create document from post
            text = f"{post.title}. {post.content}"
            doc = Document(
                page_content=text,
                metadata={
                    'post_id': post.id,
                    'title': post.title,
                    'tags': ', '.join(post.tags) if post.tags else ''
                }
            )
            # Add document to existing vector store
            self.vector_store.add_documents([doc])
        except Exception as e:
            print(f"Failed to add post to vector store: {e}")
    
    def _extract_relevant_snippet_semantic(self, content: str, query: str, max_length: int = 200) -> str:
        """Extract relevant snippet using semantic similarity"""
        # Simple approach: return beginning of content
        # In production, you might want to chunk content and find most relevant chunks
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content
    


# ==================== ADK Tool for Knowledge Base Search ====================

# Global knowledge base instance (uses MySQL by default)
_knowledge_base = KnowledgeBase(use_mysql=True)


def search_knowledge_base(query: str, top_k: int = 3) -> Dict:
    """
    Search the knowledge base for relevant posts
    
    This is a tool function that ADK agents can use
    
    Args:
        query: Search query
        top_k: Number of results to return
    
    Returns:
        Dictionary with search results
    """
    results = _knowledge_base.search_posts(query, top_k)
    
    if not results:
        return {
            "status": "not_found",
            "message": "No relevant posts found for your query.",
            "query": query,
            "results": []
        }
    
    return {
        "status": "found",
        "query": query,
        "results_count": len(results),
        "results": [
            {
                "post_id": r.post_id,
                "title": r.title,
                "relevance_score": r.relevance_score,
                "matched_content": r.matched_content,
                "reason": r.reason
            }
            for r in results
        ]
    }


def add_post_to_knowledge_base(title: str, content: str, tags: List[str] = None, post_id: Optional[str] = None) -> Dict:
    """
    Add a new post to the knowledge base
    
    Args:
        title: Post title
        content: Post content
        tags: List of tags
        post_id: Optional post ID (auto-generated if not provided)
    
    Returns:
        Dictionary with status and post info
    """
    import uuid
    
    if post_id is None:
        post_id = str(uuid.uuid4())
    
    post = Post(
        id=post_id,
        title=title,
        content=content,
        tags=tags or []
    )
    
    _knowledge_base.add_post(post)
    
    return {
        "status": "success",
        "message": "Post added successfully",
        "post_id": post_id,
        "title": title
    }


# ==================== Knowledge Base Agent ====================

def create_knowledge_base_agent() -> Agent:
    """
    Create a knowledge base agent that can answer questions from posts
    
    Returns:
        Agent instance configured for knowledge base queries
    """
    return Agent(
        model='gemini-2.0-flash-exp',
        name='knowledge_base_agent',
        description="""
        A knowledge base assistant that answers questions by searching through posts/articles.
        If no relevant posts are found, it will say that nothing was found and cannot solve the question.
        When answering, it always shows the related posts and explains why they are relevant.
        """,
        instruction="""
        You are a helpful knowledge base assistant. Your job is to answer user questions by searching 
        through available posts/articles.
        
        IMPORTANT RULES:
        1. ALWAYS use the search_knowledge_base tool first when a user asks a question
        2. If search_knowledge_base returns status "not_found", you MUST say:
           "I couldn't find any relevant posts to answer your question. I cannot solve this based on the available knowledge base."
        3. If search_knowledge_base returns results, you MUST:
           - Answer the question based on the retrieved posts
           - List ALL related posts with their titles
           - Explain WHY each post is relevant (use the "reason" field from results)
           - Cite the post IDs when referencing information
        
        Example response format when posts are found:
        "Based on the knowledge base, [your answer].
        
        Related posts:
        1. [Post Title] (ID: [post_id])
           Reason: [reason from search result]
           Relevant content: [matched_content]
        
        2. [Post Title] (ID: [post_id])
           Reason: [reason from search result]
           Relevant content: [matched_content]"
        
        Example response when nothing found:
        "I couldn't find any relevant posts to answer your question. I cannot solve this based on the available knowledge base."
        """,
        tools=[search_knowledge_base, add_post_to_knowledge_base]
    )


# ==================== Helper Functions ====================

def initialize_sample_posts():
    """Initialize knowledge base with sample posts"""
    sample_posts = [
        Post(
            id="post_001",
            title="Python Virtual Environment Guide",
            content="Python virtual environments are essential tools for isolating project dependencies. Use 'python -m venv venv' to create a virtual environment, and 'source venv/bin/activate' to activate it. Virtual environments help avoid dependency conflicts between different projects.",
            tags=["Python", "Virtual Environment", "Development Tools"]
        ),
        Post(
            id="post_002",
            title="FastAPI Quick Start",
            content="FastAPI is a modern, fast web framework. It's based on Python type hints and automatically generates API documentation. Use the @app.get() decorator to define routes, and it supports asynchronous request handling.",
            tags=["FastAPI", "Python", "Web Development"]
        ),
        Post(
            id="post_003",
            title="Google ADK Agent Development",
            content="Google ADK (Agent Development Kit) is a framework for building AI agents. It supports custom tools, plugins, and multi-agent systems. Use the Agent class to create agents, and run them through the Runner.",
            tags=["Google ADK", "AI", "Agent Development"]
        )
    ]
    
    for post in sample_posts:
        _knowledge_base.add_post(post)
    
    print(f"Initialized knowledge base with {len(sample_posts)} sample posts")


# Initialize with sample data if knowledge base is empty
if len(_knowledge_base.posts) == 0:
    initialize_sample_posts()

