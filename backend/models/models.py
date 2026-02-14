"""
SQLAlchemy ORM Models
Mirrors the SQLite schema from data-model-LOCAL.md
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey, Index, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pathlib import Path
import uuid

Base = declarative_base()


class Session(Base):
    """Core session tracking"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String, nullable=False)
    url = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, nullable=False, default='input')  # input, outline_review, framework_selection, generating_content, platform_review, iterating, completed, abandoned
    user_id = Column(String, default='default')
    session_number = Column(Integer)
    iteration_count = Column(Integer, default=0)
    
    # Relationships
    outline = relationship("Outline", back_populates="session", uselist=False, cascade="all, delete-orphan")
    content_draft = relationship("ContentDraft", back_populates="session", uselist=False, cascade="all, delete-orphan")
    platform_versions = relationship("PlatformVersion", back_populates="session", cascade="all, delete-orphan")
    iteration_feedback = relationship("IterationFeedback", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_sessions_status', 'status'),
        Index('idx_sessions_created_at', 'created_at'),
    )


class Outline(Base):
    """Generated outlines with validation"""
    __tablename__ = "outlines"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, unique=True)
    version = Column(Integer, nullable=False, default=1)
    content_angle = Column(String, nullable=False)
    target_audience = Column(String)
    primary_intent = Column(String)
    sections = Column(Text, nullable=False)  # JSON array of section objects
    user_approved = Column(Integer, default=0)  # 0=not approved, 1=approved
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="outline")
    validation_report = relationship("ValidationReport", back_populates="outline", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_outlines_session_id', 'session_id'),
    )


class ValidationReport(Base):
    """Research and fact-checking results"""
    __tablename__ = "validation_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    outline_id = Column(String, ForeignKey('outlines.id', ondelete='CASCADE'), nullable=False, unique=True)
    confidence_score = Column(Float, nullable=False)  # 0-1 scale
    credible_sources_found = Column(Integer, default=0)
    claims_checked = Column(Integer, default=0)
    validation_details = Column(Text)  # JSON object with detailed validation info
    passed_validation = Column(Integer, default=0)  # 0=failed (confidence < 0.7), 1=passed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    outline = relationship("Outline", back_populates="validation_report")


class ContentDraft(Base):
    """Generated content with framework"""
    __tablename__ = "content_drafts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, unique=True)
    body_text = Column(Text, nullable=False)
    framework_choice = Column(String)  # framework name or ID
    visual_plan = Column(Text)  # JSON array of visual objects
    code_snippets = Column(Text)  # JSON array of code examples
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="content_draft")
    
    __table_args__ = (
        Index('idx_content_drafts_session_id', 'session_id'),
    )


class PlatformVersion(Base):
    """Platform-specific content"""
    __tablename__ = "platform_versions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    platform_name = Column(String, nullable=False)  # linkedin, twitter, reddit, medium, substack, instagram
    version = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="platform_versions")
    
    __table_args__ = (
        Index('idx_platform_versions_session', 'session_id'),
    )


class IterationFeedback(Base):
    """Feedback from user refinement cycles"""
    __tablename__ = "iteration_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    iteration_number = Column(Integer, nullable=False)
    feedback_areas = Column(Text)  # JSON array of feedback area names
    feedback_text = Column(Text)
    regenerated_content = Column(Text)  # JSON object with updated content
    affected_components = Column(Text)  # JSON array of component names
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="iteration_feedback")
    
    __table_args__ = (
        Index('idx_iteration_feedback_session', 'session_id'),
    )


# Reference Data Models

class Framework(Base):
    """Storytelling framework templates"""
    __tablename__ = "frameworks"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    template_steps = Column(Text)  # JSON array
    best_for = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Platform(Base):
    """Content distribution platforms"""
    __tablename__ = "platforms"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    tone = Column(String)
    format = Column(String)
    min_length = Column(Integer)
    max_length = Column(Integer)
    visual_requirements = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class FocusArea(Base):
    """Topic classification"""
    __tablename__ = "focus_areas"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class VisualType(Base):
    """Visual content options"""
    __tablename__ = "visual_types"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    mermaid_capable = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# Database connection helper
def get_db_engine():
    """Get SQLAlchemy engine for local SQLite database"""
    db_path = Path.home() / ".content-studio" / "sessions.db"
    return create_engine(f"sqlite:///{db_path}")


def get_db_session():
    """Get SQLAlchemy session"""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initialize database (create tables if not exist)"""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
