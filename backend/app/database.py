"""
Database configuration and connection management for BIUAI
Using SQLAlchemy 2.0 with async support
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import asyncio

from app.core.config import settings
from app.models.base import Base

# Global engine instance
engine: AsyncEngine = None
async_session_factory: sessionmaker = None


def create_engine() -> AsyncEngine:
    """Create database engine with optimized settings"""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "server_settings": {
                "application_name": "biuai_backend",
            }
        }
    )


def create_session_factory(engine: AsyncEngine) -> sessionmaker:
    """Create session factory"""
    return sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False,
        autoflush=True,
        autocommit=False
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency for FastAPI
    """
    global async_session_factory
    
    if not async_session_factory:
        await init_db()
    
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database connection and create tables"""
    global engine, async_session_factory
    
    try:
        # Create engine
        engine = create_engine()
        
        # Create session factory
        async_session_factory = create_session_factory(engine)
        
        # Test connection
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            try:
                from app.models import user, financeiro, usuario
                print("✅ Models imported successfully")
            except ImportError as e:
                print(f"⚠️ Warning importing models: {e}")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created/verified")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise


async def close_db():
    """Close database connections gracefully"""
    global engine
    
    if engine:
        await engine.dispose()
        print("✅ Database connections closed")


async def check_db_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False


# Database health check for monitoring
async def get_db_health() -> dict:
    """Get database health status"""
    try:
        is_healthy = await check_db_connection()
        
        # Get basic database info
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            db_version = result.scalar()
            
            result = await conn.execute("SELECT current_database()")
            db_name = result.scalar()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "database": db_name,
            "version": db_version,
            "url": settings.DATABASE_URL.replace(settings.DATABASE_PASSWORD, "***") if hasattr(settings, 'DATABASE_PASSWORD') else "***"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Context manager for manual database sessions
class DatabaseSession:
    """Context manager for database sessions"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = async_session_factory()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


# Utility functions for common database operations
async def execute_query(query: str, params: dict = None):
    """Execute a raw SQL query"""
    async with DatabaseSession() as session:
        result = await session.execute(query, params or {})
        return result


async def get_table_count(table_name: str) -> int:
    """Get count of records in a table"""
    query = f"SELECT COUNT(*) FROM {table_name}"
    result = await execute_query(query)
    return result.scalar()


# Database initialization check
_initialized = False

async def ensure_initialized():
    """Ensure database is initialized"""
    global _initialized
    
    if not _initialized:
        await init_db()
        _initialized = True

# Alias for backward compatibility
get_db = get_session 