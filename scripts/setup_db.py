#!/usr/bin/env python3
"""
Database Initialization Script
Creates SQLite database with schema from data-model-LOCAL.md
Storage: ~/.content-studio/sessions.db
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path


def get_db_path():
    """Get or create .content-studio directory and return database path"""
    content_studio_dir = Path.home() / ".content-studio"
    content_studio_dir.mkdir(parents=True, exist_ok=True)
    return content_studio_dir / "sessions.db"


def create_tables():
    """Create all tables from data model"""
    db_path = get_db_path()
    
    # Remove existing DB if running fresh setup
    if db_path.exists():
        print(f"⚠️  Database exists at {db_path}")
        response = input("Override existing database? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return False
        db_path.unlink()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create tables from data model
    
    # sessions: Core session tracking
    cursor.execute("""
    CREATE TABLE sessions (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        url TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'input',
        user_id TEXT DEFAULT 'default',
        session_number INTEGER,
        iteration_count INTEGER DEFAULT 0,
        CONSTRAINT status_check CHECK (status IN (
            'input',
            'outline_review',
            'framework_selection',
            'generating_content',
            'platform_review',
            'iterating',
            'completed',
            'abandoned'
        ))
    )
    """)
    
    # outlines: Generated outlines with validation
    cursor.execute("""
    CREATE TABLE outlines (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL UNIQUE,
        version INTEGER NOT NULL DEFAULT 1,
        content_angle TEXT NOT NULL,
        target_audience TEXT,
        primary_intent TEXT,
        sections TEXT NOT NULL,
        user_approved INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    )
    """)
    
    # validation_reports: Research and fact-checking results
    cursor.execute("""
    CREATE TABLE validation_reports (
        id TEXT PRIMARY KEY,
        outline_id TEXT NOT NULL UNIQUE,
        confidence_score REAL NOT NULL,
        credible_sources_found INTEGER DEFAULT 0,
        claims_checked INTEGER DEFAULT 0,
        validation_details TEXT,
        passed_validation INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (outline_id) REFERENCES outlines(id) ON DELETE CASCADE
    )
    """)
    
    # content_drafts: Generated content with framework
    cursor.execute("""
    CREATE TABLE content_drafts (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL UNIQUE,
        body_text TEXT NOT NULL,
        framework_choice TEXT,
        visual_plan TEXT,
        code_snippets TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    )
    """)
    
    # platform_versions: Platform-specific content
    cursor.execute("""
    CREATE TABLE platform_versions (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        platform_name TEXT NOT NULL,
        version INTEGER NOT NULL DEFAULT 1,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
        UNIQUE(session_id, platform_name)
    )
    """)
    
    # iteration_feedback: Feedback from user refinement cycles
    cursor.execute("""
    CREATE TABLE iteration_feedback (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        iteration_number INTEGER NOT NULL,
        feedback_areas TEXT,
        feedback_text TEXT,
        regenerated_content TEXT,
        affected_components TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    )
    """)
    
    # Reference data tables
    
    # frameworks: Storytelling framework templates
    cursor.execute("""
    CREATE TABLE frameworks (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        template_steps TEXT,
        best_for TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # platforms: Content distribution platforms
    cursor.execute("""
    CREATE TABLE platforms (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        tone TEXT,
        format TEXT,
        min_length INTEGER,
        max_length INTEGER,
        visual_requirements TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # focus_areas: Topic classification
    cursor.execute("""
    CREATE TABLE focus_areas (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)
    
    # visual_types: Visual content options
    cursor.execute("""
    CREATE TABLE visual_types (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        mermaid_capable INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    
    # Create indexes for common queries
    cursor.execute("CREATE INDEX idx_sessions_status ON sessions(status)")
    cursor.execute("CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC)")
    cursor.execute("CREATE INDEX idx_outlines_session_id ON outlines(session_id)")
    cursor.execute("CREATE INDEX idx_content_drafts_session_id ON content_drafts(session_id)")
    cursor.execute("CREATE INDEX idx_platform_versions_session ON platform_versions(session_id)")
    cursor.execute("CREATE INDEX idx_iteration_feedback_session ON iteration_feedback(session_id)")
    
    conn.commit()
    conn.close()
    
    return True


def seed_reference_data():
    """Populate reference data tables"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    # Insert frameworks
    frameworks = [
        ("ted-talk", "TED Talk", "Inspiring insights with personal story", 
         '["Hook", "Build context", "Key insight", "Story examples", "Call to action"]',
         "Tech, personal development, social impact"),
        
        ("heros-journey", "Hero's Journey", "Classic narrative arc with transformation",
         '["Call to action", "Refusal", "Meeting mentor", "Crossing threshold", "Tests", "Ordeal", "Reward", "Return"]',
         "Product launches, personal stories, brand narratives"),
        
        ("problem-solution", "Problem-Solution", "Identify pain, deliver remedy",
         '["The problem", "Why it matters", "Current approaches", "Our solution", "Benefits", "Implementation"]',
         "Business pitches, educational content"),
        
        ("listicle", "Listicle", "Numbered or bulleted key points",
         '["Intro", "Item 1", "Item 2", "Item 3+", "Conclusion"]',
         "Blog posts, quick tips, best practices"),
        
        ("comparison", "Comparison", "Side-by-side analysis of alternatives",
         '["Intro", "Criteria", "Option A", "Option B", "Option C", "Recommendation"]',
         "Product reviews, technology comparisons"),
        
        ("tutorial", "Tutorial", "Step-by-step instructions with outcomes",
         '["Intro & tools needed", "Step 1", "Step 2", "Step 3+", "Expected result", "Troubleshooting"]',
         "How-to guides, technical documentation, skills training"),
    ]
    
    for framework_id, name, desc, steps, best_for in frameworks:
        cursor.execute("""
        INSERT OR IGNORE INTO frameworks (id, name, description, template_steps, best_for, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (framework_id, name, desc, steps, best_for, now))
    
    # Insert platforms
    platforms = [
        ("linkedin", "LinkedIn", "Professional network", "professional, strategic",
         "article, post, thread", 500, 3000, "bullet points, hashtags"),
        
        ("twitter", "Twitter/X", "Real-time conversation", "conversational, concise",
         "thread, post", 280, 28000, "minimal, thread-friendly"),
        
        ("reddit", "Reddit", "Discussion communities", "authentic, engaging",
         "post, comment", 300, 40000, "markdown, community norms"),
        
        ("medium", "Medium", "Curated long-form blog", "narrative, blog-style",
         "article, story", 1000, 10000, "headers, embedded media"),
        
        ("substack", "Substack", "Newsletter platform", "conversational, intimate",
         "newsletter", 800, 8000, "author voice, sections"),
        
        ("instagram", "Instagram", "Visual-first social", "casual, emoji-rich",
         "caption", 100, 2200, "visual-first, emojis"),
    ]
    
    for platform_id, name, desc, tone, fmt, min_len, max_len, visuals in platforms:
        cursor.execute("""
        INSERT OR IGNORE INTO platforms (id, name, description, tone, format, min_length, max_length, visual_requirements, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (platform_id, name, desc, tone, fmt, min_len, max_len, visuals, now))
    
    # Insert focus areas
    focus_areas = [
        ("ai", "AI & LLMs", "Artificial intelligence, large language models, AI safety", 1),
        ("cloud", "Cloud & DevOps", "Cloud platforms, containerization, infrastructure", 1),
        ("migration", "Migration & Modernization", "Application migration, legacy systems", 1),
        ("emotional-intelligence", "Emotional Intelligence", "EQ, leadership, psychology", 1),
        ("emerging-tech", "Emerging Technologies", "Blockchain, Web3, quantum computing", 1),
        ("out-of-scope", "Out of Scope", "Topics outside primary focus areas", 0),
    ]
    
    for area_id, name, desc, active in focus_areas:
        cursor.execute("""
        INSERT OR IGNORE INTO focus_areas (id, name, description, is_active, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (area_id, name, desc, active, now))
    
    # Insert visual types
    visual_types = [
        ("flowchart", "Flowchart", "Process flow diagram", 1),
        ("sequence", "Sequence Diagram", "Interaction flow between entities", 1),
        ("architecture", "Architecture Diagram", "System architecture and components", 1),
        ("mindmap", "Mind Map", "Hierarchical concept mapping", 1),
        ("gantt", "Gantt Chart", "Timeline and project planning", 1),
        ("infographic", "Infographic", "Visual data representation", 0),
        ("photo", "Photo", "Real photograph or image", 0),
        ("illustration", "Illustration", "Custom artwork", 0),
    ]
    
    for visual_id, name, desc, mermaid_capable in visual_types:
        cursor.execute("""
        INSERT OR IGNORE INTO visual_types (id, name, description, mermaid_capable, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (visual_id, name, desc, mermaid_capable, now))
    
    conn.commit()
    conn.close()


def main():
    """Run database setup"""
    print("🗄️  Personal AI Content Studio - Database Setup")
    print("=" * 60)
    
    db_path = get_db_path()
    print(f"📍 Database location: {db_path}")
    
    if create_tables():
        print("✅ Database tables created successfully")
        
        seed_reference_data()
        print("✅ Reference data seeded")
        
        # Verify database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"\n📊 Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   • {table[0]}")
        
        print("\n✨ Setup complete! Ready for implementation.")
    else:
        print("❌ Setup cancelled")


if __name__ == "__main__":
    main()
