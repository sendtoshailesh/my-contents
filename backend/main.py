"""
FastAPI Application Entry Point
Main backend server for Personal AI Content Studio
Runs on localhost:8000
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import logging
from pathlib import Path

from backend.models.models import get_db_session, Session as SessionModel, init_db
from backend.utils.logger import setup_logging

# Setup logging
LOG_DIR = Path.home() / ".content-studio"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger = setup_logging("backend", str(LOG_DIR / "app.log"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown event manager"""
    # Startup: Clean up old sessions
    logger.info("🚀 Starting FastAPI application")
    db = get_db_session()
    
    try:
        # Delete sessions older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        old_sessions = db.query(SessionModel).filter(SessionModel.created_at < cutoff_date).all()
        
        if old_sessions:
            logger.info(f"🗑️  Deleting {len(old_sessions)} old sessions")
            for session in old_sessions:
                db.delete(session)
            db.commit()
        
        # Keep only max 10 sessions per user
        db_session = get_db_session()
        user_sessions = db_session.query(SessionModel).order_by(SessionModel.created_at.desc()).all()
        
        if len(user_sessions) > 10:
            logger.info(f"⚠️  Found {len(user_sessions)} sessions, keeping last 10")
            sessions_to_delete = user_sessions[10:]
            for session in sessions_to_delete:
                db.delete(session)
            db.commit()
        
        logger.info("✅ Startup complete")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FastAPI application")


# Initialize app
app = FastAPI(
    title="Personal AI Content Studio",
    description="Local backend for AI-powered content creation",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:8501", "127.0.0.1:8501", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"❌ Unhandled error in {request.method} {request.url.path}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )


# Request/response logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses"""
    logger.debug(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"← {request.method} {request.url.path} {response.status_code}")
    return response


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)


# API Routes (to be added in Phase 2)
# Will be imported from backend.api.routes

# Import and include routes
from backend.api.routes import router

app.include_router(router)

logger.info("✅ API routes registered")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server on http://localhost:8000")
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
